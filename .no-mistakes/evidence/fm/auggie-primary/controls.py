import os,pathlib,subprocess,json,shutil
root=pathlib.Path.cwd(); lab=root/'.lab'; out=pathlib.Path('~/Dropbox/no-mistakes-evidence/01M789TVH3AK2BWP0NSPF5WCER');assert not lab.exists()
e=os.environ.copy()
for k in list(e):
 if (k.startswith('FM_') and k.endswith('_OVERRIDE')) or k=='FM_GATE_REFUSE_BYPASS':e.pop(k)
def run(args):return subprocess.run(args,env=e,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
rows=[]
try:
 r=run(['bash','bin/fm-lab-home.sh','create',str(lab)]); assert r.returncode==0,r.stdout
 e['FM_HOME']=str(lab);e['FM_BACKEND']='tmux';(lab/'tmux').mkdir();e['TMUX_TMPDIR']=str(lab/'tmux')
 r=run(['tmux','-L','fm-lab','new-session','-d','-s','firstmate','-x','120','-y','40','sleep 600']);assert r.returncode==0,r.stdout
 e['TMUX']=run(['tmux','-L','fm-lab','display-message','-p','-t','firstmate','#{socket_path}']).stdout.strip()+',0,0'
 target=root/'.lab-target';assert not target.exists();target.mkdir()
 for label,command in {
 'argument':'env true auggie --model x',
 'unset-variable':"env -u 'auggie' BAR='two words' 'true' auggie --model x",
 'redirect-target':f'env 2>{lab}/auggie true auggie --model x',
 'split-other':"env -S 'true auggie --model x'",
 'compound-other':f'cd {lab} && env true auggie --model x',
 'search-other':'env -P /opt/auggie true auggie --model x'
 }.items():
  r=run(['bash','bin/fm-spawn.sh','control-'+label,str(target),command,'--secondmate'])
  rows.append(dict(command=command,rc=r.returncode,output=r.stdout,passed='secondmate home cannot be inside the firstmate repo:' in r.stdout and 'primary harness only' not in r.stdout))
  print(label,r.returncode,r.stdout,flush=True)
 (out/'controls.json').write_text(json.dumps(rows,indent=2))
finally:
 if (lab/'tmux').exists():
  r=run(['tmux','-L','fm-lab','kill-server']);print('kill-server rc',r.returncode)
 if lab.exists():shutil.rmtree(lab)
 if (root/'.lab-target').exists():shutil.rmtree(root/'.lab-target')
print('FAILED',sum(not r['passed'] for r in rows))
