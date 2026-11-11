# Live doctor validation

The real bin/fm-doctor.sh was executed from the run worktree with disposable FM_HOME, HOME, settings, and no-mistakes configuration inside the worktree. No operator settings or credentials were used. All disposable files were removed.

Behavioral oracles: the doctor CLI header and documented configuration contracts; supported adapters in AGENTS.md; YAML sequence semantics; the memory estimator contract ceil(bytes/3); required OUTDATED mapping; and read-only preservation of existing home paths, modes and contents. The old-tool case supplies a synthetic external gh-axi executable returning 0.1.0. It does not replace the doctor or bootstrap.

Output, area filtering, usage errors, skipped checks, and existing-home read-only: PASS
Supported crew adapters (including cortex, kiro, hermes), unsupported adapter, invalid backend and dispatch: PASS
Detect missing fallback executables from scalar, flow, indented and commented unindented YAML lists: PASS
Claude auto-mode settings warning and family allow-rule boundary using synthetic settings: PASS
Real jq provenance mismatch and matching installation: PASS
Missing, malformed, exact-boundary and exceeded memory budgets: PASS
Opt-in real gh auth probe in credential-free disposable home reports failure: PASS
Real doctor classifies synthetic below-floor external gh-axi as tools/outdated: PASS


The baseline real-tool run correctly reported the available no-mistakes version as unparseable in this isolated environment. Thus its exit 1 was expected diagnostic output, not a failed assertion. The failed-auth scenario intentionally supplied a fresh GH_CONFIG_DIR and removed token variables.

The driver initially expected an ok internal check to remain visible under --area tools. The CLI suppresses successful internal checks in area mode; the driver was corrected to reject an unmapped-line failure instead. The completed rerun exited 0.


## full-json

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "fail",
  "checks": [
    {
      "id": "doctor/jq",
      "area": "doctor",
      "status": "ok",
      "evidence": "jq on PATH",
      "owner": "bin/fm-doctor.sh",
      "fix": "Install jq; the doctor needs it to read its inventory."
    },
    {
      "id": "doctor/inventory",
      "area": "doctor",
      "status": "ok",
      "evidence": "30 checks valid",
      "owner": "bin/fm-doctor.sh",
      "fix": "Correct docs/doctor-checks.json."
    },
    {
      "id": "doctor/bootstrap",
      "area": "doctor",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Rerun bin/fm-bootstrap.sh by hand to see why it did not finish.",
      "detail": [],
      "status": "ok",
      "evidence": "finished, exit 0"
    },
    {
      "id": "doctor/unmapped-line",
      "area": "doctor",
      "owner": "bin/fm-doctor.sh",
      "fix": "Map the new prefix in docs/doctor-checks.json and handle it in the bootstrap-diagnostics skill.",
      "status": "ok",
      "evidence": "every bootstrap line is mapped"
    },
    {
      "id": "tools/missing",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Ask the captain, then run bin/fm-bootstrap.sh install <tool> (the line names the install command).",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/outdated",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Ask the captain, then run the upgrade command the line names.",
      "status": "fail",
      "evidence": "OUTDATED: no-mistakes (installed: unparseable; requires 1.46.0; upgrade: no-mistakes update)",
      "detail": [
        "OUTDATED: no-mistakes (installed: unparseable; requires 1.46.0; upgrade: no-mistakes update)"
      ]
    },
    {
      "id": "tools/missing-manual",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Give the captain the printed instructions URL; never pass the tool to bin/fm-bootstrap.sh install.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/presentation",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Work in plain text; install or upgrade lavish-axi with captain consent before using Lavish.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/provenance",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Restore the pinned build named in config/tool-provenance (a plain reinstall replaced it), or drop the pin once the upstream release carries the change.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "backend/invalid",
      "area": "backend",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Correct config/backend or FM_BACKEND to one of the listed backends before dispatching.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "backend/herdr-launcher",
      "area": "backend",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Find the live pane with herdr pane list --workspace <workspace> and pass corrected HERDR_PANE_ID, HERDR_WORKSPACE_ID, and HERDR_TAB_ID on the spawn command line, or relaunch the primary inside herdr.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "config/crew-dispatch",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Fix the named problem in config/crew-dispatch.json; do not dispatch by profile until it validates.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "config/startup-memory-budget",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Correct config/startup-memory-budget; the memory/budget check reads it on demand.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "config/relay",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "No action; restart the watcher only when a cadence change must apply immediately.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "permissions/claude-fm-scripts",
      "area": "permissions",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Give the captain the exact allow rule the line names for the home's .claude/settings.local.json; a present rule does not prove auto mode honors it.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "no-mistakes/agents",
      "area": "no-mistakes",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Install the named agent or remove it from the agent: list (ask the captain before editing their no-mistakes config); confirm with no-mistakes doctor.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "auth/github",
      "area": "auth",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Confirm the network is reachable, then ask the captain to run: ! gh auth login",
      "status": "skip",
      "evidence": "network check; run fm-doctor.sh --network"
    },
    {
      "id": "fleet/tangle",
      "area": "fleet",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "The session holding the fleet lock restores the primary to its default branch as the line says.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "fleet/backlog-reconcile",
      "area": "fleet",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Follow the bootstrap-diagnostics skill for the named variant; never delete backlog-close records by hand.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "fleet/home-summary",
      "area": "fleet",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Reproduce with bin/fm-home-summary-refresh.sh (no --best-effort) and fix the reported failure.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "fleet/secondmate-handoff",
      "area": "fleet",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Keep the outbox; rerun bin/fm-backlog-handoff.sh --resume-pending once the route is fixed.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "fleet/info",
      "area": "fleet",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "No action unless the fact says an interrupted cleanup may have left an endpoint or local copy.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "fleet/sync",
      "area": "fleet",
      "owner": "bin/fm-fleet-sync.sh",
      "fix": "A STUCK clone needs hands-on attention; a skip is one-off unless it names the registry entry.",
      "status": "skip",
      "evidence": "network check; run fm-doctor.sh --network"
    },
    {
      "id": "fleet/secondmate-sync",
      "area": "fleet",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Inspect the reason; the second mate's instructions or inherited settings may be stale.",
      "status": "skip",
      "evidence": "network check; run fm-doctor.sh --network"
    },
    {
      "id": "fleet/secondmate-liveness",
      "area": "fleet",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Investigate the reason; the second mate is not guaranteed to be running.",
      "status": "skip",
      "evidence": "network check; run fm-doctor.sh --network"
    },
    {
      "id": "fleet/secondmate-nudge",
      "area": "fleet",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Keep the pending marker; fix the endpoint and rerun session start to retry the re-read nudge.",
      "status": "skip",
      "evidence": "network check; run fm-doctor.sh --network"
    },
    {
      "id": "fleet/config-reread",
      "area": "fleet",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Keep the retry records; fix the named problem and rerun session start to resend the re-read instruction.",
      "status": "skip",
      "evidence": "network check; run fm-doctor.sh --network"
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
      "evidence": "can_receive=false lock.state=free wake_consumer.state=unknown",
      "detail": [
        "{\"schema\":\"fm-primary-ready.v1\",\"home\":\".doctor-live/home\",\"observed_at\":\"2026-11-11T08:53:06Z\",\"lock\":{\"state\":\"free\",\"pid\":null,\"live_harness\":false},\"wake_consumer\":{\"state\":\"unknown\",\"reason\":\"supervision-model-unknown-for-home\",\"beacon_age_seconds\":null},\"posture\":{\"state\":\"present\"},\"can_receive\":false}"
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
    },
    {
      "id": "config/role",
      "area": "config",
      "owner": "bin/fm-role.sh",
      "fix": "Correct config/firstmate-role as docs/configuration.md \"Firstmate role\" describes.",
      "status": "ok",
      "evidence": "fm-role: user (default)",
      "detail": [
        "fm-role: user (default)"
      ]
    },
    {
      "id": "config/harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Run the doctor from inside the firstmate session's own agent so its harness can be detected.",
      "status": "ok",
      "evidence": "codex",
      "detail": [
        "codex"
      ]
    },
    {
      "id": "config/crew-harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Set config/crew-harness to a verified adapter, or leave it absent to use this session's harness.",
      "status": "ok",
      "evidence": "codex",
      "detail": [
        "codex"
      ]
    },
    {
      "id": "memory/budget",
      "area": "memory",
      "owner": "bin/fm-startup-memory-budget.sh",
      "fix": "An absent budget is written at the next locked session start; correct a malformed config/startup-memory-budget by hand.",
      "status": "info",
      "evidence": "startup-memory-budget: invalid config/startup-memory-budget - file is absent",
      "detail": [
        "stderr: startup-memory-budget: invalid config/startup-memory-budget - file is absent"
      ]
    }
  ]
}
```


## harness-kiro

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "ok",
  "checks": [
    {
      "id": "config/crew-dispatch",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Fix the named problem in config/crew-dispatch.json; do not dispatch by profile until it validates.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "config/startup-memory-budget",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Correct config/startup-memory-budget; the memory/budget check reads it on demand.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "config/relay",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "No action; restart the watcher only when a cadence change must apply immediately.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "config/role",
      "area": "config",
      "owner": "bin/fm-role.sh",
      "fix": "Correct config/firstmate-role as docs/configuration.md \"Firstmate role\" describes.",
      "status": "ok",
      "evidence": "fm-role: user (default)",
      "detail": [
        "fm-role: user (default)"
      ]
    },
    {
      "id": "config/harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Run the doctor from inside the firstmate session's own agent so its harness can be detected.",
      "status": "ok",
      "evidence": "codex",
      "detail": [
        "codex"
      ]
    },
    {
      "id": "config/crew-harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Set config/crew-harness to a verified adapter, or leave it absent to use this session's harness.",
      "status": "ok",
      "evidence": "kiro",
      "detail": [
        "kiro"
      ]
    }
  ]
}
```


## harness-hermes

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "ok",
  "checks": [
    {
      "id": "config/crew-dispatch",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Fix the named problem in config/crew-dispatch.json; do not dispatch by profile until it validates.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "config/startup-memory-budget",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Correct config/startup-memory-budget; the memory/budget check reads it on demand.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "config/relay",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "No action; restart the watcher only when a cadence change must apply immediately.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "config/role",
      "area": "config",
      "owner": "bin/fm-role.sh",
      "fix": "Correct config/firstmate-role as docs/configuration.md \"Firstmate role\" describes.",
      "status": "ok",
      "evidence": "fm-role: user (default)",
      "detail": [
        "fm-role: user (default)"
      ]
    },
    {
      "id": "config/harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Run the doctor from inside the firstmate session's own agent so its harness can be detected.",
      "status": "ok",
      "evidence": "codex",
      "detail": [
        "codex"
      ]
    },
    {
      "id": "config/crew-harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Set config/crew-harness to a verified adapter, or leave it absent to use this session's harness.",
      "status": "ok",
      "evidence": "hermes",
      "detail": [
        "hermes"
      ]
    }
  ]
}
```


## own-hermes

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "ok",
  "checks": [
    {
      "id": "config/crew-dispatch",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Fix the named problem in config/crew-dispatch.json; do not dispatch by profile until it validates.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "config/startup-memory-budget",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Correct config/startup-memory-budget; the memory/budget check reads it on demand.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "config/relay",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "No action; restart the watcher only when a cadence change must apply immediately.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "config/role",
      "area": "config",
      "owner": "bin/fm-role.sh",
      "fix": "Correct config/firstmate-role as docs/configuration.md \"Firstmate role\" describes.",
      "status": "ok",
      "evidence": "fm-role: user (default)",
      "detail": [
        "fm-role: user (default)"
      ]
    },
    {
      "id": "config/harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Run the doctor from inside the firstmate session's own agent so its harness can be detected.",
      "status": "ok",
      "evidence": "hermes",
      "detail": [
        "hermes"
      ]
    },
    {
      "id": "config/crew-harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Set config/crew-harness to a verified adapter, or leave it absent to use this session's harness.",
      "status": "ok",
      "evidence": "hermes",
      "detail": [
        "hermes"
      ]
    }
  ]
}
```


## harness-bogus

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "warn",
  "checks": [
    {
      "id": "config/crew-dispatch",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Fix the named problem in config/crew-dispatch.json; do not dispatch by profile until it validates.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "config/startup-memory-budget",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Correct config/startup-memory-budget; the memory/budget check reads it on demand.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "config/relay",
      "area": "config",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "No action; restart the watcher only when a cadence change must apply immediately.",
      "status": "skip",
      "evidence": "printed only by the locked session-start sweep; read the session-start digest"
    },
    {
      "id": "config/role",
      "area": "config",
      "owner": "bin/fm-role.sh",
      "fix": "Correct config/firstmate-role as docs/configuration.md \"Firstmate role\" describes.",
      "status": "ok",
      "evidence": "fm-role: user (default)",
      "detail": [
        "fm-role: user (default)"
      ]
    },
    {
      "id": "config/harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Run the doctor from inside the firstmate session's own agent so its harness can be detected.",
      "status": "ok",
      "evidence": "codex",
      "detail": [
        "codex"
      ]
    },
    {
      "id": "config/crew-harness",
      "area": "config",
      "owner": "bin/fm-harness.sh",
      "fix": "Set config/crew-harness to a verified adapter, or leave it absent to use this session's harness.",
      "status": "warn",
      "evidence": "bogus",
      "detail": [
        "bogus"
      ]
    }
  ]
}
```


## agent-yaml-2

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "warn",
  "checks": [
    {
      "id": "no-mistakes/agents",
      "area": "no-mistakes",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Install the named agent or remove it from the agent: list (ask the captain before editing their no-mistakes config); confirm with no-mistakes doctor.",
      "status": "warn",
      "evidence": "NO_MISTAKES_AGENTS: {run-worktree}/.doctor-live/nm/config.yaml agent: lists missing-live-doctor-agent, but missing-live-doctor-agent is no...",
      "detail": [
        "NO_MISTAKES_AGENTS: {run-worktree}/.doctor-live/nm/config.yaml agent: lists missing-live-doctor-agent, but missing-live-doctor-agent is not installed; no-mistakes silently skips a missing fallback agent - install it or drop it from the list (no-mistakes doctor is the authoritative view)"
      ]
    }
  ]
}
```


## permissions-auto-no-rule

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "warn",
  "checks": [
    {
      "id": "permissions/claude-fm-scripts",
      "area": "permissions",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Give the captain the exact allow rule the line names for the home's .claude/settings.local.json; a present rule does not prove auto mode honors it.",
      "status": "warn",
      "evidence": "CLAUDE_PERMISSIONS: Claude auto mode is on ({run-worktree}/.doctor-live/settings.json) but no Bash(...bin/fm-*...) allow rule is in any Cl...",
      "detail": [
        "CLAUDE_PERMISSIONS: Claude auto mode is on ({run-worktree}/.doctor-live/settings.json) but no Bash(...bin/fm-*...) allow rule is in any Claude settings layer, so the auto-mode classifier may refuse firstmate's own scripts - add Bash({run-worktree}/.doctor-live/home/bin/fm-*:*) to {run-worktree}/.doctor-live/home/.claude/settings.local.json (a present rule does not prove the classifier honors it)"
      ]
    }
  ]
}
```


## permissions-auto-family

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "ok",
  "checks": [
    {
      "id": "permissions/claude-fm-scripts",
      "area": "permissions",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Give the captain the exact allow rule the line names for the home's .claude/settings.local.json; a present rule does not prove auto mode honors it.",
      "status": "ok",
      "evidence": "none reported"
    }
  ]
}
```


## provenance-wrong

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "fail",
  "checks": [
    {
      "id": "tools/missing",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Ask the captain, then run bin/fm-bootstrap.sh install <tool> (the line names the install command).",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/outdated",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Ask the captain, then run the upgrade command the line names.",
      "status": "fail",
      "evidence": "OUTDATED: no-mistakes (installed: unparseable; requires 1.46.0; upgrade: no-mistakes update)",
      "detail": [
        "OUTDATED: no-mistakes (installed: unparseable; requires 1.46.0; upgrade: no-mistakes update)"
      ]
    },
    {
      "id": "tools/missing-manual",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Give the captain the printed instructions URL; never pass the tool to bin/fm-bootstrap.sh install.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/presentation",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Work in plain text; install or upgrade lavish-axi with captain consent before using Lavish.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/provenance",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Restore the pinned build named in config/tool-provenance (a plain reinstall replaced it), or drop the pin once the upstream release carries the change.",
      "status": "warn",
      "evidence": "TOOL_PROVENANCE: jq resolves to /usr/bin/jq, not the pinned {run-worktree}/.doctor-live/expected-build/; a reinstall may have replaced the...",
      "detail": [
        "TOOL_PROVENANCE: jq resolves to /usr/bin/jq, not the pinned {run-worktree}/.doctor-live/expected-build/; a reinstall may have replaced the pinned build - restore it, or remove the pin once the upstream release carries what it needs"
      ]
    }
  ]
}
```


## provenance-correct

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "fail",
  "checks": [
    {
      "id": "tools/missing",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Ask the captain, then run bin/fm-bootstrap.sh install <tool> (the line names the install command).",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/outdated",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Ask the captain, then run the upgrade command the line names.",
      "status": "fail",
      "evidence": "OUTDATED: no-mistakes (installed: unparseable; requires 1.46.0; upgrade: no-mistakes update)",
      "detail": [
        "OUTDATED: no-mistakes (installed: unparseable; requires 1.46.0; upgrade: no-mistakes update)"
      ]
    },
    {
      "id": "tools/missing-manual",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Give the captain the printed instructions URL; never pass the tool to bin/fm-bootstrap.sh install.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/presentation",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Work in plain text; install or upgrade lavish-axi with captain consent before using Lavish.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/provenance",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Restore the pinned build named in config/tool-provenance (a plain reinstall replaced it), or drop the pin once the upstream release carries the change.",
      "status": "ok",
      "evidence": "none reported"
    }
  ]
}
```


## memory-within

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "ok",
  "checks": [
    {
      "id": "memory/budget",
      "area": "memory",
      "owner": "bin/fm-startup-memory-budget.sh",
      "fix": "An absent budget is written at the next locked session start; correct a malformed config/startup-memory-budget by hand.",
      "status": "ok",
      "evidence": "estimator=ceil(UTF-8 bytes / 3) conservative-local-estimate",
      "detail": [
        "estimator=ceil(UTF-8 bytes / 3) conservative-local-estimate",
        "role=primary",
        "effective_budget_tokens=1",
        "file=data/captain.md bytes=0 estimated_tokens=0 status=absent",
        "file=data/captain-shared.md bytes=3 estimated_tokens=1 status=present",
        "file=data/learnings.md bytes=0 estimated_tokens=0 status=absent",
        "total_estimated_tokens=1",
        "budget_status=within-budget"
      ]
    }
  ]
}
```


## memory-over

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "warn",
  "checks": [
    {
      "id": "memory/budget",
      "area": "memory",
      "owner": "bin/fm-startup-memory-budget.sh",
      "fix": "An absent budget is written at the next locked session start; correct a malformed config/startup-memory-budget by hand.",
      "status": "warn",
      "evidence": "estimator=ceil(UTF-8 bytes / 3) conservative-local-estimate",
      "detail": [
        "estimator=ceil(UTF-8 bytes / 3) conservative-local-estimate",
        "role=primary",
        "effective_budget_tokens=1",
        "file=data/captain.md bytes=0 estimated_tokens=0 status=absent",
        "file=data/captain-shared.md bytes=4 estimated_tokens=2 status=present",
        "file=data/learnings.md bytes=0 estimated_tokens=0 status=absent",
        "total_estimated_tokens=2",
        "budget_status=over-budget"
      ]
    }
  ]
}
```


## network-no-login

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "fail",
  "checks": [
    {
      "id": "auth/github",
      "area": "auth",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Confirm the network is reachable, then ask the captain to run: ! gh auth login",
      "status": "fail",
      "evidence": "NEEDS_GH_AUTH",
      "detail": [
        "NEEDS_GH_AUTH"
      ]
    }
  ]
}
```


## outdated-tool

Command: `bin/fm-doctor.sh` with arguments retained in drive-doctor.py.

```json
{
  "verdict": "fail",
  "checks": [
    {
      "id": "tools/missing",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Ask the captain, then run bin/fm-bootstrap.sh install <tool> (the line names the install command).",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/outdated",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Ask the captain, then run the upgrade command the line names.",
      "status": "fail",
      "evidence": "OUTDATED: no-mistakes (installed: unparseable; requires 1.46.0; upgrade: no-mistakes update) (+1 more)",
      "detail": [
        "OUTDATED: no-mistakes (installed: unparseable; requires 1.46.0; upgrade: no-mistakes update)",
        "OUTDATED: gh-axi (installed: 0.1.0; requires 0.1.29; upgrade: gh-axi update)"
      ]
    },
    {
      "id": "tools/missing-manual",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Give the captain the printed instructions URL; never pass the tool to bin/fm-bootstrap.sh install.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/presentation",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Work in plain text; install or upgrade lavish-axi with captain consent before using Lavish.",
      "status": "ok",
      "evidence": "none reported"
    },
    {
      "id": "tools/provenance",
      "area": "tools",
      "owner": "bin/fm-bootstrap.sh",
      "fix": "Restore the pinned build named in config/tool-provenance (a plain reinstall replaced it), or drop the pin once the upstream release carries the change.",
      "status": "ok",
      "evidence": "none reported"
    }
  ]
}
```


## Herdr lab limitation

`bin/fm-herdr-lab.sh prepare fm-lab-doctor` was attempted with both absolute and relative isolated XDG_CONFIG_HOME paths. No lab was provisioned.

```text
fm-herdr-lab: session 'fm-lab-doctor' would bind a 139-byte socket path, over the 103-byte sun_path limit: {run-worktree}/.herdr-live/config/herdr/sessions/fm-lab-doctor/herdr-client.sock
fm-herdr-lab: fleet-state tripwire requires exactly one running default session
```

A running default-session tripwire prerequisite is unavailable in the isolated configuration. Creating or changing that default session is forbidden by the trusted runbook. A future run needs an approved lab environment with the required existing tripwire and a socket path short enough for Herdr. No Herdr process was launched.
