#!/usr/bin/env bash
set -eu
ROOT=$PWD
LAB=$ROOT/.l
export FM_HOME=$LAB TMUX_TMPDIR=$LAB/tmux
unset FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE FM_GATE_REFUSE_BYPASS HERDR_ENV HERDR_SESSION HERDR_PANE_ID HERDR_SOCKET_PATH
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
ID=labpr$$
printf '%s\n' "$ID" > "$LAB/task-id"
mkdir "$LAB/proj"
git -C "$LAB/proj" init -q
printf 'Disposable live relaunch fixture\n' > "$LAB/proj/README.md"
git -C "$LAB/proj" add README.md
git -C "$LAB/proj" -c user.name=Test -c user.email=test@example.invalid commit -qm initial
git -C "$LAB/proj" worktree add -q -b "$ID" "$LAB/wt"
mkdir -p "$LAB/data/$ID"
cat > "$LAB/data/$ID/brief.md" <<'EOF'
# Disposable test
## Captain's intent
Validate restarting a worker with an existing PR record.
## Firstmate spec
This is a disposable CLI test. Do not change files, execute commands, start validation, or contact any service. Reply with "Ready for the relaunch test" and wait.
EOF
{
 echo "window=lab:fm-$ID"
 echo "endpoint_task_id=$ID"
 echo "backend=tmux"
 echo "worktree=$LAB/wt"
 echo "project=$LAB/proj"
 echo 'harness=codex'
 echo 'kind=ship'
 echo 'mode=no-mistakes'
 echo 'yolo=off'
 echo "tasktmp=/tmp/fm-$ID"
 echo 'model=default'
 echo 'effort=default'
 echo 'traceparent=00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb-01'
 echo 'pr=https://github.com/example/repo/pull/35'
 echo 'pr_head=0123456789abcdef0123456789abcdef01234567'
 echo 'x_request=request-35'
} > "$LAB/state/$ID.meta"
printf '%s\n' "$$" > "$LAB/state/.lock"
printf '%s off\n' "$$" > "$LAB/state/.trace-context-effective"
. "$ROOT/bin/fm-pr-lib.sh"
fm_pr_poll_prepare "$LAB/state" "$ID" github https://github.com/example/repo/pull/35 github.com example/repo 35 "$ROOT/bin/fm-pr-poll.sh"
fm_pr_poll_publish_prepared
fm_pr_poll_artifacts_valid "$LAB/state" "$ID" "$ROOT/bin/fm-pr-poll.sh"
echo 'Before relaunch: existing merge check authenticated'
tmux -L fm-lab new-window -t lab -n "fm-$ID" -c "$LAB/wt" -e FM_HOME="$LAB" 'codex --disable hooks --dangerously-bypass-approvals-and-sandbox'
sleep 4
tmux -L fm-lab capture-pane -p -t "lab:fm-$ID"
FM_SPAWN_NO_GUARD=1 "$ROOT/bin/fm-control.sh" "$ID" relaunch --note 'Validate the restart only; reply Ready and wait. Do not execute commands or change files.'
fm_pr_poll_artifacts_valid "$LAB/state" "$ID" "$ROOT/bin/fm-pr-poll.sh"
echo 'Tracing off: original merge check remains authenticated after real worker relaunch'
cat "$LAB/state/$ID.meta"
tmux -L fm-lab capture-pane -p -t "lab:fm-$ID"
