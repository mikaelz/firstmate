import os,pathlib,subprocess,shutil,hashlib
root=pathlib.Path.cwd();lab=root/'.e';E=pathlib.Path('~/.no-mistakes/evidence/01M5NE3CGFXBCW16A0FAHJWVYF');log=(E/'round2-park-teardown-live.txt').open('w')
env=os.environ.copy()
for k in ['FM_ROOT_OVERRIDE','FM_STATE_OVERRIDE','FM_DATA_OVERRIDE','FM_CONFIG_OVERRIDE','FM_PROJECTS_OVERRIDE','FM_GATE_REFUSE_BYPASS','FM_TASK_ID','REX_SESSION','REX_BLOCK']:env.pop(k,None)
def run(args,expected=0):
 r=subprocess.run(list(map(str,args)),env=env,capture_output=True,text=True);log.write('$ '+' '.join(map(str,args))+'\nexit='+str(r.returncode)+'\n'+r.stdout+r.stderr);log.flush();assert r.returncode==expected,(r.stdout,r.stderr);return r.stdout
run(['bin/fm-lab-home.sh','create',lab]);(lab/'t').mkdir();env.update(FM_HOME=str(lab),TMUX_TMPDIR=str(lab/'t'))
try:
 run(['tmux','-L','fm-lab','new-session','-d','-s','cleanup','-n','fm-cleanup','-x','120','-y','40','-c',str(root)])
 socket=run(['tmux','-L','fm-lab','display-message','-p','#{socket_path}']).strip();env['TMUX']=socket+',0,0'
 # Recovered task with a vanished workspace: teardown must retire its still-registered PR wait.
 (lab/'state'/'cleanup.meta').write_text(f'kind=ship\nharness=codex\nmode=local-only\nwindow=cleanup:fm-cleanup\nendpoint_task_id=cleanup\nworktree={lab}/vanished-work\nproject={lab}/vanished-project\n')
 (lab/'state'/'cleanup.park').write_text('fm-pr-park-v1\nhttps://github.com/acme/widget/pull/42\nOPEN abc 0 0 test=pending\n');(lab/'state'/'cleanup.park').chmod(0o600)
 name='park-'+hashlib.sha256(b'cleanup').hexdigest()[:54]
 run(['bin/fm-procevent-when.sh','arm',name,'--interval','300','--stable','1','--condition',root/'bin/fm-pr-park.sh','changed','cleanup','--action',root/'bin/fm-pr-park.sh','resume-note','cleanup'])
 run(['bin/fm-teardown.sh','cleanup'])
 assert not (lab/'state'/'cleanup.park').exists()
 assert not (lab/'state'/'cleanup.meta').exists()
 run(['bin/fm-procevent.sh','list'])
 log.write('OBSERVED: task metadata, park record and registered wait all removed.\n')
finally:
 r=subprocess.run(['tmux','-L','fm-lab','kill-server'],env=env,capture_output=True,text=True);log.write('private tmux kill-server exit='+str(r.returncode)+'\n')
 for base,dirs,files in os.walk(lab):os.chmod(base,0o700)
 shutil.rmtree(lab);log.write('CLEANUP: disposable home removed.\n');log.close()
