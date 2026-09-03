#!/bin/sh
# pre-push-guard.sh — 防止把 dev 分支推送到远程（开源仓库仅 main 公开）。
#
# 安装（仓库根目录执行）：
#   cp scripts/pre-push-guard.sh .git/hooks/pre-push && chmod +x .git/hooks/pre-push
#
# 说明：本项目发布流程 = 在本地 dev 开发 → `git checkout main && git checkout dev -- .`
# → 提交打标推送 main。dev 含完整开发历史，仅保留在本地。

while read local_ref local_sha remote_ref remote_sha; do
  case "$remote_ref" in
    refs/heads/dev)
      echo "⛔ 禁止推送 dev 分支：开发历史仅保留本地，发布请合并到 main" >&2
      exit 1
      ;;
  esac
done
exit 0
