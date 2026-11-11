import os, pathlib, subprocess, json, shutil, hashlib
root=pathlib.Path.cwd(); evidence=pathlib.Path('~/Dropbox/no-mistakes-evidence/01M74WBY8EPPJVWYM9RG34D7ZM'); lab=root/'.doctor-live'
lab.mkdir(exist_ok=False)
base={k:v for k,v in os.environ.items() if not k.startswith(('FM_','HERDR_','CMUX_','CLAUDE_','CODEX_','TASKS_AXI_')) and k not in ('TMUX','TMUX_PANE','GH_TOKEN','GITHUB_TOKEN','GH_ENTERPRISE_TOKEN','GITHUB_ENTERPRISE_TOKEN','NM_HOME')}
base.update(HOME=str(lab/'user'),XDG_CONFIG_HOME=str(lab/'user/config'),GH_CONFIG_DIR=str(lab/'user/gh'),FM_BOOTSTRAP_NO_MISTAKES_HOME=str(lab/'nm'),FM_BOOTSTRAP_CLAUDE_USER_SETTINGS=str(lab/'settings.json'),FM_BACKEND='tmux')
(lab/'user').mkdir(); (lab/'nm').mkdir(); (lab/'settings.json').write_text('{}')
results=[]
def home(name):
 p=lab/name
 for d in ('state','data','config','projects'): (p/d).mkdir(parents=True,exist_ok=True)
 return p
h=home('home')
def run(label,args=(),extra=None,target=h,expected=None):
 env=base|dict(FM_HOME=str(target),FM_ROOT_OVERRIDE=str(target),FM_SUPERVISION_ACTOR='branch',FM_SUPERVISION_PRIMARY_HARNESS='codex')|(extra or {})
 p=subprocess.run([str(root/'bin/fm-doctor.sh'),*args],env=env,cwd=root,capture_output=True,text=True,timeout=100)
 (evidence/(label+'.stdout')).write_text(p.stdout); (evidence/(label+'.stderr')).write_text(p.stderr)
 print(label,'exit',p.returncode,flush=True)
 if expected is not None: assert p.returncode==expected,(label,p.returncode)
 return json.loads(p.stdout) if '--json' in args else p

def status(m,id,want):
 c=next(c for c in m['checks'] if c['id']==id); assert c['status']==want,(id,c,want)
def snap(p):
 return {str(f.relative_to(p)):(f.stat().st_mode,hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else 'dir') for f in p.rglob('*')}
try:
 before=snap(h)
 m=run('full-json',['--json']); toon=run('full-toon')
 assert m['schema']=='fm-doctor.v1' and 'verdict: '+m['verdict'] in toon.stdout
 status(m,'auth/github','skip'); status(m,'config/startup-memory-budget','skip')
 area=run('tools-area',['--json','--area','tools']); assert {c['area'] for c in area['checks']} <= {'doctor','tools'}
 run('bad-area',['--area','no-such-area'],expected=2); run('bad-option',['--unknown'],expected=2); run('missing-area',['--area'],expected=2); run('help',['--help'],expected=0)
 assert before==snap(h),'doctor mutated an existing home'
 results.append('Output, area filtering, usage errors, skipped checks, and existing-home read-only: PASS')
 for adapter in ('codex','cortex','hermes','kiro','bogus'):
  (h/'config/crew-harness').write_text(adapter+'\n')
  a=run('harness-'+adapter,['--json','--area','config'])
  status(a,'config/crew-harness','warn' if adapter=='bogus' else 'ok')
  if adapter!='kiro' and adapter!='bogus':
   a=run('own-'+adapter,['--json','--area','config'],{'FM_SUPERVISION_PRIMARY_HARNESS':adapter}); status(a,'config/harness','ok')
 (h/'config/crew-harness').unlink()
 (h/'config/backend').write_text('bogus\n')
 # Explicit FM_BACKEND wins, so remove it for the configured-backend proof.
 saved=base.pop('FM_BACKEND'); a=run('invalid-backend',['--json','--area','backend']); status(a,'backend/invalid','fail'); base['FM_BACKEND']=saved; (h/'config/backend').unlink()
 (h/'config/crew-dispatch.json').write_text('{"rules":[')
 status(run('invalid-dispatch',['--json','--area','config']),'config/crew-dispatch','fail'); (h/'config/crew-dispatch.json').unlink()
 results.append('Supported crew adapters (including cortex, kiro, hermes), unsupported adapter, invalid backend and dispatch: PASS')
 for i,yaml in enumerate(('agent: missing-live-doctor-agent\n','agent: [codex, missing-live-doctor-agent]\n','agent: # fallback order\n- codex\n- missing-live-doctor-agent\n','agent:\n  - codex\n  - missing-live-doctor-agent\n')):
  (lab/'nm/config.yaml').write_text(yaml); a=run('agent-yaml-'+str(i),['--json','--area','no-mistakes']); status(a,'no-mistakes/agents','warn'); assert 'missing-live-doctor-agent' in str(a['checks'])
 (lab/'nm/config.yaml').write_text('agent: auto\n'); status(run('agent-auto',['--json','--area','no-mistakes']),'no-mistakes/agents','ok')
 results.append('Detect missing fallback executables from scalar, flow, indented and commented unindented YAML lists: PASS')
 for label,mode,allow,want in [('auto-no-rule','auto',[],'warn'),('auto-single','auto',['Bash(bin/fm-doctor.sh:*)'],'warn'),('auto-family','auto',['Bash(bin/fm-*:*)'],'ok'),('default','default',[],'ok')]:
  (lab/'settings.json').write_text(json.dumps({'permissions':{'defaultMode':mode,'allow':allow}}))
  status(run('permissions-'+label,['--json','--area','permissions'],{'FM_SUPERVISION_PRIMARY_HARNESS':'claude'}),'permissions/claude-fm-scripts',want)
 (lab/'settings.json').write_text('{}'); results.append('Claude auto-mode settings warning and family allow-rule boundary using synthetic settings: PASS')
 (h/'config/tool-provenance').write_text('jq '+str(lab/'expected-build')+'/\n')
 status(run('provenance-wrong',['--json','--area','tools']),'tools/provenance','warn')
 (h/'config/tool-provenance').write_text('jq '+str(pathlib.Path(shutil.which('jq')).resolve().parent)+'/\n')
 status(run('provenance-correct',['--json','--area','tools']),'tools/provenance','ok'); (h/'config/tool-provenance').unlink()
 results.append('Real jq provenance mismatch and matching installation: PASS')
 status(run('memory-absent',['--json','--area','memory']),'memory/budget','info')
 (h/'config/startup-memory-budget').write_text('invalid\n'); status(run('memory-invalid',['--json','--area','memory']),'memory/budget','warn')
 (h/'config/startup-memory-budget').write_text('1\n')
 for n,text in [('within','abc'),('over','abcd')]:
  (h/'data/captain-shared.md').write_text(text); status(run('memory-'+n,['--json','--area','memory']),'memory/budget','ok' if n=='within' else 'warn')
 results.append('Missing, malformed, exact-boundary and exceeded memory budgets: PASS')
 a=run('network-no-login',['--json','--network','--area','auth'],expected=1); status(a,'auth/github','fail')
 results.append('Opt-in real gh auth probe in credential-free disposable home reports failure: PASS')
 # Synthetic installed executable models an outdated external tool, not the product.
 (lab/'tools').mkdir(); shim=lab/'tools/gh-axi'; shim.write_text('#!/bin/sh\nprintf "0.1.0\\n"\n'); shim.chmod(0o755)
 a=run('outdated-tool',['--json','--area','tools'],{'PATH':str(lab/'tools')+':'+base['PATH']},expected=1); status(a,'tools/outdated','fail'); assert not any(c['id']=='doctor/unmapped-line' and c['status']=='fail' for c in a['checks'])
 results.append('Real doctor classifies synthetic below-floor external gh-axi as tools/outdated: PASS')
 (evidence/'manual-results.txt').write_text('\n'.join(results)+'\n')
finally:
 shutil.rmtree(lab)
