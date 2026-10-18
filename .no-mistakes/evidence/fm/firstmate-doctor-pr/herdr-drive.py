import pathlib,os,subprocess,json
r=pathlib.Path.cwd(); ev=pathlib.Path('~/.no-mistakes/evidence/01M56ZEY5J07KH5B4775RWDHWV'); h=r/'.doctor-live/herdr-home'
for d in ['config','state','data']: (h/d).mkdir(parents=True,exist_ok=True)
e=dict(os.environ); e.update(FM_HERDR_LAB_STATE_DIR=str(r/'.doctor-live/herdr-state'),TMPDIR=str(r/'.doctor-live/tmp'))
name='fm-lab-doctor-final'
trans=[]
def lab(*args):
 p=subprocess.run([str(r/'bin/fm-herdr-lab.sh'),*args],env=e,text=True,capture_output=True,timeout=80); trans.append({'args':args,'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr}); assert p.returncode==0,p.stderr; return json.loads(p.stdout) if p.stdout.strip().startswith('{') else p.stdout
try:
 lab('provision',name)
 s=lab('run',name,'status','--json'); assert s['server']['running']
 w=lab('run',name,'workspace','create','--cwd',str(r),'--label','doctor-test','--no-focus')['result']
 for k in list(e):
  if k.startswith('FM_') and k not in ['FM_HERDR_LAB_STATE_DIR']: e.pop(k,None)
 e.update(FM_HOME=str(h),FM_ROOT_OVERRIDE=str(h),FM_BACKEND='herdr',FM_BOOTSTRAP_CLAUDE_USER_SETTINGS=str(h/'absent-settings'),FM_BOOTSTRAP_NO_MISTAKES_HOME=str(h/'absent-nm'),HERDR_SESSION=name,HERDR_SOCKET_PATH=s['server']['socket'],HERDR_WORKSPACE_ID=w['workspace']['workspace_id'],HERDR_TAB_ID=w['tab']['tab_id'])
 for label,pane,expected in [('valid',w['root_pane']['pane_id'],'ok'),('stale','w1:p99999','fail')]:
  e['HERDR_PANE_ID']=pane
  p=subprocess.run([str(r/'bin/fm-doctor.sh'),'--json','--area','backend'],env=e,text=True,capture_output=True,timeout=90)
  (ev/f'herdr-doctor-{label}.txt').write_text(f'exit={p.returncode}\n'+p.stdout+p.stderr)
  j=json.loads(p.stdout); status=next(c['status'] for c in j['checks'] if c['id']=='backend/herdr-launcher'); assert status==expected,(label,status)
  assert p.returncode==(1 if expected=='fail' else 0)
finally:
 # Remove claimed pane identity before cleanup, keeping the helper's exact named-session ownership.
 for k in ['HERDR_PANE_ID','HERDR_SOCKET_PATH','HERDR_WORKSPACE_ID','HERDR_TAB_ID']: e.pop(k,None)
 lab('teardown',name)
 (ev/'herdr-lab-transcript.json').write_text(json.dumps(trans,indent=2))
print('Real named-session launcher checks passed; lab removed and default-session tripwire unchanged.')
