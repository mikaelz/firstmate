#!/usr/bin/env bash
set -euo pipefail
E=/home/mike/.no-mistakes/evidence/01M4MQZR12Q7QC44Q6WM6MW6PD
H=$PWD/.test-disposable/link-home
mkdir -p "$H/state" "$H/data" "$H/config" "$H/projects" "$H/tmux"
export FM_HOME=$H TMUX="$H/tmux/unstarted,0,0"
printf '## Done\n' > "$H/data/backlog.md"
while IFS='|' read -r id url; do
  printf -- '- [x] %s - Review <%s> (kind: ship) (merged 2026-10-10)\n' "$id" "$url" >> "$H/data/backlog.md"
done <<'URLS'
gl|https://gitlab.com/gitlab-org/cli/-/merge_requests/4055
nested|https://gitlab.example.test/group/sub/project/-/merge_requests/7
gh|https://github.com/owner/repo/pull/7
fj|https://forgejo.example.test/owner/repo/pulls/7
query|https://gitlab.com/group/project/-/merge_requests/7?x=1
leadingzero|https://gitlab.com/group/project/-/merge_requests/07
issue|https://gitlab.com/group/project/-/issues/7
URLS
for scenario in latest meta scout incidental resumed malformed; do
  kind=ship; [ "$scenario" != scout ] || kind=scout
  printf 'kind=%s\nmode=%s\nproject=disposable\nharness=codex\n' "$kind" "$kind" > "$H/state/$scenario.meta"
  if [ "$scenario" = meta ] || [ "$scenario" = scout ]; then
    printf 'pr=https://gitlab.com/group/project/-/merge_requests/9\n' >> "$H/state/$scenario.meta"
  fi
  printf 'done: PR https://gitlab.com/group/project/-/merge_requests/7\ndone: PR https://gitlab.com/group/project/-/merge_requests/8 checks green\n' > "$H/state/$scenario.status"
  case "$scenario" in
    incidental) printf 'done: mentioned https://gitlab.com/group/project/-/merge_requests/9 in documentation\n' >> "$H/state/$scenario.status" ;;
    resumed) printf 'working: preparing another change\n' >> "$H/state/$scenario.status" ;;
    malformed) printf 'done: PR https://gitlab.com/group/project/-/merge_requests/0\n' >> "$H/state/$scenario.status" ;;
  esac
done
bin/fm-fleet-snapshot.sh --json > "$E/live-link-snapshot.json"
jq -e '.backlog.records | map({key:.id,value:.pr_url}) | from_entries | .gl == "https://gitlab.com/gitlab-org/cli/-/merge_requests/4055" and .nested == "https://gitlab.example.test/group/sub/project/-/merge_requests/7" and .gh == "https://github.com/owner/repo/pull/7" and .fj == "https://forgejo.example.test/owner/repo/pulls/7" and .query == null and .leadingzero == null and .issue == null' "$E/live-link-snapshot.json" >/dev/null
jq -e '[.tasks[] | if .id == "latest" then (.pr.url | endswith("8")) and .pr.source == "status_event" elif .id == "meta" then (.pr.url | endswith("9")) and .pr.source == "meta" else .pr.url == null and .pr.source == "absent" end] | length == 6 and all' "$E/live-link-snapshot.json" >/dev/null
printf 'Real snapshot consumer output:\n'
jq '{backlog:[.backlog.records[]|{id,pr_url}],tasks:[.tasks[]|{id,kind,pr}]}' "$E/live-link-snapshot.json"
bin/fm-fleet-view.sh > "$E/live-link-view.txt"
