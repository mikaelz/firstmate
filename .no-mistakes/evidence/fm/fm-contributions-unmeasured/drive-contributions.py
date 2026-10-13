import json, os, pathlib, shutil, subprocess, tempfile
ROOT = pathlib.Path.cwd()
E = pathlib.Path('/home/mike/.no-mistakes/evidence/01M4V7KED2NMFN9WG1FW7VBW9S')
lab = pathlib.Path(tempfile.mkdtemp(prefix='.contributions-live-', dir=ROOT))
log = []
urls = ['https://gitlab.com/o/r/-/merge_requests/2', 'https://git.example.org/group/subgroup/r/-/merge_requests/3']
def home(name):
    h = lab/name
    for p in ['data','state','config','projects','gh','tmux','tmp']:
        (h/p).mkdir(parents=True)
    (h/'config/backend').write_text('tmux\n')
    (h/'config/supervision-host-off').touch()
    (h/'data/backlog.md').write_text('# Backlog\n\n## Queued\n')
    return h

def env(h):
    e = dict(os.environ)
    for k in list(e):
        if k.startswith(('FM_', 'GH_', 'GITHUB_', 'TASKS_AXI_', 'HERDR_', 'BEADS_', 'BD_')) or k == 'TMUX':
            e.pop(k)
    e.update(FM_HOME=str(h), FM_ROOT_OVERRIDE=str(ROOT), FM_STATE_OVERRIDE=str(h/'state'),
             FM_DATA_OVERRIDE=str(h/'data'), FM_CONFIG_OVERRIDE=str(h/'config'), FM_PROJECTS_OVERRIDE=str(h/'projects'),
             GH_CONFIG_DIR=str(h/'gh'), GH_TOKEN='disposable-invalid-token', GH_NO_UPDATE_NOTIFIER='1',
             TMUX_TMPDIR=str(h/'tmux'), TMPDIR=str(h/'tmp'),
             HTTPS_PROXY='http://127.0.0.1:1', HTTP_PROXY='http://127.0.0.1:1', ALL_PROXY='http://127.0.0.1:1', NO_PROXY='',
             FM_POLL='1', FM_CHECK_INTERVAL='0', FM_SIGNAL_GRACE='0', FM_HEARTBEAT='999999')
    return e

def run(h, label, args, traced=False, expected=0):
    cmd = [str(ROOT/'bin'/args[0]), *args[1:]]
    trace = h/(label+'.trace')
    if traced: cmd = ['strace','-f','-e','trace=execve,connect','-o',str(trace),*cmd]
    p = subprocess.run(cmd, env=env(h), capture_output=True, text=True, timeout=60)
    log.append({'step':label, 'command':args, 'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    assert p.returncode == expected, log[-1]
    if traced:
        t = trace.read_text()
        gh = [l for l in t.splitlines() if 'execve(' in l and ', ["gh", "api"' in l and ') = 0' in l]
        log[-1]['gh_api_execs'] = gh
        log[-1]['connections'] = [l for l in t.splitlines() if 'connect(' in l and 'AF_INET' in l]
        return p, gh
    return p

def snapshot(h,label):
    p=run(h,label,['fm-bearings-snapshot.sh','--json'])
    d=json.loads(p.stdout)['contributions']
    log[-1]['stdout']=json.dumps(d,indent=2)
    (E/(label+'.json')).write_text(json.dumps(d,indent=2)+'\n')
    return d

def backlog(h, pairs):
    (h/'data/backlog.md').write_text('# Backlog\n\n## Queued\n'+''.join('- [ ] '+task+' - Filed '+url+' (repo: sample) (kind: ship)\n' for task,url in pairs))

def row(url):
    return dict(url=url,kind='pr', checked_at='2026-09-16T08:00:00Z',error='forge observation unavailable or changed during read',
                observation=None,verdict=None,seen=[],pending=[],notified=[],provenance='retained ownership')

def save(h,task,rows):
    (h/'data'/task).mkdir(exist_ok=True)
    (h/'data'/task/'contributions.json').write_text(json.dumps(dict(schema='fm-contributions.v1',task=task,records=rows)))

def read(h,task): return json.loads((h/'data'/task/'contributions.json').read_text())
try:
    h=home('before-fix')
    backlog(h,[('gitlab',urls[0])])
    before=lab/'before-code'
    shutil.copytree(ROOT/'bin',before/'bin')
    for name in ['fm-contributions.sh','fm-contributions.jq']:
        content=subprocess.check_output(['git','show','6407052f4c521e39401ce2305dfa45d201249827:bin/'+name])
        (before/'bin'/name).write_bytes(content)
    p=subprocess.run([str(before/'bin/fm-contributions.sh'),'poll'],env=env(h),capture_output=True,text=True,timeout=60)
    log.append({'step':'before-fix-reproduction','base':'6407052f4c521e39401ce2305dfa45d201249827','exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    assert p.returncode != 0 and 'BUDGET_EXHAUSTED' in p.stderr
    h=home('fresh')
    backlog(h,list(zip(['gitlab','selfhosted'],urls))+[('forgejo','https://codeberg.org/o/r/pulls/2')])
    p,gh=run(h,'fresh-poll',['fm-contributions.sh','poll'],True)
    assert not gh and not p.stdout and not p.stderr
    assert not list((h/'data').glob('*/contributions.json'))
    d=snapshot(h,'fresh-coverage')
    assert (d['known'],d['checked'],d['unmeasured'],d['unreadable_records'])==(2,0,2,0)
    assert all(v==0 for v in d['counts'].values()) and not d['complete']
    run(h,'fresh-arm',['fm-contributions.sh','arm','--if-owned'])
    p,gh=run(h,'fresh-watcher',['fm-watch-checkpoint.sh','--seconds','4'],True,124)
    assert not gh and (not (h/'state/.wake-queue').exists() or not (h/'state/.wake-queue').read_text().strip())
    h=home('real-diagnostic')
    backlog(h,[('gitlab',urls[0])])
    run(h,'diagnostic-arm',['fm-contributions.sh','arm','--if-owned'])
    (h/'data/unreadable').mkdir()
    (h/'data/unreadable/contributions.json').write_text('incomplete JSON\n')
    p,gh=run(h,'real-diagnostic-watcher',['fm-watch-checkpoint.sh','--seconds','10'],True)
    assert not gh and '1 unreadable durable record(s)' in p.stdout and 'observation unavailable' not in p.stdout
    log.append({'step':'real-diagnostic-durable-wake','wake_queue':(h/'state/.wake-queue').read_text()})

    h=home('legacy')
    # Two unsupported rows in the same saved file, absent from backlog.
    rows=[row(u) for u in urls]
    save(h,'retained',rows)
    p,gh=run(h,'legacy-poll',['fm-contributions.sh','poll'],True)
    assert not gh and not p.stdout and not p.stderr
    expected=[dict(r,error=None) for r in rows]
    assert read(h,'retained')['records']==expected
    (E/'legacy-after.json').write_text(json.dumps(read(h,'retained'),indent=2)+'\n')
    d=snapshot(h,'legacy-coverage')
    assert (d['known'],d['checked'],d['unmeasured'])==(2,0,2) and all(v==0 for v in d['counts'].values())

    h=home('mixed')
    github='https://github.com/o/r/pull/8'
    save(h,'mixed',[row(github),row(urls[0])])
    p,gh=run(h,'mixed-poll',['fm-contributions.sh','poll'],True)
    assert gh and not p.stdout and not p.stderr
    saved=read(h,'mixed')['records']
    assert next(r for r in saved if r['url']==github)['error'] is not None
    assert next(r for r in saved if r['url']==urls[0])==dict(row(urls[0]),error=None)
    assert all(r['observation'] is None for r in saved)
    (E/'mixed-after.json').write_text(json.dumps(read(h,'mixed'),indent=2)+'\n')
    d=snapshot(h,'mixed-coverage')
    assert (d['known'],d['checked'],d['unmeasured'],d['counts']['fleet'])==(2,0,1,1)

    h=home('github-outage')
    backlog(h,[('github',github),('gitlab',urls[0])])
    # The installed real gh tries a deliberately unreachable loopback proxy;
    # no forge executable, login, or response is replaced.
    p,gh=run(h,'outage-first-poll',['fm-contributions.sh','poll'],True)
    assert gh and p.stdout.strip()=='contributions: observation unavailable for '+github
    p,gh=run(h,'outage-repeat-poll',['fm-contributions.sh','poll'],True)
    assert gh and not p.stdout and not p.stderr
    assert read(h,'github')['records'][0]['error'] is not None
    assert not (h/'data/gitlab/contributions.json').exists()
    d=snapshot(h,'outage-coverage')
    assert (d['known'],d['checked'],d['unmeasured'],d['counts']['fleet'])==(2,0,1,1)

    h=home('watcher-outage')
    backlog(h,[('github',github),('gitlab',urls[0])])
    run(h,'outage-arm',['fm-contributions.sh','arm','--if-owned'])
    p,gh=run(h,'outage-watcher',['fm-watch-checkpoint.sh','--seconds','10'],True)
    assert gh and 'observation unavailable for '+github in p.stdout and 'gitlab' not in p.stdout
    wake=(h/'state/.wake-queue').read_text()
    assert 'observation unavailable for '+github in wake and 'gitlab' not in wake
    log.append({'step':'outage-durable-wake','wake_queue':wake})
    (E/'outage-record.json').write_text(json.dumps(read(h,'github'),indent=2)+'\n')
    (E/'outage-wake.txt').write_text(wake)
    log.append({'result':'all live assertions passed','isolation':'All homes removed; real gh used with isolated config and unreachable loopback proxy. No production credentials or fleet endpoints used.'})
finally:
    (E/'live-contributions.json').write_text(json.dumps(log,indent=2)+'\n')
    shutil.rmtree(lab)
