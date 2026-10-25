import os, pathlib, subprocess, json, hashlib
root=pathlib.Path.cwd(); lab=root/'.validation-doctor/live'; lab.mkdir(parents=True)
evidence=pathlib.Path('~/.no-mistakes/evidence/01M5RYSKZFZY93GH9N3WG9ZXCT')
for p in ['home/state','home/config','home/data','user','tmp','nm','herdr-state']:(lab/p).mkdir(parents=True,exist_ok=True)
env={'PATH':os.environ['PATH'],'HOME':str(lab/'user'),'TMPDIR':str(lab/'tmp'),'LANG':'C.UTF-8','TERM':'xterm-256color','FM_HOME':str(lab/'home'),'FM_ROOT_OVERRIDE':str(lab/'home'),'FM_BOOTSTRAP_NO_MISTAKES_HOME':str(lab/'nm'),'FM_BOOTSTRAP_CLAUDE_USER_SETTINGS':str(lab/'user/settings.json'),'FM_SUPERVISION_ACTOR':'branch','FM_SUPERVISION_PRIMARY_HARNESS':'codex'}
log=[]; results=[]
def run(label,args=(),extra=None,exe='bin/fm-doctor.sh'):
 e=env.copy();e.update(extra or {})
 p=subprocess.run([str(root/exe),*args],env=e,text=True,capture_output=True,timeout=100)
 log.append(f'\n### {label}\n$ {exe} {" ".join(args)}\nexit={p.returncode}\n{p.stdout}{p.stderr}')
 return p

def check(name,fn):
 try:fn(); results.append({'name':name,'result':'pass'})
 except Exception as e:results.append({'name':name,'result':'fail','reason':str(e)})

def model(p):return json.loads(p.stdout)
def status(p,id):return next(c['status'] for c in model(p)['checks'] if c['id']==id)
def expect(value,want):assert value==want,(value,want)
def formats():
 p=run('Full isolated home JSON',['--json']);j=model(p);expect(j['schema'],'fm-doctor.v1');expect(status(p,'auth/github'),'skip')
 p=run('Full isolated home TOON');assert 'checks[' in p.stdout and 'findings[' in p.stdout
 for args in [['--area','absent'],['--unknown'],['--area']]:expect(run('Usage error',args).returncode,2)
 p=run('Scoped memory output',['--json','--area','memory']);expect(set(c['area'] for c in model(p)['checks']),{'doctor','memory'});expect(p.returncode,0)
check('Run default TOON, JSON and area selection; usage errors exit 2',formats)
def config():
 f=lab/'home/config/crew-harness'
 f.write_text('cortex\n');p=run('Cortex is supported',['--json','--area','config'],{'FM_SUPERVISION_PRIMARY_HARNESS':'cortex'});expect(status(p,'config/harness'),'ok');expect(status(p,'config/crew-harness'),'ok')
 f.write_text('bogus\n');p=run('Reject unsupported harness',['--json','--area','config']);expect(status(p,'config/crew-harness'),'warn');f.unlink()
 (lab/'home/config/backend').write_text('bogus\n');p=run('Invalid backend',['--json','--area','backend']);expect(status(p,'backend/invalid'),'fail');expect(p.returncode,1);(lab/'home/config/backend').unlink()
check('Accept cortex, warn for unsupported harness and fail an invalid backend',config)
def perms():
 f=lab/'user/settings.json'
 for rules,want in [([], 'warn'),(['Bash(bin/fm-doctor.sh:*)'],'warn'),(['Bash(/other-checkout/bin/fm-*:*)'],'warn'),(['Bash(bin/fm-*:*)'],'ok')]:
  f.write_text(json.dumps({'permissions':{'defaultMode':'auto','allow':rules}}));before=f.read_bytes();p=run('Auto permissions '+str(rules),['--json','--area','permissions'],{'FM_SUPERVISION_PRIMARY_HARNESS':'claude'});expect(status(p,'permissions/claude-fm-scripts'),want);expect(p.returncode,0);expect(f.read_bytes(),before)
 f.unlink()
check('Warn on Claude auto mode without this home script-family coverage; leave settings intact',perms)
def agents():
 for config in [lab/'nm/config.yaml',lab/'home/.no-mistakes.yaml']:
  for header in ['agent:\n','agent: # fallback order\n']:
   config.write_text(header+'- codex\n- fm-absent-validation-agent\n')
   p=run('Agent list '+config.name+' '+header.strip(),['--json','--area','no-mistakes']);expect(status(p,'no-mistakes/agents'),'warn');assert 'fm-absent-validation-agent' in p.stdout
  config.write_text('agent: [auto]\n');p=run('Auto agent requires no binary',['--json','--area','no-mistakes']);expect(status(p,'no-mistakes/agents'),'ok');config.unlink()
check('Detect unavailable agents in global and repository commented unindented YAML lists',agents)
def provenance():
 f=lab/'home/config/tool-provenance'
 for prefix,want in [(str(lab/'wrong-build')+'/', 'warn'),('/','ok')]:
  f.write_text('jq '+prefix+'\n');p=run('Tool provenance '+prefix,['--json','--area','tools']);expect(status(p,'tools/provenance'),want)
 f.unlink()
check('Report a real jq executable outside its pinned build prefix',provenance)
def memory():
 f=lab/'home/config/startup-memory-budget';f.write_text('1\n');data=lab/'home/data/captain-shared.md';data.write_text('abcd')
 p=run('Exceeded memory budget',['--json','--area','memory']);expect(status(p,'memory/budget'),'warn');expect(p.returncode,0)
 data.write_text('abc');p=run('Memory at budget',['--json','--area','memory']);expect(status(p,'memory/budget'),'ok');f.unlink();data.unlink()
check('Expose exceeded memory budget despite successful owner report',memory)
def inventory():
 inv=json.loads((root/'docs/doctor-checks.json').read_text());del inv['sources']['bootstrap']['env']['FM_BOOTSTRAP_DETECT_ONLY'];f=lab/'invalid-inventory.json';f.write_text(json.dumps(inv))
 p=run('Unsafe inventory refused',['--json'],{'FM_DOCTOR_INVENTORY':str(f)});expect(status(p,'doctor/inventory'),'fail');expect(p.returncode,1);expect(set(c['area'] for c in model(p)['checks']),{'doctor'})
check('Refuse an inventory that removes detect-only safety before running checks',inventory)
def network():
 p=run('No login in disposable home',['--json','--area','auth','--network']);expect(status(p,'auth/github'),'fail');expect(p.returncode,1)
 state=lab/'home/state';(state/'.startup-network.status').write_text('generation=1\nstate=timeout\nstarted=100\nfinished=105\nphases=probe,sweeps\nreport_published=1\nlocked=1\n');(state/'.startup-network.report').write_text('NETWORK_CHECKS: the deferred checks may be incomplete\n')
 p=run('Incomplete network report',['--json','--area','fleet','--network']);expect(status(p,'fleet/sync'),'skip');expect(status(p,'fleet/secondmate-sync'),'skip')
 for f in ['.startup-network.status','.startup-network.report']:(state/f).unlink()
check('Network opt-in reports absent disposable credentials and does not clear incomplete fleet results',network)
def snapshot():
 return {str(f.relative_to(lab/'home')):(f.stat().st_mode,hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None) for f in (lab/'home').rglob('*')}
def readonly():
 before=snapshot();run('Read-only home verification',['--json']);expect(snapshot(),before)
check('Inspect a provisioned home without changing its files or permissions',readonly)
p=run('Herdr isolated lab prepare',['prepare','fm-lab-doctor-gate'],{'FM_HERDR_LAB_STATE_DIR':str(lab/'herdr-state')},'bin/fm-herdr-lab.sh')
results.append({'name':'Report stale launcher against a real disposable Herdr session','result':'untested','reason':'Isolated HOME lab prepare exit '+str(p.returncode)+': '+p.stderr.strip()})
# No provisioning follows a failed prepare; no Herdr server or pane was created.
(evidence/'doctor-live-transcript.log').write_text('\n'.join(log));(evidence/'doctor-live-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
assert not any(r['result']=='fail' for r in results)
