# Doctor live CLI validation

Executed the real doctor and owner scripts using real PATH tools, isolated homes and synthetic local settings. No CLI replacements were used in the live driver. The focused shell suites separately use their own test doubles and are not claimed as live proof.

## Read a fresh home in JSON and TOON, filter checks, reject bad usage, and leave state absent

pass

Evidence: readonly-json.stdout; readonly-toon.stdout; readonly-area.stdout; readonly-usage.stderr; readonly-help.stdout

Real CLI and owner commands executed with disposable local homes and synthetic configuration.

## Detect and clear a provenance mismatch for the actual bash executable

pass

Evidence: provenance-mismatch.stdout; provenance-match.stdout

Real CLI and owner commands executed with disposable local homes and synthetic configuration.

## Report invalid dispatch and backend settings while accepting cortex, kiro, and hermes crew settings

pass

Evidence: configuration-malformed.stdout; configuration-cortex.stdout; configuration-kiro.stdout; configuration-hermes.stdout; configuration-not-supported.stdout; configuration-backend.stdout

Real CLI and owner commands executed with disposable local homes and synthetic configuration.

## Diagnose Claude auto-mode allow rules and respect local settings precedence without launching Claude

pass

Evidence: permissions-absent.stdout; permissions-one.stdout; permissions-family.stdout; permissions-other-root.stdout; permissions-local-precedence.stdout

Real CLI and owner commands executed with disposable local homes and synthetic configuration.

## Find an absent fallback executable in scalar, flow, and commented or unindented YAML lists

pass

Evidence: agents-scalar.stdout; agents-flow.stdout; agents-unindented.stdout; agents-commented.stdout; agents-indented.stdout; agents-installed.stdout

Real CLI and owner commands executed with disposable local homes and synthetic configuration.

## Report absent, malformed, at-limit, and over-limit startup memory budgets

pass

Evidence: memory-absent.stdout; memory-invalid.stdout; memory-at-budget.stdout; memory-over-budget.stdout

Real CLI and owner commands executed with disposable local homes and synthetic configuration.

## Warn when a real reaped primary PID leaves a stale lock and cannot receive work

pass

Evidence: readiness-dead.stdout

Real CLI and owner commands executed with disposable local homes and synthetic configuration.

## Opt into real unauthenticated GitHub probing and read synthetic completed or incomplete network reports

pass

Evidence: network-opt-out.stdout; network-opt-in.stdout; network-incomplete.stdout

Real CLI and owner commands executed with disposable local homes and synthetic configuration.

## Report a stale launcher pane against a real disposable Herdr session

untested

Evidence: herdr-prepare.log

Ran bin/fm-herdr-lab.sh prepare fm-lab-doctor-live with workspace-local XDG_CONFIG_HOME and lab state. The helper refused because its required running default fleet tripwire is absent. Provisioning before prepare or creating a default session would violate the trusted lab contract; using the operator configuration for provisioning would write outside the permitted workspace. Provide a pre-existing reference fleet and permission for named lab session files in its Herdr configuration root to run this check. No lab server was started.

The baseline correctly reports an unparseable installed no-mistakes version as tools/outdated, fail, with exit 1. This environment diagnostic is expected; it does not mean the scenario failed. The unauthenticated network scenario intentionally uses an empty disposable gh configuration and no tokens; it proves credential-failure handling, not authenticated GitHub access. Read-only assertions compare names, modes, mtimes and file hashes before and after execution. No runtime Claude permission enforcement was exercised.

## Default CLI output

```text
home: {run-worktree}/.doctor-live/readonly
verdict: fail
summary: "1 fail, 1 warn, 23 ok, 2 info, 9 skip"
checks[36]{id,status,evidence}:
  doctor/jq,ok,jq on PATH
  doctor/inventory,ok,32 checks valid
  doctor/bootstrap,ok,"finished, exit 0"
  doctor/unmapped-line,ok,every bootstrap line is mapped
  tools/missing,ok,none reported
  tools/outdated,fail,"OUTDATED: no-mistakes (installed: unparseable; requires 1.46.0; upgrade: no-mistakes update)"
  tools/missing-manual,ok,none reported
  tools/presentation,ok,none reported
  tools/provenance,ok,none reported
  backend/invalid,ok,none reported
  backend/herdr-launcher,ok,none reported
  config/crew-dispatch,ok,none reported
  config/startup-memory-budget,skip,printed only by the locked session-start sweep; read the session-start digest
  config/relay,skip,printed only by the locked session-start sweep; read the session-start digest
  permissions/claude-fm-scripts,ok,none reported
  no-mistakes/agents,ok,none reported
  auth/github,skip,network check; run fm-doctor.sh --network
  fleet/tangle,ok,none reported
  fleet/backlog-reconcile,ok,none reported
  fleet/home-summary,ok,none reported
  fleet/secondmate-handoff,ok,none reported
  fleet/record-hygiene,ok,none reported
  fleet/treehouse-pools,ok,none reported
  fleet/info,ok,none reported
  fleet/sync,skip,network check; run fm-doctor.sh --network
  fleet/secondmate-sync,skip,network check; run fm-doctor.sh --network
  fleet/secondmate-liveness,skip,network check; run fm-doctor.sh --network
  fleet/secondmate-nudge,skip,network check; run fm-doctor.sh --network
  fleet/config-reread,skip,network check; run fm-doctor.sh --network
  supervision/network-checks,skip,network check; run fm-doctor.sh --network
  supervision/ready,warn,can_receive=false lock.state=free wake_consumer.state=unknown
  supervision/startup-network,info,not started - no deferred network checks have run for this home yet.
  config/role,ok,"fm-role: user (default)"
  config/harness,ok,codex
  config/crew-harness,ok,codex
  memory/budget,info,"startup-memory-budget: invalid config/startup-memory-budget - file is absent"
findings[2]{id,fix}:
  tools/outdated,"Ask the captain, then run the upgrade command the line names."
  supervision/ready,Start or resume a firstmate session for this home and keep its supervision cycle live.
help[3]: Apply each fix through its owner command; never edit captain-owned files to clear a finding,Run fm-doctor.sh --network to add the GitHub auth probe and the last network report,Run fm-doctor.sh --json for every evidence line
```

## Stale primary output

```json
{
  "schema": "fm-doctor.v1",
  "home": "{run-worktree}/.doctor-live/readiness",
  "area": "supervision",
  "verdict": "warn",
  "counts": {
    "ok": 1,
    "warn": 1,
    "fail": 0,
    "info": 1,
    "skip": 1
  },
  "checks": [
    {
      "id": "doctor/inventory",
      "area": "doctor",
      "status": "ok",
      "evidence": "32 checks valid",
      "owner": "bin/fm-doctor.sh",
      "fix": "Correct docs/doctor-checks.json."
    },
    {
      "id": "supervision/network-checks",
      "area": "supervision",
      "owner": "bin/fm-startup-network.sh",
      "fix": "Rerun the command the line prints; the named checks are unknown, not failed.",
      "status": "skip",
      "evidence": "network check; run fm-doctor.sh --network"
    },
    {
      "id": "supervision/ready",
      "area": "supervision",
      "owner": "bin/fm-inbox.sh",
      "fix": "Start or resume a firstmate session for this home and keep its supervision cycle live.",
      "status": "warn",
      "evidence": "can_receive=false lock.state=stale wake_consumer.state=unknown",
      "detail": [
        "{\"schema\":\"fm-primary-ready.v1\",\"home\":\".doctor-live/readiness\",\"observed_at\":\"2026-11-16T05:30:49Z\",\"lock\":{\"state\":\"stale\",\"pid\":1352512,\"live_harness\":false},\"wake_consumer\":{\"state\":\"unknown\",\"reason\":\"supervision-model-unknown-for-home\",\"beacon_age_seconds\":null},\"posture\":{\"state\":\"present\"},\"can_receive\":false}"
      ]
    },
    {
      "id": "supervision/startup-network",
      "area": "supervision",
      "owner": "bin/fm-startup-network.sh",
      "fix": "Read bin/fm-startup-network.sh report and rerun the command it names.",
      "status": "info",
      "evidence": "not started - no deferred network checks have run for this home yet.",
      "detail": [
        "not started - no deferred network checks have run for this home yet."
      ]
    }
  ]
}
```

## Targeted regression validation

`bash tests/fm-doctor.test.sh` and `bash tests/fm-toon-lib.test.sh` exited 0. The initial bootstrap suite exited 1 because an absence fixture inherited the real `/usr/bin/herdr` through its fallback PATH. The rerun uses `FM_TEST_BASE_PATH=$PWD/.doctor-live/base-path`, a symlink directory preserving system commands while omitting herdr, zellij, cmux, paseo, rex, tern and tmux. This is test isolation only; live scenarios used the real PATH. Both bootstrap logs are retained.

The isolated-PATH bootstrap rerun exited 0, including the originally affected missing-session-CLI assertion. All three targeted suites completed. All live driver subprocesses were awaited; the guarded Herdr prepare attempt started no server. Disposable homes and the temporary driver were removed from the source tree.
