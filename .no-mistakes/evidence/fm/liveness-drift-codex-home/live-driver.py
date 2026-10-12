import os, pathlib, subprocess, time, json, signal
root=pathlib.Path.cwd()
evidence=pathlib.Path('/home/mike/.no-mistakes/evidence/01M4QXY2X5WJ2QTF7GGBDPFS08')
env=os.environ.copy()
env.update(TMPDIR=str(root/'.live-validation/tmp with spaces'), HOME=str(root/'.live-validation/home'))
for k in ['CODEX_HOME','FM_ROOT_OVERRIDE','FM_STATE_OVERRIDE','FM_DATA_OVERRIDE','FM_CONFIG_OVERRIDE','FM_PROJECTS_OVERRIDE']:
    env.pop(k,None)
inherited_home=root/'.live-validation/inherited-codex-home'
if os.environ.get('BASH32'):
    inherited_home.mkdir(exist_ok=True)
    (inherited_home/'sentinel').write_text('operator data surrogate: unchanged\n')
    env['CODEX_HOME']=str(inherited_home)
seen=set(); tracked={}; rows=[]
adversarial = os.environ.get("PID_REUSE") == "1"
sentinel = subprocess.Popen(["sleep", "60"]) if adversarial else None
suffix = "-pid-reuse" if adversarial else "-bash32" if os.environ.get("BASH32") else ""
with (evidence/('liveness-live'+suffix+'.log')).open('w') as log:
    command=['.live-validation/bash-build/bash-3.2/bash','tests/fm-harness-liveness-drift-live-e2e.test.sh'] if os.environ.get('BASH32') else ['bin/fm-test-run.sh','tests/fm-harness-liveness-drift-live-e2e.test.sh']
    log.write('command: '+repr(command)+'\n'); log.flush()
    proc=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
    while proc.poll() is None:
        for lab in (root/'.live-validation/tmp with spaces').glob('fm-liveness-drift.*'):
            for f in (lab/'codex-home/app-server-daemon').glob('*.pid'):
                try:
                    pid=json.loads(f.read_text())['pid']
                    if pid in seen: continue
                    p=pathlib.Path('/proc')/str(pid)
                    environ=(p/'environ').read_bytes().split(b'\0')
                    ch=[x.decode() for x in environ if x.startswith(b'CODEX_HOME=')]
                    args=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode()
                    cwd=os.readlink(p/'cwd')
                    row={'pid_file':str(f.relative_to(root)),'pid':pid,'CODEX_HOME':ch,'cwd':cwd,'args':args}
                    rows.append(row); tracked[pid]=args; seen.add(pid)
                    print(json.dumps(row),flush=True)
                    if adversarial and f.name == 'daemon-updater.pid' and 'codex app-server daemon' in args:
                        os.kill(pid,signal.SIGTERM)
                        for _ in range(100):
                            if not p.exists(): break
                            time.sleep(.01)
                        f.write_text(json.dumps({'pid':sentinel.pid},separators=(',',':')))
                        rows.append({'injected_stale_updater_pid':sentinel.pid,'unrelated_command':'sleep 60'})
                except (OSError,ValueError,KeyError): pass
        time.sleep(.02)
    rc=proc.wait()
time.sleep(2)
for pid,args in tracked.items():
    p=pathlib.Path('/proc')/str(pid)
    try: state=(p/'stat').read_text().split(') ')[1].split()[0]
    except OSError: state='absent'
    rows.append({'post_run_pid':pid,'state':state,'stopped':state in ['absent','Z']})
if sentinel:
    rows.append({'unrelated_pid':sentinel.pid,'survived_cleanup':sentinel.poll() is None})
    sentinel.terminate(); sentinel.wait()
if os.environ.get('BASH32'):
    rows.append({'inherited_CODEX_HOME':str(inherited_home),'contents_after':[p.name for p in inherited_home.iterdir()],'sentinel_unchanged':(inherited_home/'sentinel').read_text()=='operator data surrogate: unchanged\n'})
rows.append({'exit_code':rc,'remaining_labs':[str(p.relative_to(root)) for p in (root/'.live-validation/tmp with spaces').glob('fm-liveness-drift.*')]})
(evidence/('daemon-observations'+suffix+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows[-1]),flush=True)
raise SystemExit(rc)
