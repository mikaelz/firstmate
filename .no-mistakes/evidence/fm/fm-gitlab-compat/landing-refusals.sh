#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
D=$(mktemp -d "$ROOT/.test-phase-tmp/landing-refusals.XXXXXX")
trap 'rm -rf "$D"' EXIT
unset FM_HOME FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE TASKS_AXI_FILE TASKS_AXI_BACKEND FM_TASKS_AXI_COMPATIBLE
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
# This is a marked lab home with a missing-endpoint legacy task. No runtime
# server, harness, endpoint, or cleanup is started, queried or killed.
bin/fm-lab-home.sh create "$D/home"
export FM_HOME="$D/home"
mkdir -p "$FM_HOME/tmux"
export TMUX_TMPDIR="$FM_HOME/tmux" TMUX="$FM_HOME/tmux/tmux-$(id -u)/fm-lab,0,0"
printf 'backend="markdown"\n[markdown]\npath="data/backlog.md"\n' > "$FM_HOME/.tasks.toml"
. "$ROOT/bin/fm-pr-lib.sh"
P=KarotKris/gitlab-merge-watch-fixture
URL="https://gitlab.com/$P/-/merge_requests/1"
fm_pr_gitlab_read_record gitlab.com "$P" 1 proof
SHA=$FM_PR_RECORD_HEAD
git init -q "$D/repo"
git -C "$D/repo" remote add origin "https://gitlab.com/$P.git"
fm_pr_gitlab_fetch_head "$D/repo" gitlab.com "$P" 1 "$SHA" refs/fm-review/live-proof/merge-request/1/head
git -C "$D/repo" fetch -q origin '+refs/heads/main:refs/remotes/origin/main'
git -C "$D/repo" checkout -q -b fm/landing-live "$SHA"
(cd "$FM_HOME"; /home/mike/.local/bin/tasks-axi add landing-live 'Local work must survive' --start)
printf 'kind=ship\nmode=no-mistakes\nharness=codex\nbackend=tmux\nworktree=%s\nproject=%s\nbranch=fm/landing-live\nbase_branch=deleted-legacy-source\npr=%s\n' "$D/repo" "$D/repo" "$URL" > "$FM_HOME/state/landing-live.meta"
cp "$FM_HOME/state/landing-live.meta" "$D/meta.before"
cp "$FM_HOME/data/backlog.md" "$D/backlog.before"
for scenario in clean untracked dirty extra; do
 git -C "$D/repo" reset -q --hard "$SHA"
 rm -f "$D/repo/untouched-local.txt"
 case "$scenario" in
 untracked) printf 'keep my work\n' > "$D/repo/untouched-local.txt";;
 dirty) printf 'keep my edits\n' >> "$D/repo/merged-example.txt";;
 extra) printf 'unlanded work\n' > "$D/repo/untouched-local.txt"; git -C "$D/repo" add .; git -C "$D/repo" -c user.name=Lab -c user.email=lab@example.test commit -qm 'extra unlanded commit';;
 esac
 before=$(git -C "$D/repo" rev-parse HEAD)
 printf '\n=== real missing-endpoint teardown %s ===\n' "$scenario"
 if "$ROOT/bin/fm-teardown.sh" landing-live > "$D/output" 2>&1; then echo 'FAIL: unsafe teardown accepted'; exit 1; fi
 while IFS= read -r line; do printf '%s\n' "$line"; done < "$D/output"
 cmp "$FM_HOME/state/landing-live.meta" "$D/meta.before"
 cmp "$FM_HOME/data/backlog.md" "$D/backlog.before"
 [ "$before" = "$(git -C "$D/repo" rev-parse HEAD)" ]
 case "$scenario" in
 clean) grep -q 'requires --dry-run support' "$D/output";;
 untracked|dirty) grep -q 'uncommitted changes' "$D/output";;
 extra) grep -q 'not on any remote and not landed' "$D/output";;
 esac
 printf 'Preserved task row, metadata, worktree HEAD and local work after refusal.\n'
done
