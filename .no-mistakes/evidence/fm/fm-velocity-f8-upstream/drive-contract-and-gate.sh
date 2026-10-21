#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
EVIDENCE=~/.no-mistakes/evidence/01M5CZ1860EBX8A6QARV9XGDDB
LAB=$ROOT/.f8-validation/lab
mkdir -p "$LAB/home" "$LAB/project"
unset FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE GIT_DIR GIT_COMMON_DIR GIT_WORK_TREE GIT_INDEX_FILE
export FM_HOME=$LAB/home TMPDIR=$ROOT/.f8-validation/tmp GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME=Validation GIT_AUTHOR_EMAIL=validation@example.invalid GIT_COMMITTER_NAME=Validation GIT_COMMITTER_EMAIL=validation@example.invalid
for forge in none gerrit; do
  bin/fm-brief.sh "f8-$forge" disposable --mode no-mistakes --forge "$forge"
  cp "$FM_HOME/data/f8-$forge/brief.md" "$EVIDENCE/brief-$forge.md"
done
python3 - "$EVIDENCE" <<'PY'
import pathlib,sys
for forge in ('none','gerrit'):
    brief=(pathlib.Path(sys.argv[1])/f'brief-{forge}.md').read_text()
    assert 'start the no-mistakes run yourself in that same turn' in brief
    assert 'do not end your turn, and do not append `done:`, between your commit and the run' in brief
    assert 'Firstmate will then instruct you' not in brief
    assert 'done [at=<epoch>]: {summary}' not in brief
    ready='PR {url} checks green' if forge=='none' else 'PR {change url} published for review'
    assert f'done [at=<epoch>]: {ready}' in brief
    print(f'{forge}: generated worker brief requires same-turn validation, omits handoff, retains {ready}')
PY
git -C "$LAB/project" init -q -b main
git -C "$LAB/project" commit -q --allow-empty -m baseline
git clone -q --bare "$LAB/project" "$LAB/origin.git"
git -C "$LAB/project" remote add origin "$LAB/origin.git"
git -C "$LAB/project" worktree add -q -b fm/f8 "$LAB/worker"
git -C "$LAB/worker" commit -q --allow-empty -m implementation
. bin/fm-dod-lib.sh
check() {
  local expected=$1 line=$2 out rc=0
  out=$(fm_dod_accept_ship_done ship no-mistakes "$LAB/worker" "$LAB/project" "$line") || rc=$?
  printf 'REPORT: %s\nACCEPTANCE: exit=%s %s\n' "$line" "$rc" "$out"
  [ "$rc" -eq "$expected" ]
}
check 0 'done: implemented legacy task'
check 1 'done: PR https://example.test/o/r/pull/1 checks green'
check 1 'done: PR https://example.test/o/r/pull/1 published for review'
git -C "$LAB/worker" push -q origin HEAD:refs/heads/fm/f8
git -C "$LAB/worker" fetch -q origin
check 0 'done: PR https://example.test/o/r/pull/1 checks green'
git -C "$LAB/worker" commit -q --allow-empty -m unpushed-followup
check 1 'done: PR https://example.test/o/r/pull/1 checks green'
