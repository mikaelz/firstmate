# Current-head test reconciliation

Validated head: `7dea21b6bd302f6b74094bdc39b629d20ed7b176`. No source changes.

## Complete fresh receipts
- `current-ruby`: exit 0; 2 complete scripts; 424155 ms. Full transcript and JSON retained.
  - `tests/fm-test-run.test.sh`: exit 0, gate_skip=False, 413499 ms.
  - `tests/fm-ci-workflow.test.sh`: exit 0, gate_skip=False, 10478 ms.
- `current-landing`: exit 0; 15 complete scripts; 2569313 ms. Full transcript and JSON retained.
  - `tests/fm-review-diff.test.sh`: exit 0, gate_skip=False, 31862 ms.
  - `tests/fm-crew-state.test.sh`: exit 0, gate_skip=False, 219690 ms.
  - `tests/fm-pr-merge.test.sh`: exit 0, gate_skip=False, 628718 ms.
  - `tests/fm-captain-hold-lifecycle.test.sh`: exit 0, gate_skip=False, 1246677 ms.
  - `tests/fm-inactive-reconcile.test.sh`: exit 0, gate_skip=False, 40626 ms.
  - `tests/fm-teardown.test.sh`: exit 0, gate_skip=False, 286180 ms.
  - `tests/fm-pr-check-security.test.sh`: exit 0, gate_skip=False, 312123 ms.
  - `tests/fm-bootstrap.test.sh`: exit 0, gate_skip=False, 63852 ms.
  - `tests/fm-backlog-atomicity.test.sh`: exit 0, gate_skip=False, 251632 ms.
  - `tests/fm-public-followup.test.sh`: exit 0, gate_skip=False, 402240 ms.
  - `tests/fm-teardown-endpoint-safety.test.sh`: exit 0, gate_skip=False, 34393 ms.
  - `tests/fm-tasks-axi.test.sh`: exit 0, gate_skip=False, 2713 ms.
  - `tests/fm-fleet-snapshot-view.test.sh`: exit 0, gate_skip=False, 25570 ms.
  - `tests/fm-bearings-snapshot.test.sh`: exit 0, gate_skip=False, 188110 ms.
  - `tests/fm-project-capacity.test.sh`: exit 0, gate_skip=False, 63375 ms.
- `current-fixtures`: exit 0; 4 complete scripts; 1600011 ms. Full transcript and JSON retained.
  - `tests/fm-supervision-host.test.sh`: exit 0, gate_skip=False, 906770 ms.
  - `tests/fm-remote-delta-read.test.sh`: exit 0, gate_skip=False, 8374 ms.
  - `tests/fm-spawn-orca-worktree.test.sh`: exit 0, gate_skip=False, 136103 ms.
  - `tests/fm-backend-herdr-presentation-e2e.test.sh`: exit 0, gate_skip=False, 548303 ms.
- `current-orca-nohup`: exit 0; 1 complete scripts; 88802 ms. Full transcript and JSON retained.
  - `tests/fm-spawn-orca-worktree.test.sh`: exit 0, gate_skip=False, 88680 ms.

## Commands
```sh
ruby --version
ruby -ryaml -e 'puts YAML::VERSION'
unshare --user --map-current-user --pid --fork --mount-proc bin/fm-test-run.sh --jobs 1 --json "$E/current-ruby.json" tests/fm-test-run.test.sh tests/fm-ci-workflow.test.sh
bin/fm-test-run.sh --json "$E/current-landing.json" tests/fm-review-diff.test.sh tests/fm-crew-state.test.sh tests/fm-pr-merge.test.sh tests/fm-captain-hold-lifecycle.test.sh tests/fm-inactive-reconcile.test.sh tests/fm-teardown.test.sh tests/fm-pr-check-security.test.sh tests/fm-bootstrap.test.sh tests/fm-backlog-atomicity.test.sh tests/fm-public-followup.test.sh tests/fm-teardown-endpoint-safety.test.sh tests/fm-tasks-axi.test.sh tests/fm-fleet-snapshot-view.test.sh tests/fm-bearings-snapshot.test.sh tests/fm-project-capacity.test.sh
bin/fm-test-run.sh --jobs 1 --json "$E/current-fixtures.json" tests/fm-supervision-host.test.sh tests/fm-remote-delta-read.test.sh tests/fm-spawn-orca-worktree.test.sh tests/fm-backend-herdr-presentation-e2e.test.sh
nohup bin/fm-test-run.sh --json "$E/current-orca-nohup.json" tests/fm-spawn-orca-worktree.test.sh
LC_ALL=en_US.utf8 bin/fm-test-run.sh --check-coverage
```

E names this evidence directory. The landing list above is the complete executed inventory (displayed in completion order).

## Product observations
- Actual GitLab MR 780 proof read and exact origin-bound source-head fetch succeeded using the existing login; no credentials changed. See current-provider.txt.
- Separate-clone real Git rebase, squash, fast-forward, source deletion, and expired MR-ref scenarios passed through the actual teardown executable. Provider/endpoint boundaries are fixtures, not production teardown.
- Extra committed work, dirty/untracked files, forged identities/projects/heads/targets, stale heads, and private-ref boundaries were exercised by complete security, teardown and review suites.
- Actual snapshot and fleet-view commands on a disposable worktree-local home preserved GitLab (including nested groups), GitHub and Forgejo URLs; issue/zero-IID/query URLs were rejected. current-fleet.html is an escaped rendering of actual CLI output; this is not a browser UI, so no screenshot was taken.
- Real Herdr 0.9.5 lab presentation suite completed all cases, including simultaneous cross-home recovery, explicit lock-wait and default-session tripwire verification. The suite used only the guarded named fm-lab helper and completed teardown.
- Complete runner and workflow suites now pass with Ruby 3.4.10 and real YAML 5.2.2. Current-user PID isolation retained. No parser substitutions, installations, weakened assertions or new skips.

## Receipt reconciliation and boundaries
Earlier receipts remain untouched. Their recorded head 9cf2a1a is not the present 7dea21b head, so they are historical context, not substituted current passes. All fifteen required suites and fixture corrections were freshly executed here. tests/fm-teardown-endpoint-safety.test.sh is the actual endpoint suite; no fake alias was created. Existing markdown-only capability case skips remain disclosed in the full transcripts; no complete selected script gate-skipped.
Seven deferred-only paths equal the supplied upstream base 9fe25bca (git diff --exit-code succeeded). No completion preflight was added. Disposable .test-current home and clone were removed. No lint, formatter, static-analysis, publication, PR, hosted CI, merge, credential mutation, production teardown or completion replay was performed. Local test success is not current-head hosted CI readiness; those other phases belong to the outer executor.
