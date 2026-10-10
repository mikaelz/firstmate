#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/mike/.no-mistakes/worktrees/cb3ff81633e8/01M4JBM95D48A03T591CXFSNHX
AXI=/home/mike/github/kunchenguid/firstmate/data/fm-gitlab-compat/dependency/node_modules/.bin/tasks-axi
ARTIFACT=/home/mike/github/kunchenguid/firstmate/data/tasks-gitlab-compat/tasks-axi-ad17640f013adf8120175db621f804d1b4554f48.tgz
unset FM_HOME FM_STATE_DIR FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE TASKS_AXI_FILE TASKS_AXI_BACKEND
export PATH="${AXI%/*}:$PATH"
lab=$(mktemp -d "$ROOT/.test-phase-tmp/fm-compatible-integration.XXXXXX")
trap 'chmod -R u+w "$lab"; rm -rf "$lab"' EXIT
export FM_HOME="$lab/home"
mkdir -p "$FM_HOME"/{data,state,config}
printf 'backend = "markdown"\n[markdown]\npath = "data/backlog.md"\n' > "$FM_HOME/.tasks.toml"
cd "$FM_HOME"
. "$ROOT/bin/fm-tasks-axi-lib.sh"
. "$ROOT/bin/fm-backlog-transition-lib.sh"
url=https://gitlab.example.test/group/sub/project/-/merge_requests/7
"$AXI" add close-test 'real consumer completion' --body 'original body' >/dev/null
"$AXI" start close-test >/dev/null
cp data/backlog.md "$lab/before"
"$AXI" done close-test --pr "$url" --dry-run --json > "$lab/done-preview.json"
"$AXI" update close-test --pr "$url" --body 'replacement body' --archive-body --dry-run --json > "$lab/update-preview.json"
jq -e '.dry_run == true' "$lab/done-preview.json" "$lab/update-preview.json" >/dev/null
cmp data/backlog.md "$lab/before"
[ ! -e data/done-archive.md ] && [ ! -e data/note-archive.md ]
echo 'PASS: real done/update previews preserve row, body, dates and archives'
printf 'spawn_gen=integration-gen\n' > state/close-test.meta
fm_backlog_close_marker_write "$FM_HOME/state" close-test "$FM_HOME/data" integration-gen --pr "$url"
cp state/close-test.backlog-close "$lab/marker-before"
# Read-only data permits real validation previews but refuses actual consumer writes.
chmod u-w data
"$AXI" done close-test --pr "$url" --dry-run --json | jq -e '.dry_run == true' >/dev/null
if "$AXI" done close-test --pr "$url" --json > "$lab/write-error" 2>&1; then echo 'FAIL: read-only actual write succeeded'; exit 1; fi
grep -E 'EACCES|permission denied' "$lab/write-error"
if fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/close-test.backlog-close" "$FM_HOME/data"; then echo 'FAIL: read-only replay succeeded'; exit 1; fi
[ -f state/close-test.backlog-close ]
cmp data/backlog.md "$lab/before"
echo 'PASS: positive preview, real filesystem write refusal, surviving retry record'
chmod u+w data
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/close-test.backlog-close" "$FM_HOME/data"
[ ! -e state/close-test.meta ] && [ ! -e state/close-test.backlog-close ]
"$AXI" done close-test --dry-run --json > "$lab/closed.json"
cp data/backlog.md "$lab/closed"
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/close-test.backlog-close" "$FM_HOME/data"
cmp data/backlog.md "$lab/closed"
echo 'PASS: real successful close and idempotent replay'
# Already-Done recovery adds exactly one link and keeps the original close date.
"$AXI" add backfill-test 'already done backfill' >/dev/null
"$AXI" done backfill-test --json > "$lab/backfill-before.json"
fm_backlog_close_marker_write "$FM_HOME/state" backfill-test "$FM_HOME/data" absent-generation --pr "$url"
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/backfill-test.backlog-close" "$FM_HOME/data"
"$AXI" done backfill-test --dry-run --json > "$lab/backfill-after.json"
python3 - "$lab/backfill-before.json" "$lab/backfill-after.json" "$url" <<'PY'
import json,sys
before,after=(json.load(open(p)) for p in sys.argv[1:3])
assert before['task']['closed']==after['task']['closed'], (before,after)
assert after['task']['links']==[{'kind':'pr','url':sys.argv[3]}], after
PY
cp data/backlog.md "$lab/backfilled"
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/backfill-test.backlog-close" "$FM_HOME/data"
cmp data/backlog.md "$lab/backfilled"
echo 'PASS: absent-metadata backfill retains original close date and one exact link'
"$AXI" add held-test 'unresolved captain call' >/dev/null
"$AXI" start held-test >/dev/null
"$AXI" hold held-test --kind captain --reason 'choose next work' >/dev/null
printf 'spawn_gen=held-generation\n' > state/held-test.meta
fm_backlog_close_marker_write "$FM_HOME/state" held-test "$FM_HOME/data" held-generation --pr "$url"
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/held-test.backlog-close" "$FM_HOME/data"
"$AXI" update held-test --pr "$url" --dry-run --json > "$lab/held.json"
jq -e '.task.held == true and .task.state != "done"' "$lab/held.json" >/dev/null
cat "$lab/held.json"
[ ! -e state/held-test.meta ] && [ ! -e state/held-test.backlog-close ]
"$AXI" show held-test | grep -q 'hold_kind: captain'
echo 'PASS: real held retention records delivery without closing unresolved captain call'

# Exercise a real retirement failure after real completion, not a mocked rm.
"$AXI" add retirement-test 'completion before failed record retirement' >/dev/null
fm_backlog_close_marker_write "$FM_HOME/state" retirement-test "$FM_HOME/data" retirement-generation --pr "$url"
chmod u-w state
if fm_backlog_atomic_transition close '' "$FM_HOME/state/retirement-test.backlog-close" "$FM_HOME/data" retirement-test "$FM_HOME/state" --pr "$url"; then
  echo 'FAIL: read-only completion record retired'; exit 1
fi
printf 'Actual retirement error: %s\n' "$FM_BACKLOG_TRANSITION_ERROR"
[ -f state/retirement-test.backlog-close ]
"$AXI" done retirement-test --dry-run --json > "$lab/retirement.json"
jq -e '.task.state == "done"' "$lab/retirement.json" >/dev/null
cp data/backlog.md "$lab/retired-before"
chmod u+w state
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/retirement-test.backlog-close" "$FM_HOME/data"
[ ! -e state/retirement-test.backlog-close ]
cmp data/backlog.md "$lab/retired-before"
cat "$lab/retirement.json"
echo 'PASS: completed row survives real retirement refusal; recovery retires record without duplicate link or date mutation'
# A new generation cannot be moved by a saved old-generation completion.
"$AXI" add new-generation-test 'new incarnation must survive' --start >/dev/null
fm_backlog_close_marker_write "$FM_HOME/state" new-generation-test "$FM_HOME/data" old-generation --pr "$url"
printf 'spawn_gen=new-generation\n' > state/new-generation-test.meta
cp data/backlog.md "$lab/generation-before"
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/new-generation-test.backlog-close" "$FM_HOME/data"
cmp data/backlog.md "$lab/generation-before"
[ -f state/new-generation-test.meta ] && [ ! -e state/new-generation-test.backlog-close ]
echo 'PASS: stale intent retired without moving the new generation'
# Interrupted physical cleanup reports a distinct outcome, not ordinary success.
"$AXI" add incomplete-test 'incomplete cleanup must retain retry evidence' --start >/dev/null
fm_backlog_close_marker_write "$FM_HOME/state" incomplete-test "$FM_HOME/data" incomplete-generation --pr "$url"
fm_backlog_close_marker_mark_cleanup_incomplete "$FM_HOME/state" "$FM_HOME/state/incomplete-test.backlog-close" incomplete-test "$FM_HOME/data" incomplete-generation --pr "$url"
fm_backlog_close_marker_replay "$FM_HOME/state" "$FM_HOME/state/incomplete-test.backlog-close" "$FM_HOME/data"
[ "$FM_BACKLOG_CLOSE_REPLAY_RESULT" = closed_incomplete ]
printf 'Interrupted-cleanup replay result: %s (not ordinary closed success)\n' "$FM_BACKLOG_CLOSE_REPLAY_RESULT"
[ ! -e state/incomplete-test.backlog-close ]
"$AXI" done incomplete-test --dry-run --json | jq -e '.task.state == "done"' >/dev/null
printf "\nFinal persisted private backlog:\n"
cat data/backlog.md
printf "\nReal consumer preview receipts:\n"
cat "$lab/done-preview.json" "$lab/update-preview.json" "$lab/backfill-before.json" "$lab/backfill-after.json"
