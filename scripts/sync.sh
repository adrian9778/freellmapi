#!/usr/bin/env bash
#
# sync.sh — 同步上游(fork 源)的 main 分支到本地, 并把工作分支 rebase 到最新 main
#
#   1. stash 当前所有未提交改动(含未跟踪文件)
#   2. fetch 上游, 将本地 main 快进到 upstream/main, 再推送到 MAIN_REMOTE
#      (只同步上游的 MAIN_BRANCH, 不碰上游其它分支)
#   3. DOCS_BRANCH 不存在则基于最新 main 创建; 存在则 rebase 到最新 main,
#      再用 --force-with-lease 推送(rebase 改写了已推送的历史)
#
# 用法:
#   path/to/sync.sh              # 正常执行
#   path/to/sync.sh --dry-run    # 只打印将要做的事, 不改动任何状态
#
# 可从任意子目录运行: 脚本自动定位 git 仓库根目录并 cd 过去。
#
# 移植到其它项目时, 只改下面「可配置项」即可。

set -euo pipefail

# ── 可配置项(按项目改这里) ──────────────────────────────────────────
UPSTREAM_REMOTE="${UPSTREAM_REMOTE:-upstream}"   # 上游 remote 名
UPSTREAM_URL="${UPSTREAM_URL:-}"                 # 上游 URL; 为空则要求 remote 已存在
MAIN_REMOTE="${MAIN_REMOTE:-origin}"             # 推送目标 remote(fork)
MAIN_BRANCH="${MAIN_BRANCH:-main}"               # 要同步的主分支名
DOCS_BRANCH="${DOCS_BRANCH:-adrian}"             # 文档/工作分支名(rebase + force push)
# ────────────────────────────────────────────────────────────────

DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

log()  { printf '\033[1;34m[sync]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[sync]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[sync]\033[0m %s\n' "$*" >&2; exit 1; }

run() {
  if (( DRY_RUN )); then
    log "(dry-run) $*"
  else
    log "$*"
    "$@"
  fi
}

STASHED=0
START_BRANCH=""
BACKUP_BRANCH=""   # 本次建的 <工作分支>-backup; 成功后清理, 失败保留作回滚锚点

# 清理本次成功后遗留的 backup 分支(仅成功路径调用)
cleanup_backup() {
  if [[ -n "$BACKUP_BRANCH" ]] && git show-ref --verify --quiet "refs/heads/$BACKUP_BRANCH"; then
    run git branch -D "$BACKUP_BRANCH"
    log "已清理本地备份分支 $BACKUP_BRANCH"
  fi
}

# 失败时恢复现场: 已 stash 就 pop 回来, 不把用户改动吞在 stash 里
# 注意: 失败路径刻意保留 <工作分支>-backup, 作为回滚锚点
restore_on_failure() {
  local rc=$?
  if (( STASHED )) && [[ -n "$(git stash list | head -1 || true)" ]]; then
    warn "中途失败(rc=$rc), 恢复 stash 的改动"
    [[ -n "$START_BRANCH" ]] && git checkout "$START_BRANCH" >/dev/null 2>&1 || true
    git stash pop || warn "stash pop 有冲突, 改动仍在 stash 里, 请手动处理: git stash list"
    [[ -n "$BACKUP_BRANCH" ]] && warn "备份分支 $BACKUP_BRANCH 已保留供回滚: git branch -D $BACKUP_BRANCH"
  fi
  exit "$rc"
}

# 定位 git 仓库根目录并 cd 过去 —— 脚本放在子目录也能用
cd_to_git_root() {
  local toplevel
  toplevel="$(git rev-parse --show-toplevel 2>/dev/null)" \
    || die "不在 git 仓库里(无法定位仓库根目录)"
  [[ -n "$toplevel" ]] || die "不在 git 仓库里"
  cd "$toplevel"
  log "仓库根目录: $toplevel"
}

require_clean_branch() {
  # detached HEAD 下 branch --show-current 为空, checkout/回退逻辑会失效
  [[ -n "$(git branch --show-current)" ]] || die "当前处于 detached HEAD, 请先切到一个分支再运行"
}

# 确保上游 remote 可用; 不存在且给了 UPSTREAM_URL 才自动添加
ensure_upstream_remote() {
  if git remote get-url "$UPSTREAM_REMOTE" >/dev/null 2>&1; then
    log "上游 remote 已存在: $UPSTREAM_REMOTE -> $(git remote get-url "$UPSTREAM_REMOTE")"
    return
  fi
  if [[ -z "$UPSTREAM_URL" ]]; then
    die "上游 remote '$UPSTREAM_REMOTE' 不存在, 且未配置 UPSTREAM_URL。请在脚本顶部设置 UPSTREAM_URL。"
  fi
  run git remote add "$UPSTREAM_REMOTE" "$UPSTREAM_URL"
}

# 步骤 1: stash 当前所有改动(含未跟踪文件)
stash_workdir() {
  if [[ -z "$(git status --porcelain)" ]]; then
    log "工作区干净, 无需 stash"
    STASHED=0
    return
  fi
  local stash_msg="sync.sh auto-stash $(date '+%Y-%m-%d %H:%M:%S')"
  run git stash push --include-untracked -m "$stash_msg"
  STASHED=1
  warn "已 stash 未提交改动"
}

# 步骤 2: 让本地 main 与 upstream/main 严格一致, 再推送到 MAIN_REMOTE
sync_main() {
  run git fetch "$UPSTREAM_REMOTE" --prune
  run git fetch "$MAIN_REMOTE" --prune

  if (( DRY_RUN )); then
    # dry-run 下 upstream remote 可能并未真的添加, 无法 rev-parse upstream/main
    log "(dry-run) 将 checkout $MAIN_BRANCH → reset --hard $UPSTREAM_REMOTE/$MAIN_BRANCH → push --force-with-lease $MAIN_REMOTE"
    return
  fi

  local local_main upstream_main
  local_main="$(git rev-parse "$MAIN_BRANCH")"
  upstream_main="$(git rev-parse "$UPSTREAM_REMOTE/$MAIN_BRANCH")"

  if [[ "$local_main" == "$upstream_main" ]]; then
    log "本地 $MAIN_BRANCH 已与上游一致"
  else
    local behind ahead
    behind="$(git rev-list --count "$MAIN_BRANCH..$UPSTREAM_REMOTE/$MAIN_BRANCH")"
    ahead="$(git rev-list --count "$UPSTREAM_REMOTE/$MAIN_BRANCH..$MAIN_BRANCH")"
    log "本地 $MAIN_BRANCH 与上游分叉: 落后 $behind / 领先 $ahead, 将硬重置到 $upstream_main"
    if (( ahead > 0 )); then
      warn "本地 $MAIN_BRANCH 有 $ahead 个上游没有的提交, 重置后将丢弃(可用 reflog 找回)"
    fi
    run git checkout "$MAIN_BRANCH"
    # 目标是与上游严格一致, 故用 reset --hard 而非 merge(不留 fork 独有提交)
    run git reset --hard "$UPSTREAM_REMOTE/$MAIN_BRANCH"
  fi

  run git push --force-with-lease "$MAIN_REMOTE" "$MAIN_BRANCH"
}

# 步骤 3: DOCS_BRANCH 不存在则创建; 存在则把其净变更 squash 成一个提交、
#         rebase 到最新 main, 再 force push。
#
# 为什么 squash 而不直接 rebase: 工作分支历史里可能有「先加文件后删文件」的
# 中间提交, 逐个重放会在中间态撞 add/add 冲突; squash 成单个提交只重放净变更,
# 能干净套到 main 上(最终树与 squash 前完全一致)。
sync_docs() {
  if ! git show-ref --verify --quiet "refs/heads/$DOCS_BRANCH"; then
    log "$DOCS_BRANCH 不存在, 基于最新 $MAIN_BRANCH 创建"
    run git checkout -b "$DOCS_BRANCH"
    return
  fi

  log "$DOCS_BRANCH 已存在, 准备 squash 后 rebase 到 $MAIN_BRANCH"
  run git checkout "$DOCS_BRANCH"

  if (( DRY_RUN )); then
    warn "(dry-run) 将 backup -> soft reset 到 $MAIN_BRANCH -> 重新提交 -> push --force-with-lease $MAIN_REMOTE $DOCS_BRANCH"
    return
  fi

  # 已与 main 同步且无净变更则无需处理
  if [[ "$(git rev-parse "$DOCS_BRANCH")" == "$(git rev-parse "$MAIN_BRANCH")" ]]; then
    log "$DOCS_BRANCH 已与 $MAIN_BRANCH 一致, 跳过"
    return
  fi

  # 备份当前工作分支顶端, 便于回滚
  local backup="${DOCS_BRANCH}-backup"
  run git branch -f "$backup" "$DOCS_BRANCH"
  BACKUP_BRANCH="$backup"
  warn "已备份原 $DOCS_BRANCH 到 $backup"

  # 净变更: 工作分支相对 main 的最终差异
  local base
  base="$(git merge-base "$DOCS_BRANCH" "$MAIN_BRANCH")"
  if [[ -z "$(git diff --name-only "$base" "$DOCS_BRANCH")" ]]; then
    log "$DOCS_BRANCH 相对 $MAIN_BRANCH 无内容差异, 直接对齐"
    run git reset --hard "$MAIN_BRANCH"
    cleanup_backup
    return
  fi

  # 把净变更 squash 成单个提交, 落在最新 main 之上
  log "squash $DOCS_BRANCH 的净变更到 $MAIN_BRANCH 之上"
  run git reset --hard "$MAIN_BRANCH"
  run git merge --squash "$backup"
  run git commit -m "sync: $DOCS_BRANCH 工作内容(基于 $MAIN_BRANCH)"

  log "推送 $DOCS_BRANCH (--force-with-lease)"
  run git push --force-with-lease "$MAIN_REMOTE" "$DOCS_BRANCH"

  # 成功推送后清理本地备份分支
  cleanup_backup
}

main() {
  cd_to_git_root
  require_clean_branch

  START_BRANCH="$(git branch --show-current)"
  trap restore_on_failure EXIT
  log "当前分支: $START_BRANCH"

  ensure_upstream_remote
  stash_workdir
  sync_main
  sync_docs

  log "完成。$MAIN_BRANCH 已与上游同步, $DOCS_BRANCH 已 rebase。"
  # 成功路径: 回到进来时的分支(除非本来就在 MAIN/DOCS 分支)
  if [[ "$START_BRANCH" != "$DOCS_BRANCH" && "$START_BRANCH" != "$MAIN_BRANCH" ]]; then
    run git checkout "$START_BRANCH"
  fi
  if (( STASHED )); then
    warn "有 stash 待恢复, 切回原分支后执行: git stash pop"
  fi
  trap - EXIT
}

main "$@"