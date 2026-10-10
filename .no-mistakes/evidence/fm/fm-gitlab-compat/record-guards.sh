#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
AXI=/home/mike/github/kunchenguid/firstmate/data/fm-gitlab-compat/dependency/node_modules/.bin/tasks-axi
unset FM_HOME FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE TASKS_AXI_FILE TASKS_AXI_BACKEND FM_TASKS_AXI_COMPATIBLE
export PATH="${AXI%/*}:$PATH"
D=$(mktemp -d "$ROOT/.test-phase-tmp/guards.XXXXXX")
trap 'rm -rf "$D"' EXIT
export FM_HOME="$D/home"
mkdir -p "$FM_HOME"/{state,data,config}
printf 'backend="markdown"\n[markdown]\npath="data/backlog.md"\n' > "$FM_HOME/.tasks.toml"
cd "$FM_HOME"
. "$ROOT/bin/fm-tasks-axi-lib.sh"
. "$ROOT/bin/fm-backlog-transition-lib.sh"
"$AXI" add guards 'Protected completion' --start
printf 'spawn_gen=guard-generation\n' > state/guards.meta
URL=https://gitlab.example.test/group/sub/project/-/merge_requests/7
fm_backlog_close_marker_write "$FM_HOME/state" guards "$FM_HOME/data" guard-generation --pr "$URL"
cp data/backlog.md "$D/backlog.before"; cp state/guards.meta "$D/meta.before"; cp state/guards.backlog-close "$D/marker.before"
ln state/guards.backlog-close "$D/alias"
if fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/guards.backlog-close" "$FM_HOME/data"; then exit 1; fi
printf 'Hardlink refused: %s\n' "$FM_BACKLOG_TRANSITION_ERROR"
cmp data/backlog.md "$D/backlog.before"; cmp state/guards.meta "$D/meta.before"; cmp state/guards.backlog-close "$D/marker.before"
rm "$D/alias"
# Malformed review link must fail consumer preview while records survive.
if fm_backlog_completion_preview "$FM_HOME/data" guards close --pr "$URL?injected=1"; then exit 1; fi
printf 'Malformed artifact refused: %s\n' "$FM_BACKLOG_TRANSITION_ERROR"
cmp data/backlog.md "$D/backlog.before"; cmp state/guards.meta "$D/meta.before"
# Foreign data and symlink records remain structurally invalid independently of preview support.
mkdir "$D/foreign"
if fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/guards.backlog-close" "$D/foreign"; then exit 1; fi
printf 'Foreign root refused: %s\n' "$FM_BACKLOG_TRANSITION_ERROR"
mv state/guards.backlog-close "$D/real-marker"
ln -s "$D/real-marker" state/guards.backlog-close
if fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/guards.backlog-close" "$FM_HOME/data"; then exit 1; fi
printf 'Symlink refused: %s\n' "$FM_BACKLOG_TRANSITION_ERROR"
rm state/guards.backlog-close; mv "$D/real-marker" state/guards.backlog-close
cmp data/backlog.md "$D/backlog.before"; cmp state/guards.meta "$D/meta.before"
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/guards.backlog-close" "$FM_HOME/data"
[ ! -e state/guards.meta ] && [ ! -e state/guards.backlog-close ]
"$AXI" done guards --dry-run --json
printf 'Single-link retry succeeded after guard refusals; original task remained untouched until valid replay.\n'
