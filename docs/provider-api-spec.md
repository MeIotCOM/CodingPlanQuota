# Coding Plan 套餐额度查询接口规格

> 本文档从 cc-switch 源码（`src-tauri/src/services/coding_plan.rs` 及 `subscription.rs`）逐行提取，
> 是 CodingPlanQuota App 数据层的唯一事实来源。所有解析规则、鉴权细节、边界情况均与 cc-switch
> v3.20.x 的实现对齐。供应商接口均为**非官方文档化接口**，上游变更时以 cc-switch 仓库为
> 跟踪对象同步修订本文档。

## 1. 共享数据模型

### 1.1 窗口层（QuotaTier）

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | 窗口标识，见下方常量表 |
| `utilization` | number | **已用**百分比 0–100（注意：MiniMax 上游给的是剩余，需反转） |
| `resetsAt` | string \| null | 重置时间，统一归一化为 ISO 8601 字符串 |
| `usedValueUsd` | number \| null | 已用美元额度（仅 ZenMux 返回） |
| `maxValueUsd` | number \| null | 窗口美元上限（仅 ZenMux 返回） |

窗口名常量（与 cc-switch `subscription.rs:301-313` 对齐）：

| 常量 | 值 | 语义 |
|---|---|---|
| `TIER_FIVE_HOUR` | `five_hour` | 5 小时滚动窗口 |
| `TIER_WEEKLY_LIMIT` | `weekly_limit` | 周（7 天）窗口 |
| `TIER_MONTHLY` | `monthly` | 月窗口（火山、OpenCode Go 有） |

### 1.2 查询结果（QuotaResult）

| 字段 | 类型 | 说明 |
|---|---|---|
| `success` | boolean | 查询是否成功 |
| `credentialExpired` | boolean | 401/403 → Key 无效，UI 应提示重新录入 |
| `message` | string \| null | 套餐等级等附加信息（智谱 `level`、ZenMux plan tier） |
| `error` | string \| null | 确定性失败的错误文案 |
| `tiers` | QuotaTier[] | 窗口列表 |
| `queriedAt` | number | 查询时间戳（毫秒） |

### 1.3 错误处理约定（与 cc-switch 一致）

- **瞬时失败**（网络错误、超时、连接中断）：抛异常 / reject → UI 可重试，并保留上次成功值；
- **确定性失败**（401/403、非 2xx、业务错误码、JSON 解析失败）：返回 `success: false` + 错误文案，不重试。
- HTTP 401/403 统一映射为 `credentialExpired = true`（OpenCode Go 例外：403 = Key 有效但无 Go 订阅）。

### 1.4 通用解析工具

- `parseF64(value)`：兼容数字和字符串两种 JSON 形态（如 `100` 与 `"100"`）。
- `extractResetTime(value)`：字符串直接透传；数字自动区分秒（< 1e12）/毫秒（≥ 1e12）并转 ISO 8601；`<= 0`（火山无活跃窗口回 -1）视为无重置时间。
- 时间戳转 ISO 的秒/毫秒判断边界：`1_000_000_000_000`。

---

## 2. Kimi For Coding

**端点**：`GET https://api.kimi.com/coding/v1/usages`

**请求头**：
```
Authorization: Bearer {api_key}
Accept: application/json
```

**响应示例**：
```json
{
  "limits": [
    { "detail": { "limit": 60, "remaining": 42.5, "resetTime": "2026-09-02T12:00:00Z" } }
  ],
  "usage": { "limit": 600, "remaining": 512, "resetTime": 1756848000000 }
}
```

**解析规则**：
- `limits[]` 每项 → 一个 `five_hour` tier：`used = limit - remaining`（下限 0），
  `utilization = used / limit * 100`；`limit` 缺省按 1，`remaining` 缺省按 0。
- `usage` 对象 → 一个 `weekly_limit` tier，算法同上。
- `resetTime` 走 `extractResetTime`（字符串或毫秒时间戳都可能出现）。
- 注意：limit/remaining 是**配额点数**而非百分比，除法后才得到百分比。

**状态码语义**：401/403 → Key 无效；其余非 2xx → `API error (HTTP xxx): body`。

---

## 3. 智谱 GLM（个人版 CN/EN + 团队版）

**端点**：`GET {quota_base}/api/monitor/usage/quota/limit`

`quota_base` 由用户配置的 base_url 路由（cc-switch `zhipu_quota_base`）：
- base_url 含 `bigmodel.cn` → `https://open.bigmodel.cn`
- 否则（`api.z.ai` 等）→ `https://api.z.ai`

**请求头**（⚠️ 智谱**不加 Bearer 前缀**，Key 直接作为 Authorization 值）：
```
Authorization: {api_key}
Content-Type: application/json
Accept-Language: en-US,en
```

**团队版差异**：URL 追加 `?type=2`，另加两个头：
```
bigmodel-organization: {organization_id}
bigmodel-project: {project_id}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "level": "MaxPlan",
    "limits": [
      { "type": "TOKENS_LIMIT", "percentage": 35.2, "nextResetTime": 1756800000000, "unit": 3, "number": 5 },
      { "type": "TOKENS_LIMIT", "percentage": 61.8, "nextResetTime": 1757232000000, "unit": 6, "number": 7 }
    ]
  }
}
```

**解析规则**（cc-switch `parse_zhipu_token_tiers`，防御性较强，务必照抄语义）：
1. 只取 `type` 为 `TOKENS_LIMIT` 或 `CREDIT_LIMIT` 的条目（大小写不敏感）。
2. **窗口分类优先用显式字段 `unit`**：`unit == 3` → `five_hour`；`unit == 6` → `weekly_limit`。
   - 不能按 `nextResetTime` 排序代替——周期末尾每周窗口会比 5 小时窗口更早重置，时间排序必然标反（cc-switch issue #3036 的结论）。
3. `unit` 缺失或不认识时的兜底启发式：无 `nextResetTime` 的条目优先归 `five_hour`（5 小时桶在 0% 状态可能没有 reset），其余按 reset 时间升序依次填入空缺槽位。
4. 老套餐（2026-02-12 前订阅）只回 1 条 → 自然降级为只展示 `five_hour`；新套餐回 2 条。
5. `nextResetTime` 是毫秒时间戳 → 转 ISO。
6. `data.level` → `message`（套餐等级展示）。

**业务错误**：`success == false` 时读 `msg` 字段作为错误文案。

---

## 4. MiniMax（CN / EN）

**端点**：`GET https://{api_domain}/v1/api/openplatform/coding_plan/remains`
- CN：`api.minimaxi.com`；EN：`api.minimax.io`

**请求头**：
```
Authorization: Bearer {api_key}
Content-Type: application/json
```

**响应示例**：
```json
{
  "base_resp": { "status_code": 0, "status_msg": "" },
  "model_remains": [
    {
      "model_name": "general",
      "current_interval_remaining_percent": 64.0,
      "end_time": 1756812345000,
      "current_weekly_status": 1,
      "current_weekly_remaining_percent": 78.5,
      "weekly_end_time": 1757232000000
    },
    { "model_name": "video", "...": "..." }
  ]
}
```

**解析规则**（cc-switch `parse_minimax_tiers`）：
1. `model_remains[]` 中**只取 `model_name == "general"`** 的条目（video 等其他模型跳过）。
2. 5h 桶：上游给的是**剩余**百分比 → `utilization = 100 - current_interval_remaining_percent`；
   `end_time`（毫秒）→ resetsAt。
3. 周桶：**仅当 `current_weekly_status == 1` 时激活**（无周限额套餐该字段为 3，remaining 恒 100，不得展示）；
   `utilization = 100 - current_weekly_remaining_percent`；`weekly_end_time` → resetsAt。

**业务错误**：`base_resp.status_code != 0` → 读 `status_msg`，格式 `API error (code xxx): msg`。

---

## 5. ZenMux

**端点**：`GET {base_url}` —— 用户配置的 base_url **本身就是完整额度端点**（与推理地址无关，
由用户从 ZenMux 控制台复制）。

**请求头**：
```
Authorization: Bearer {api_key}
Accept: application/json
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "quota_5_hour": {
      "usage_percentage": 0.42,
      "resets_at": "2026-09-02T15:00:00Z",
      "used_value_usd": 5.04,
      "max_value_usd": 12.0
    },
    "quota_7_day": {
      "usage_percentage": 0.31,
      "resets_at": "2026-09-07T00:00:00Z",
      "used_value_usd": 9.3,
      "max_value_usd": 30.0
    },
    "plan": { "tier": "pro" },
    "account_status": "active"
  }
}
```

**解析规则**：
- `quota_5_hour` → `five_hour`；`quota_7_day` → `weekly_limit`。
- ⚠️ `usage_percentage` 是 **0–1 的小数** → `utilization = usage_percentage * 100`。
- `resets_at` 已是 ISO 字符串，直接透传；`used_value_usd` / `max_value_usd` 是 ZenMux 独有的美元金额字段。
- `plan.tier (account_status)` 拼为 `message`。
- 数值兼容 `parseF64`（数字/字符串双形态）。

**业务错误**：`success != true` → 读 `message` 字段。

---

## 6. OpenCode Go

**端点**：`GET https://opencode.ai/zen/go/v1/usage`（第一方但**未文档化**的路由）

**请求头**（⚠️ 用量端点只认 Bearer——与推理侧 `/messages` 只认 `x-api-key` 正好相反，不能互换）：
```
Authorization: Bearer {api_key}
Accept: application/json
```

**响应示例**：
```json
{
  "usage": {
    "rolling": { "status": "ok", "percent": 42, "resetsAt": "2026-09-02T15:00:00Z" },
    "weekly":  { "status": "ok", "percent": 61, "resetsAt": "2026-09-07T00:00:00Z" },
    "monthly": { "status": "rate-limited", "percent": 100, "resetsAt": "2026-09-30T00:00:00Z" }
  }
}
```

**解析规则**（cc-switch `parse_opencode_go_tiers`）：
- 窗口映射：`rolling` → `five_hour`、`weekly` → `weekly_limit`、`monthly` → `monthly`。
- `percent` 是 0–100 的**已用**整数百分比。
- `status == "rate-limited"` 时上游已把 percent 钉在 100，无需特判。
- ⚠️ `percent == 0` 时上游的 `resetsAt` 是「now + 窗口时长」的占位值（滚动窗按最后记账时间整窗清零），**丢弃不展示倒计时**。
- `resetsAt` 走 `extractResetTime`（字符串或时间戳皆可）。
- 三窗口一个都解析不出来 → 报 `Unexpected usage response shape`（该端点 2026-08-11 上线当天就改过一次形态，需防御）。
- 文档口径（端点不回传金额）：$12/5h、$30/周、$60/月。

**状态码语义**：
- 403：Key 有效（Zen 与 Go 共用同一把 workspace key）但**该 workspace 无 Go 订阅**，与 401 分开提示；
- 401：Key 无效。

---

## 7. 火山方舟 Agent Plan / Coding Plan（二期实现）

与上述「数据面 Bearer」供应商完全不同，火山用量接口是**控制面 OpenAPI**：

- 端点：`POST https://open.volcengineapi.com/?Action=...&Version=2024-01-01&Region=cn-beijing`
  （**不是**推理域名 `ark.cn-beijing.volces.com`）
- Action：`GetAFPUsage`（Agent Plan，回绝对额度 Quota/Used）→ 未订阅再试
  `GetCodingPlanUsage`（Coding Plan，回百分比窗口）。双 plan 自动探测，共用同一份 AK/SK。
- 鉴权：**火山引擎签名 V4**，强制 HMAC-SHA256（AK/SK 签名）。实测用推理 Bearer Key 会被
  网关以 `400 InvalidAuthorization` 拒绝。用户需另填火山账号的 AccessKey ID + Secret
  （与推理 Key 是两套凭据）。
- Region 从推理 base_url 提取（如 `ark.cn-beijing.volces.com` → `cn-beijing`），识别失败回落 cn-beijing。
- 鉴权类错误直接停（两个 plan 共用凭据，不再试另一个）。

**移动端实现要点**：需要在 UTS 层实现 HMAC-SHA256（纯 TS 实现或 UTS 加密插件），
且 AK/SK 为账户级密钥，UI 必须显著提示风险并建议使用权限最小化的子账号 AK。

---

## 8. tier 展示名映射（UI 层参考）

| tier 值 | 中文展示 |
|---|---|
| `five_hour` | 5 小时窗口 |
| `weekly_limit` | 本周额度 |
| `monthly` | 本月额度 |

## 9. 修订跟踪

上游接口变形时，对照 cc-switch 仓库以下位置更新本文档：
- `src-tauri/src/services/coding_plan.rs`（全部供应商的请求与解析）
- `src-tauri/src/services/subscription.rs:301-313`（tier 常量）
- `src/config/codingPlanProviders.ts`（供应商路由表）
