import os,subprocess,pathlib,shlex,time
root=pathlib.Path.cwd(); local=root/'.live-auggie'; lab=local/'home'
real=subprocess.check_output(['which','auggie'],text=True).strip()
(local/'Agent Tools').mkdir(exist_ok=True)
link=local/'Agent Tools/auggie'; link.symlink_to(real)
preload=str(local/'preload.cjs')
cases=[('require',['--require',preload]),('require-equals',['--require='+preload]),('underscore',['--unhandled_rejections','warn']),('dash-equals',['--unhandled-rejections=warn'])]
tmux=['tmux','-S','.live-auggie/socket']
for name,opts in cases:
    cmd=['node']+opts+[str(link),'--no-session','--no-extensions','--no-skills','--no-rules','--no-cloud','--offline']
    subprocess.run(tmux+['new-window','-d','-n',name,'-c',str(root),shlex.join(cmd)],check=True)
    pid=subprocess.check_output(tmux+['display-message','-p','-t','primary:'+name,'#{pane_pid}'],text=True).strip()
    try:
        time.sleep(3)
        comm=subprocess.check_output(['ps','-o','comm=','-p',pid],text=True).strip()
        args=subprocess.check_output(['ps','-o','args=','-p',pid],text=True).strip()
        print(f'\nActual Auggie launch: {shlex.join(cmd)}\npid={pid} comm={comm}\nargs={args}',flush=True)
        got=subprocess.check_output(['bin/fm-harness.sh','ancestry',pid],text=True).strip()
        print('Public ancestry:',got,flush=True)
        assert got=='comm auggie',got
        for mode in ['proc','flattened']:
            command='. bin/fm-auggie-lib.sh; fm_auggie_process_matches "$1" "$2" "$3"; result=$?; printf "identity exit=%s\\n" "$result"; exit "$result"'
            p=subprocess.run(['bash','-c',command,'check',comm,args,pid if mode=='proc' else ''],text=True,capture_output=True)
            print(mode+': '+p.stdout.strip(),flush=True)
            assert p.returncode==0,p.stderr
        p=subprocess.run(['bash','-c','. bin/fm-session-lock-lib.sh; fm_harness_pid_alive "$1" && echo "live lock holder recognized"','check',pid],text=True,capture_output=True)
        print(p.stdout.strip(),flush=True); assert p.returncode==0,p.stderr
    finally:
        subprocess.run(tmux+['kill-window','-t','primary:'+name],check=True)
# Real Node programs outside the Auggie package are adversarial inputs, not substitute harnesses.
for name in ['auggie','ordinary.mjs']:
    p=subprocess.Popen(['node',str(local/name)])
    try:
        time.sleep(.2)
        got=subprocess.check_output(['bin/fm-harness.sh','ancestry',str(p.pid)],text=True).strip()
        status=subprocess.run(['bash','-c','. bin/fm-auggie-lib.sh; fm_auggie_process_matches node "$1" "$2"','check','node '+str(local/name),str(p.pid)])
        print(f'\nNon-package Node program {name}: public ancestry={got!r}; Auggie identity exit={status.returncode}',flush=True)
        assert 'auggie' not in got and status.returncode!=0
    finally:
        p.terminate(); p.wait(timeout=5)
print('\nAll real Node option and non-package boundaries behaved as required.')
