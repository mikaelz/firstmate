import os,subprocess,pathlib,json
root=pathlib.Path.cwd(); lab=root/'.live-auggie/home'
env=os.environ.copy()
for k in ['FM_ROOT_OVERRIDE','FM_STATE_OVERRIDE','FM_DATA_OVERRIDE','FM_CONFIG_OVERRIDE','FM_PROJECTS_OVERRIDE','FM_GATE_REFUSE_BYPASS','HERDR_ENV','HERDR_PANE_ID','HERDR_TAB_ID','HERDR_WORKSPACE_ID','HERDR_SOCKET_PATH','HERDR_SESSION','TMUX']:
    env.pop(k,None)
env.update(FM_HOME=str(lab),FM_BACKEND='tmux',FM_SPAWN_NO_GUARD='1')
forms=[
'auggie --model x','env auggie --model x','command -p auggie --model x','exec -a worker auggie --model x','nohup auggie --model x','sudo -n -u worker auggie --model x','timeout -s TERM 1h auggie --model x',
'FOO=1 env BAR=2 auggie --model x',"env '/opt/Agent Tools/bin/auggie' --model x",'env /opt/Agent\\ Tools/bin/auggie --model x','env 2>worker.log auggie --model x','2>worker.log env auggie --model x',
'env --default-signal auggie --model x','env --default-signal=INT auggie --model x','env --block-signal auggie --model x','env --ignore-signal auggie --model x',
'env - /opt/tools/bin/auggie --model x','env -- - /opt/tools/bin/auggie --model x','env - sudo auggie --model x',
'sudo FOO=1 -n auggie --model x','sudo FOO=1 -n BAR=2 --no-update auggie --model x','sudo -a passwd auggie --model x','sudo -c staff auggie --model x',
"env -C '/opt/Agent Tools' auggie --model x",'env -i -u CLAUDECODE PATH=/usr/bin auggie --model x',"env -S 'auggie --model x'", "env --split-string='auggie --model x'",
'FOO=1 nohup command -p exec -a worker env BAR=2 auggie --model x','cd /tmp && env auggie --model x','(env auggie --model x)',
'FOO=$(touch .live-auggie/EVALUATED) env auggie --model x']
failures=[]
for kind,flags in [('ship',['--mode','no-mistakes','--yolo','off']),('scout',['--scout']),('secondmate',['--secondmate'])]:
    for how,raw in [('config',None),('explicit','auggie')]+[('raw',f) for f in forms]:
        config=lab/'config'/('secondmate-harness' if kind=='secondmate' else 'crew-harness')
        if how=='config': config.write_text('auggie\n')
        args=['bin/fm-spawn.sh','live-refusal',str(lab)]+([] if raw is None else [raw])+flags
        p=subprocess.run(args,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20)
        print(f'\n$ {kind} {how}: {raw or "config=auggie"}\nexit={p.returncode}\n{p.stdout}',flush=True)
        if p.returncode==0 or 'auggie is verified as a primary harness only' not in p.stdout or (lab/'state/live-refusal.meta').exists(): failures.append((kind,how,raw,p.returncode))
        config.unlink(missing_ok=True)
assert not (root/'.live-auggie/EVALUATED').exists(), 'Parser executed command substitution'
print('\nNo worker metadata or substitution side effects created.')
print('Failures:',json.dumps(failures))
raise SystemExit(bool(failures))
