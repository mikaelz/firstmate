# Contribution polling verification

## Real product checks

Executed `python3 /home/mike/.no-mistakes/evidence/01M4V7KED2NMFN9WG1FW7VBW9S/drive-contributions.py` from the gate worktree.
The driver invokes the repository's actual contribution CLI, Bearings, check registration and foreground watcher, without replacing any product executable.
All disposable operational homes and tmux socket directories were inside the worktree and removed afterwards.
No runtime primary, production fleet endpoint or production credential was used.

`live-contributions.json` contains product stdout/stderr, return codes, relevant strace exec/connect evidence and durable wakes.

- Before-fix reproduction: the base commit's contribution scripts, copied into a disposable code directory with the remaining helpers, fail a GitLab-only poll with `BUDGET_EXHAUSTED: unbound variable`.
- Fresh public and self-hosted GitLab merge requests: poll exits 0 with empty stdout/stderr, no gh execution, no network connections, no fabricated contribution files, and no unavailable wake.
- Bearings reports known=2, checked=0, unmeasured=2, unreadable_records=0, all actor counts=0, incomplete coverage.
- Existing Forgejo `/pulls/` ownership exclusion is unchanged: it does not increase known coverage.
- The registered watcher over unsupported-only ownership exits 124 with `checkpoint: no actionable wake within 4s` and no durable wake.
- A separate GitLab-owned home with an intentionally unreadable contribution record produces the real unreadable-record diagnostic, not an unavailable GitLab alert.
- Two retained unsupported rows in one saved file, with their backlog links absent, clear only their error fields on the next poll. Ownership, timestamps, provenance and null observations remain exact. Coverage stays known=2, unmeasured=2.
- Mixed saved GitHub/GitLab errors: the installed gh retries the supported URL; the existing GitHub failure episode remains silent and error-stamped; only the GitLab error clears. Bearings reports unmeasured=1 and fleet=1.
- Real GitHub read failure: the installed gh is given isolated config, a disposable token and an unreachable loopback proxy. strace shows gh attempting the API read and connecting only to 127.0.0.1:1. First failure prints the unavailable alert; repeated failure retries but prints nothing. The error remains persisted, with no GitLab record fabricated.
- Through the authenticated watcher, that same real GitHub failure creates the durable unavailable wake for GitHub only.

## Targeted regression suite

Executed `bash bin/fm-test-run.sh tests/fm-contributions.test.sh --json /home/mike/.no-mistakes/evidence/01M4V7KED2NMFN9WG1FW7VBW9S/contributions-timing.json`.
Exit 0, no gate skips or waived failures.
The suite covers the colocated unsupported-ownership and GitHub-failure regressions, including successful-read episode reset followed by a new alert, and maintainer-signal versus unreadable-record wake separation.
Those success/recovery and maintainer-event checks use deterministic forge mocks, not live GitHub evidence.
The separate real-product checks above provide live evidence for the changed polling surface and actual read-failure behavior.

No complete repository suite, linter, static analyzer, publication or CI commands were run.
No screenshot was needed: this change affects command output and persisted contribution records, not a rendered UI.
No source or permanent test changes were made; the worktree was clean after cleanup.
