# Test-phase receipts

Tested HEAD: `9cf2a1accc610cf62877df63d7921bb250f22297`. No source changes were made. Disposable worktree-local manual fixtures were removed. No publication, merge, completion replay, or live Herdr lifecycle was performed.

## Complete targeted landing regression

```sh
bash bin/fm-test-run.sh --json ~/.no-mistakes/evidence/01M5D2ERZK5D9ND4HZQD9PQ6FV/landing-regression.json tests/fm-pr-check-security.test.sh tests/fm-pr-merge.test.sh tests/fm-crew-state.test.sh tests/fm-teardown.test.sh tests/fm-teardown-endpoint-safety.test.sh tests/fm-review-diff.test.sh tests/fm-backlog-atomicity.test.sh tests/fm-tasks-axi.test.sh tests/fm-bootstrap.test.sh tests/fm-public-followup.test.sh tests/fm-fleet-snapshot-view.test.sh tests/fm-bearings-snapshot.test.sh tests/fm-inactive-reconcile.test.sh tests/fm-captain-hold-lifecycle.test.sh tests/fm-project-capacity.test.sh
```

Exit 0; all fifteen complete scripts ran, with no gate skips. Real production commands operated on disposable homes and Git repositories. Provider responses and endpoint operations in these hermetic suites are boundary fixtures, not proof of a real forge or harness login. In particular, the teardown cases use real separate-clone rebases, squash/fast-forward landings, source deletion and Git fetches; destructive endpoint completion is stubbed.

## Independent live product checks

- `fm_pr_gitlab_read_record gitlab.com im3sk/erp 780 proof`: actual GitLab response validated; state merged, head `6c5f61e4388fb99c7ba0dbda8b1909267011daa0`, target main.
- `fm_pr_gitlab_fetch_head <disposable-repository> gitlab.com im3sk/erp 780 <verified-head> refs/fm-review/disposable/merge-request/780/head`: exact actual provider head fetched. Anonymous/noninteractive default transport failed first; setting only the disposable repository's credential helper to `!glab auth git-credential` used the existing login and succeeded. No credential stores were modified. Both receipts are retained.
- `FM_HOME=<disposable-home> bash bin/fm-fleet-snapshot.sh --contribution-input`: canonical GitLab/GitHub/Forgejo review links survived as exact URLs, while a GitLab issue URL had null pr_url. Independent explicit jq assertions passed.
- `FM_HOME=<disposable-home> TMUX=<nonexistent-private-socket> bash bin/fm-fleet-view.sh`: actual CLI output is retained as fleet-view.md and escaped into fleet-view.html for reviewer-visible display. No browser UI was changed.
- `LC_ALL=en_US.utf8 bash bin/fm-test-run.sh --check-coverage`: real installed non-C locale; complete coverage succeeded without ordering errors.
- `git diff --exit-code 3eabd356 HEAD -- bin/fm-backlog-transition-lib.sh bin/fm-tasks-axi-lib.sh tests/fixtures.sh tests/fm-backlog-atomicity.test.sh tests/fm-tasks-axi.test.sh tests/fm-captain-hold-lifecycle.test.sh tests/fm-project-capacity.test.sh`: exit 0; deferred-only paths equal the supplied upstream base.

## Targeted test-infrastructure repair checks and limitations

```sh
bash bin/fm-test-run.sh --json ~/.no-mistakes/evidence/01M5D2ERZK5D9ND4HZQD9PQ6FV/runner-repairs.json tests/fm-supervision-host.test.sh tests/fm-remote-delta-read.test.sh tests/fm-spawn-orca-worktree.test.sh tests/fm-test-run.test.sh tests/fm-ci-workflow.test.sh
nohup bash bin/fm-test-run.sh --json ~/.no-mistakes/evidence/01M5D2ERZK5D9ND4HZQD9PQ6FV/orca-nohup.json tests/fm-spawn-orca-worktree.test.sh
unshare --user --map-root-user --pid --fork --mount-proc bash bin/fm-test-run.sh --json ~/.no-mistakes/evidence/01M5D2ERZK5D9ND4HZQD9PQ6FV/runner-pidns.json tests/fm-test-run.test.sh
unshare --user --map-current-user --pid --fork --mount-proc bash bin/fm-test-run.sh --json ~/.no-mistakes/evidence/01M5D2ERZK5D9ND4HZQD9PQ6FV/runner-user-pidns.json tests/fm-test-run.test.sh
```

Full host, delta reader and Orca suites passed; Orca also passed under nohup with inherited ignored HUP. This is local fixture evidence, not a real vendor-harness proof or hosted-CI readiness/performance claim.

The initial full runner suite failed a nested ancestry fixture requiring orphan PPID=1. A kernel double-fork diagnostic showed the host reparents orphans to user systemd PID 638 instead. A root-mapped private PID namespace resolved that assumption but invalidated a read-only-file assertion through namespace-root permissions. The final current-user-mapped private PID namespace retained zero effective capabilities and enforced read-only files; the complete runner invocation then passed the previously failing family scheduling assertion and continued to its YAML prerequisite. It exited 1 solely at `ruby is required to parse .github/workflows/ci.yml as YAML`. The workflow suite independently exited 1 with the same prerequisite diagnostic. Earlier failed receipts are retained, not replaced by a claim of a full pass.

`command -v ruby` found no Ruby on PATH; no repository-local interpreter was supplied. No host filesystem search, package installation, parser substitution, or assertion weakening was attempted. Provide Ruby on an approved PATH (or an approved repository-local interpreter) and rerun the complete runner and workflow suites. Required full validation remains blocked.

All background runner exit receipts and JSON results were read after completion. No runner remained active at final inspection; git status was clean. Lint, documentation gates, hosted CI, and publication belong to other outer phases and were not run here.
