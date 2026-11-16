import os, pathlib, subprocess, json, hashlib, shutil

root = pathlib.Path.cwd()
work = root / '.doctor-live'
evidence = pathlib.Path('~/Dropbox/no-mistakes-evidence/01M7HD50BZS7D6KSB1G3N0BS0T')
base = os.environ.copy()
for k in list(base):
    if k.startswith(('FM_', 'HERDR_', 'CMUX_', 'REX_', 'TASKS_AXI_', 'GH_', 'GITHUB_')) or k in ('TMUX','TMUX_PANE','NM_HOME','CLAUDE_CONFIG_DIR'):
        base.pop(k)
base.update(HOME=str(work/'user'), XDG_CONFIG_HOME=str(work/'xdg'), GH_CONFIG_DIR=str(work/'gh'), TMPDIR=str(work/'tmp'))
for k in ('HOME','XDG_CONFIG_HOME','GH_CONFIG_DIR'):
    pathlib.Path(base[k]).mkdir(exist_ok=True)
results=[]

def home(name):
    h=work/name
    for p in ('config','data','nm'):
        (h/p).mkdir(parents=True,exist_ok=True)
    return h

def put(h,p,text):
    f=h/p; f.parent.mkdir(parents=True,exist_ok=True); f.write_text(text)

def snap(h):
    return {str(p.relative_to(h)):('dir' if p.is_dir() else hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_mode,p.stat().st_mtime_ns) for p in h.rglob('*')}

def run(h,label,args=(),extra=None,raw=False):
    env=base|dict(FM_HOME=str(h), FM_ROOT_OVERRIDE=str(h), FM_BOOTSTRAP_NO_MISTAKES_HOME=str(h/'nm'), FM_BOOTSTRAP_CLAUDE_USER_SETTINGS=str(h/'user-settings.json'),FM_BACKEND='tmux')
    env.update(extra or {})
    cmd=['bin/fm-doctor.sh']+([] if raw else ['--json'])+list(args)
    p=subprocess.run(cmd,env=env,text=True,capture_output=True,timeout=100)
    (evidence/(label+'.stdout')).write_text(p.stdout)
    (evidence/(label+'.stderr')).write_text(p.stderr)
    print(label, 'exit',p.returncode,flush=True)
    with (evidence/'live-commands.log').open('a') as f:
        f.write(f'{label}: FM_HOME={h} FM_ROOT_OVERRIDE={h} FM_BACKEND={env["FM_BACKEND"]} '+ ' '.join(cmd)+f'\nexit={p.returncode}\n')
    return (p, p.stdout if raw or not p.stdout.startswith('{') else json.loads(p.stdout))

def status(j,id):
    return next(x['status'] for x in j['checks'] if x['id']==id)

def scenario(name,fn):
    try:
        fn(); results.append(dict(name=name,result='pass',live=True,reason='Real CLI and owner commands executed with disposable local homes and synthetic configuration.',evidence=name))
    except Exception as ex:
        results.append(dict(name=name,result='fail',live=True,reason=repr(ex),evidence=name))
        print('FAIL',name,repr(ex),flush=True)
    (evidence/'live-results.json').write_text(json.dumps(results,indent=2))

def readonly():
    h=home('readonly'); before=snap(h)
    p,j=run(h,'readonly-json'); assert j['schema']=='fm-doctor.v1'
    assert status(j,'doctor/inventory')=='ok' and status(j,'doctor/unmapped-line')=='ok'
    assert status(j,'auth/github')=='skip'
    p,t=run(h,'readonly-toon',raw=True); assert 'findings[' in t and 'help[' in t
    assert f'verdict: {j["verdict"]}' in t
    p,a=run(h,'readonly-area',['--area','supervision']); assert {x['area'] for x in a['checks']}=={'doctor','supervision'}
    p,_=run(h,'readonly-usage',['--area','nowhere']); assert p.returncode==2
    p,_=run(h,'readonly-help',['--help'],raw=True); assert p.returncode==0
    assert snap(h)==before, 'doctor mutated fresh home'
    assert not (h/'state').exists()
scenario('Read a fresh home in JSON and TOON, filter checks, reject bad usage, and leave state absent',readonly)

def provenance():
    h=home('provenance'); bash=shutil.which('bash'); assert bash
    put(h,'config/tool-provenance',f'bash {work}/missing-pin/\n')
    p,j=run(h,'provenance-mismatch',['--area','tools']); assert status(j,'tools/provenance')=='warn'
    put(h,'config/tool-provenance',f'bash {pathlib.Path(bash).resolve().parent}/\n')
    p,j=run(h,'provenance-match',['--area','tools']); assert status(j,'tools/provenance')=='ok'
scenario('Detect and clear a provenance mismatch for the actual bash executable',provenance)

def config():
    h=home('configuration')
    put(h,'config/crew-dispatch.json','{"rules":[')
    p,j=run(h,'configuration-malformed',['--area','config']); assert status(j,'config/crew-dispatch')=='fail' and p.returncode==1
    (h/'config/crew-dispatch.json').unlink()
    for harness in ('cortex','hermes','kiro','not-supported'):
        put(h,'config/crew-harness',harness+'\n')
        p,j=run(h,'configuration-'+harness,['--area','config'])
        assert status(j,'config/crew-harness')==('warn' if harness=='not-supported' else 'ok')
    p,j=run(h,'configuration-backend',['--area','backend'],{'FM_BACKEND':'not-supported'})
    assert status(j,'backend/invalid')=='fail' and p.returncode==1
scenario('Report invalid dispatch and backend settings while accepting cortex, kiro, and hermes crew settings',config)

def permissions():
    h=home('permissions'); extra={'FM_SUPERVISION_ACTOR':'branch','FM_SUPERVISION_PRIMARY_HARNESS':'claude'}
    for label,allow,want in [('absent',[],'warn'),('one',['Bash(bin/fm-doctor.sh:*)'],'warn'),('family',['Bash(bin/fm-*:*)'],'ok'),('other-root',['Bash(/another/bin/fm-*:*)'],'warn')]:
        put(h,'user-settings.json',json.dumps({'permissions':{'defaultMode':'auto','allow':allow}}))
        p,j=run(h,'permissions-'+label,['--area','permissions'],extra); assert status(j,'permissions/claude-fm-scripts')==want
    put(h,'.claude/settings.local.json','{"permissions":{"defaultMode":"default"}}')
    p,j=run(h,'permissions-local-precedence',['--area','permissions'],extra); assert status(j,'permissions/claude-fm-scripts')=='ok'
scenario('Diagnose Claude auto-mode allow rules and respect local settings precedence without launching Claude',permissions)

def agents():
    h=home('agents')
    forms={'scalar':'agent: fm-live-missing-agent\n','flow':'agent: [bash, fm-live-missing-agent]\n','unindented':'agent:\n- bash\n- fm-live-missing-agent\n','commented':'agent: # fallback order\n- bash\n- fm-live-missing-agent\n','indented':'agent:\n  - bash\n  - fm-live-missing-agent\n'}
    assert not shutil.which('fm-live-missing-agent')
    for label,text in forms.items():
        put(h,'nm/config.yaml',text)
        p,j=run(h,'agents-'+label,['--area','no-mistakes']); assert status(j,'no-mistakes/agents')=='warn'
    put(h,'nm/config.yaml','agent: bash\n')
    p,j=run(h,'agents-installed',['--area','no-mistakes']); assert status(j,'no-mistakes/agents')=='ok'
scenario('Find an absent fallback executable in scalar, flow, and commented or unindented YAML lists',agents)

def memory():
    h=home('memory')
    p,j=run(h,'memory-absent',['--area','memory']); assert status(j,'memory/budget')=='info'
    put(h,'config/startup-memory-budget','invalid\n')
    p,j=run(h,'memory-invalid',['--area','memory']); assert status(j,'memory/budget')=='warn'
    put(h,'config/startup-memory-budget','1\n'); put(h,'data/captain-shared.md','abc')
    p,j=run(h,'memory-at-budget',['--area','memory']); assert status(j,'memory/budget')=='ok'
    put(h,'data/captain-shared.md','abcd')
    p,j=run(h,'memory-over-budget',['--area','memory']); assert status(j,'memory/budget')=='warn'
scenario('Report absent, malformed, at-limit, and over-limit startup memory budgets',memory)

def readiness():
    h=home('readiness')
    child=subprocess.Popen(['bash','-c','exit 0']); child.wait()
    put(h,'state/.lock',str(child.pid)+'\n'); before=snap(h)
    p,j=run(h,'readiness-dead',['--area','supervision'])
    c=next(c for c in j['checks'] if c['id']=='supervision/ready')
    detail=json.loads(c['detail'][0]); assert c['status']=='warn' and detail['lock']['state']=='stale' and detail['can_receive']==False
    assert p.returncode==0 and snap(h)==before
scenario('Warn when a real reaped primary PID leaves a stale lock and cannot receive work',readiness)

def network():
    h=home('network')
    put(h,'state/.startup-network.status','generation=1\nstate=done\nstarted=100\nfinished=105\nphases=probe,sweeps\nreport_published=1\nlocked=1\n')
    put(h,'state/.startup-network.report','FLEET_SYNC: synthetic-repo: STUCK: needs attention\nCONFIG_REREAD: synthetic-mate: send failed: unavailable\n')
    p,j=run(h,'network-opt-out'); assert status(j,'fleet/sync')=='skip'
    before=snap(h)
    p,j=run(h,'network-opt-in',['--network'],{'GH_TOKEN':'','GITHUB_TOKEN':''})
    assert status(j,'auth/github')=='fail' and status(j,'fleet/sync')=='warn' and status(j,'fleet/config-reread')=='warn'
    assert status(j,'fleet/secondmate-sync')=='ok' and p.returncode==1 and snap(h)==before
    put(h,'state/.startup-network.status','generation=1\nstate=timeout\nstarted=100\nfinished=105\nphases=probe,sweeps\nreport_published=1\nlocked=1\n')
    p,j=run(h,'network-incomplete',['--network'],{'GH_TOKEN':'','GITHUB_TOKEN':''})
    assert status(j,'fleet/secondmate-sync')=='skip'
scenario('Opt into real unauthenticated GitHub probing and read synthetic completed or incomplete network reports',network)
