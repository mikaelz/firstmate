#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
AXI=/home/mike/github/kunchenguid/firstmate/data/fm-gitlab-compat/dependency/node_modules/.bin/tasks-axi
unset FM_HOME FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE TASKS_AXI_FILE TASKS_AXI_BACKEND FM_TASKS_AXI_COMPATIBLE
export PATH="${AXI%/*}:$PATH"
D=$(mktemp -d "$ROOT/.test-phase-tmp/retain.XXXXXX")
trap 'chmod -R u+w "$D"; rm -rf "$D"' EXIT
export FM_HOME="$D/home"
mkdir -p "$FM_HOME"/{state,data,config}
printf 'backend="markdown"\n[markdown]\npath="data/backlog.md"\n' > "$FM_HOME/.tasks.toml"
cd "$FM_HOME"
. "$ROOT/bin/fm-tasks-axi-lib.sh"
. "$ROOT/bin/fm-backlog-transition-lib.sh"
"$AXI" add retained 'Decision with deliverable' --start --body 'Original body'
"$AXI" hold retained --kind captain --reason 'Retain unresolved decision'
URL=https://gitlab.example.test/group/sub/project/-/merge_requests/7
printf 'spawn_gen=retained-gen\n' > state/retained.meta
fm_backlog_close_marker_write "$FM_HOME/state" retained "$FM_HOME/data" retained-gen --retain --pr "$URL"
cp data/backlog.md "$D/before"
fm_backlog_completion_preview "$FM_HOME/data" retained retain --pr "$URL"
printf 'Positive retention preview: %s\n' "$FM_BACKLOG_TRANSITION_OUTPUT"
chmod u-w data
if fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/retained.backlog-close" "$FM_HOME/data"; then exit 1; fi
printf 'Real retained write refusal: %s\n' "$FM_BACKLOG_TRANSITION_ERROR"
[ -f state/retained.backlog-close ]
grep -q 'mode=retain' state/retained.backlog-close
cmp data/backlog.md "$D/before"
printf 'Persisted retained retry intent:\n'; while IFS= read -r line; do printf '%s\n' "$line"; done < state/retained.backlog-close
chmod u+w data
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/retained.backlog-close" "$FM_HOME/data"
[ ! -e state/retained.backlog-close ]
"$AXI" update retained --pr "$URL" --dry-run --json > "$D/receipt.json"
jq -e '.task.held == true and .task.state != "done" and .task.links == [{kind:"pr",url:"https://gitlab.example.test/group/sub/project/-/merge_requests/7"}]' "$D/receipt.json"
cp data/backlog.md "$D/after"
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/retained.backlog-close" "$FM_HOME/data"
cmp data/backlog.md "$D/after"
printf 'Held delivery recovered once without closing captain call or duplicating link/body.\n'
