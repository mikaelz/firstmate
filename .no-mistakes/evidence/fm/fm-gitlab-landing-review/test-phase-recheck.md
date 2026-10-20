# Test-phase recheck

HEAD: `9cf2a1accc610cf62877df63d7921bb250f22297`. No source edits or publication actions.

## Commands and actual completion

- `bin/fm-test-run.sh --json <evidence>/landing-regressions.json tests/fm-pr-check-security.test.sh tests/fm-pr-merge.test.sh tests/fm-crew-state.test.sh tests/fm-teardown.test.sh tests/fm-teardown-endpoint-safety.test.sh tests/fm-review-diff.test.sh tests/fm-backlog-atomicity.test.sh tests/fm-tasks-axi.test.sh tests/fm-bootstrap.test.sh tests/fm-public-followup.test.sh tests/fm-fleet-snapshot-view.test.sh tests/fm-bearings-snapshot.test.sh tests/fm-inactive-reconcile.test.sh tests/fm-captain-hold-lifecycle.test.sh tests/fm-project-capacity.test.sh`: tool terminated this invocation at 1200 seconds. Do not treat this invocation as an overall pass or as producing a timing JSON. `landing-regressions.log` retains completed exit=0 records for review-diff, crew-state, pr-merge, captain-hold-lifecycle, inactive-reconcile, teardown, pr-check-security, and bootstrap.
- `bin/fm-test-run.sh --json <evidence>/landing-remaining.json tests/fm-backlog-atomicity.test.sh tests/fm-tasks-axi.test.sh tests/fm-public-followup.test.sh tests/fm-fleet-snapshot-view.test.sh tests/fm-bearings-snapshot.test.sh tests/fm-teardown-endpoint-safety.test.sh tests/fm-project-capacity.test.sh`: re-drove every unfinished script completely; exit 0, no gate skips. Thus all fifteen requested targeted suites completed in this turn, but not in one uninterrupted aggregate invocation.
- `bin/fm-test-run.sh --jobs 1 --json <evidence>/fixture-repairs.json tests/fm-supervision-host.test.sh tests/fm-remote-delta-read.test.sh tests/fm-spawn-orca-worktree.test.sh`: exit 0; host duration 543416 ms. Local evidence only, not a hosted timing guarantee.
- `nohup bin/fm-test-run.sh --json <evidence>/orca-nohup-recheck.json tests/fm-spawn-orca-worktree.test.sh`: exit 0 under ignored-HUP inheritance.
- `unshare --user --map-root-user --pid --fork --mount-proc bin/fm-test-run.sh --jobs 1 --json <evidence>/runner-regressions.json tests/fm-test-run.test.sh tests/fm-ci-workflow.test.sh`: exit 1. Root mapping invalidated a read-only-lock assertion in a nested fixture; the independent workflow suite failed because Ruby is absent.
- `unshare --user --map-current-user --pid --fork --mount-proc bin/fm-test-run.sh --json <evidence>/runner-current-user.json tests/fm-test-run.test.sh`: corrected the namespace identity without source edits. Earlier scheduling/ancestry cases passed; suite then exited 1 at the missing Ruby YAML prerequisite. Not a complete suite pass.
- `LC_ALL=en_US.utf8 bin/fm-test-run.sh --check-coverage`: exit 0 with the actual installed non-C locale.

## Product evidence

- Real `fm_pr_gitlab_read_record gitlab.com im3sk/erp 780 proof`: exit 0; canonical URL, merged state, source SHA and main target retained in gitlab-provider-recheck.txt.
- Real `fm_pr_gitlab_fetch_head` against that MR in a disposable worktree-local repository using its own `credential.helper=!glab auth git-credential`: exit 0; exact live SHA matched. Existing login used; no credential-store changes. See gitlab-fetch-recheck.txt.
- Real `fm-fleet-snapshot.sh --contribution-input` on disposable backlog rows: exact GitLab, nested GitLab, GitHub and Forgejo URLs retained; issue, query-bearing and zero-IID URLs null. jq assertions passed. See canonical-links-recheck.json.
- Real `fm-fleet-view.sh` against that home: exit 0. CLI output retained as fleet-view-recheck.md and escaped into fleet-view-recheck.html. This is a CLI surface, not a browser UI; rendered HTML is supplied instead of a screenshot.
- Complete teardown suite drove separate-clone rebase, actual squash/fast-forward landing, deleted source and missing MR ref with real Git operations. Negative variants actively tried extra commits, dirty/untracked files, forged identity/project/head/target and expired heads. Provider metadata and endpoint cleanup are test boundary fixtures; these are not production endpoint lifecycle proofs.
- Complete review suite drove live fixture MR-head changes and stale metadata, unavailable/wrong heads and identities, exact target selection and another task's private ref preservation.
- Deferred-only seven paths equal supplied upstream base (`git diff --exit-code 3eabd356 HEAD -- <seven paths>` returned 0). Completion regression suites executed unchanged.

## Remaining limitation and cleanup

`command -v ruby` found no interpreter; no repository-local interpreter was provided. Author evidence explicitly forbids interpreter shims, alternate YAML consumers and host package installation. Provide approved Ruby on PATH, then rerun the entire runner and workflow suites using current-user PID isolation for the runner. Full requested validation is therefore incomplete, despite all driven product scenarios passing.

All launched batches ended; actual exit receipts and available timing JSONs were read. The interrupted first batch has no fabricated exit receipt. Disposable `.test-phase` home/repository removed. Final git status clean; no active processes referencing this worktree were observed. No Herdr lifecycle, live teardown, completion replay, lint, documentation gate, push, PR or CI phase was run. Existing earlier-turn evidence was not used as fresh validation.
