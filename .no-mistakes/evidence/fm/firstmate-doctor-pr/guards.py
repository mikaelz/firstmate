import os,pathlib,subprocess,json
r=pathlib.Path.cwd(); h=r/'.doctor-live/guard-home'; h.mkdir(exist_ok=True); ev=pathlib.Path('~/.no-mistakes/evidence/01M56ZEY5J07KH5B4775RWDHWV')
e={k:v for k,v in os.environ.items() if not k.startswith(('FM_','HERDR_')) and k not in ['TMUX','TMUX_PANE']}; e.update(HOME=str(h),FM_HOME=str(h),FM_ROOT_OVERRIDE=str(h),TMPDIR=str(r/'.doctor-live/tmp'),FM_BOOTSTRAP_CLAUDE_USER_SETTINGS=str(h/'absent'),FM_BOOTSTRAP_NO_MISTAKES_HOME=str(h/'absent-nm'))
inv=json.loads((r/'docs/doctor-checks.json').read_text()); inv['checks'].append(inv['checks'][0]); f=h/'inventory.json'; f.write_text(json.dumps(inv)); e['FM_DOCTOR_INVENTORY']=str(f)
p=subprocess.run([str(r/'bin/fm-doctor.sh'),'--json'],env=e,text=True,capture_output=True,timeout=30); (ev/'invalid-inventory.txt').write_text(f'exit={p.returncode}\n'+p.stdout+p.stderr)
j=json.loads(p.stdout); assert p.returncode==1 and next(c['status'] for c in j['checks'] if c['id']=='doctor/inventory')=='fail'; assert all(c['area']=='doctor' for c in j['checks'])
print('Inventory guard rejects duplicate checks before running owners.')
