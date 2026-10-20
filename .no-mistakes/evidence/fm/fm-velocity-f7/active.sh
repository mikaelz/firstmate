#!/usr/bin/env bash
set -euo pipefail
export FM_HOME="$PWD/.lab"
unset FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE
export TMUX_TMPDIR="$FM_HOME/tmux"
export TMUX=$(tmux -L fm-lab display-message -p -t primary '#{socket_path},#{pid},0')
tmux -L fm-lab rename-window -t primary fm-active
tmux -L fm-lab set-option -w -t primary remain-on-exit on
mkdir -p "$FM_HOME/work" "$FM_HOME/data/active"
git -C "$FM_HOME/work" init -q
git -C "$FM_HOME/work" -c user.name=Lab -c user.email=lab@example.invalid commit --allow-empty -qm initial
printf 'uncommitted sentinel\n' > "$FM_HOME/work/preserve.txt"
printf 'kind=scout\nbackend=tmux\nwindow=primary:fm-active\nworktree=%s/work\nproject=lab\nharness=codex\n' "$FM_HOME" > "$FM_HOME/state/active.meta"
printf 'This is a disposable runtime validation. Reply READY and wait. Do not run tools, change files, or contact services.\n' > "$FM_HOME/data/active/brief.md"
bin/fm-pr-park.sh park active https://github.com/kunchenguid/firstmate/pull/7577
tmux -L fm-lab display-message -p -t primary 'after park: command=#{pane_current_command} dead=#{pane_dead}'
bin/fm-pr-park.sh resume-note active
bin/fm-control.sh active relaunch --note-file "$FM_HOME/data/active/park-resume.md"
bin/fm-pr-park.sh unpark active
test "$(cat "$FM_HOME/work/preserve.txt")" = 'uncommitted sentinel'
tmux -L fm-lab capture-pane -p -t primary
