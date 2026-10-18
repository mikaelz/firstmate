import os, pathlib, subprocess, json, hashlib
root=pathlib.Path.cwd(); work=root/'.doctor-live'; home=work/'home'; ev=pathlib.Path('~/.no-mistakes/evidence/01M56ZEY5J07KH5B4775RWDHWV')
for d in ['config','state','data','.claude','projects']: (home/d).mkdir(parents=True,exist_ok=True)
env=dict(os.environ)
for k in list(env):
    if k.startswith('FM_') or k.startswith('HERDR_') or k in ['TMUX','TMUX_PANE','CLAUDE_CONFIG_DIR','TASKS_AXI_FILE','TASKS_AXI_BACKEND','GH_TOKEN','GITHUB_TOKEN','GH_ENTERPRISE_TOKEN','GITHUB_ENTERPRISE_TOKEN']: env.pop(k,None)
env.update(HOME=str(home),FM_HOME=str(home),FM_ROOT_OVERRIDE=str(home),FM_BOOTSTRAP_CLAUDE_USER_SETTINGS=str(home/'.claude/settings.json'),FM_BOOTSTRAP_NO_MISTAKES_HOME=str(home/'nm'),FM_SUPERVISION_ACTOR='branch',FM_SUPERVISION_PRIMARY_HARNESS='claude',TMPDIR=str(work/'tmp'),XDG_CONFIG_HOME=str(home/'.config'),XDG_CACHE_HOME=str(home/'.cache'))
log=[]
def snap():
    return {str(p.relative_to(home)):(p.stat().st_mode,p.stat().st_mtime_ns,hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else 'dir') for p in home.rglob('*')}
def run(label,args,extra=None):
    e=env| (extra or {}); before=snap()
    p=subprocess.run([str(root/'bin/fm-doctor.sh'),*args],env=e,text=True,capture_output=True,timeout=100)
    after=snap(); assert before==after, f'{label}: doctor mutated home'
    (ev/(label+'.txt')).write_text('$ bin/fm-doctor.sh '+' '.join(args)+'\nexit='+str(p.returncode)+'\n'+p.stdout+p.stderr+'\nHome unchanged: yes\n')
    log.append(dict(scenario=label,exit=p.returncode,home_unchanged=True))
    return p,json.loads(p.stdout) if '--json' in args else None
def status(j,id): return next(c['status'] for c in j['checks'] if c['id']==id)
def settings(rule=None,mode='auto'):
    p={'defaultMode':mode}
    if rule: p['allow']=[rule]
    (home/'.claude/settings.json').write_text(json.dumps({'permissions':p}))
settings()
for label,rule,expected in [('auto-no-rule',None,'warn'),('auto-single-script','Bash(bin/fm-doctor.sh:*)','warn'),('auto-other-home','Bash(/another/home/bin/fm-*:*)','warn'),('auto-relative-family','Bash(bin/fm-*:*)','ok'),('auto-absolute-family',f'Bash({home}/bin/fm-*:*)','ok')]:
    settings(rule); p,j=run(label,['--json','--area','permissions']); assert status(j,'permissions/claude-fm-scripts')==expected
settings(mode='default'); p,j=run('non-auto',['--json','--area','permissions']); assert status(j,'permissions/claude-fm-scripts')=='ok'
(home/'.claude/settings.json').write_text('{bad'); p,j=run('malformed-settings',['--json','--area','permissions']); assert status(j,'permissions/claude-fm-scripts')=='warn'
settings()
(home/'nm').mkdir(); (home/'nm/config.yaml').write_text('agent: [definitely-absent-doctor-agent]\n')
p,j=run('unavailable-agent',['--json','--area','no-mistakes']); assert status(j,'no-mistakes/agents')=='warn'
(home/'config/tool-provenance').write_text('jq /unavailable/pinned-build/\n')
p,j=run('replaced-tool',['--json','--area','tools']); assert status(j,'tools/provenance')=='warn'
(home/'config/startup-memory-budget').write_text('1\n'); (home/'data/captain-shared.md').write_text('this exceeds a one-token budget')
p,j=run('over-budget',['--json','--area','memory']); assert status(j,'memory/budget')=='warn' and p.returncode==0
(home/'config/crew-harness').write_text('bogus\n'); p,j=run('unsupported-harness',['--json','--area','config']); assert status(j,'config/crew-harness')=='warn'
(home/'config/backend').write_text('bogus\n'); p,j=run('invalid-backend',['--json','--area','backend']); assert status(j,'backend/invalid')=='fail' and p.returncode==1
(home/'config/backend').unlink()
for label,args in [('help',['--help']),('unknown-option',['--bogus']),('unknown-area',['--area','nowhere']),('missing-area',['--area'])]:
    p,j=run(label,args); assert p.returncode==(0 if label=='help' else 2)
p,j=run('default-toon',[]); assert 'checks[' in p.stdout and 'findings[' in p.stdout
p,j=run('default-json',['--json']); assert j['schema']=='fm-doctor.v1' and status(j,'auth/github')=='skip'
# Real owner reads its published report contract, with real gh isolated from credentials.
for state,expected in [('done','ok'),('timeout','skip'),('failed','skip')]:
    (home/'state/.startup-network.status').write_text(f'generation=1\nstate={state}\nstarted=100\nfinished=105\nphases=probe,sweeps\nreport_published=1\nlocked=1\n')
    (home/'state/.startup-network.report').write_text('FLEET_SYNC: alpha: STUCK: needs attention\n'+('NETWORK_CHECKS: the deferred checks may be incomplete\n' if state!='done' else ''))
    p,j=run('network-'+state,['--json','--network']); assert status(j,'fleet/sync')=='warn' and status(j,'fleet/secondmate-sync')==expected
    assert status(j,'auth/github')=='fail' and p.returncode==1
# Exercise the shared renderer through its other real public consumer.
p=subprocess.run([str(root/'bin/fm-bearings-snapshot.sh')],env=env,text=True,capture_output=True,timeout=100)
(ev/'bearings-toon.txt').write_text(p.stdout+p.stderr); assert p.returncode==0 and 'schema: fm-bearings.v1' in p.stdout
(ev/'live-results.json').write_text(json.dumps(log,indent=2))
print(json.dumps(log,indent=2))
