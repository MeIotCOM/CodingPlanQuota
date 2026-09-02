# CodingPlanQuota

> 把 Coding Plan 的额度，放在指尖。

**CodingPlanQuota** 是一个移动端 App：随时查看各家 AI 编程套餐（Coding Plan / Agent Plan）
的 **5 小时 / 周 / 月额度消耗**与重置倒计时，不必再打开电脑。

**English** | [简体中文](README.zh-CN.md)

- 🏢 维护团队：**MelotCOM Team**
- 📱 目标平台：Android / iOS / 鸿蒙 HarmonyOS NEXT（一套 uni-app x 代码，三端原生）
- 🌐 界面语言：中文 / English / Deutsch / Français / 日本語 / 한국어 / Русский（自动检测 + 手动切换）
- 🧩 项目灵感与全部接口知识来自开源项目 [cc-switch](https://github.com/farion1231/cc-switch)
  ——PC 端请继续使用 cc-switch，本项目只做它的移动端补充。应用图标基于 cc-switch
  的视觉母题重制（cc-switch 基于 MIT 许可开源）。

## 支持的供应商

| 供应商 | 展示内容 | 凭据 |
|---|---|---|
| 智谱 GLM 个人版（CN/EN） | 5h / 周窗口 | API Key |
| 智谱 GLM 团队版 | 5h / 周窗口 | API Key + 组织 ID + 项目 ID |
| Kimi For Coding | 5h / 周窗口 | API Key |
| MiniMax（CN/EN） | 5h / 周窗口 | API Key |
| ZenMux | 5h / 周窗口 | API Key + 额度端点地址 |
| OpenCode Go | 5h / 周 / 月窗口 | workspace API Key |
| 火山方舟（Agent / Coding Plan） | 5h / 周 / 月窗口 | 访问密钥 AK/SK（火山签名 V4） |
| DeepSeek | 账户余额 | 开放平台 API Key |
| 自定义 / 中转站 | 取决于所选协议 | 完整端点 URL + API Key + 协议模板 |

**自定义 / 中转站**：填完整的额度查询端点 URL，再选一个解析协议模板——八家内置协议，
或「自定义 JSON 映射」（对应 cc-switch 的自定义额度查询）：声明鉴权方式
（Bearer / Key 直传 / 无鉴权头）+ 每个窗口的 JSON 取值路径（百分比直读，或上限+剩余差值，
可配 0–1 小数自动 ×100），无需写代码即可适配任意只读 GET 用量接口。

## 功能特性

- **聚合视图**：一个 App 管理多家套餐，卡片式仪表盘 + 进度条 + 重置倒计时（80% 红色预警）
- **离线友好**：每次查询独立缓存，打开即见最后状态与「🕐 x 分钟前 - 更新于 HH:mm」
- **查询行为可配**：打开时自动刷新开关 + 前台轮询间隔（关 / 5 / 15 / 30 / 60 分钟）
- **配置备份**：导出/导入 JSON（按 ID 合并），换机不丢配置
- **密钥安全**：Android 密钥经 AndroidKeyStore（AES-256/GCM）加密存储；旧明文自动迁移；
  设置页如实显示存储状态
- **隐私干净**：App 无后端，不收集不上传任何数据；所有查询均为只读 GET
- **多语言**：8 语界面，自动跟随系统，协议文档中英双份

## 配置备份（导出 / 导入）

入口：**设置 → 配置备份**。

**导出**生成全部供应商配置的 JSON 快照并复制到剪贴板：

```json
{
  "app": "CodingPlanQuota",
  "schemaVersion": 1,
  "exportedAt": 1788000000000,
  "providers": [
    {
      "id": "1788332457164-28992",
      "kind": "zhipu",
      "label": "智谱主力号",
      "baseUrl": "",
      "apiKey": "你的明文 API Key",
      "protocol": "",
      "customQuery": "",
      "accessKeyId": "",
      "secretAccessKey": "",
      "organizationId": "",
      "projectId": ""
    }
  ]
}
```

**导入**把粘贴的快照合并进本地存储：

- `id` 相同 → 被备份内容覆盖；新 `id` → 追加；
- 缺 `id` / `kind` / `apiKey` 的记录跳过，并在结果提示中计数。

典型用途：换机、卸载重装、在自己的多台设备间复制同一套配置。存储结构带
`schemaVersion`，未来格式变更可平滑迁移。

> ⚠️ **导出内容为明文，包含全部 API Key。** 不要粘贴到任何不可信渠道（聊天群、
> issue 区、截图）。App 内也有同样的警示。

## 多语言

界面内置 **8 种语言**：中文、English、Deutsch、Français、日本語、한국어、Русский。

- **首次启动**跟随系统语言；系统语言不在支持列表时回落英文。
- **手动切换**：设置 → 语言 → 弹出菜单选择，App 重载后生效。
- **回退链**：当前语言 → 英文 → 中文 → 键名本身，缺翻译时不会在界面上露出键名。
- [用户使用协议](pages/agreement/agreement.uvue) 内嵌中英双份全文，其他语言显示英文版。

**新增一门语言**（贡献者指南）：

1. 新建 `utils/locale/xx.uts` 导出 `xxTable`——以 `en.uts` 为底稿翻译；
2. 在 `utils/i18n.uts`：添加 `LANG_XX` 常量、import 语言表，并在
   `detectSystemLang()`（系统语言前缀）、`tableFor()`、`resolveLocale()` 各加一个分支；
3. 在 `pages/settings/settings.uvue`：把语言名（用该语言书写）追加进
   `LANG_VALUES` / `langLabels`。

新语言表缺键会自动回落英文，翻译不完整也可以先合入。

## 技术栈与目录

uni-app x（Vue 3 语法 + UTS，编译为三端原生）。

```
codingplanquota/
├── docs/                          # 接口规格 / 用户协议 / 竞品调研
├── pages/
│   ├── index/index.uvue           # 仪表盘：供应商卡片 + 窗口进度条 + 重置倒计时
│   ├── provider/edit.uvue         # 添加/编辑供应商凭据
│   ├── settings/settings.uvue     # 设置：查询行为 / 备份 / 数据管理 / 关于
│   └── agreement/agreement.uvue   # 用户使用协议（中英双份内嵌）
├── services/
│   ├── registry.uts               # 供应商注册表 + vault 存储 + 查询分发 + 迁移
│   ├── lastquota.uts              # 上次查询缓存
│   ├── settings.uts               # 查询行为设置
│   └── quota/                     # 各供应商查询与解析（一供应商一文件）
├── utils/
│   ├── i18n.uts                   # 集中字符串表（中英）+ 语言解析
│   ├── locale/                    # 德法日韩俄语言表
│   ├── crypto.uts                 # HMAC-SHA256 / SHA-256（火山签名用，条件编译）
│   ├── vault.uts                  # 安全存储包装（可用性探测 + 明文回落）
│   ├── http.uts / format.uts / types.uts
├── uni_modules/pq-vault/          # UTS 插件：AndroidKeyStore 加密存储
│   └── utssdk/app-android/        #   Android 实装；iOS / 鸿蒙待接入
├── icons/                         # 应用图标（cc-switch 米字母题复刻）
├── main.uts / App.uvue / pages.json / manifest.json
└── CHANGELOG.md / LICENSE
```

## 如何运行（HBuilderX）

1. 下载安装 [HBuilderX](https://www.dcloud.io/hbuilderx.html)（最新正式版）。
2. 「文件 → 导入 → 从本地目录导入」，选择本仓库目录。
3. 运行：
   - **Android**：「运行 → 运行到手机或模拟器」（需开启 USB 调试）；
   - **iOS**：「运行 → 运行到 iOS App 基座」（需 Xcode 与签名）；
   - **鸿蒙**：「运行 → 运行到鸿蒙」（需 DevEco Studio + HarmonyOS SDK）。
4. 发行：「发行 → 原生 App-云打包 / 本地打包」，三端各自出包。

> UTS 在各端的个别 API 行为以真机运行结果为准；解析层全部为防御式写法
> （上游接口变形时报错而非崩溃）。数据解析的语义规格见
> [docs/provider-api-spec.md](docs/provider-api-spec.md)。

## 安全说明

- **密钥存储**：Android 上 API Key 经 AndroidKeyStore（AES-256/GCM）加密，密钥材料
  不出系统安全区；iOS / 鸿蒙的系统安全区接入进行中，当前密钥保存在应用沙盒
  （设置 → 关于 可查看当前存储状态，如实显示、不伪装）。
- 所有额度查询均为**只读 GET**，Key 不用于任何写操作；App 无后端，不上传任何数据。
- 火山方舟使用**账户级访问密钥 AK/SK**（权限大于推理 API Key），建议使用权限最小化的
  子账号 AK，并仅为方舟用量查询（OpenAPI）授权。

## 上游跟踪

供应商接口均为非官方文档化接口，可能随上游改版。跟踪对象：

- cc-switch 仓库 `src-tauri/src/services/coding_plan.rs`（请求与解析）
- cc-switch 仓库 `src/config/codingPlanProviders.ts`（供应商路由表）

上游变更时：先更新 `docs/provider-api-spec.md`，再对照修改 `services/quota/` 对应模块。

## 致谢

- [cc-switch](https://github.com/farion1231/cc-switch)：本项目全部接口规格与设计灵感的来源

## License

[BSD-3-Clause](LICENSE) © 2026 MelotCOM Team（允许商用；分发时须保留版权声明与许可文本，不得用项目名义背书衍生品）
