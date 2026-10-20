#!/usr/bin/env bash
set -euo pipefail
export FM_HOME="$PWD/.lab"
unset FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE
export TMUX_TMPDIR="$FM_HOME/tmux"
export TMUX=$(tmux -L fm-lab display-message -p -t primary '#{socket_path},#{pid},0')
mkdir -p "$FM_HOME/work"
printf 'uncommitted sentinel\n' > "$FM_HOME/work/preserve.txt"
meta() { printf 'kind=ship\nbackend=tmux\nwindow=primary:fm-%s\nworktree=%s/work\nproject=lab\nharness=claude\n' "$1" "$FM_HOME" > "$FM_HOME/state/$1.meta"; }
expect() { local expected=$1; shift; set +e; "$@"; local got=$?; set -e; printf 'exit=%s expected=%s: %s\n' "$got" "$expected" "$*"; test "$got" -eq "$expected"; }
PR=https://github.com/kunchenguid/firstmate/pull/7577
meta live
bin/fm-pr-park.sh park live "$PR"
cat "$FM_HOME/state/live.park"
bin/fm-procevent.sh list
expect 1 bin/fm-pr-park.sh changed live
expect 1 bin/fm-pr-park.sh park live "$PR"
meta other
expect 1 bin/fm-pr-park.sh park other https://gitlab.com/acme/widget/-/merge_requests/3
printf 'kind=secondmate\n' > "$FM_HOME/state/mate.meta"
expect 1 bin/fm-pr-park.sh park mate "$PR"
expect 1 bin/fm-pr-park.sh park other https://github.com/kunchenguid/firstmate/pull/999999999
expect 1 bin/fm-pr-park.sh park other "$PR"
test ! -e "$FM_HOME/state/other.park"
# Seed historical state in the disposable persisted baseline, leaving the real
# GitHub endpoint and every production executable unchanged.
python3 - <<'PY'
from pathlib import Path
p=Path('.lab/state/live.park'); lines=p.read_text().splitlines(); lines[2]=lines[2].replace(lines[2].split()[1], '0'*40); p.write_text('\n'.join(lines)+'\n')
PY
expect 0 bin/fm-pr-park.sh changed live
name="park-$(printf live | sha256sum | cut -c1-54)"
bin/fm-procevent.sh ensure-listening "when-$name"
for i in {1..100}; do
  results=("$FM_HOME/state/procevent-inbox/when-$name".*.result)
  test -f "${results[0]}" && break
  sleep .1
done
test -f "${results[0]}"
cat "${results[0]}"
test "$(bin/fm-procevent-when.sh classify "${results[0]}")" = fired
cat "$FM_HOME/data/live/park-resume.md"
bin/fm-pr-park.sh unpark live
bin/fm-pr-park.sh unpark live
seq=${results[0]%.result}; seq=${seq##*.}
bin/fm-procevent.sh handled "when-$name" "$seq"
bin/fm-procevent.sh handled "when-$name" "$seq"
test "$(cat "$FM_HOME/work/preserve.txt")" = 'uncommitted sentinel'
tmux -L fm-lab list-windows -t primary -F '#{window_name} #{pane_current_command}'
printf 'Endpoint and uncommitted sentinel preserved; watcher fired once and acknowledgement is idempotent.\n'
# The largest accepted id must register through the real source-name validator.
id=$(printf '%064d' 0)
tmux -L fm-lab new-window -d -t primary -n "fm-$id" bash
meta "$id"
bin/fm-pr-park.sh park "$id" "$PR"
bin/fm-procevent.sh list
bin/fm-pr-park.sh unpark "$id"
