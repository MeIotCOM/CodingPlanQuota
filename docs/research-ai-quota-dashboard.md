# 供应商扩展调研 — ai-quota-dashboard（CodexBar-android fork）

> 调研对象：`ai-quota-dashboard-main`（Kotlin/Compose，fork 自 hyunnnchoi/CodexBar-android）。
> 目标：评估其 7 个供应商接入 CodingPlanQuota 的可行性与实现顺序。
> 所有端点/字段均从源码提取，作为移植规格。

## 一、候选供应商逐个评估

| 供应商 | 端点 | 凭据 | 展示 | 移植难度 | 评估 |
|---|---|---|---|---|---|
| **Codex** | `GET chatgpt.com/backend-api/wham/usage` | ChatGPT access_token（+可选 Account-Id 头） | 5h / 7d 窗口（`rate_limit.primary_window` / `secondary_window`，字段 `used_percent` / `reset_at`(unix秒) / `limit_window_seconds`），plan_type、credits | **低** | ✅ 首批。纯 Bearer GET，无刷新也可用（token 有效期内） |
| **Codex (feelol)** | `GET feea.lol/api/v1/subscriptions`（Bearer） | feela.lol token | 日 / 周 / 月美元额度（daily/monthly Usage+Limit+WindowStart）+ `expiresAt` 套餐到期 | **低** | ✅ 首批。结构简单 |
| **ChatGPT Plus** | 无网络请求：解析用户粘贴的 **session JSON**（`accessToken` + `plan.title/renewalDate/interval`） | 手动粘贴 | 套餐名 + 续费倒计时（按 30/365 天周期算百分比） | **低** | ✅ 首批（纯解析，无网络层） |
| **DeepSeek（增强）** | `GET platform.deepseek.com/api/v0/users/get_user_summary`（Bearer） | API Key | 结算/充值/赠送明细（比现有 `user/balance` 更细） | **低** | ✅ 可与现有模块合并增强 |
| **MiMo Token Plan** | 双模式：①后端代理 URL（Bearer）②**直连** `platform.xiaomimimo.com/console/plan-manage/api/v1/tokenPlan/{usage,detail}`（**Cookie**） | 后端 URL+Token 或 Cookie | 令牌余额、月用量、套餐到期、自动续订 | **中** | ✅ 首批或第二批。Cookie 模式与现有 Bearer 表单不同，编辑页需条件字段 |
| **Claude** | `GET platform.claude.com/api/oauth/usage`（OAuth Bearer） | access_token（+refresh） | five_hour / seven_day / opus / sonnet 等 ≥4 窗口 | **中高** | ⚠️ 二批。查询简单；但 token 过期快，完整体验需 OAuth 刷新链（client_id `9d1c250a-…`） |
| **Gemini（Code Assist）** | `POST cloudcode-pa.googleapis.com/v1internal:{loadCodeAssist,retrieveUserQuota}` | OAuth Bearer（**需 client_id+client_secret 刷新**） | 模型分级 quota buckets | **高** | ⚠️ 谨慎。需要用户自己的 OAuth client 凭据 + 刷新链，门槛最高，放最后 |

## 二、与现有架构的匹配度

完全兼容，无破坏性改动：
- `QuotaTier/utilization/resetsAt` 模型可直接表达以上全部窗口（ChatGPT Plus 的续费进度、feelol 的美元窗口 → 用已有字段；美元额度可复用 ZenMux 的 `usedValueUsd/maxValueUsd`）；
- `balanceText`（DeepSeek 已用）可承载「套餐到期」类标量信息；
- 编辑页的条件字段机制（AK/SK、组织/项目 ID）可扩展 Cookie / session JSON 粘贴框；
- 凭据全部走现有 vault 加密存储。

## 三、建议实现顺序（三个批次）

1. **批次 A（低风险高价值）**：Codex、Codex(feelol)、ChatGPT Plus、DeepSeek 增强
   —— 全部纯 GET 或纯解析，一周内可完成
2. **批次 B**：MiMo（双模式表单）、Claude（先只做 access_token 手动模式，刷新链后置）
3. **批次 C**：Gemini（需 OAuth client + 刷新链，评估投入产出后再做）

## 四、风险与合规

- **Claude/Gemini/Codex 属灰色地带**：走的是官方应用的内部接口（OAuth usage / wham / v1internal），
  官方可能随时变更或风控；cc-switch 的 subscription.rs 已有 Claude/Gemini 的同款实现先例（同类项目均如此），
  用户协议第 4 条「供应商接口依赖与不可控风险」已覆盖，无需修改。
- 参考项目同样声明「非官方应用，凭据用户自备且仅存本地」——与我们现有立场一致。
- 移植注意：参考项目用 Kotlin，逐字段移植时以其实测注释（如 Codex `Level` 字段 2026-06-21 实测）
  为规格，JSON 解析保持防御式。

## 五、结论

7 家全部可接。按三批次推进，第一批（Codex 系 + ChatGPT Plus + DeepSeek 增强）性价比最高。
