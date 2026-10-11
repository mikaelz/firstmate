#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
E=/home/mike/.no-mistakes/evidence/01M4MQZR12Q7QC44Q6WM6MW6PD
H=$ROOT/.test-disposable/landing-home
R=$ROOT/.test-disposable/provider
HEAD_SHA=65f7619a15f3af64b39619d7a36a8cd9bae04a2b
mkdir -p "$H"
bin/fm-lab-home.sh create "$H"
mkdir -p "$H/tmux"
SOCKET=$ROOT/.test-disposable/live-sock
export FM_HOME=$H TMUX="$SOCKET,0,0" TREEHOUSE_ROOT="$ROOT/.test-disposable/treehouse-pool"
tmux -S "$SOCKET" new-session -d -s fm-lab-landing -n keeper 'sleep 600'
tmux -S "$SOCKET" new-window -t fm-lab-landing -n fm-live-landed 'sleep 600'
trap 'tmux -S "$SOCKET" kill-server 2>/dev/null || true' EXIT
printf 'manual\n' > "$H/config/backlog-backend"
git -C "$R" branch -f live-provider-base "$HEAD_SHA^"
WT=$(cd "$R" && treehouse get --lease --no-fetch --base live-provider-base -b fm/live-landed)
case "$WT" in "$ROOT"/.test-disposable/*) ;; *) echo 'ERROR: pool not contained'; exit 1 ;; esac
printf 'Disposable real treehouse allocation: %s\n' "$WT"
git -C "$WT" -c core.hooksPath=/dev/null -c user.name=LiveValidation -c user.email=validation@example.invalid cherry-pick "$HEAD_SHA"
LOCAL=$(git -C "$WT" rev-parse HEAD)
[ "$LOCAL" != "$HEAD_SHA" ]
printf 'Replayed local commit=%s; actual verified provider source=%s\n' "$LOCAL" "$HEAD_SHA"
printf 'window=fm-lab-landing:fm-live-landed\nendpoint_task_id=live-landed\nworktree=%s\nproject=%s\nkind=ship\nmode=no-mistakes\nspawn_gen=s1791699000.124.456\npr=https://gitlab.com/gitlab-org/cli/-/merge_requests/4055\nbase_branch=deleted-legacy-source\n' "$WT" "$R" > "$H/state/live-landed.meta"
printf 'done: PR https://gitlab.com/gitlab-org/cli/-/merge_requests/4055 checks green\n' > "$H/state/live-landed.status"
printf '\nExecute real cleanup against merged public-provider evidence and a deleted recorded base:\n'
"$ROOT/bin/fm-teardown.sh" live-landed > "$E/live-landing-teardown.log" 2>&1
printf 'Cleanup output:\n'
tail -30 "$E/live-landing-teardown.log"
[ ! -f "$H/state/live-landed.meta" ]
[ ! -f "$H/state/live-landed.status" ]
(cd "$R" && treehouse status) > "$E/live-treehouse-status.txt"
printf '\nReal pool state after cleanup:\n'
head -30 "$E/live-treehouse-status.txt"
printf 'Verified: only disposable worker records retired; real treehouse lease released; operator homes and provider untouched.\n'
