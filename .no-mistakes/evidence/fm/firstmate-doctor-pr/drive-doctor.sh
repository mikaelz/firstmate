#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
E=~/.no-mistakes/evidence/01M74YV2J31HJE1E64YH86DZ07
W=$(mktemp -d "$ROOT/l.XXXXXX")
cleanup() {
  if [ -S "$W/tmux/tmux-$(id -u)/fm-lab" ]; then
    TMUX_TMPDIR="$W/tmux" tmux -L fm-lab kill-server || true
  fi
  rm -rf "$W"
}
trap cleanup EXIT
# Clear inherited operational routing. None of these checks use a fleet home.
unset FM_HOME FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE FM_BACKEND FM_SUPERVISION_MODEL TMUX TMUX_PANE HERDR_ENV HERDR_PANE_ID HERDR_SESSION HERDR_SOCKET_PATH CMUX_WORKSPACE_ID CMUX_SURFACE_ID CMUX_SOCKET_PATH
export FM_BOOTSTRAP_CLAUDE_USER_SETTINGS="$W/absent-settings.json"
export FM_BOOTSTRAP_NO_MISTAKES_HOME="$W/absent-nm"
run_doctor() {
  local label=$1 home=$2; shift 2
  local rc=0
  FM_HOME="$home" FM_ROOT_OVERRIDE="$home" bash "$ROOT/bin/fm-doctor.sh" "$@" > "$E/$label.out" 2> "$E/$label.err" || rc=$?
  printf '\n$ FM_HOME=<disposable> bash bin/fm-doctor.sh %s\nexit=%s\n' "$*" "$rc"
  python3 - "$E/$label.out" <<'PY'
import json,sys
text=open(sys.argv[1]).read()
try:
 d=json.loads(text)
 print(json.dumps({'verdict':d['verdict'],'checks':[c for c in d['checks'] if c['id']=='supervision/ready']},indent=2))
except ValueError: print(text)
PY
  return "$rc"
}
mkdir -p "$W/dead/state"
bash -c 'exit 0' & dead=$!; wait "$dead"
printf '%s\n' "$dead" > "$W/dead/state/.lock"
run_doctor dead-primary "$W/dead" --json --area supervision
jq -e '.verdict == "warn" and any(.checks[]; .id=="supervision/ready" and .status=="warn" and (.detail[0]|fromjson|.lock.state=="stale" and .can_receive==false and .wake_consumer.state=="unknown"))' "$E/dead-primary.out" >/dev/null
run_doctor dead-primary-toon "$W/dead" --area supervision
grep -q 'supervision/ready,Start or resume' "$E/dead-primary-toon.out"
# Replay the same real owner against the pre-fix inventory, not a mocked owner.
git show d5c552b1^:docs/doctor-checks.json > "$W/before.json"
FM_DOCTOR_INVENTORY="$W/before.json" run_doctor dead-primary-before "$W/dead" --json --area supervision
jq -e '.verdict == "ok" and any(.checks[]; .id=="supervision/ready" and .status=="info")' "$E/dead-primary-before.out" >/dev/null
printf 'Counterfactual: identical dead-owner state was info/ok under the pre-fix inventory.\n'
# Direct readiness and each public doctor format/filter must leave state absent.
mkdir -p "$W/empty/config" "$W/empty/data"
FM_HOME="$W/empty" bash bin/fm-inbox.sh ready | tee "$E/uninitialized-ready.json"
[ ! -e "$W/empty/state" ]
for args in '--json --area supervision' '--area supervision' '--json' ''; do
  label=readonly-$(echo "${args:-default}" | tr ' -' '__')
  run_doctor "$label" "$W/empty" $args || rc=$?
  [ ! -e "$W/empty/state" ]
done
printf 'Read-only boundary: direct ready and all four doctor format/filter combinations leave state/ absent.\n'
# Exercise the real configurable doctor consumer and real owner, with malformed
# responses induced using public owner commands (not replacement executables).
for mode in failed unreadable; do
  if [ "$mode" = failed ]; then argv='["bin/fm-inbox.sh","ready","unexpected-argument"]'; else argv='["bin/fm-inbox.sh","--help"]'; fi
  jq --argjson argv "$argv" '(.checks[]|select(.id=="supervision/ready")|.command)=$argv' docs/doctor-checks.json > "$W/$mode.json"
  FM_DOCTOR_INVENTORY="$W/$mode.json" run_doctor "$mode" "$W/empty" --json --area supervision
  jq -e '.verdict=="warn" and any(.checks[]; .id=="supervision/ready" and .status=="warn")' "$E/$mode.out" >/dev/null
 done
printf 'Failure guards: actual owner usage failure and successful text-only help both warn.\n'
# A separate marked home hosts only a real Claude CLI on its private socket.
mkdir "$W/primary-home"
bash bin/fm-lab-home.sh create "$W/primary-home"
# Keep the socket below Unix path length limits and within the worktree.
mkdir -p "$W/tmux"
env -u NO_MISTAKES_GATE -u FM_GATE_REFUSE_BYPASS -u FM_ROOT_OVERRIDE -u FM_STATE_OVERRIDE -u FM_DATA_OVERRIDE -u FM_CONFIG_OVERRIDE -u FM_PROJECTS_OVERRIDE TMUX_TMPDIR="$W/tmux" tmux -L fm-lab new-session -d -s primary -x 100 -y 32 -c "$PWD" -e FM_HOME="$W/primary-home" claude
sleep 7
TMUX_TMPDIR="$W/tmux" tmux -L fm-lab capture-pane -p -t primary > "$E/claude-primary-pane.txt"
printf '\nReal Claude primary startup surface:\n'
python3 -c 'import sys;print(open(sys.argv[1]).read())' "$E/claude-primary-pane.txt"
# Read-only inspection of only this private pane's process descendants.
pane_pid=$(TMUX_TMPDIR="$W/tmux" tmux -L fm-lab display-message -p -t primary '#{pane_pid}')
ps -o pid,ppid,comm,args -p "$pane_pid" > "$E/claude-primary-process.txt"
printf '%s\n' "$pane_pid" > "$W/primary-home/state/.lock"
touch "$W/primary-home/state/.last-watcher-beat"
FM_SUPERVISION_MODEL=autoarm run_doctor healthy-primary "$W/primary-home" --json --area supervision
jq -e '.verdict=="ok" and any(.checks[]; .id=="supervision/ready" and .status=="ok" and (.detail[0]|fromjson|.lock.state=="held" and .wake_consumer.state=="healthy" and .can_receive==true))' "$E/healthy-primary.out" >/dev/null
printf 'Healthy control: real Claude process plus synthetic fresh auto-arm beacon reports held/healthy/true and ok.\n'
TMUX_TMPDIR="$W/tmux" tmux -L fm-lab kill-server
printf '\nAll disposable homes and private tmux server are removed by the EXIT trap.\n'
