#!/usr/bin/env bash
set -euo pipefail
D=$PWD/.test-phase-tmp/fork-named
mkdir -p "$D"
trap 'rm -rf "$D"' EXIT
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
. bin/fm-pr-lib.sh
fm_pr_gitlab_read_record gitlab.com gitlab-org/cli 4046 proof
H=$FM_PR_RECORD_HEAD
printf 'Fork MR verified: url=%s state=%s head=%s target=%s\n' "$FM_PR_RECORD_URL" "$FM_PR_RECORD_STATE" "$H" "$FM_PR_RECORD_TARGET"
GITLAB_HOST=gitlab.com glab mr view 4046 -R https://gitlab.com/gitlab-org/cli -F json | jq '{iid,web_url,state,sha,diff_refs,target_branch,target_project_id,source_project_id}'
git init -q "$D/repo"
git -C "$D/repo" remote add origin https://gitlab.com/gitlab-org/cli.git
resolved=$(fm_pr_gitlab_fetch_head "$D/repo" gitlab.com gitlab-org/cli 4046 "$H" refs/fm-review/fork/merge-request/4046/head)
[ "$resolved" = "$H" ]
printf 'Target-repository fork source resolved exactly: %s\n' "$resolved"
git -C "$D/repo" show --format=fuller --no-patch "$resolved"
if fm_pr_gitlab_fetch_head "$D/repo" gitlab.com foreign/project 4046 "$H" refs/fm-review/foreign/head; then exit 1; fi
printf 'Unverified foreign target refused\n'
fm_pr_gitlab_read_record gitlab.com gitlab-org/gitlab 201855 proof
[ "$FM_PR_RECORD_TARGET" = 18-0-stable-ee ]
printf 'Named target verified: url=%s state=%s head=%s target=%s\n' "$FM_PR_RECORD_URL" "$FM_PR_RECORD_STATE" "$FM_PR_RECORD_HEAD" "$FM_PR_RECORD_TARGET"
GITLAB_HOST=gitlab.com glab api projects/gitlab-org%2Fgitlab | jq '{path_with_namespace,default_branch}'
git ls-remote https://gitlab.com/gitlab-org/gitlab.git refs/heads/18-0-stable-ee
printf 'Named target exists independently of default; runtime tree-equality fallback is covered separately by focused executable regression.\n'
