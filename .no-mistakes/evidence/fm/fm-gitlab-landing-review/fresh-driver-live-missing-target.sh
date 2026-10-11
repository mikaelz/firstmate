#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
E=/home/mike/.no-mistakes/evidence/01M4MQZR12Q7QC44Q6WM6MW6PD
R=$ROOT/.test-fresh/provider
H=$ROOT/.m
bin/fm-lab-home.sh create "$H"
mkdir -p "$H/tmux"
export FM_HOME="$H" TMUX_TMPDIR="$H/tmux" TREEHOUSE_ROOT="$ROOT/.test-fresh/treehouse-pool"
export TMUX="$H/tmux/tmux-$(id -u)/fm-lab,0,0"
tmux -L fm-lab new-session -d -s fm-lab-missing -n keeper 'sleep 600'
tmux -L fm-lab new-window -t fm-lab-missing -n fm-missing-target 'sleep 600'
trap 'tmux -L fm-lab kill-server 2>/dev/null || true' EXIT
printf 'manual\n' > "$H/config/backlog-backend"
. "$ROOT/bin/fm-pr-lib.sh"
fm_pr_gitlab_read_record gitlab.com gitlab-org/cli 3869 proof
printf 'Actual merged MR: %s source=%s literal target=%s\n' "$FM_PR_RECORD_URL" "$FM_PR_RECORD_HEAD" "$FM_PR_RECORD_TARGET"
[ -z "$(git -C "$R" ls-remote origin "refs/heads/$FM_PR_RECORD_TARGET")" ]
printf 'Verified live target branch is absent from origin.\n'
WT=$(cd "$R" && treehouse get --lease --no-fetch --base live-provider-base -b fm/missing-target)
case "$WT" in "$ROOT"/.test-fresh/*) ;; *) exit 1 ;; esac
git -C "$WT" read-tree --reset -u origin/main
git -C "$WT" -c core.hooksPath=/dev/null -c user.name=LiveValidation -c user.email=validation@example.invalid commit -qm 'isolated content landed in main, not the literal target'
HEAD_BEFORE=$(git -C "$WT" rev-parse HEAD)
[ "$(git -C "$WT" rev-parse 'HEAD^{tree}')" = "$(git -C "$WT" rev-parse 'origin/main^{tree}')" ]
printf 'window=fm-lab-missing:fm-missing-target\nendpoint_task_id=missing-target\nworktree=%s\nproject=%s\nkind=ship\nmode=no-mistakes\nspawn_gen=s1791699000.126.456\npr=https://gitlab.com/gitlab-org/cli/-/merge_requests/3869\nbase_branch=deleted-legacy-source\n' "$WT" "$R" > "$H/state/missing-target.meta"
printf 'done: PR https://gitlab.com/gitlab-org/cli/-/merge_requests/3869 checks green\n' > "$H/state/missing-target.status"
BEFORE=$(sha256sum "$H/state/missing-target.meta")
rc=0
bin/fm-teardown.sh missing-target > "$E/fresh-missing-target-teardown.log" 2>&1 || rc=$?
[ "$rc" != 0 ]
grep -E 'REFUSED|not landed|unpushed' "$E/fresh-missing-target-teardown.log"
[ "$BEFORE" = "$(sha256sum "$H/state/missing-target.meta")" ]
[ "$HEAD_BEFORE" = "$(git -C "$WT" rev-parse HEAD)" ]
[ -f "$H/state/missing-target.status" ]
printf 'exit=%s; main content is landed, but missing literal target correctly refuses; all task records and committed work remain intact.\n' "$rc"
