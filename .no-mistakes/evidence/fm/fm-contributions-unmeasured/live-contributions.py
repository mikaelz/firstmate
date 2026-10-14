#!/usr/bin/env python3
"""Drive shipped CLI with disposable FM_HOME and real gh against local HTTPS forge data.
No tool shims, operator data, or production credentials are used.
"""
import os, json, pathlib, tempfile, subprocess, ssl, threading, http.server, shutil
ROOT = pathlib.Path.cwd()
EVIDENCE = pathlib.Path('/home/mike/.no-mistakes/evidence/01M4V7KED2NMFN9WG1FW7VBW9S')
lab = pathlib.Path(tempfile.mkdtemp(prefix='live-contributions-', dir=ROOT / '.test-validation-tmp'))
requests = []
mode = 'healthy'
class Forge(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        requests.append({'path': self.path, 'mode': mode})
        code = 502 if mode == 'down' else 200
        if code == 502: data = {'message': 'Disposable forge outage'}
        elif self.path.endswith('/issues/9'): data = {'state':'open', 'user':{'login':'author'}, 'labels':[], 'html_url':'https://github.com/o/r/issues/9'}
        elif mode == 'signal' and '/comments?' in self.path: data = [{'id':12,'user':{'login':'maintainer'},'author_association':'OWNER','body':'Please clarify the contract','html_url':'https://github.com/o/r/issues/9#issuecomment-12','updated_at':'2026-10-14T08:01:00Z'}]
        else: data = []
        payload = json.dumps(data).encode()
        self.send_response(code); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(payload))); self.end_headers(); self.wfile.write(payload)
    def log_message(self, *args): pass
server = None
log = []
def emit(title, data): log.append({'step':title, 'product_output':data})
try:
    subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(lab/'key.pem'),'-out',str(lab/'cert.pem'),'-days','1','-subj','/CN=127.0.0.1','-addext','subjectAltName=IP:127.0.0.1'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    server = http.server.ThreadingHTTPServer(('127.0.0.1',0),Forge)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(lab/'cert.pem',lab/'key.pem'); server.socket = ctx.wrap_socket(server.socket,server_side=True)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    env = dict(os.environ)
    for key in list(env):
        if key.startswith(('FM_', 'GH_', 'GITHUB_', 'TASKS_AXI_')) or key == 'TMUX': env.pop(key)
    env.update(GH_HOST=f'127.0.0.1:{server.server_port}', GH_ENTERPRISE_TOKEN='disposable-local-fixture-only', GH_CONFIG_DIR=str(lab/'gh-config'), SSL_CERT_FILE=str(lab/'cert.pem'), GH_PROMPT_DISABLED='1', TMPDIR=str(lab))
    def home(name):
        h=lab/name
        for d in ['data','state','config','projects']: (h/d).mkdir(parents=True)
        (h/'data/backlog.md').write_text('# Backlog\n\n## Queued\n')
        return h
    def run(h, script, *args):
        e=dict(env); e.update(FM_HOME=str(h),FM_ROOT_OVERRIDE=str(ROOT),FM_STATE_OVERRIDE=str(h/'state'),FM_DATA_OVERRIDE=str(h/'data'),FM_CONFIG_OVERRIDE=str(h/'config'),FM_PROJECTS_OVERRIDE=str(h/'projects'))
        p=subprocess.run(['bash',str(ROOT/'bin'/script),*args],env=e,text=True,capture_output=True,timeout=40)
        assert p.returncode==0,(script,p.returncode,p.stdout,p.stderr)
        return p
    def snapshot(h):
        p=run(h,'fm-fleet-snapshot.sh','--contribution-input'); (h/'input.json').write_text(p.stdout)
        s=json.loads(run(h,'fm-contributions.sh','snapshot',str(h/'input.json'),'--all').stdout)
        return s
    def coverage(s,known,checked,unmeasured,counts):
        assert (s['known'],s['checked'],s['unmeasured'],s['unreadable_records'],s['counts']) == (known,checked,unmeasured,0,counts),s
    zeros={'captain':0,'fleet':0,'maintainer':0,'nobody':0}
    urls=['https://gitlab.com/o/r/-/merge_requests/2','https://git.example.org/group/subgroup/r/-/merge_requests/3','https://github-com/o/r/pull/8','https://githubXcom/o/r/issues/9']
    h=home('fresh')
    for i,url in enumerate(urls):
        with (h/'data/backlog.md').open('a') as f: f.write(f'- [ ] u{i} - Filed {url} (repo: sample) (kind: ship) (hold: choose scope) (hold-kind: captain)\n')
    p=run(h,'fm-contributions.sh','poll'); assert not p.stdout and not p.stderr; assert not requests
    assert not list((h/'data').glob('*/contributions.json')) and not (h/'state/.wake-queue').exists()
    s=snapshot(h); coverage(s,4,0,4,zeros); emit('Fresh unsupported and held lookalike links: silent poll, no HTTP calls, no error records or wakes',{'stdout':p.stdout,'stderr':p.stderr,'forge_requests':list(requests),'snapshot':s})
    with (h/'data/backlog.md').open('a') as f: f.write('- [ ] forgejo - Filed https://codeberg.org/o/r/pulls/2 (repo: sample) (kind: ship)\n')
    p=run(h,'fm-contributions.sh','poll'); assert not p.stdout and not p.stderr and not requests
    coverage(snapshot(h),4,0,4,zeros); emit('Existing Forgejo pull ownership boundary unchanged',snapshot(h))
    emit('Bearings end-user coverage',json.loads(run(h,'fm-bearings-snapshot.sh','--json').stdout)['contributions'])
    h=home('retained')
    def record(url): return {'url':url,'kind':'issue' if '/issues/' in url else 'pr','checked_at':'2026-09-16T08:00:00Z','error':'forge observation unavailable or changed during read','observation':None,'verdict':None,'seen':[],'pending':[],'notified':[],'provenance':'retained ownership'}
    for i,url in enumerate(urls):
        d=h/'data'/f'u{i}'; d.mkdir(); (d/'contributions.json').write_text(json.dumps({'schema':'fm-contributions.v1','task':f'u{i}','records':[record(url)]}))
    p=run(h,'fm-contributions.sh','poll'); assert not p.stdout and not p.stderr and not requests
    for i,url in enumerate(urls):
        row=json.loads((h/'data'/f'u{i}'/'contributions.json').read_text())['records'][0]; expected=record(url); expected['error']=None; assert row==expected
    s=snapshot(h); coverage(s,4,0,4,zeros); emit('Retained unsupported ownership after backlog removal: only error cleared',s)
    h=home('mixed'); d=h/'data'/'delivery'; d.mkdir(); supported='https://github.com/o/r/issues/9'
    rows=[record(supported)]+[record(u) for u in urls]
    (d/'contributions.json').write_text(json.dumps({'schema':'fm-contributions.v1','task':'delivery','records':rows}))
    mode='down'; start=len(requests)
    p=run(h,'fm-contributions.sh','poll'); assert not p.stdout and not p.stderr
    assert len(requests)-start==1 and requests[-1]['path'].endswith('/issues/9'),requests
    stored=json.loads((d/'contributions.json').read_text()); assert len(stored['records'])==5
    for row in stored['records']:
        if row['url']!=supported:
            expected=record(row['url']); expected['error']=None; assert row==expected
        else: assert row['error'] and row['observation'] is None
    s=snapshot(h); coverage(s,5,0,4,dict(zeros,fleet=1)); emit('Mixed retained file: unsupported errors cleared, existing GitHub episode retried silently',{'snapshot':s,'records':stored,'HTTP':requests[start:]})
    mode='healthy'; p=run(h,'fm-contributions.sh','poll'); assert not p.stdout and not p.stderr
    s=snapshot(h); coverage(s,5,1,4,dict(zeros,maintainer=1)); emit('Mixed file GitHub read recovers without dropping unsupported records',{'snapshot':s,'records':json.loads((d/'contributions.json').read_text())})
    h=home('episode'); (h/'data/backlog.md').write_text(f'# Backlog\n\n## Queued\n- [ ] delivery - Filed {supported} (repo: sample) (kind: ship)\n')
    run(h,'fm-contributions.sh','arm'); line=f'contributions: observation unavailable for {supported}\n'
    mode='down'; p=run(h,'fm-contributions.sh','poll'); assert p.stdout==line and not p.stderr; emit('GitHub failure episode starts with unavailable alert',{'stdout':p.stdout,'records':json.loads((h/'data/delivery/contributions.json').read_text())})
    p=run(h,'fm-contributions.sh','poll'); assert not p.stdout and not p.stderr; emit('Repeated GitHub outage remains failed without repeated alert',{'stdout':p.stdout,'snapshot':snapshot(h)})
    mode='healthy'; p=run(h,'fm-contributions.sh','poll'); assert not p.stdout and not p.stderr; assert json.loads((h/'data/delivery/contributions.json').read_text())['records'][0]['error'] is None
    emit('Successful GitHub read ends episode',snapshot(h))
    mode='down'; p=run(h,'fm-contributions.sh','poll'); assert p.stdout==line and not p.stderr; emit('New GitHub outage alerts again after recovery',{'stdout':p.stdout,'snapshot':snapshot(h)})
    h=home('watcher'); (h/'data/backlog.md').write_text(f'# Backlog\n\n## Queued\n- [ ] unsupported - Filed {urls[0]} (repo: sample) (kind: ship)\n- [ ] delivery - Filed {supported} (repo: sample) (kind: ship)\n')
    mode='healthy'; run(h,'fm-contributions.sh','arm'); run(h,'fm-contributions.sh','poll')
    (h/'data/unreadable').mkdir(); (h/'data/unreadable/contributions.json').write_text('incomplete JSON\n')
    mode='signal'
    we=dict(env); we.update(FM_HOME=str(h),FM_ROOT_OVERRIDE=str(ROOT),FM_STATE_OVERRIDE=str(h/'state'),FM_DATA_OVERRIDE=str(h/'data'),FM_CONFIG_OVERRIDE=str(h/'config'),FM_PROJECTS_OVERRIDE=str(h/'projects'),FM_POLL='1',FM_SIGNAL_GRACE='0',FM_CHECK_INTERVAL='0',FM_HEARTBEAT='999999')
    p=subprocess.run(['bash',str(ROOT/'bin/fm-watch-checkpoint.sh'),'--seconds','15'],env=we,text=True,capture_output=True,timeout=30)
    assert p.returncode==0,(p.returncode,p.stdout,p.stderr)
    wakes=(h/'state/.wake-queue').read_text(); lines=[x for x in wakes.splitlines() if '\tcheck\t' in x]; assert len(lines)==2,wakes
    assert '1 unreadable durable record(s)' in wakes and 'check: contributions delivery ' in wakes
    assert 'observation unavailable' not in wakes and 'gitlab.com' not in wakes
    emit('Authenticated watcher surfaces only real unreadable-record diagnostic and maintainer signal with GitLab ownership present',{'stdout':p.stdout,'stderr':p.stderr,'durable_wake_queue':wakes,'pending':json.loads(run(h,'fm-contributions.sh','snapshot',str(h/'input.json'),'--all').stdout) if (h/'input.json').exists() else json.loads((h/'data/delivery/contributions.json').read_text())})
    (EVIDENCE/'live-contributions-results.json').write_text(json.dumps({'product':'unmodified bin/fm-contributions.sh, fleet snapshot, Bearings; installed gh CLI','isolation':'Disposable FM_HOME; real gh HTTPS reads to disposable local forge dataset; no production credentials or CLI mocks','steps':log,'forge_requests':requests},indent=2)+'\n')
    print('CLI live scenarios completed; evidence: live-contributions-results.json')
finally:
    if server: server.shutdown(); server.server_close()
    shutil.rmtree(lab)
