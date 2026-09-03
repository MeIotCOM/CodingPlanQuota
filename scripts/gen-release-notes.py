#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen-release-notes.py — 生成「EN 上 / 中文下」双段格式的 GitHub Release 说明。

用法:
  python3 scripts/gen-release-notes.py <version> [--out FILE] [--publish] [--draft]

参数:
  <version>    版本号，可带或不带 v 前缀（0.4.1 / v0.4.1）
  --out FILE   输出文件路径（默认 /tmp/relnotes-v<version>.md）
  --publish    生成后直接用 gh 创建/更新 Release（需已登录 gh；
               APK 附件仍需手动 `gh release upload vX.Y.Z 文件` 上传）
  --draft      --publish 时创建为草稿（默认正式发布）

流程约定:
  1. 在 dev 分支完成开发，CHANGELOG.md 先写好对应版本条目（中文）；
  2. 运行本脚本生成双语说明，填写英文段（原样为中文条目的位置替换成英文要点）；
  3. main 分支发布（git checkout main && git checkout dev -- . && 提交打标推送）；
  4. HBuilderX 云打包 APK → `gh release upload vX.Y.Z APK SHA256SUMS.txt`。

规则:
  - 版式固定「EN 上 / 中文下」，中间 --- 分隔，两段各带安装说明与 CHANGELOG 链接
  - 中文段自动从 CHANGELOG.md 抽取该版本条目（原样保留）
  - 英文段生成 TODO 骨架，由维护者填写英文要点
"""

import argparse
import re
import subprocess
import sys

REPO = "MeIotCOM/CodingPlanQuota"


def normalize(version: str) -> str:
    return version[1:] if version.startswith("v") else version


def extract_changelog_section(changelog_path: str, version: str):
    """从 CHANGELOG.md 抽取 `## [version]` 到下一个 `## [` 之间的内容"""
    with open(changelog_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    heading_prefix = f"## [{version}]"
    start = None
    for i, line in enumerate(lines):
        if line.startswith(heading_prefix):
            start = i + 1
            break
    if start is None:
        sys.exit(f"CHANGELOG.md 中没有找到版本条目: ## [{version}]（先写好再生成）")

    section = []
    for line in lines[start:]:
        if line.startswith("## ["):
            break
        section.append(line)

    # 去掉首尾空行
    while section and section[0].strip() == "":
        section.pop(0)
    while section and section[-1].strip() == "":
        section.pop()
    return "\n".join(section)


def build_notes(version: str, cn_section: str, repo: str, en_section: str | None = None) -> str:
    tag = f"v{version}"
    changelog_url = f"https://github.com/{repo}/blob/main/CHANGELOG.md"
    return f"""## ✨ What's New

{en_section}

Also in this release: see the Chinese section below and
[CHANGELOG.md]({changelog_url}) for the full details.

## 📲 Install (Android)

Download the APK attached below (allow "install unknown apps").
Integrity can be verified against `SHA256SUMS.txt`.

---

## ✨ 新特性（中文）

{cn_section}

## 📲 安装（安卓）

下载附件中的 APK 安装（允许未知来源）；可用 `SHA256SUMS.txt` 校验文件完整性。

完整变更：[CHANGELOG.md]({changelog_url})
"""


def publish(tag: str, notes_file: str, draft: bool) -> None:
    """已有同名 Release 则更新，否则创建"""
    view = subprocess.run(
        ["gh", "release", "view", tag, "--repo", REPO],
        capture_output=True,
    )
    if view.returncode == 0:
        cmd = ["gh", "release", "edit", tag, "--repo", REPO,
               "--title", tag, "--notes-file", notes_file]
    else:
        cmd = ["gh", "release", "create", tag, "--repo", REPO,
               "--title", tag, "--notes-file", notes_file]
        if draft:
            cmd.append("--draft")
    subprocess.run(cmd, check=True)
    print("已提醒：APK 附件请另行上传 → "
          f"gh release upload {tag} <apk> SHA256SUMS.txt --clobber --repo {REPO}")


def main() -> None:
    parser = argparse.ArgumentParser(description="生成双语 Release 说明")
    parser.add_argument("version", help="版本号，如 0.4.1 或 v0.4.1")
    parser.add_argument("--out", default=None, help="输出文件路径")
    parser.add_argument("--repo", default=REPO, help="GitHub 仓库（owner/name）")
    parser.add_argument("--publish", action="store_true",
                        help="生成后用 gh 创建/更新 Release")
    parser.add_argument("--draft", action="store_true",
                        help="配合 --publish，创建为草稿")
    parser.add_argument("--en-file", default=None,
                        help="英文要点文件（Markdown 片段）；提供后英文段不再留 TODO。"
                             "可让 AI 依据 CHANGELOG 中文条目翻译生成")
    args = parser.parse_args()

    version = normalize(args.version)
    en_section = None
    if args.en_file:
        with open(args.en_file, encoding="utf-8") as f:
            en_section = f.read().strip()
        if en_section == "":
            en_section = None
    notes = build_notes(version, extract_changelog_section("CHANGELOG.md", version),
                        args.repo, en_section)

    out = args.out or f"/tmp/relnotes-v{version}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(notes)
    print(f"已生成: {out}")
    if en_section is None:
        print("下一步: 填写英文段 TODO（或用 --en-file 传入英文要点）→ 上传 APK → "
              f"(可选) --publish 或 gh release edit/create v{version}")

    if args.publish:
        publish(f"v{version}", out, args.draft)


if __name__ == "__main__":
    main()
