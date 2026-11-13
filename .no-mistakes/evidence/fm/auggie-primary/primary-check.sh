#!/usr/bin/env bash
set -eu
printf 'Detected harness: '
bin/fm-harness.sh
printf 'Ancestry: '
bin/fm-harness.sh ancestry
bin/fm-lock.sh
bin/fm-lock.sh
bin/fm-lock.sh status
printf 'Lock owner identity: '
pid=$(head -1 "$FM_HOME/state/.lock")
ps -o pid=,comm=,args= -p "$pid"
printf 'Primary check complete\n'
