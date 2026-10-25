import pathlib,os,subprocess,json
r=pathlib.Path.cwd();lab=r/'.validation-doctor/live';e={'PATH':os.environ['PATH'],'HOME':str(lab/'user'),'TMPDIR':str(lab/'tmp'),'FM_HOME':str(lab/'home'),'FM_ROOT_OVERRIDE':str(lab/'home'),'FM_SUPERVISION_ACTOR':'branch','FM_SUPERVISION_PRIMARY_HARNESS':'codex'}
log=[]
for args in [[],['--json']]:
 p=subprocess.run([str(r/'bin/fm-bearings-snapshot.sh'),*args],env=e,text=True,capture_output=True,timeout=90);log.append(f'$ bin/fm-bearings-snapshot.sh {" ".join(args)}\nexit={p.returncode}\n{p.stdout}{p.stderr}');assert p.returncode==0
 if args: assert isinstance(json.loads(p.stdout),dict)
 else: assert 'schema:' in p.stdout
pathlib.Path('~/.no-mistakes/evidence/01M5RYSKZFZY93GH9N3WG9ZXCT/bearings-live-transcript.log').write_text('\n'.join(log))
print('Bearings TOON and JSON rendered successfully')
