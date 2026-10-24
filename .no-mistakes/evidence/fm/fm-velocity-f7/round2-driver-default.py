exec((__import__('pathlib').Path('.live-park/probe.py').read_text().split('r=subprocess.run')[0]))
import time,shutil
E=pathlib.Path('~/.no-mistakes/evidence/01M5NE3CGFXBCW16A0FAHJWVYF');log=(E/'round2-default-home.txt').open('w')
def run(args,expected=0):
 r=subprocess.run(list(map(str,args)),env=env,capture_output=True,text=True)
 log.write('$ '+' '.join(map(str,args))+'\nexit='+str(r.returncode)+'\n'+r.stdout+r.stderr);log.flush()
 assert r.returncode==expected,(args,r.stdout,r.stderr)
 return r.stdout
lab=root/'.f';subprocess.run(['bin/fm-lab-home.sh','create',str(lab)],check=True,capture_output=True);env['FM_HOME']=str(lab)
for k in ['FM_ROOT_OVERRIDE','FM_STATE_OVERRIDE','FM_DATA_OVERRIDE','FM_CONFIG_OVERRIDE','FM_PROJECTS_OVERRIDE','FM_GATE_REFUSE_BYPASS']:env.pop(k,None)
pr['statusCheckRollup']={'nodes':[{'commit':{'statusCheckRollup':{'contexts':{'nodes':[{'__typename':'CheckRun','name':'test','status':'QUEUED','conclusion':''}]}}}}]}

import hashlib
try:
 shutil.copytree(root/'bin',lab/'bin')
 (lab/'t').mkdir();env['TMUX_TMPDIR']=str(lab/'t')
 run(['tmux','-L','fm-lab','new-session','-d','-s','defaultproof','-n','fm-defaultproof','-x','120','-y','40','-c',str(root)])
 socket=run(['tmux','-L','fm-lab','display-message','-p','#{socket_path}']).strip();env['TMUX']=socket+',0,0'
 subprocess.run(['git','init','-b','main',str(lab/'work')],check=True,capture_output=True)
 (lab/'state/defaultproof.meta').write_text('worktree='+str(lab/'work')+'\nproject='+str(lab/'work')+'\n'+'kind=scout\nharness=codex\nwindow=defaultproof:fm-defaultproof\nendpoint_task_id=defaultproof\n')
 env.pop('FM_HOME')
 run([lab/'bin/fm-pr-park.sh','park','defaultproof','https://github.com/acme/widget/pull/42'])
 assert (lab/'state/defaultproof.park').exists()
 run([lab/'bin/fm-pr-park.sh','unpark','defaultproof'])
 log.write('OBSERVED: FM_HOME unset; real control accepted the resolved default marked lab home.\n')
finally:
 subprocess.run(['tmux','-L','fm-lab','kill-server'],env=env,capture_output=True)
 server.shutdown();server.server_close();shutil.rmtree(lab);log.write('CLEANUP: endpoint and disposable home removed.\n');log.close()
