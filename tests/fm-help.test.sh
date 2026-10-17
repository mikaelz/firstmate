#!/usr/bin/env bash
# Behavior tests for the main operator-facing bin/fm-* commands' -h/--help:
# each prints a usage to stdout, exits 0, and changes nothing in its home, and
# the short form stays short. The script headers remain the owners of each
# command's full contract; these tests pin only the help surface.
set -u

. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

TMP_ROOT=$(fm_test_tmproot fm-help-tests)

# Commands whose help is the short form. Each must fit in SHORT_HELP_MAX lines.
SHORT_HELP_COMMANDS=(
  fm-bootstrap fm-send fm-crew-state fm-wake-drain fm-pr-check fm-pr-merge
  fm-merge-local fm-teardown fm-update fm-lock fm-harness fm-project-mode
  fm-remote-doctor fm-branch-outcome fm-fleet-sync
)
SHORT_HELP_MAX=15

# Commands whose help prints their full header.
HEADER_HELP_COMMANDS=(
  fm-session-start fm-spawn fm-control fm-brief fm-tasks-axi fm-captain-hold
  fm-dispatch-resolve fm-inbox fm-startup-network fm-secondmate-restart
)

# run_help <command> <flag> <case-dir>: run the help in an isolated empty home
# and set HELP_OUT, HELP_ERR, and HELP_RC.
run_help() {
  local cmd=$1 flag=$2 dir=$3
  mkdir -p "$dir/home"
  HELP_RC=0
  HELP_OUT=$(cd "$dir" && FM_HOME="$dir/home" FM_ROOT_OVERRIDE="$dir/home" \
    "$ROOT/bin/$cmd.sh" "$flag" 2>"$dir/err" </dev/null) || HELP_RC=$?
  HELP_ERR=$(cat "$dir/err")
}

assert_help_contract() {  # <command> <flag> <case-dir>
  local cmd=$1 flag=$2 dir=$3
  [ "$HELP_RC" -eq 0 ] || fail "$cmd.sh $flag exited $HELP_RC: $HELP_ERR"
  assert_contains "$HELP_OUT" "$cmd.sh" "$cmd.sh $flag did not name the command on stdout"
  printf '%s\n' "$HELP_OUT" | grep -qi 'usage' \
    || fail "$cmd.sh $flag printed no usage line on stdout"
  [ -z "$(find "$dir/home" -mindepth 1 -print -quit)" ] \
    || fail "$cmd.sh $flag changed its home: $(find "$dir/home" -mindepth 1)"
}

test_short_help() {
  local cmd flag dir lines
  for cmd in "${SHORT_HELP_COMMANDS[@]}"; do
    for flag in -h --help; do
      dir="$TMP_ROOT/short-$cmd$flag"
      run_help "$cmd" "$flag" "$dir"
      assert_help_contract "$cmd" "$flag" "$dir"
      lines=$(printf '%s\n' "$HELP_OUT" | wc -l | tr -d ' ')
      [ "$lines" -le "$SHORT_HELP_MAX" ] \
        || fail "$cmd.sh $flag printed $lines lines, more than the short-help bound $SHORT_HELP_MAX"
      [ -z "$HELP_ERR" ] || fail "$cmd.sh $flag wrote to stderr: $HELP_ERR"
    done
  done
  pass "short -h/--help prints usage, exits 0, and changes nothing for every main command"
}

test_header_help() {
  local cmd flag dir
  for cmd in "${HEADER_HELP_COMMANDS[@]}"; do
    for flag in -h --help; do
      dir="$TMP_ROOT/header-$cmd$flag"
      run_help "$cmd" "$flag" "$dir"
      assert_help_contract "$cmd" "$flag" "$dir"
    done
  done
  pass "header -h/--help prints usage, exits 0, and changes nothing"
}

test_short_help
test_header_help
