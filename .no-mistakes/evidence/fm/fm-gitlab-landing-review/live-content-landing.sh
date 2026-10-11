#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
E=/home/mike/.no-mistakes/evidence/01M4MQZR12Q7QC44Q6WM6MW6PD
H=$ROOT/.test-disposable/content-home
R=$ROOT/.test-disposable/provider
HEAD_SHA=65f7619a15f3af64b39619d7a36a8cd9bae04a2b
mkdir -p "$H"
bin/fm-lab-home.sh create "$H"
mkdir -p "$H/tmux"
SOCKET=$ROOT/.test-disposable/content-sock
export FM_HOME=$H TMUX="$SOCKET,0,0" TREEHOUSE_ROOT="$ROOT/.test-disposable/treehouse-pool"
tmux -S "$SOCKET" new-session -d -s fm-lab-content -n keeper 'sleep 600'
tmux -S "$SOCKET" new-window -t fm-lab-content -n fm-content-landed 'sleep 600'
trap 'tmux -S "$SOCKET" kill-server 2>/dev/null || true' EXIT
printf 'manual\n' > "$H/config/backlog-backend"
WT=$(cd "$R" && treehouse get --lease --no-fetch --base live-provider-base -b fm/content-landed)
case "$WT" in "$ROOT"/.test-disposable/*) ;; *) exit 1 ;; esac
git -C "$WT" checkout origin/main -- .
git -C "$WT" -c core.hooksPath=/dev/null -c user.name=LiveValidation -c user.email=validation@example.invalid commit -qm 'isolated composite already-landed target content'
LOCAL=$(git -C "$WT" rev-parse HEAD)
printf 'Fixture composite commit=%s; real provider source=%s\n' "$LOCAL" "$HEAD_SHA"
CHERRY=$(git -C "$WT" cherry "$HEAD_SHA" "$LOCAL")
printf 'Source-head containment must fail (independent of the product): %s\n' "$CHERRY"
[[ "$CHERRY" = '+ '* ]]
[ "$(git -C "$WT" rev-parse HEAD^{tree})" = "$(git -C "$WT" rev-parse origin/main^{tree})" ]
printf 'worktree=%s\nproject=%s\nwindow=fm-lab-content:fm-content-landed\nendpoint_task_id=content-landed\nkind=ship\nmode=no-mistakes\nspawn_gen=s1791699000.125.456\npr=https://gitlab.com/gitlab-org/cli/-/merge_requests/4055\nbase_branch=deleted-legacy-source\n' "$WT" "$R" > "$H/state/content-landed.meta"
printf 'done: PR https://gitlab.com/gitlab-org/cli/-/merge_requests/4055 checks green\n' > "$H/state/content-landed.status"
printf 'Real cleanup requires independent verified-target content proof; recorded base does not exist.\n'
"$ROOT/bin/fm-teardown.sh" content-landed > "$E/live-content-teardown.log" 2>&1
tail -18 "$E/live-content-teardown.log"
[ ! -e "$H/state/content-landed.meta" ] && [ ! -e "$H/state/content-landed.status" ]
(cd "$R" && treehouse status)
printf 'Verified: composite content not contained in MR source; actual target main tree proves landing, and cleanup succeeds without rewriting the stale base.\n'
