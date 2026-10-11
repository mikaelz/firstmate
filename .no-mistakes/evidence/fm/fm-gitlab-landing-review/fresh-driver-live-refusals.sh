#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
E=/home/mike/.no-mistakes/evidence/01M4MQZR12Q7QC44Q6WM6MW6PD
H=$ROOT/.test-fresh/refusal-home
R=$ROOT/.test-fresh/provider
mkdir -p "$H"
bin/fm-lab-home.sh create "$H"
mkdir -p "$H/tmux"
export FM_HOME=$H TMUX="$H/tmux/unstarted,0,0"
printf 'manual\n' > "$H/config/backlog-backend"
printf 'window=fm-lab-refusal:fm-live-refusal\nendpoint_task_id=live-refusal\nworktree=%s\nproject=%s\nkind=ship\nmode=no-mistakes\nspawn_gen=s1791699000.123.456\npr=https://gitlab.com/gitlab-org/cli/-/merge_requests/4055\nbase_branch=deleted-legacy-source\n' "$R" "$R" > "$H/state/live-refusal.meta"
printf 'done: PR https://gitlab.com/gitlab-org/cli/-/merge_requests/4055 checks green\n' > "$H/state/live-refusal.status"
BEFORE=$(sha256sum "$H/state/live-refusal.meta")
HEAD_BEFORE=$(git -C "$R" rev-parse HEAD)
for variant in extra-commit untracked tracked-dirty; do
  case "$variant" in
    untracked) printf 'preserve untracked\n' > "$R/untracked-proof.txt" ;;
    tracked-dirty) rm "$R/untracked-proof.txt"; printf 'preserve dirty\n' >> "$R/stale-local-only.txt" ;;
  esac
  printf '\nReal teardown attempt: %s against actual merged public MR\n' "$variant"
  rc=0
  "$ROOT/bin/fm-teardown.sh" live-refusal > "$E/fresh-live-refusal-$variant.log" 2>&1 || rc=$?
  printf 'exit=%s\n' "$rc"
  grep -E 'REFUSED|unpushed commits|uncommitted|stale-local|untracked-proof' "$E/fresh-live-refusal-$variant.log"
  [ "$rc" -ne 0 ]
  case "$variant" in
    extra-commit) grep -q 'not landed' "$E/fresh-live-refusal-$variant.log" ;;
    *) grep -q 'uncommitted changes' "$E/fresh-live-refusal-$variant.log" ;;
  esac
  [ "$BEFORE" = "$(sha256sum "$H/state/live-refusal.meta")" ]
  [ "$HEAD_BEFORE" = "$(git -C "$R" rev-parse HEAD)" ]
  [ -d "$R" ] && [ -f "$H/state/live-refusal.status" ]
  printf 'Preserved: metadata bytes, status, checkout, committed HEAD, and local work.\n'
done
