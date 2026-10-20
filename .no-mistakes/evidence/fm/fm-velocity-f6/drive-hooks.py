import os, pathlib, tempfile, subprocess, shutil, json, hashlib
ROOT=pathlib.Path.cwd()
E=pathlib.Path('~/.no-mistakes/evidence/01M5CYCB67YA6HX73JXW4GQKV1')
lab=pathlib.Path(tempfile.mkdtemp(prefix='.f6-hook-lab-',dir=ROOT))
records=[]
def run(args, **kw):
    return subprocess.run(args, text=True,capture_output=True,timeout=20,**kw)
def git(*args):
    p=run(['git',*map(str,args)], env={**os.environ,'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null'})
    assert p.returncode==0,p.stderr
    return p.stdout

def state(home):
    return {str(p.relative_to(home/'state')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (home/'state').rglob('*') if p.is_file()}
def hook(home,script,task=None,active=False,expected=0):
    env={k:v for k,v in os.environ.items() if not k.startswith('FM_') and k not in ('GROK_AGENT','GROK_HOOK_EVENT','CLAUDE_PROJECT_DIR')}
    env.update(FM_HOME=str(home), CLAUDE_PROJECT_DIR=str(home),FM_CLAUDE_AUTOARM_SYNC_WAIT_MS='10')
    if task is not None: env['FM_TASK_ID']=task
    command=next(h['command'] for group in json.loads((home/'.claude/settings.json').read_text())['hooks']['Stop'] for h in group['hooks'] if script in h['command']) if script!='fm-subagent-pretool-check.sh' else 'exec "$CLAUDE_PROJECT_DIR"/bin/fm-subagent-pretool-check.sh --claude'
    before=state(home)
    p=run(['bash','-c',command],cwd=home,env=env,input=json.dumps({'session_id':'f6-live-hook','stop_hook_active':active,'tool_name':'Agent'}))
    same=state(home)==before
    records.append(dict(home=home.name,hook=script,task=task,stop_hook_active=active,exit=p.returncode,stdout=p.stdout,stderr=p.stderr,state_unchanged=same))
    assert p.returncode==expected, records[-1]
    if expected==0: assert not p.stdout and not p.stderr,records[-1]
    if task and expected==0: assert same,records[-1]
try:
    base=lab/'primary'; base.mkdir()
    git('init','-q',base)
    git('-C',base,'-c','user.name=F6 lab','-c','user.email=f6@example.invalid','commit','-q','--allow-empty','-m','fixture')
    wt=lab/'recycled-worker'
    git('-C',base,'worktree','add','-q','-b','f6-lab',wt)
    for h in [base,wt]:
        shutil.copytree(ROOT/'bin',h/'bin')
        shutil.copy2(ROOT/'AGENTS.md',h/'AGENTS.md')
        (h/'.claude').mkdir(); shutil.copy2(ROOT/'.claude/settings.json',h/'.claude/settings.json')
        (h/'state').mkdir(); (h/'state/task.meta').touch()
    # Ordinary linked worker: both Stop commands remain silent.
    for script in ['fm-turnend-guard.sh','fm-claude-stop-autoarm.sh']:
        hook(wt,script,task='ship-f6')
    # Adversarial stale valid marker, repeated Stop events for ship and scout.
    (wt/'.fm-secondmate-home').write_text('sm-former-owner\n')
    for task in ['ship-f6','scout-f6']:
        for active in [False,True]:
            for script in ['fm-turnend-guard.sh','fm-claude-stop-autoarm.sh']:
                hook(wt,script,task=task,active=active)
        hook(wt,'fm-subagent-pretool-check.sh',task=task)
    # Unmarked genuine linked secondmate and plain primary stay guarded.
    for h in [wt,base]:
        hook(h,'fm-turnend-guard.sh',expected=2)
        hook(h,'fm-subagent-pretool-check.sh',expected=2)
    # Demonstrate the regression on the same disposable worker with base library.
    lib=wt/'bin/fm-primary-scope-lib.sh'; fixed=lib.read_bytes()
    lib.write_text(git('show','3eabd356abc99bdb0c1d2cefc5a1dec4a9fe39c1:bin/fm-primary-scope-lib.sh'))
    hook(wt,'fm-turnend-guard.sh',task='ship-f6',expected=2)
    records[-1]['baseline']=True
    lib.write_bytes(fixed)
    hook(wt,'fm-turnend-guard.sh',task='ship-f6')
    print('All real hook invocations matched expected output, exit status, and worker state preservation.')
finally:
    (E/'hook-transcript.json').write_text(json.dumps(records,indent=2)+'\n')
    shutil.rmtree(lab)
    print('Disposable repositories and homes removed.')
