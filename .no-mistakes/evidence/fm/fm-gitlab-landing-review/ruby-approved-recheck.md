# Approved Ruby prerequisite recheck

Tested HEAD: `9cf2a1accc610cf62877df63d7921bb250f22297` (unchanged).

The reported failure was an environment prerequisite, not a demonstrated product defect. `/usr/bin/ruby` now reports Ruby 3.4.10; `ruby -ryaml` successfully loaded YAML. No interpreter installation, alternate parser, assertion change, or source edit was needed.

Executed both complete named suites through the real runner, preserving current-user private PID isolation:

```
unshare --user --map-current-user --pid --fork --mount-proc bin/fm-test-run.sh --jobs 1 --json <evidence>/ruby-approved-regressions.json tests/fm-test-run.test.sh tests/fm-ci-workflow.test.sh
```

Actual process exit: 0, retained in `ruby-approved-regressions.exit`. Full output: `ruby-approved-regressions.log`; exact command: `ruby-approved-regressions.command`; machine timing: `ruby-approved-regressions.json`. Runner suite exit 0 (231777 ms); workflow suite exit 0 (4900 ms). Total 2, failed 0, skipped_gate 0, 236759 ms. The real Ruby YAML consumer completed both suites, including workflow partition and timeout semantics. All three selected findings concerned this same prerequisite/incomplete verification and are resolved by these actual complete executions.

## Reconciliation with preserved same-head receipts

No prior receipts were edited or replaced. `test-phase-recheck.md` records the same tested HEAD. Re-read actual completion records in the retained transcripts:

- `landing-regressions.log`: complete exit-0 records for review-diff, crew-state, pr-merge, captain-hold-lifecycle, inactive-reconcile, teardown, pr-check-security, bootstrap (8 suites). The interrupted aggregate invocation remains interrupted, not an aggregate pass.
- `landing-remaining.log`: complete exit-0 records for backlog-atomicity, public-followup, tasks-axi, fleet-snapshot-view, bearings-snapshot, teardown-endpoint-safety, project-capacity (7 suites); aggregate total 7, failed 0, skipped_gate 0.
- Together these receipts cover all fifteen required landing/completion suites; none were rerun or newly claimed in this repair turn.
- `fixture-repairs.log`: host, delta reader, Orca complete exit-0 records; total 3, failed 0, skipped_gate 0. `orca-nohup-recheck.log`: complete Orca exit 0 under nohup.
- Prior real-provider, canonical-link and locale evidence remains as recorded in `test-phase-recheck.md`; this turn did not repeat those scenarios.
- Earlier runner/workflow prerequisite failures remain historical failures, superseded only by the new complete two-suite run above.

Final tracked diff and git status are clean. No transient working-tree artifacts remain. Private PID namespace exited with the runner; no disposable server/browser was launched, and no process referencing the exact working-tree path remained in the post-check process listing. No lint, formatter, static analysis, full-repository test invocation, publication, PR or hosted CI phase was executed. Current-head hosted CI readiness remains owned by the outer executor and is not established by these local passes.
