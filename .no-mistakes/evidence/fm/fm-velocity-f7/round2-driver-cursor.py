exec((__import__('pathlib').Path('.live-cursor/probe.py').read_text().split('r=subprocess.run')[0]))
import time, hashlib, shutil, sys
E=pathlib.Path('~/.no-mistakes/evidence/01M5NE3CGFXBCW16A0FAHJWVYF');log=(E/'round2-cursor-live.txt').open('w')
def out(s): print(s,flush=True);log.write(s+'\n');log.flush()
def run(args,expect=0,ev=None):
 r=subprocess.run(list(map(str,args)),env=ev or env,capture_output=True,text=True)
 out('$ '+' '.join(map(str,args))+'\nexit='+str(r.returncode)+'\n'+r.stdout+r.stderr)
 if expect is not None and r.returncode!=expect:raise RuntimeError('expected '+str(expect))
 return r
lab=root/'.c';subprocess.run(['bin/fm-lab-home.sh','create',str(lab)],check=True,capture_output=True)
(lab/'t').mkdir();env.update(FM_HOME=str(lab),TMUX_TMPDIR=str(lab/'t'))
for k in ['FM_ROOT_OVERRIDE','FM_STATE_OVERRIDE','FM_DATA_OVERRIDE','FM_CONFIG_OVERRIDE','FM_PROJECTS_OVERRIDE','FM_GATE_REFUSE_BYPASS','FM_TASK_ID','REX_SESSION','REX_BLOCK']:env.pop(k,None)
# gh pr view aliases commits to statusCheckRollup, then flattens the last commit.
check={'__typename':'CheckRun','name':'test','status':'QUEUED','conclusion':''}
pr['statusCheckRollup']={'nodes':[{'commit':{'statusCheckRollup':{'contexts':{'nodes':[check]}}}}]}
url='https://github.com/acme/widget/pull/42';id='labpark';name='park-'+hashlib.sha256(id.encode()).hexdigest()[:54]
try:
 run(['gh','pr','view',url,'--json','state,headRefOid,reviewDecision,statusCheckRollup,comments,reviews'])
 run(['tmux','-L','fm-lab','new-session','-d','-s','lab','-n','fm-'+id,'-x','120','-y','40','-c',str(root)],ev={k:v for k,v in env.items() if k not in ['HTTPS_PROXY','SSL_CERT_FILE','GH_TOKEN','GH_CONFIG_DIR']})
 socket=run(['tmux','-L','fm-lab','display-message','-p','#{socket_path}']).stdout.strip()
 env['TMUX']=socket+',0,0'
 work=lab/'work';proj=lab/'proj';subprocess.run(['git','init','-b','main',str(proj)],check=True,capture_output=True);subprocess.run(['git','-C',str(proj),'-c','user.name=Lab','-c','user.email=lab@example.invalid','commit','--allow-empty','-m','fixture'],check=True,capture_output=True);subprocess.run(['git','-C',str(proj),'worktree','add','-b','labpark',str(work)],check=True,capture_output=True);(work/'uncommitted.txt').write_text('preserve this uncommitted work\n')
 (lab/'state'/f'{id}.meta').write_text(f'window=lab:fm-{id}\nendpoint_task_id={id}\nworktree={work}\nproject={proj}\nharness=cursor\nkind=scout\nmode=local-only\nyolo=off\nmodel=default\neffort=default\n')
 (lab/'data'/id).mkdir();(lab/'data'/id/'brief.md').write_text('# Task\nThis disposable test has one task: write RESUMED into resumed.txt in the current directory, then reply RESUMED. Do not run other commands or external tools.\n')
 import shlex
 run(['tmux','-L','fm-lab','send-keys','-t','lab:fm-'+id,'cd '+str(work)+' && env -u HTTPS_PROXY -u SSL_CERT_FILE '+shutil.which('cursor-agent')+' --trust --yolo --workspace '+str(work)+' '+shlex.quote('Reply READY. Do not use tools.'),'Enter'])
 time.sleep(20)
 pane=run(['tmux','-L','fm-lab','capture-pane','-p','-t','lab:fm-'+id]).stdout
 (E/'round2-cursor-before.txt').write_text(pane)
 # Exercise running-agent stop if the composer is available; preserve diagnostic if trust prevents it.
 r=run(['bin/fm-pr-park.sh','park',id,url],expect=None)
 if r.returncode:
  out('LIVE AGENT PARK BLOCKED; using a second, already-stopped endpoint for remaining park contracts.')
  # Stop only our own private server, then recreate an endpoint at the shell.
  run(['tmux','-L','fm-lab','kill-server'])
  run(['tmux','-L','fm-lab','new-session','-d','-s','lab','-n','fm-'+id,'-x','120','-y','40','-c',str(root)],ev={k:v for k,v in env.items() if k not in ['HTTPS_PROXY','SSL_CERT_FILE','GH_TOKEN','GH_CONFIG_DIR']})
  socket=run(['tmux','-L','fm-lab','display-message','-p','#{socket_path}']).stdout.strip();env['TMUX']=socket+',0,0'
  run(['bin/fm-pr-park.sh','park',id,url])
 out('PARK RECORD:\n'+(lab/'state'/f'{id}.park').read_text())
 assert (work/'uncommitted.txt').read_text()=='preserve this uncommitted work\n'
 run(['tmux','-L','fm-lab','list-windows','-t','lab'])
 run(['bin/fm-procevent.sh','list'])
 run(['bin/fm-pr-park.sh','park',id,url],1)
 run(['bin/fm-pr-park.sh','changed',id],1)
 check['status']='IN_PROGRESS';run(['bin/fm-pr-park.sh','changed',id],1)
 for field,value in [('state','MERGED'),('headRefOid','b'*40),('reviewDecision','APPROVED'),('reviews',{'nodes':[{'id':'R1'}]}),('comments',{'nodes':[{'id':'C1'}]})]:
  old=pr[field];pr[field]=value;out('API mutation: '+field);run(['bin/fm-pr-park.sh','changed',id],0);pr[field]=old
 check.update(status='COMPLETED',conclusion='SUCCESS');run(['bin/fm-pr-park.sh','changed',id],0)
 (d/'api-fail').touch();run(['bin/fm-pr-park.sh','changed',id],2);(d/'api-fail').unlink()
 # Start the actual registered event runner after changing data, so the first 300s poll fires immediately.
 run(['bin/fm-procevent.sh','reconcile'])
 result=None
 for _ in range(80):
  matches=list((lab/'state'/'procevent-inbox').glob('*.result'))
  if matches:result=matches[0];break
  time.sleep(.25)
 assert result,'runner produced no result'
 out('CAPTURED RESULT:\n'+result.read_text());run(['bin/fm-procevent-when.sh','classify',result])
 note=lab/'data'/id/'park-resume.md';out('RESUME NOTE:\n'+note.read_text());(E/'round2-park-resume.md').write_text(note.read_text())
 run(['tmux','-L','fm-lab','send-keys','-t','lab:fm-'+id,'cd '+str(work),'Enter'])
 time.sleep(1)
 # Keep the failed/blocked resumption observable; do not answer persistent trust dialogs.
 run(['bin/fm-control.sh',id,'relaunch','--note-file',note],expect=None)
 for _ in range(50):
  if (work/'resumed.txt').exists():break
  time.sleep(1)
 out('RESUMED TASK FILE: '+((work/'resumed.txt').read_text() if (work/'resumed.txt').exists() else 'MISSING'))
 pane=run(['tmux','-L','fm-lab','capture-pane','-p','-t','lab:fm-'+id]).stdout;(E/'round2-cursor-after.txt').write_text(pane)
 run(['bin/fm-pr-park.sh','unpark',id]);run(['bin/fm-pr-park.sh','unpark',id])
 assert not (lab/'state'/f'{id}.park').exists()
 seq=result.name[len('when-'+name)+1:-len('.result')]
 run(['bin/fm-procevent.sh','handled','when-'+name,seq]);run(['bin/fm-procevent.sh','handled','when-'+name,seq])
 # Guards run before worker lifecycle and must create no park record.
 run(['bin/fm-pr-park.sh','park','unknown',url],1)
 run(['bin/fm-pr-park.sh','park',id,'https://gitlab.com/acme/widget/-/merge_requests/42'],1)
 meta=lab/'state'/f'{id}.meta';original=meta.read_text();meta.write_text(original.replace('kind=scout','kind=secondmate'))
 run(['bin/fm-pr-park.sh','park',id,url],1);meta.write_text(original)
 # Bad socket endpoint forces real control to refuse and the real watch to roll back.
 meta.write_text(original.replace('window=lab:fm-'+id,'window=lab:fm-wrong'))
 run(['bin/fm-pr-park.sh','park',id,url],1)
 assert not (lab/'state'/f'{id}.park').exists()
 run(['bin/fm-procevent.sh','list'])
 meta.write_text(original)
 (d/'api-fail').touch();run(['bin/fm-pr-park.sh','park',id,url],1);(d/'api-fail').unlink()
 assert not (lab/'state'/f'{id}.park').exists()
 longid='x'*64
 longmeta=lab/'state'/f'{longid}.meta';longmeta.write_text(original.replace(id,longid))
 run(['tmux','-L','fm-lab','new-window','-t','lab','-n','fm-'+longid,'-c',str(work)])
 run(['bin/fm-pr-park.sh','park',longid,url])
 run(['bin/fm-procevent.sh','list'])
 run(['bin/fm-pr-park.sh','unpark',longid]);assert not (lab/'state'/f'{longid}.park').exists()
 # A pre-existing watch must not be replaced by a failed park registration.
 run(['bin/fm-procevent-when.sh','arm',name,'--condition',str(root/'bin/fm-pr-park.sh'),'changed',id,'--action',str(root/'bin/fm-pr-park.sh'),'resume-note',id])
 run(['bin/fm-pr-park.sh','park',id,url],1)
 assert not (lab/'state'/f'{id}.park').exists()
 run(['bin/fm-procevent-when.sh','retire',name])
 out('ALL DRIVEN CONTRACT ASSERTIONS PASSED');out('RESUME_PROOF='+str((work/'resumed.txt').exists()))
finally:
 subprocess.run(['tmux','-L','fm-lab','kill-server'],env=env,capture_output=True)
 server.shutdown();server.server_close();
 for base,dirs,files in os.walk(lab):os.chmod(base,0o700)
 shutil.rmtree(lab);out('CLEANUP: private tmux server stopped; disposable home removed');log.close()
