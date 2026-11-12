import os, pathlib, subprocess, json, time, shutil
root=pathlib.Path.cwd(); evidence=pathlib.Path('~/Dropbox/no-mistakes-evidence/01M789TVH3AK2BWP0NSPF5WCER'); lab=root/'.lab'
assert not lab.exists()
env=os.environ.copy()
for key in list(env):
    if key.startswith('FM_') and key.endswith('_OVERRIDE'): env.pop(key)
env.pop('FM_GATE_REFUSE_BYPASS',None)
def run(args, **kw):
    return subprocess.run(args,cwd=root,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60,**kw)
rows=[]
try:
    r=run(['bash','bin/fm-lab-home.sh','create',str(lab)]); assert r.returncode==0,r.stdout
    env['FM_HOME']=str(lab); env['FM_BACKEND']='tmux'
    (lab/'tmux').mkdir(); env['TMUX_TMPDIR']=str(lab/'tmux')
    def tm(*args): return run(['tmux','-L','fm-lab',*args])
    r=tm('new-session','-d','-s','firstmate','-x','120','-y','40','-c',str(root),'sleep 600'); assert r.returncode==0,r.stdout
    socket=tm('display-message','-p','-t','firstmate','#{socket_path}').stdout.strip()
    env['TMUX']=socket+',0,0'
    for kind in ['ship','scout','secondmate']:
        cases={'explicit':'auggie','raw':'auggie --model x','env':'env auggie --model x',
          'nested':'FLAG=1 nohup command -p exec -a worker env OTHER=2 auggie --model x',
          'quoted':"env '/opt/Agent Tools/bin/auggie' --model x",
          'assignment':"FLAG='two words' env -C '/opt/Agent Tools' auggie --model x",
          'redirect':'env 2>worker.log auggie --model x',
          'split':"env -S 'auggie --model x'",'search-path':'env -P /usr/bin auggie --model x',
          'compound':'cd /tmp && env auggie --model x','pipeline':'true | env auggie --model x',
          'group':'(env auggie --model x)',
          'no-evaluation':f"FLAG=$(touch '{lab}/evaluated') env auggie --model x"}
        for label,command in cases.items():
            ident=f'{kind}-{label}'
            args=['bash','bin/fm-spawn.sh',ident,str(lab/'target'),command]
            args += ['--secondmate'] if kind=='secondmate' else ['--scout'] if kind=='scout' else ['--mode','no-mistakes','--yolo','off']
            r=run(args)
            passed=r.returncode!=0 and 'auggie is verified as a primary harness only' in r.stdout and not (lab/'state'/f'{ident}.meta').exists() and not (lab/'evaluated').exists()
            rows.append(dict(scenario='refusal',kind=kind,case=label,command=command,rc=r.returncode,passed=passed,output=r.stdout))
            print(ident, 'PASS' if passed else 'FAIL',r.stdout[-300:],flush=True)
    # Config resolution uses the same real home and scripts.
    for kind in ['ship','scout','secondmate']:
        cfg=lab/'config'/('secondmate-harness' if kind=='secondmate' else 'crew-harness');cfg.write_text('auggie\n')
        ident='config-'+kind
        args=['bash','bin/fm-spawn.sh',ident,str(lab/'target')]
        args += ['--secondmate'] if kind=='secondmate' else ['--scout'] if kind=='scout' else ['--mode','no-mistakes','--yolo','off']
        r=run(args); passed=r.returncode!=0 and 'auggie is verified as a primary harness only' in r.stdout and not (lab/'state'/f'{ident}.meta').exists()
        rows.append(dict(scenario='configured',kind=kind,rc=r.returncode,passed=passed,output=r.stdout)); cfg.unlink()
    # Bare real CLI, no prompt or permission answer.
    primaryenv=env.copy()
    for k in ['NO_MISTAKES_GATE','FM_GATE_REFUSE_BYPASS']:primaryenv.pop(k,None)
    r=subprocess.run(['tmux','-L','fm-lab','new-session','-d','-s','primary','-x','120','-y','40','-c',str(root),'-e','FM_HOME='+str(lab),'auggie'],env=primaryenv,text=True,capture_output=True);assert r.returncode==0,r.stderr
    time.sleep(7)
    pid=tm('display-message','-p','-t','primary','#{pane_pid}').stdout.strip()
    capture=tm('capture-pane','-p','-t','primary').stdout
    (evidence/'auggie-pane.txt').write_text(capture)
    detect=run(['bash','bin/fm-harness.sh','ancestry-descent',pid])
    lock=run(['bash','-c','. bin/fm-session-lock-lib.sh; fm_harness_pid_alive "$1"; printf "holder_alive_rc=%s\\n" "$?"','check',pid])
    rows.append(dict(scenario='primary',pid=pid,detection=detect.stdout,lock=lock.stdout,passed='comm auggie' in detect.stdout and 'holder_alive_rc=0' in lock.stdout,output=capture))
    (evidence/'results.json').write_text(json.dumps(rows,indent=2))
finally:
    if (lab/'tmux').exists():
        r=run(['tmux','-L','fm-lab','kill-server']); print('cleanup kill-server',r.returncode,r.stdout,flush=True)
    if lab.exists():shutil.rmtree(lab)
print('RESULTS',len(rows),'FAILED',sum(not r['passed'] for r in rows))
