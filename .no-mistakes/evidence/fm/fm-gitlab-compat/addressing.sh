#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
AXI=/home/mike/github/kunchenguid/firstmate/data/fm-gitlab-compat/dependency/node_modules/.bin/tasks-axi
unset FM_HOME FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE TASKS_AXI_FILE TASKS_AXI_BACKEND FM_TASKS_AXI_COMPATIBLE
export PATH="${AXI%/*}:$PATH"
D=$(mktemp -d "$ROOT/.test-phase-tmp/addressing.XXXXXX")
trap 'rm -rf "$D"' EXIT
export FM_HOME="$D/home" FM_DATA_OVERRIDE="$D/home/relocated"
mkdir -p "$FM_HOME"/{data,relocated,state,config} "$D/caller"
printf 'backend="markdown"\n[markdown]\npath="relocated/backlog.md"\ndone_keep=1\n' > "$FM_HOME/.tasks.toml"
printf 'Untouched default backlog sentinel\n' > "$FM_HOME/data/backlog.md"
. "$ROOT/bin/fm-tasks-axi-lib.sh"
. "$ROOT/bin/fm-backlog-transition-lib.sh"
cd "$FM_HOME"
"$AXI" add older 'Old completion to archive'
"$AXI" done older
"$AXI" add addressed 'Relocated close' --body 'Archive candidate' --start
cp "$FM_DATA_OVERRIDE/backlog.md" "$D/before"
cd "$D/caller"
URL=https://gitlab.example.test/nested/group/project/-/merge_requests/123
fm_backlog_completion_preview "$FM_DATA_OVERRIDE" addressed close --pr "$URL" --keep 1 || { printf 'Preview error: %s\n' "$FM_BACKLOG_TRANSITION_ERROR"; exit 1; }
printf '%s\n' "$FM_BACKLOG_TRANSITION_OUTPUT"
cmp "$FM_DATA_OVERRIDE/backlog.md" "$D/before"
[ ! -e "$FM_DATA_OVERRIDE/done-archive.md" ]
fm_backlog_close_marker_write "$FM_HOME/state" addressed "$FM_DATA_OVERRIDE" addressed-gen --pr "$URL"
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/addressed.backlog-close" "$FM_DATA_OVERRIDE"
"$AXI" show addressed --file "$FM_DATA_OVERRIDE/backlog.md"
grep -q 'older' "$FM_DATA_OVERRIDE/done-archive.md"
grep -q '^Untouched default backlog sentinel$' "$FM_HOME/data/backlog.md"
printf 'Relocated addressed preview and archive close succeeded from unrelated caller; default backlog untouched.\n'
"$AXI" add gerrit 'Preserved Gerrit completion' --start --file "$FM_DATA_OVERRIDE/backlog.md"
fm_backlog_close_marker_write "$FM_HOME/state" gerrit "$FM_DATA_OVERRIDE" gerrit-gen --pr https://review.example.com/c/project/+/7
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/gerrit.backlog-close" "$FM_DATA_OVERRIDE"
"$AXI" show gerrit --file "$FM_DATA_OVERRIDE/backlog.md" --full
printf 'Gerrit review recorded through note translation.\n'
printf 'manual\n' > "$FM_HOME/config/backlog-backend"
cp "$FM_DATA_OVERRIDE/backlog.md" "$D/manual.before"
if fm_backlog_transition_applies "$FM_HOME/config" "$FM_DATA_OVERRIDE" ship; then exit 1; fi
printf 'Manual mode skips automatic transitions: %s\n' "$FM_BACKLOG_TRANSITION_SKIP"
cmp "$FM_DATA_OVERRIDE/backlog.md" "$D/manual.before"
