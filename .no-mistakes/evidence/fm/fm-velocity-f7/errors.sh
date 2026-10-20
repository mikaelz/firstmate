#!/usr/bin/env bash
set -euo pipefail
export FM_HOME="$PWD/.lab"
unset FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE
# Exercise the real adapter's terminal error path with the actual park condition.
bin/fm-procevent-when.sh arm park-error-lab --interval 0.05 --error-budget 3 --condition "$PWD/bin/fm-pr-park.sh" changed missing --action "$PWD/bin/fm-pr-park.sh" resume-note missing
bin/fm-procevent.sh ensure-listening when-park-error-lab
for i in {1..100}; do
  results=("$FM_HOME/state/procevent-inbox/when-park-error-lab".*.result)
  test -f "${results[0]}" && break
  sleep .1
done
test -f "${results[0]}"
cat "${results[0]}"
test "$(bin/fm-procevent-when.sh classify "${results[0]}")" = condition-error
test ! -e "$FM_HOME/data/missing/park-resume.md"
printf 'No resume note was created on condition-error.\n'
bin/fm-procevent-when.sh retire park-error-lab
