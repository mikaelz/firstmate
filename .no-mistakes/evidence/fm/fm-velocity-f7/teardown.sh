#!/usr/bin/env bash
set -euo pipefail
export FM_HOME="$PWD/.lab" TREEHOUSE_ROOT="$PWD/.lab/pool"
unset FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE
export TMUX_TMPDIR="$FM_HOME/tmux"
export TMUX=$(tmux -L fm-lab display-message -p -t primary '#{socket_path},#{pid},0')
wt=$(cd "$FM_HOME/project" && treehouse get --lease --no-fetch)
tmux -L fm-lab new-window -d -t primary -n fm-clean -c "$wt" bash
mkdir -p "$FM_HOME/data/clean"
printf 'Runtime cleanup test complete; no outstanding decisions.\n' > "$FM_HOME/data/clean/report.md"
printf 'manual\n' > "$FM_HOME/config/backlog-backend"
printf 'kind=scout\nbackend=tmux\nwindow=primary:fm-clean\nendpoint_task_id=clean\nworktree=%s\nproject=%s/project\nharness=codex\nspawn_gen=s1792510777.1954399.10926\n' "$wt" "$FM_HOME" > "$FM_HOME/state/clean.meta"
bin/fm-pr-park.sh park clean https://github.com/kunchenguid/firstmate/pull/7577
bin/fm-teardown.sh clean
test ! -e "$FM_HOME/state/clean.park"
test ! -e "$FM_HOME/state/clean.meta"
name="when-park-$(printf clean | sha256sum | cut -c1-54)"
listing=$(bin/fm-procevent.sh list)
printf '%s\n' "$listing"
! printf '%s\n' "$listing" | grep -F "$name"
printf 'Teardown removed task metadata, park record, watch registration, and endpoint.\n'
