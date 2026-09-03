#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n 完整性校验脚本。

用法：
  python3 scripts/check-i18n.py

检查内容：
  1. 扫描 pages/ services/ utils/ 下所有 t("key") 调用（单词边界，避免误匹配
     split("T") / get("id") 这类非 i18n 字符串）；
  2. 校验每个被引用的键都在中文表(zhTable)与英文表(enTable)中；
  3. 报告五语表(de/fr/ja/ko/ru)中缺失的键（仅供参考——运行时会回落英文，
     不阻塞，但列出便于贡献者补全）。

退出码：0 = 中英表完整；1 = 存在缺失（用于 CI 门禁）。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIRS = ["pages", "services", "utils"]
I18N_FILE = ROOT / "utils" / "i18n.uts"
LOCALE_DIR = ROOT / "utils" / "locale"
LOCALES = ["de", "fr", "ja", "ko", "ru"]

KEY_RE = re.compile(r"\bt\(\"([a-zA-Z0-9._]+)\"\)")


def extract_source() -> str:
    chunks = []
    for d in SRC_DIRS:
        for ext in ("*.uvue", "*.uts"):
            for p in sorted((ROOT / d).rglob(ext)):
                chunks.append(p.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def table_keys(text: str, table_name: str) -> set:
    """从 i18n.uts 中提取某语言表的全部键（形如 "key" : value）。"""
    # 找到表起点与下一个 "const ...Table" 或文件尾
    start = text.index(f"const {table_name}")
    # 表内容到文件尾（zh/en 在 i18n.uts 末尾之前各有边界，稳妥起见取到最近的下一个表或文件尾）
    rest = text[start:]
    # 键模式：行内 "xxx" : 
    keys = set(re.findall(r'"([a-zA-Z0-9._]+)"\s*:', rest))
    # 排除后续表的键：en 表跟在 zh 后；五语表在独立文件不在此文件
    # 简单可靠：分别提取 zh 与 en 时，先切割两表区间
    return keys


def split_tables(text: str):
    zh_start = text.index("const zhTable")
    en_start = text.index("const enTable", zh_start)
    zh_body = text[zh_start:en_start]
    en_body = text[en_start:]
    zh_keys = set(re.findall(r'"([a-zA-Z0-9._]+)"\s*:', zh_body))
    en_keys = set(re.findall(r'"([a-zA-Z0-9._]+)"\s*:', en_body))
    return zh_keys, en_keys


def main() -> int:
    source = extract_source()
    used = set(KEY_RE.findall(source))
    i18n_text = I18N_FILE.read_text(encoding="utf-8")
    zh_keys, en_keys = split_tables(i18n_text)

    missing_zh = sorted(k for k in used if k not in zh_keys)
    missing_en = sorted(k for k in used if k not in en_keys)

    print(f"引用键总数: {len(used)}")
    print(f"中文表键数: {len(zh_keys)} | 英文表键数: {len(en_keys)}")

    fail = False
    if missing_zh:
        fail = True
        print("\n❌ 中文表缺失（代码已引用）:")
        for k in missing_zh:
            print(f"   - {k}")
    if missing_en:
        fail = True
        print("\n❌ 英文表缺失（代码已引用）:")
        for k in missing_en:
            print(f"   - {k}")

    # 五语表完整性（参考性）
    for loc in LOCALES:
        p = LOCALE_DIR / f"{loc}.uts"
        if not p.exists():
            print(f"\n⚠️ 语言表缺失文件: {loc}")
            continue
        body = p.read_text(encoding="utf-8")
        keys = set(re.findall(r'"([a-zA-Z0-9._]+)"\s*:', body))
        miss = [k for k in zh_keys if k not in keys]
        print(f"\n{loc} 表: {len(keys)} 键，相对中文表缺失 {len(miss)} 个（运行时回落英文）")
        if miss:
            print("   e.g.", ", ".join(miss[:8]))

    if not fail:
        print("\n✅ 中英表完整，无缺失键")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
