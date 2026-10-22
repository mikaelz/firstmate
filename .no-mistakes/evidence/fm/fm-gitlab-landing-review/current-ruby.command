unshare --user --map-current-user --pid --fork --mount-proc bin/fm-test-run.sh --jobs 1 --json "$E/current-ruby.json" tests/fm-test-run.test.sh tests/fm-ci-workflow.test.sh
