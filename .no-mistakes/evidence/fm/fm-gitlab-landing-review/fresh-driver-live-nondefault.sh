#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
E=/home/mike/.no-mistakes/evidence/01M4MQZR12Q7QC44Q6WM6MW6PD
H=$ROOT/.n
R=$ROOT/.test-fresh/provider
HEAD_SHA=dbef12b25aac57877fe1dc86332b065707c57d5b
mkdir -p "$H"
bin/fm-lab-home.sh create "$H"
mkdir -p "$H/tmux"
export TMUX_TMPDIR="$H/tmux"
SOCKET="$H/tmux/tmux-$(id -u)/fm-lab"
export FM_HOME=$H TMUX="$SOCKET,0,0" TREEHOUSE_ROOT="$ROOT/.test-fresh/treehouse-pool"
tmux -L fm-lab new-session -d -s fm-lab-nondefault -n keeper 'sleep 600'
tmux -L fm-lab new-window -t fm-lab-nondefault -n fm-nondefault-landed 'sleep 600'
trap 'tmux -L fm-lab kill-server 2>/dev/null || true' EXIT
printf 'manual\n' > "$H/config/backlog-backend"
git -C "$R" fetch --quiet origin "+refs/heads/jhebden/mr-issue-list-repo-less-scoping:refs/remotes/origin/jhebden/mr-issue-list-repo-less-scoping"
git -C "$R" branch -f live-provider-base "$HEAD_SHA^"
WT=$(cd "$R" && treehouse get --lease --no-fetch --base live-provider-base -b fm/nondefault-landed)
case "$WT" in "$ROOT"/.test-fresh/*) ;; *) exit 1 ;; esac
git -C "$WT" read-tree --reset -u origin/jhebden/mr-issue-list-repo-less-scoping
git -C "$WT" -c core.hooksPath=/dev/null -c user.name=LiveValidation -c user.email=validation@example.invalid commit -qm 'isolated composite already-landed target content'
LOCAL=$(git -C "$WT" rev-parse HEAD)
printf 'Fixture composite commit=%s; real provider source=%s\n' "$LOCAL" "$HEAD_SHA"
CHERRY=$(git -C "$WT" cherry "$HEAD_SHA" "$LOCAL")
printf 'Source-head containment must fail (independent of the product): %s\n' "$CHERRY"
[[ "$CHERRY" = '+ '* ]]
[ "$(git -C "$WT" rev-parse HEAD^{tree})" = "$(git -C "$WT" rev-parse origin/jhebden/mr-issue-list-repo-less-scoping^{tree})" ]
printf 'worktree=%s\nproject=%s\nwindow=fm-lab-nondefault:fm-nondefault-landed\nendpoint_task_id=nondefault-landed\nkind=ship\nmode=no-mistakes\nspawn_gen=s1791699000.125.456\npr=https://gitlab.com/gitlab-org/cli/-/merge_requests/3257\nbase_branch=deleted-legacy-source\n' "$WT" "$R" > "$H/state/nondefault-landed.meta"
printf 'done: PR https://gitlab.com/gitlab-org/cli/-/merge_requests/3257 checks green\n' > "$H/state/nondefault-landed.status"
printf 'Real cleanup requires independent verified-target content proof; recorded base does not exist.\n'
"$ROOT/bin/fm-teardown.sh" nondefault-landed > "$E/fresh-nondefault-live-content-teardown.log" 2>&1
tail -18 "$E/fresh-nondefault-live-content-teardown.log"
[ ! -e "$H/state/nondefault-landed.meta" ] && [ ! -e "$H/state/nondefault-landed.status" ]
(cd "$R" && treehouse status)
printf 'Verified: composite content not contained in MR source; actual nondefault target tree proves landing, and cleanup succeeds without rewriting the stale base.\n'
