#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
E=/home/mike/.no-mistakes/evidence/01M4JBM95D48A03T591CXFSNHX
D=$ROOT/.test-phase-tmp/live
mkdir -p "$D/home" "$D/repo"
trap 'rm -rf "$D"' EXIT
H=$D/home
mkdir -p "$H"/{state,config,data,projects}
printf 'backend = "markdown"\n' > "$H/.tasks.toml"
printf '# Backlog\n\n## In flight\n\n## Queued\n\n## Done\n' > "$H/data/backlog.md"
export FM_HOME=$H
unset FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE FM_ROOT_OVERRIDE TASKS_AXI_BACKEND TASKS_AXI_FILE
. "$ROOT/bin/fm-pr-lib.sh"
URL=https://gitlab.com/KarotKris/gitlab-merge-watch-fixture/-/merge_requests/1
P=KarotKris/gitlab-merge-watch-fixture
fm_pr_gitlab_read_record gitlab.com "$P" 1
printf 'State-only: state=%s merged=%s head=%s\n' "$FM_PR_RECORD_STATE" "$FM_PR_RECORD_MERGED" "$FM_PR_RECORD_HEAD"
[ "$FM_PR_RECORD_STATE" = merged ] && [ -z "$FM_PR_RECORD_HEAD" ]
fm_pr_gitlab_read_record gitlab.com "$P" 1 proof
SHA=$FM_PR_RECORD_HEAD
printf 'Verified identity=%s state=%s head=%s target=%s\n' "$FM_PR_RECORD_URL" "$FM_PR_RECORD_STATE" "$SHA" "$FM_PR_RECORD_TARGET"
GITLAB_HOST=gitlab.com glab mr view 1 -R "https://gitlab.com/$P" -F json | jq '{iid,web_url,state,sha,diff_refs,target_branch,target_project_id,source_project_id}' > "$E/live-mr-fields.json"
git -C "$D/repo" init -q
git -C "$D/repo" remote add origin "https://gitlab.com/$P.git"
RESOLVED=$(fm_pr_gitlab_fetch_head "$D/repo" gitlab.com "$P" 1 "$SHA" refs/fm-review/live/merge-request/1/head)
[ "$RESOLVED" = "$SHA" ]
printf 'Fetched exact source head into private ref: %s\n' "$RESOLVED"
git -C "$D/repo" show --stat "$RESOLVED"
if fm_pr_gitlab_fetch_head "$D/repo" gitlab.com "$P" 1 1111111111111111111111111111111111111111 refs/fm-review/wrong/head; then exit 1; fi
printf 'Wrong expected SHA refused\n'
if fm_pr_gitlab_fetch_head "$D/repo" gitlab.com "$P" 999999 "$SHA" refs/fm-review/missing/head; then exit 1; fi
printf 'Missing MR ref refused\n'
if fm_pr_gitlab_fetch_head "$D/repo" gitlab.com unrelated/project 1 "$SHA" refs/fm-review/foreign/head; then exit 1; fi
printf 'Foreign target repository refused\n'
git -C "$D/repo" fetch -q origin '+refs/heads/main:refs/remotes/origin/main'
git -C "$D/repo" checkout -q -b local origin/main
STALE=$(git -C "$D/repo" rev-parse HEAD)
printf 'worktree=%s\nproject=%s\nbranch=local\nbase_branch=deleted-legacy-base\npr=%s\npr_head=%s\nkind=ship\n' "$D/repo" "$D/repo" "$URL" "$STALE" > "$H/state/review.meta"
"$ROOT/bin/fm-review-diff.sh" review > "$E/live-review-diff.txt" 2>&1
[ "$(git -C "$D/repo" rev-parse refs/fm-review/review/merge-request/1/head)" = "$SHA" ]
printf 'Real review-diff selected live SHA over stale recorded head and deleted legacy base\n'
rm "$H/state/review.meta"
for id in latest meta scout incidental; do
  kind=ship; [ "$id" != scout ] || kind=scout
  printf 'kind=%s\nmode=%s\nharness=codex\nproject=alpha\n' "$kind" "$kind" > "$H/state/$id.meta"
  printf 'done: PR https://gitlab.example.test/group/sub/project/-/merge_requests/7\ndone [at=2026-07-09T12:00:00Z]: PR https://gitlab.example.test/group/sub/project/-/merge_requests/8 checks green\n' > "$H/state/$id.status"
done
printf 'pr=%s\n' "$URL" >> "$H/state/meta.meta"
printf 'done: mentioned %s in documentation\n' "$URL" >> "$H/state/incidental.status"
"$ROOT/bin/fm-fleet-snapshot.sh" --json > "$E/live-snapshot.json"
jq -e '.tasks | map({key:.id,value:.pr.url}) | from_entries | (.latest | endswith("8")) and .meta == "https://gitlab.com/KarotKris/gitlab-merge-watch-fixture/-/merge_requests/1" and .scout == null and .incidental == null' "$E/live-snapshot.json" >/dev/null
printf 'Snapshot: latest terminal link, metadata precedence, scout/incidental exclusion verified\n'
. "$ROOT/bin/fm-public-followup-lib.sh"
for u in "$URL" https://gitlab.example.test/group/sub/project/-/merge_requests/7 https://github.com/owner/repo/pull/7 https://forgejo.example.test/owner/repo/pulls/7; do fm_pf_pr_url_valid "$u"; printf 'Accepted canonical URL: %s\n' "$u"; done
for u in https://gitlab.com/group/project/-/issues/7 https://gitlab.com/group/project/-/merge_requests/0 https://gitlab.com/group/project/-/merge_requests/7?x=1; do if fm_pf_pr_url_valid "$u"; then exit 1; fi; printf 'Rejected non-review URL: %s\n' "$u"; done
unset FM_TASKS_AXI_COMPATIBLE
. "$ROOT/bin/fm-tasks-axi-lib.sh"
. "$ROOT/bin/fm-backlog-transition-lib.sh"
tasks-axi add private-completion 'Private completion scenario' --start --file "$H/data/backlog.md"
printf 'spawn_gen=private-generation\n' > "$H/state/private-completion.meta"
fm_backlog_close_marker_write "$H/state" private-completion "$H/data" private-generation --pr "$URL"
cp "$H/data/backlog.md" "$D/backlog.before"
cp "$H/state/private-completion.meta" "$D/meta.before"
cp "$H/state/private-completion.backlog-close" "$D/marker.before"
if fm_backlog_close_marker_replay "$H/state" "$H/state/private-completion.backlog-close" "$H/data"; then exit 1; fi
printf 'Completion replay refusal: %s\n' "$FM_BACKLOG_TRANSITION_ERROR"
cmp "$D/backlog.before" "$H/data/backlog.md"
cmp "$D/meta.before" "$H/state/private-completion.meta"
cmp "$D/marker.before" "$H/state/private-completion.backlog-close"
if fm_backlog_completion_preview "$H/data" private-completion retain --pr "$URL"; then exit 1; fi
printf 'Retention preview refusal: %s\n' "$FM_BACKLOG_TRANSITION_ERROR"
cmp "$D/backlog.before" "$H/data/backlog.md"
tasks-axi show private-completion --file "$H/data/backlog.md"
printf 'All live checks above completed; real consumer %s retained row, metadata and completion record without writes\n' "$(tasks-axi --version)"
