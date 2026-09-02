# 竞品调研 — 2026-09

> 结论先行：**「聚合国内 Coding Plan 套餐额度」的移动端 App 目前是空白**。已有产品分三类：
> 国际移动端 App（只覆盖 Claude/Codex/Gemini）、桌面菜单栏工具（覆盖面广但不移动）、
> 各家官方渠道（Kimi 已有手机端入口，智谱/火山只有网页控制台和插件）。
> CodingPlanQuota 的差异化定位：**国内套餐聚合 + 三端（含鸿蒙）+ 小组件/推送**。

## 一、移动端 App（直接竞品）

| 产品 | 平台 | 覆盖供应商 | 与 CodingPlanQuota 的差异 |
|---|---|---|---|
| [Limits: AI Usage Tracker](https://apps.apple.com/us/app/limits-ai-usage-tracker/id6783130074) | iOS | 国际主流（Claude/Codex 系） | 功能形态最接近（会话/周额度/重置倒计时），但无国内套餐、无安卓/鸿蒙 |
| [Usage for Claude](https://apps.apple.com/us/app/usage-for-claude/id6755173244) | iOS | 仅 Claude | 单供应商 |
| [AI Usage: Claude & Gemini](https://play.google.com/store/apps/details?id=u.sage) | Android | Claude、Gemini | 国际双供应商，无国内套餐 |

**关键空白**：没有任何移动端 App 覆盖智谱 GLM（个人/团队）、Kimi For Coding、MiniMax、
ZenMux、火山方舟 Agent/Coding Plan、OpenCode Go 这一组合。

## 二、桌面 / 菜单栏工具（相邻竞品，不移动）

| 产品 | 平台 | 覆盖 | 备注 |
|---|---|---|---|
| [CodexBar](https://codexbar.app) | macOS 菜单栏 | 69 家，含 z.ai、MiniMax | 供应商覆盖最广，证明「解析知识」护城河不深，胜负手在移动端体验 |
| [LimitBar](https://limitbar.artsvit.com) / CUStats / AIUsageBar（47+ 家） | macOS 菜单栏 | Claude/Codex/Cursor 等 | 同上 |
| cc-switch | Win/macOS/Linux | 国内套餐全覆盖 | 本项目接口知识的来源，PC 端首选，无移动端 |
| cc-switch 生态之外：[ccusage](https://ccusage.com/) + ccusage-monitor | CLI + Web | Claude Code/Codex | Web 仪表板可用手机浏览器访问，但依赖 PC 常开 |
| 火山方舟助手（VS Code 插件） | VS Code 状态栏 | 火山 Agent/Coding Plan | 官方控制台之外的唯一火山第三方查询 |

## 三、各家官方渠道（事实上的竞品）

| 供应商 | 官方查询方式 | 是否已有移动端入口 |
|---|---|---|
| Claude | App 内 Settings → Usage（v2.0.0 起），CLI `/usage` | ✅ 官方 App 已内置 |
| Kimi | Kimi App「设置→订阅和发票→我的额度」；CLI `/usage` | ✅ 官方 App 已内置 |
| 智谱 GLM | 网页控制台；Claude Code 内 `glm-plan-usage` 插件（仅个人版） | ❌ 无 |
| MiniMax / ZenMux / OpenCode Go | 网页控制台 | ❌ 无 |
| 火山方舟 | 网页控制台（额度明细/TPM 曲线）；`GetAFPUsage` API | ❌ 无 |

## 四、对产品策略的启示

1. **单供应商用户可能流失给官方**：Claude、Kimi 已把额度查询做进官方 App。CodingPlanQuota
   的价值在**聚合**——一个 App 看全部套餐 + 统一的重置倒计时 + 跨供应商预警推送。
2. **鸿蒙端是无人区**：所有调研范围内（国际/国内/官方）均无鸿蒙原生额度查询应用，
   可作为差异化首发切口（国内 Coding Plan 用户与鸿蒙用户重合度不低）。
3. **护城河不在接口解析**：CodexBar 69 家供应商说明解析能力易被复制；真正的壁垒是
   移动端体验（小组件、推送、多账号管理）+ 跟上游接口变化的运维速度。
4. **风险**：各家供应商随时可能把额度查询做进自家 App（Claude/Kimi 已发生），
   产品叙事应强调「聚合与统一视图」而非「查某一家的额度」。
