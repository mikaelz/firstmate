import os, pathlib, subprocess, tempfile, json, shutil
root=pathlib.Path.cwd()
lab=pathlib.Path(tempfile.mkdtemp(prefix='parity.',dir=root/'.test-phase-tmp'))
axi='/home/mike/github/kunchenguid/firstmate/data/fm-gitlab-compat/dependency/node_modules/.bin/tasks-axi'
env={k:v for k,v in os.environ.items() if not k.startswith('FM_') and k not in ('TASKS_AXI_FILE','TASKS_AXI_BACKEND')}
env.update(TASKS_AXI_BACKEND='markdown',TASKS_AXI_FILE=str(lab/'backlog.md'))
base='https://gitlab.example.test/group/sub/project/-/merge_requests'
valid=['https://gitlab.com/group/project/-/merge_requests/7',base+'/780','https://github.com/o/r/pull/7','https://forgejo.example.test/o/r/pulls/7']
invalid=[base+x for x in ['/0','/0780','/780junk','/780/','/780?x=1','/780#x','/780\n','/780\x01']]+[' '+base+'/780','http://gitlab.com/o/r/-/merge_requests/7','https://Gitlab.com/o/r/-/merge_requests/7','https://user@gitlab.com/o/r/-/merge_requests/7','https://gitlab.com:443/o/r/-/merge_requests/7','https://gitlab.com/o%2Fr/r/-/merge_requests/7','https://gitlab.com/o/../r/-/merge_requests/7','https://gitlab.com/o//r/-/merge_requests/7','https://gitlab.com/o/-/r/-/merge_requests/7','https://gitlab.com/o/-repo/-/merge_requests/7','https://gitlab.com/o/r.git/-/merge_requests/7','https://github.com/o/r/-/merge_requests/7','https://github.com/o/r/pulls/7','https://forgejo.example.test/o/r/pull/7','https://gitlab.com/o/r/-/issues/7']
try:
 subprocess.run([axi,'add','parity-test','private URL validation'],env=env,cwd=lab,check=True,capture_output=True)
 before=(lab/'backlog.md').read_bytes()
 receipts=[]
 for expected,urls in [(True,valid),(False,invalid)]:
  for url in urls:
   shell=subprocess.run(['bash','-c','. "$1/bin/fm-public-followup-lib.sh"; fm_pf_pr_url_valid "$2"','_',str(root),url],env=env,cwd=lab,capture_output=True,text=True)
   consumer=subprocess.run([axi,'update','parity-test','--pr',url,'--dry-run','--json'],env=env,cwd=lab,capture_output=True,text=True)
   assert (shell.returncode==0)==expected,(url,shell)
   assert (consumer.returncode==0)==expected,(url,consumer.stdout,consumer.stderr)
   assert (lab/'backlog.md').read_bytes()==before
   receipts.append(dict(url=url,firstmate_accepts=shell.returncode==0,consumer_accepts=consumer.returncode==0,consumer_response=consumer.stdout or consumer.stderr))
 print(json.dumps({'absolute_consumer':axi,'preview_did_not_mutate_backlog':True,'receipts':receipts},indent=2))
finally:
 shutil.rmtree(lab)
