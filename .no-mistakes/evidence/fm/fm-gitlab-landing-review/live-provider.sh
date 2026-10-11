#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
E=/home/mike/.no-mistakes/evidence/01M4MQZR12Q7QC44Q6WM6MW6PD
R=$ROOT/.test-disposable/provider
S=$ROOT/.test-disposable/provider-state
mkdir -p "$S"
. "$ROOT/bin/fm-pr-lib.sh"
printf 'Public provider: https://gitlab.com/gitlab-org/cli/-/merge_requests/4055\n'
fm_pr_gitlab_read_record gitlab.com gitlab-org/cli 4055 proof
printf 'Verified provider record: state=%s merged=%s source_head=%s target=%s url=%s\n' "$FM_PR_RECORD_STATE" "$FM_PR_RECORD_MERGED" "$FM_PR_RECORD_HEAD" "$FM_PR_RECORD_TARGET" "$FM_PR_RECORD_URL"
HEAD_SHA=$FM_PR_RECORD_HEAD
[ "$FM_PR_RECORD_MERGED" = true ]
[ "$FM_PR_RECORD_TARGET" = main ]
FETCHED=$(fm_pr_gitlab_fetch_head "$R" gitlab.com gitlab-org/cli 4055 "$HEAD_SHA" refs/fm-review/live-provider/merge-request/4055/head)
printf 'Exact provider MR ref fetched: %s\n' "$FETCHED"
[ "$FETCHED" = "$HEAD_SHA" ]
git -C "$R" update-ref refs/fm-review/other-task/merge-request/4055/head HEAD
OTHER=$(git -C "$R" rev-parse refs/fm-review/other-task/merge-request/4055/head)
if fm_pr_gitlab_fetch_head "$R" gitlab.com gitlab-org/cli 4055 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa refs/fm-review/rejected/merge-request/4055/head; then
  echo 'ERROR: wrong source SHA accepted'; exit 1
fi
printf 'Adversarial exact-SHA mismatch: REFUSED\n'
if fm_pr_gitlab_fetch_head "$R" gitlab.com unrelated/project 4055 "$HEAD_SHA" refs/fm-review/rejected-origin/merge-request/4055/head; then
  echo 'ERROR: wrong origin identity accepted'; exit 1
fi
printf 'Adversarial raw origin mismatch: REFUSED; no rejected-origin ref created\n'
! git -C "$R" show-ref --verify --quiet refs/fm-review/rejected-origin/merge-request/4055/head
git -C "$R" checkout -qb fm/live-provider
printf 'DO NOT REVIEW STALE LOCAL CONTENT\n' > "$R/stale-local-only.txt"
git -C "$R" add stale-local-only.txt
git -C "$R" -c user.name=LiveValidation -c user.email=validation@example.invalid -c core.hooksPath=/dev/null commit -qm 'isolated stale local branch'
STALE=$(git -C "$R" rev-parse HEAD)
printf 'worktree=%s\nproject=%s\nbranch=fm/live-provider\nbase_branch=deleted-legacy-source\npr=https://gitlab.com/gitlab-org/cli/-/merge_requests/4055\npr_head=%s\n' "$R" "$R" "$STALE" > "$S/live-provider.meta"
printf '\nReal review command with stale local commit and deleted recorded base:\n'
FM_STATE_OVERRIDE="$S" "$ROOT/bin/fm-review-diff.sh" live-provider > "$E/live-review-diff.txt" 2> "$E/live-review-diff.stderr"
head -50 "$E/live-review-diff.txt"
! grep -q 'stale-local-only\|DO NOT REVIEW STALE' "$E/live-review-diff.txt"
grep -q '^diff base: origin/main$' "$E/live-review-diff.txt"
! grep -q 'PR head unavailable' "$E/live-review-diff.stderr"
[ "$(git -C "$R" rev-parse refs/fm-review/live-provider/merge-request/4055/head)" = "$HEAD_SHA" ]
[ "$(git -C "$R" rev-parse refs/fm-review/other-task/merge-request/4055/head)" = "$OTHER" ]
printf 'Verified: live MR source selected over stale local/pr_head; literal main selected over deleted base; unrelated task ref unchanged.\n'
TREE=$(git -C "$R" merge-tree --write-tree origin/main "$HEAD_SHA")
[ "$TREE" = "$(git -C "$R" rev-parse 'origin/main^{tree}')" ]
printf 'Real provider landing content: merge-tree(source_head, origin/main) equals target tree %s\n' "$TREE"
