# CodingPlanQuota

> Your AI coding-plan quotas, at your fingertips.

**CodingPlanQuota** is a mobile app for checking the **5-hour / weekly / monthly quota
usage** and reset countdowns of your AI coding subscriptions (Coding Plan / Agent Plan)
anytime — no computer required.

[简体中文](README.zh-CN.md) | **English**

- 🏢 Maintained by **MelotCOM Team**
- 📱 Platforms: Android / iOS / HarmonyOS NEXT (one uni-app x codebase, native on all three)
- 🌐 UI languages: 中文 / English / Deutsch / Français / 日本語 / 한국어 / Русский
  (system auto-detect + manual switch)
- 🧩 Inspired by the open-source project [cc-switch](https://github.com/farion1231/cc-switch)
  — keep using cc-switch on desktop; this project is a mobile companion only.
  The app icon reworks cc-switch's visual motif (cc-switch is MIT licensed).

## Supported Providers

| Provider | Shown | Credentials |
|---|---|---|
| Zhipu GLM Personal (CN/EN) | 5h / weekly windows | API Key |
| Zhipu GLM Team | 5h / weekly windows | API Key + Organization ID + Project ID |
| Kimi For Coding | 5h / weekly windows | API Key |
| MiniMax (CN/EN) | 5h / weekly windows | API Key |
| ZenMux | 5h / weekly windows | API Key + quota endpoint URL |
| OpenCode Go | 5h / weekly / monthly | workspace API Key |
| Volcengine Ark (Agent / Coding Plan) | 5h / weekly / monthly | AccessKey ID + Secret (Volcengine SigV4) |
| DeepSeek | account balance | platform API Key |
| Custom / Relay | depends on chosen protocol | full endpoint URL + API Key + protocol template |

**Custom / Relay**: paste the full quota-endpoint URL and pick a parsing-protocol template —
one of the built-in provider protocols, or **Custom JSON mapping** (the mobile equivalent of
cc-switch's custom usage scripts): declare the auth style (Bearer / raw key / none) and the
JSON paths per window (direct percent, or limit+remaining with optional 0–1 fraction ×100).
No coding required to support any read-only GET usage API.

## Features

- **Aggregated view**: manage multiple plans in one app — card dashboard with progress bars,
  reset countdowns, and a red alert at 80% usage
- **Offline friendly**: every query result is cached; the last status and
  "🕐 5 min ago - Updated 14:32" are available on launch without network
- **Configurable polling**: auto-refresh on launch + foreground polling interval
  (off / 5 / 15 / 30 / 60 minutes)
- **Config backup**: export/import as JSON (merged by ID) — your setup survives device changes
- **Secure keys**: on Android, API keys are encrypted via AndroidKeyStore (AES-256/GCM);
  legacy plaintext is migrated automatically; the About page honestly shows the storage state
- **Privacy-clean**: no backend, nothing collected or uploaded; all queries are read-only GET
- **8 UI languages** with system auto-detect; the user agreement is available in English and Chinese

## Config Backup (Export / Import)

Location: **Settings → Backup**.

**Export** generates a JSON snapshot of all providers and copies it to the clipboard:

```json
{
  "app": "CodingPlanQuota",
  "schemaVersion": 1,
  "exportedAt": 1788000000000,
  "providers": [
    {
      "id": "1788332457164-28992",
      "kind": "zhipu",
      "label": "Zhipu main",
      "baseUrl": "",
      "apiKey": "your-api-key-in-plaintext",
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

**Import** merges a pasted snapshot into local storage:

- same `id` → overwritten by the backup; new `id` → appended;
- records missing `id` / `kind` / `apiKey` are skipped and counted in the result toast.

Typical use: device migration, reinstalling the app, or replicating a setup across your own
devices. The storage schema carries a `schemaVersion` so future format changes migrate cleanly.

> ⚠️ **The export is plaintext and contains every API key.** Never paste it into untrusted
> channels (chat groups, issue trackers, screenshots). The in-app warning says the same.

## Localization

The UI ships in **8 languages**: 中文, English, Deutsch, Français, 日本語, 한국어, Русский.

- **First launch** follows the system language; unsupported system languages fall back to English.
- **Manual switch**: Settings → Language → action sheet. The app reloads to apply.
- **Fallback chain**: current language → English → Chinese → the key itself, so a missing
  translation never surfaces as a raw key on the English/Chinese UIs.
- The [user agreement](pages/agreement/agreement.uvue) is embedded in English and Chinese;
  other locales display the English text.

**Adding a language** (contributor guide):

1. Create `utils/locale/xx.uts` exporting `xxTable` — copy `en.uts` as the base and translate.
2. In `utils/i18n.uts`: add a `LANG_XX` constant, import the table, and add a branch in
   `detectSystemLang()` (system-language prefix), `tableFor()` and `resolveLocale()`.
3. In `pages/settings/settings.uvue`: append the language name (written in that language)
   to `LANG_VALUES` / `langLabels`.

Keys missing from a new table automatically fall back to English, so partial translations
are safe to land.

## Tech Stack & Layout

uni-app x (Vue 3 syntax + UTS, compiled to native on all three platforms).

```
codingplanquota/
├── docs/                          # API spec / user agreement / competitive research
├── pages/
│   ├── index/index.uvue           # dashboard: provider cards + progress bars + countdowns
│   ├── provider/edit.uvue         # add/edit provider credentials
│   ├── settings/settings.uvue     # settings: polling / backup / data / about
│   └── agreement/agreement.uvue   # user agreement (EN + ZH embedded)
├── services/
│   ├── registry.uts               # provider registry + vault storage + query dispatch + migration
│   ├── lastquota.uts              # last-query cache
│   ├── settings.uts               # query behavior settings
│   └── quota/                     # one file per provider (matches the spec doc)
├── utils/
│   ├── i18n.uts                   # centralized string tables (EN/ZH) + locale resolution
│   ├── locale/                    # de / fr / ja / ko / ru tables
│   ├── crypto.uts                 # HMAC-SHA256 / SHA-256 (conditional compilation)
│   ├── vault.uts                  # secure-storage wrapper (availability probe + fallback)
│   ├── http.uts / format.uts / types.uts
├── uni_modules/pq-vault/          # UTS plugin: AndroidKeyStore encrypted storage
│   └── utssdk/app-android/        #   Android implemented; iOS / Harmony pending
├── icons/                         # app icons (asterisk motif reworked from cc-switch)
├── main.uts / App.uvue / pages.json / manifest.json
└── CHANGELOG.md / LICENSE
```

## Getting Started (HBuilderX)

1. Install [HBuilderX](https://www.dcloud.io/hbuilderx.html) (latest stable).
2. "File → Import → From local directory" and select this repository folder.
3. Run:
   - **Android**: "Run → Run to device" (USB debugging enabled);
   - **iOS**: "Run → iOS base" (requires Xcode and signing);
   - **HarmonyOS**: "Run → Harmony" (requires DevEco Studio + HarmonyOS SDK).
4. Release: "Release → Native app cloud/local packaging" per platform.

> Some UTS APIs behave slightly differently per platform; the parsers are written defensively
> (upstream changes produce errors, never crashes). The semantic reference for all parsing is
> [docs/provider-api-spec.md](docs/provider-api-spec.md).

## Security Notes

- **Key storage**: on Android, API keys are encrypted with AndroidKeyStore (AES-256/GCM);
  the key material never leaves the system security area. iOS / HarmonyOS integration is in
  progress — keys are currently kept in the app sandbox there (Settings → About shows the
  actual storage state honestly).
- All quota queries are **read-only GET** requests; keys are never used for writes, and the
  app has no backend — nothing is ever uploaded.
- Volcengine uses **account-level AK/SK** (broader than an inference API key). Prefer a
  least-privilege sub-account AK granted only Ark usage-query (OpenAPI) permissions.

## Upstream Tracking

These provider endpoints are undocumented and may change upstream. Track:

- cc-switch `src-tauri/src/services/coding_plan.rs` (requests & parsing)
- cc-switch `src/config/codingPlanProviders.ts` (provider routing table)

When upstream changes: update `docs/provider-api-spec.md` first, then the matching module
in `services/quota/`.

## Acknowledgements

- [cc-switch](https://github.com/farion1231/cc-switch) — the source of all API knowledge
  and the design inspiration for this project

## License

[BSD-3-Clause](LICENSE) © 2026 MelotCOM Team — commercial use allowed; keep the copyright notice, license text, and do not use the project name for endorsement when redistributing.
