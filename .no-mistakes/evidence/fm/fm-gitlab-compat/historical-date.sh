#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
AXI=/home/mike/github/kunchenguid/firstmate/data/fm-gitlab-compat/dependency/node_modules/.bin/tasks-axi
unset FM_HOME FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE TASKS_AXI_FILE TASKS_AXI_BACKEND FM_TASKS_AXI_COMPATIBLE
export PATH="${AXI%/*}:$PATH"
D=$(mktemp -d "$ROOT/.test-phase-tmp/historical-date.XXXXXX")
trap 'rm -rf "$D"' EXIT
export FM_HOME="$D/home"
mkdir -p "$FM_HOME"/{data,state,config}
printf 'backend="markdown"\n[markdown]\npath="data/backlog.md"\n' > "$FM_HOME/.tasks.toml"
cd "$FM_HOME"
. "$ROOT/bin/fm-tasks-axi-lib.sh"
. "$ROOT/bin/fm-backlog-transition-lib.sh"
"$AXI" add historical 'Historical completion' >/dev/null
"$AXI" done historical >/dev/null
# The Markdown adapter's persisted row is the input data contract, not source.
python3 - <<'PY'
import pathlib,re
p=pathlib.Path('data/backlog.md')
s=p.read_text()
print('Seeded persisted row:',s)
s,n=re.subn(r'\(done \d{4}-\d{2}-\d{2}\)', '(done 2025-01-02)',s)
assert n==1
p.write_text(s)
PY
URL=https://gitlab.example.test/group/sub/project/-/merge_requests/7
for round in 1 2; do
 fm_backlog_close_marker_write "$FM_HOME/state" historical "$FM_HOME/data" absent-generation --pr "$URL"
 fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/historical.backlog-close" "$FM_HOME/data"
 "$AXI" done historical --dry-run --json > "$D/receipt.json"
 jq -e '.task.closed == "2025-01-02" and .task.links == [{kind:"pr",url:"https://gitlab.example.test/group/sub/project/-/merge_requests/7"}]' "$D/receipt.json"
 if [ "$round" = 1 ]; then cp data/backlog.md "$D/first"; else cmp data/backlog.md "$D/first"; fi
 cat "$D/receipt.json"
done
printf 'Historical close date preserved across repeated persisted-record backfill; exactly one canonical link.\n'
