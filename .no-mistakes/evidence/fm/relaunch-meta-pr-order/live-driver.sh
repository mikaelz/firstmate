#!/usr/bin/env bash
set -eu
ROOT=$PWD
LAB=$ROOT/.l
export FM_HOME=$LAB TMUX_TMPDIR=$LAB/tmux
export TMUX=$(tmux -L fm-lab display-message -p '#{socket_path},#{pid},0')
unset FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE FM_GATE_REFUSE_BYPASS HERDR_ENV HERDR_SESSION HERDR_PANE_ID HERDR_SOCKET_PATH
ID=$(cat "$LAB/task-id")
. "$ROOT/bin/fm-pr-lib.sh"
printf '%s\n' "$$" > "$LAB/state/.lock"
for tracing in off on; do
 printf '%s %s\n' "$$" "$tracing" > "$LAB/state/.trace-context-effective"
 if [ "$tracing" = on ]; then
   { echo 'traceparent=00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-bbbbbbbbbbbbbbbb-01'; cat "$LAB/state/$ID.meta"; } > "$LAB/seed.meta"
   mv "$LAB/seed.meta" "$LAB/state/$ID.meta"
 fi
 fm_pr_poll_artifacts_valid "$LAB/state" "$ID" "$ROOT/bin/fm-pr-poll.sh"
 echo "Tracing $tracing before restart: merge check authenticated"
 FM_SPAWN_NO_GUARD=1 "$ROOT/bin/fm-control.sh" "$ID" relaunch --note 'Validate the restart only; reply Ready and wait. Do not execute commands or change files.'
 fm_pr_poll_artifacts_valid "$LAB/state" "$ID" "$ROOT/bin/fm-pr-poll.sh"
 echo "Tracing $tracing after restart: original merge check authenticated"
 cat "$LAB/state/$ID.meta"
 tmux -L fm-lab capture-pane -p -t "lab:fm-$ID"
 sleep 3
 if [ "$tracing" = off ]; then
 tmux -L fm-lab kill-window -t "lab:fm-$ID"
 tmux -L fm-lab new-window -d -t lab -n "fm-$ID" -c "$LAB/wt" -e FM_HOME="$LAB" -e PATH="$LAB/bin:$PATH" 'bash --noprofile --norc -i'
 sleep 1
 fi
 done
cp "$LAB/state/$ID.meta" "$LAB/good.meta"
echo 'control_relaunch_tx=illegal-suffix' >> "$LAB/state/$ID.meta"
if fm_pr_poll_artifacts_valid "$LAB/state" "$ID" "$ROOT/bin/fm-pr-poll.sh"; then
 echo 'FAIL: accepted illegal suffix'; exit 1
fi
echo 'Adversarial illegal suffix after PR identity: correctly rejected'
cp "$LAB/good.meta" "$LAB/state/$ID.meta"
fm_pr_poll_artifacts_valid "$LAB/state" "$ID" "$ROOT/bin/fm-pr-poll.sh"
echo 'Restored valid record: original merge check authenticated'
