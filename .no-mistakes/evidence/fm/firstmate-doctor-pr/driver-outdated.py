import pathlib,os,subprocess,json
r=pathlib.Path.cwd();l=r/'.validation-doctor/live';env={'PATH':str(r/'.validation-doctor/old-tool/node_modules/.bin')+':'+os.environ['PATH'],'HOME':str(l/'user'),'TMPDIR':str(l/'tmp'),'FM_HOME':str(l/'home'),'FM_ROOT_OVERRIDE':str(l/'home'),'FM_BOOTSTRAP_NO_MISTAKES_HOME':str(l/'nm'),'FM_BOOTSTRAP_CLAUDE_USER_SETTINGS':str(l/'user/settings.json'),'FM_SUPERVISION_ACTOR':'branch','FM_SUPERVISION_PRIMARY_HARNESS':'codex'}
p=subprocess.run([str(r/'bin/fm-doctor.sh'),'--json','--area','tools'],env=env,text=True,capture_output=True,timeout=90)
pathlib.Path('~/.no-mistakes/evidence/01M5RYSKZFZY93GH9N3WG9ZXCT/outdated-live-transcript.log').write_text('Real npm release gh-axi@0.1.28 on PATH\n$ bin/fm-doctor.sh --json --area tools\nexit='+str(p.returncode)+'\n'+p.stdout+p.stderr)
j=json.loads(p.stdout);cs={c['id']:c for c in j['checks']};assert cs['tools/outdated']['status']=='fail';assert 'gh-axi' in cs['tools/outdated']['evidence'];assert cs['tools/missing']['status']=='ok';assert p.returncode==1
print('Real below-floor gh-axi is reported as tools/outdated fail, tools/missing ok, exit 1')
