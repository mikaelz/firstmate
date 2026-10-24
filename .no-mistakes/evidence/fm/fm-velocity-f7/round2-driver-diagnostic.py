exec((__import__('pathlib').Path('.live-park/probe.py').read_text().split('r=subprocess.run')[0]))
import time,shutil
E=pathlib.Path('~/.no-mistakes/evidence/01M5NE3CGFXBCW16A0FAHJWVYF');log=(E/'round2-park-diagnostics.txt').open('w')
def run(args,expected=0):
 r=subprocess.run(list(map(str,args)),env=env,capture_output=True,text=True)
 log.write('$ '+' '.join(map(str,args))+'\nexit='+str(r.returncode)+'\n'+r.stdout+r.stderr);log.flush()
 assert r.returncode==expected,(args,r.stdout,r.stderr)
 return r.stdout
lab=root/'.d';subprocess.run(['bin/fm-lab-home.sh','create',str(lab)],check=True,capture_output=True);env['FM_HOME']=str(lab)
for k in ['FM_ROOT_OVERRIDE','FM_STATE_OVERRIDE','FM_DATA_OVERRIDE','FM_CONFIG_OVERRIDE','FM_PROJECTS_OVERRIDE','FM_GATE_REFUSE_BYPASS']:env.pop(k,None)
pr['statusCheckRollup']={'nodes':[{'commit':{'statusCheckRollup':{'contexts':{'nodes':[{'__typename':'CheckRun','name':'test','status':'QUEUED','conclusion':''}]}}}}]}
f=lab/'state'/'diagnostic.park';f.write_text('fm-pr-park-v1\nhttps://github.com/acme/widget/pull/42\nOPEN '+'a'*40+'  0 0 test=pending\n');f.chmod(0o600)
try:
 for name,want,fail in [('api-error','condition-error',True),('deadline','never-true',False)]:
  if fail:(d/'api-fail').touch()
  args=['bin/fm-procevent-when.sh','arm',name,'--interval','0.1','--stable','1']
  if not fail:args+=['--deadline','1']
  args+=['--condition',str(root/'bin/fm-pr-park.sh'),'changed','diagnostic','--action',str(root/'bin/fm-pr-park.sh'),'resume-note','diagnostic']
  run(args);run(['bin/fm-procevent.sh','reconcile'])
  result=lab/'state'/'procevent-inbox'/('when-'+name+'.1.result')
  for _ in range(100):
   if result.exists():break
   time.sleep(.1)
  assert result.exists()
  log.write('CAPTURED RESULT:\n'+result.read_text());log.flush()
  assert run(['bin/fm-procevent-when.sh','classify',result]).strip()==want
  assert not (lab/'data'/'diagnostic'/'park-resume.md').exists(),'non-fired result must not create a resume note'
  run(['bin/fm-procevent.sh','handled','when-'+name,'1']);run(['bin/fm-procevent-when.sh','retire',name])
  if fail:(d/'api-fail').unlink()
 run(['bin/fm-procevent.sh','list'])
 log.write('OBSERVED: neither API failure nor deadline ran the resume-note action. Park record retained.\n')
finally:
 server.shutdown();server.server_close();shutil.rmtree(lab);log.write('CLEANUP: API endpoint stopped; disposable home removed.\n');log.close()
