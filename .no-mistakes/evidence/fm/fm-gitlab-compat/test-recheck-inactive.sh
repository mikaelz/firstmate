#!/usr/bin/env bash
set -euo pipefail
ROOT=$PWD
D=$(mktemp -d "$ROOT/.test-phase-tmp/inactive.XXXXXX")
trap 'rm -rf "$D"' EXIT
unset FM_HOME FM_ROOT_OVERRIDE FM_STATE_OVERRIDE FM_DATA_OVERRIDE FM_CONFIG_OVERRIDE FM_PROJECTS_OVERRIDE FM_INACTIVE_CREW_STATE_BIN TASKS_AXI_FILE TASKS_AXI_BACKEND
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
MAIN=$D/main
MATE=$D/mate
mkdir -p "$MAIN/state" "$MATE"/{state,config,data,projects}
printf 'mate\n' > "$MATE/.fm-secondmate-home"
printf 'schema=fm-secondmate-parent.v1\nroute=local\nparent_home=%s\n' "$MAIN" > "$MATE/.fm-secondmate-parent"
for id in ready metadata incidental scout malformed; do
 repo=$MATE/projects/$id
 git init -q "$repo"
 git -C "$repo" -c user.name=Lab -c user.email=lab@example.test commit -q --allow-empty -m 'private persisted task'
 sha=$(git -C "$repo" rev-parse HEAD)
 git -C "$repo" update-ref refs/remotes/origin/main "$sha"
 kind=ship; [ "$id" != scout ] || kind=scout
 printf 'kind=%s\nmode=no-mistakes\nharness=codex\nspawn_gen=live-%s\nworktree=%s\nproject=%s\nbranch=master\npr_head=%s\n' "$kind" "$id" "$repo" "$repo" "$sha" > "$MATE/state/$id.meta"
 case "$id" in
  ready|metadata|scout) printf 'done: PR https://gitlab.example.test/group/sub/project/-/merge_requests/7 checks green\n' > "$MATE/state/$id.status";;
  incidental) printf 'done: report mentions https://gitlab.example.test/group/sub/project/-/merge_requests/7 in documentation\n' > "$MATE/state/$id.status";;
  malformed) printf 'done: PR https://gitlab.example.test/group/sub/project/-/merge_requests/0 checks green\n' > "$MATE/state/$id.status";;
 esac
 [ "$id" != metadata ] || printf 'pr=https://gitlab.example.test/group/sub/project/-/merge_requests/8\n' >> "$MATE/state/$id.meta"
 FM_HOME="$MATE" "$ROOT/bin/fm-inactive-reconcile.sh" report "$id"
 FM_HOME="$MATE" "$ROOT/bin/fm-inactive-reconcile.sh" report "$id"
done
cat "$MAIN/state/mate.status"
python3 - "$MAIN/state/mate.status" <<'PY'
import pathlib,sys
lines=pathlib.Path(sys.argv[1]).read_text().splitlines()
for name in ['ready','metadata','incidental','scout','malformed']:
 matching=[l for l in lines if 'child '+name+' done:' in l]
 assert len(matching)==1,(name,matching)
 line=matching[0]
 if name=='ready': assert ' pr=https://gitlab.example.test/group/sub/project/-/merge_requests/7 ' in line,line
 elif name=='metadata': assert ' pr=https://gitlab.example.test/group/sub/project/-/merge_requests/8 ' in line,line
 else: assert ' pr=' not in line,line
PY
printf 'Exact canonical parent delivery, metadata precedence, exclusion and once-only receipts verified.\n'
