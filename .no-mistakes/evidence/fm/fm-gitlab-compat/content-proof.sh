#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
D=$(mktemp -d "$ROOT/.test-phase-tmp/content.XXXXXX")
trap 'rm -rf "$D"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
. "$ROOT/bin/fm-pr-lib.sh"
fm_pr_gitlab_read_record gitlab.com im3sk/erp 780 proof
head=$FM_PR_RECORD_HEAD; target=$FM_PR_RECORD_TARGET
[ "$FM_PR_RECORD_STATE" = merged ]
git init -q "$D/repo"
protocol=$(glab config get git_protocol --host gitlab.com)
case "$protocol" in ssh) origin=git@gitlab.com:im3sk/erp.git ;; https) origin=https://gitlab.com/im3sk/erp.git ;; *) exit 2 ;; esac
git -C "$D/repo" remote add origin "$origin"
fetched=$(fm_pr_gitlab_fetch_head "$D/repo" gitlab.com im3sk/erp 780 "$head" refs/fm-review/private-proof/merge-request/780/head)
git -C "$D/repo" fetch --quiet origin "+refs/heads/$target:refs/remotes/origin/$target"
target_tree=$(git -C "$D/repo" rev-parse "refs/remotes/origin/$target^{tree}")
merged_tree=$(git -C "$D/repo" merge-tree --write-tree "refs/remotes/origin/$target" "$head")
printf 'web_url=%s\nhead=%s\nfetched_source_sha=%s\ntarget=%s\ntarget_identity=verified\n' "$FM_PR_RECORD_URL" "$head" "$fetched" "$target"
[ "${merged_tree%%$'\n'*}" = "$target_tree" ]
printf 'content_tree_equal=yes\nIndependent disposable copy; no endpoint cleanup or completion replay.\n'
