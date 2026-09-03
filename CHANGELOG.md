# Changelog

本项目的所有重要变更都记录在此文件中。
格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [0.5.0] - 2026-09-02

### Added

- 卡片排序：供应商卡片左滑露出操作列（置顶 / 上移 / 下移），跟手交互带方向锁
  防误触；置顶项显示 el-tag 风格「置顶」标签并排在最前，旧数据零迁移兼容。

### Changed

- 许可证由 MIT 更换为 BSD-3-Clause（允许商用闭源，附加非背书条款）；LICENSE 附
  cc-switch 图标（MIT）与供应商商标的第三方声明。
- manifest 应用描述丰富为完整定位（供应商清单 / 核心能力 / 隐私）。
- README 补充配置备份（格式 / 合并规则）与多语言专题（机制 / 新增语言贡献者指南）；
  GitHub About 区补充描述与 17 个 topics。

## [0.4.0] - 2026-09-02

### Added

- 火山方舟（Agent / Coding Plan）：火山变体 SigV4 忠实移植（固定顺序 headers、
  HMAC-SHA256 无 AWS4 前缀、密钥链不加前缀），AK/SK 凭据入加密存储，
  GetAFPUsage → GetCodingPlanUsage 双 plan 自动探测。
- DeepSeek：开放平台余额查询（/user/balance），卡片展示余额与赠送金额。
- 供应商品牌图标：接入 cc-switch 收集的官方 SVG（智谱/Kimi/MiniMax/DeepSeek/火山），
  无图标供应商回退字母头像。
- 密钥安全存储（pq-vault UTS 插件）：Android 走 AndroidKeyStore（AES-256/GCM，密钥
  材料不出系统安全区，密文落沙盒）；iOS Keychain / 鸿蒙 HUKS 待接入，当前如实回落
  普通沙盒并在设置页显示存储状态。启动时自动把旧明文凭据一次性迁入（幂等）。

### Changed

- README 双语化：英文版为默认入口，中文版独立 README.zh-CN.md；补充配置备份格式、
  多语言机制与新增语言贡献者指南；移除公开路线图。

### Fixed

- i18n 缺键：火山/DeepSeek/余额相关 13 键补齐（中文表 9、英文表 13），修复余额行
  显示原始键名。
- UTS 桥接：charCodeAt 可空返回判空；平台整型显式 Int（number 编译为 Double）；
  ByteArray 长度用 .size；KeyStore 正确包名 java.security。

## [0.3.0] - 2026-09-02

### Added

- 自定义供应商（自定义 / 中转站）：填写完整额度查询端点 URL + 自选解析协议模板
  （智谱 / 智谱团队 / Kimi / MiniMax / ZenMux / OpenCode Go 六选一），复用内置解析器；
  五个查询模块端点全部参数化。
- 自定义 JSON 映射协议（`custom_json`）：cc-switch「自定义额度查询」的移动端等价物。
  声明式配置端点鉴权（Bearer / Key 直传 / 无）+ 双窗口 JSON 取值路径（百分比直读或
  上限+剩余差值，0–1 小数自动 ×100），不引入 JS 脚本引擎。
- 上次查询缓存：每供应商独立保存最后一次成功查询，打开 App 离线回填；瞬时失败
  （断网/超时）保留上次数据展示并提示，缓存不因失败而污染。
- 设置页完整四分区：查询行为（自动刷新开关 + 前台轮询间隔 关/5/15/30/60 分钟，
  onHide 自动停止）、配置备份（导出/导入，按 ID 合并）、数据管理（双重确认清除全部）、
  关于（版本/团队/协议入口）。
- 本地存储加 `schemaVersion: 1`；配置导出为 JSON 文本（明文警示）+ 粘贴导入合并。
- 多语言（8 语）：中文 / English / Deutsch / Français / 日本語 / 한국어 / Русский，
  自动检测系统语言 + 设置页动作菜单手动切换（切换后重载生效），回退链
  当前语言 → 英文 → 中文。相对时间按语言模板化（vor 5 Min. / il y a 5 min / 5分前）。
- 用户使用协议（中英双份全文，App 内离线可看）：含供应商接口依赖与不可控风险条款
  （接口变更尽力适配、永久关闭无法支持）、无后端/凭据仅存本地的隐私说明。
- 应用图标：复刻 cc-switch 米字形母题（十瓣圆头射线 + 实心核心，橙/青/金三色，
  MIT 出处已标注），Android 四尺寸 + iOS 1024，已接线 manifest。
- 竞品调研文档 `docs/competitive-landscape-2026-09.md`。

### Changed

- manifest 补 `"uni-app-x"` 项目标识（缺失会被 HBuilderX 识别为 web 应用）与
  Android/iOS 图标接线。
- 首页 UI：品牌色供应商头像、cc-switch 同款 RefreshCw 刷新图标、
  「🕐 x 分钟前 - 更于 HH:mm」组合时间、紧凑头部布局。
- 设置页更名「设置」并结构化为四分区。

### 决策记录

- cc-switch 的「费用设置」（模型 token 计价）暂不引入：其依赖 PC 端代理记录的请求
  日志，移动端无此数据，待 P4（PC 数据同步）落地后再评估。
- cc-switch 的「自定义用量脚本」（JS 执行）不直接照搬：UTS 无 eval 且移动端执行
  用户脚本的安全面不可控，改用声明式 JSON 路径映射达成同等能力。
- 协议的联系方式/适用法律条款暂缓：待团队信息确定后以正式文案补回。

## [0.1.0] - 2026-09-02

### Added

- 供应商接口规格文档 `docs/provider-api-spec.md`：从 cc-switch 源码逐行提取的
  6 家供应商（智谱个人/团队、Kimi、MiniMax、ZenMux、OpenCode Go）额度查询完整规格，
  含火山方舟（二期）的签名要求说明。
- uni-app x 三端脚手架（Android / iOS / 鸿蒙 HarmonyOS NEXT）。
- 数据层：HTTP 封装（瞬时/确定性错误分离）、共享解析工具、5 个供应商查询模块。
- 页面：仪表盘（供应商卡片、窗口进度条、重置倒计时、下拉刷新、80% 预警配色）
  与供应商编辑页（按类型条件展示表单、删除确认）。
- 项目初始化：README、MIT LICENSE、Changelog、git 仓库。

[Unreleased]: https://github.com/MeIotCOM/CodingPlanQuota/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/MeIotCOM/CodingPlanQuota/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/MeIotCOM/CodingPlanQuota/compare/v0.1.0...v0.3.0
[0.1.0]: https://github.com/MeIotCOM/CodingPlanQuota/releases/tag/v0.1.0
