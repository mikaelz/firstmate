import os, pathlib, subprocess, tempfile, shutil, json, hashlib
root=pathlib.Path.cwd()
evidence=pathlib.Path('~/Dropbox/no-mistakes-evidence/01M6R3S6B9R70NPF9R370M87DV')
lab=pathlib.Path(tempfile.mkdtemp(prefix='.f6-hook-lab-',dir=root))
records=[]
env=os.environ.copy()
for key in list(env):
    if key.startswith('FM_') or key in ('GROK_AGENT','GROK_HOOK_EVENT','CLAUDE_PROJECT_DIR'):
        env.pop(key)
env.update(GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',GIT_AUTHOR_NAME='Fixture',GIT_AUTHOR_EMAIL='fixture@example.invalid',GIT_COMMITTER_NAME='Fixture',GIT_COMMITTER_EMAIL='fixture@example.invalid')
def git(*args):
    subprocess.run(['git',*map(str,args)],check=True,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
def state(home):
    return {str(p.relative_to(home)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (home/'state').rglob('*') if p.is_file()}
def run(home, name, argv, payload, task=None, code=0, silent=True):
    e=env.copy(); e.update(FM_ROOT_OVERRIDE=str(home), FM_HOME=str(home),FM_STATE_OVERRIDE=str(home/'state'), FM_CONFIG_OVERRIDE=str(home/'config'),CLAUDE_PROJECT_DIR=str(home),FM_CLAUDE_AUTOARM_SYNC_WAIT_MS='0')
    if task: e['FM_TASK_ID']=task
    before=state(home)
    p=subprocess.run(argv,input=json.dumps(payload),text=True,capture_output=True,env=e,cwd=home,timeout=20)
    after=state(home)
    rec=dict(name=name,task=task,command=argv,payload=payload,exit=p.returncode,stdout=p.stdout,stderr=p.stderr,state_unchanged=before==after)
    records.append(rec)
    print(json.dumps(rec),flush=True)
    assert p.returncode==code,(name,p.returncode,code)
    if silent: assert not p.stdout and not p.stderr and before==after,name
try:
    primary=lab/'primary'; git('init','-q',primary)
    # Use the existing tracked agent contract in a disposable repository.
    shutil.copyfile(root/'AGENTS.md', primary/'AGENTS.md')
    git('-C',primary,'add','AGENTS.md');git('-C',primary,'commit','-qm','Fixture')
    recycled=lab/'recycled';git('-C',primary,'worktree','add','-qb','recycled',recycled)
    clean=lab/'clean';git('-C',primary,'worktree','add','-qb','clean',clean)
    for home in (primary,recycled,clean):
        (home/'bin').symlink_to(root/'bin',target_is_directory=True)
        (home/'state').mkdir();(home/'config').mkdir()
        (home/'state'/'task.meta').write_text('kind=ship\n')
        # A pending notification and absent watcher make supervisor guard non-vacuous.
        (home/'state'/'.wake-queue').write_text('synthetic pending notification\n')
    (recycled/'.fm-secondmate-home').write_text('sm-recycled-1\n')
    # Positive controls: same pending work blocks a real supervisor in both shapes.
    for home in (primary,recycled):
        run(home,home.name+' supervisor Stop blocks', ['bash',str(root/'bin/fm-turnend-guard.sh'),'--claude'],{'stop_hook_active':False,'session_id':'f6-control'},code=2,silent=False)
        run(home,home.name+' supervisor delegation denies', ['bash',str(root/'bin/fm-subagent-pretool-check.sh'),'--claude'],{'tool_name':'Agent'},code=2,silent=False)
    settings=json.loads((root/'.claude/settings.json').read_text())
    stops=[h['command'] for group in settings['hooks']['Stop'] for h in group['hooks']]
    for task in ('ship-recycled','scout-recycled'):
        for active in (False,True):
            for index,cmd in enumerate(stops):
                run(recycled,f'{task} registered Stop {index}, retry={active}', ['bash','-c',cmd],{'stop_hook_active':active,'session_id':'f6-worker'},task)
        run(recycled,task+' delegation allowed',['bash',str(root/'bin/fm-subagent-pretool-check.sh'),'--claude'],{'tool_name':'Agent'},task)
    # Existing linked-worker exemption must survive without relying on FM_TASK_ID.
    for index,cmd in enumerate(stops):
        run(clean,f'clean linked worker registered Stop {index}',['bash','-c',cmd],{'stop_hook_active':False,'session_id':'f6-clean'})
    run(clean,'clean linked worker delegation allowed',['bash',str(root/'bin/fm-subagent-pretool-check.sh'),'--claude'],{'tool_name':'Agent'})
    # Guard must also honor the explicit worker identity before plain-checkout eligibility.
    run(primary,'explicit worker identity overrides plain checkout',['bash',str(root/'bin/fm-turnend-guard.sh'),'--claude'],{'stop_hook_active':False},'ship-explicit')
    print('All direct product-hook scenarios passed.')
finally:
    (evidence/'hook-results.json').write_text(json.dumps(records,indent=2)+'\n')
    shutil.rmtree(lab)
    print('Disposable repositories and state removed.')
