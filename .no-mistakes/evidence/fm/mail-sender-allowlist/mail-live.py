import os, sys, pathlib, tempfile, shutil, ssl, socketserver, threading, subprocess, json, re
ROOT=pathlib.Path.cwd()
E=pathlib.Path('/home/mike/.no-mistakes/evidence/01M4N9DY51RSN2FJKTDEXARH3E')
lab=pathlib.Path(tempfile.mkdtemp(prefix='.mail-live-',dir=ROOT))
trans=[]; results=[]; messages={}; failures=set(); requests=[]
class IMAP(socketserver.StreamRequestHandler):
 def handle(self):
  def send(s): self.wfile.write(s.encode() if isinstance(s,str) else s); self.wfile.flush()
  send('* OK disposable IMAP ready\r\n')
  while True:
   line=self.rfile.readline().decode().strip()
   if not line: break
   tag,cmd,*args=line.split(' ',2); cmd=cmd.upper(); arg=args[0] if args else ''
   if cmd!='LOGIN': requests.append(line)
   if cmd=='CAPABILITY': send('* CAPABILITY IMAP4rev1\r\n'+tag+' OK capability\r\n')
   elif cmd=='LOGIN': send(tag+' OK login\r\n')
   elif cmd=='SELECT': send('* FLAGS (\\Seen)\r\n* '+str(len(messages))+' EXISTS\r\n* OK [UIDVALIDITY 12345] generation\r\n'+tag+' OK [READ-WRITE] selected\r\n')
   elif cmd=='UID':
    action,*rest=arg.split(' ',1); tail=rest[0] if rest else ''
    if action.upper()=='SEARCH': send('* SEARCH '+ ' '.join(map(str,messages))+'\r\n'+tag+' OK search\r\n')
    elif action.upper()=='FETCH':
     uid=int(tail.split()[0])
     if uid in failures: send(tag+' NO temporarily unfetchable\r\n')
     else:
      body=messages[uid]; send('* 1 FETCH (UID '+str(uid)+' BODY[] {'+str(len(body))+'}\r\n'); send(body); send(')\r\n'+tag+' OK fetch\r\n')
    else: send(tag+' BAD unexpected UID command\r\n')
   elif cmd=='LOGOUT': send('* BYE goodbye\r\n'+tag+' OK logout\r\n'); break
   else: send(tag+' BAD unexpected command\r\n')
class Server(socketserver.ThreadingTCPServer):
 allow_reuse_address=True; daemon_threads=True
 def get_request(self):
  sock,addr=super().get_request(); return ctx.wrap_socket(sock,server_side=True),addr

def msg(fr,subject):
 return ((('From: '+fr+'\r\n') if fr is not None else '')+'Date: Sun, 11 Oct 2026 12:00:00 +0000\r\nSubject: '+subject+'\r\n\r\n'+subject+' body\r\n').encode()
def contents(home,name):
 p=home/'state'/name; return p.read_text() if p.exists() else ''
def home(name,allow=None):
 h=lab/name; h.mkdir(); text=f'FM_MAIL_USER=fixture@example.test\nFM_MAIL_PASS=disposable-password\nFM_IMAP_HOST=localhost\nFM_IMAP_PORT={server.server_address[1]}\nFM_SMTP_HOST=localhost\n'
 if allow is not None: text+='FM_MAIL_SOURCE_ALLOW="'+allow+'"\n'
 (h/'.env').write_text(text); return h
def run(h,command,extra=None):
 env={k:v for k,v in os.environ.items() if not k.startswith(('FM_','FMX_')) and k not in ('STATE','SSL_CERT_FILE')}
 env.update(FM_HOME=str(h),SSL_CERT_FILE=str(lab/'cert.pem'),FM_MAIL_TIMEOUT='4')
 if extra: env.update(extra)
 p=subprocess.run([str(ROOT/'bin/fm-mail.sh'),command],env=env,text=True,capture_output=True,timeout=30)
 trans.append(f'$ FM_HOME=<disposable {h.name}> bin/fm-mail.sh {command}\nexit: {p.returncode}\n{p.stdout}{p.stderr}')
 return p

def scenario(name,fn):
 start=len(trans)
 try: fn(); status='pass'; reason=''
 except Exception as ex: status='fail'; reason=str(ex)
 results.append(dict(name=name,result=status,live=True,evidence='mail-live-transcript.txt: '+name,reason=reason))
 trans.insert(start,'SCENARIO: '+name)
 trans.append('RESULT: '+status+' '+reason+'\n')
try:
 subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(lab/'key.pem'),'-out',str(lab/'cert.pem'),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost'],check=True,capture_output=True)
 ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.load_cert_chain(lab/'cert.pem',lab/'key.pem')
 server=Server(('127.0.0.1',0),IMAP);threading.Thread(target=server.serve_forever,daemon=True).start()
 def matching():
  messages.clear(); failures.clear()
  senders=['Alice <ALICE@NEVILLEWEB.SK>','username@gmail.com','Username@IM3.SK','other@gmail.com','evil@sub.nevilleweb.sk','evil@nevilleweb.sk.evil.test','"username@gmail.com" <evil@evil.test>','username@gmail.com, evil@evil.test',None,'invalid','username@gmail.com\r\nFrom: evil@evil.test']
  messages.update({i:msg(fr,f'message-{i}') for i,fr in enumerate(senders,1)})
  h=home('matching',' @nevilleweb.sk, username@gmail.com, username@im3.sk ')
  p=run(h,'read'); assert p.returncode==0
  for i in (1,2,3): assert f'Subj: message-{i}\n' in p.stdout
  for i in range(4,12): assert f'Subj: message-{i}\n' not in p.stdout
  assert '8 unseen message(s)' in p.stdout
  p=run(h,'poll'); assert p.returncode==0
  q=contents(h,'.wake-queue'); trans.append('Persisted wake queue:\n'+q)
  assert len(q.splitlines())==3
  for i in (1,2,3): assert f'check: mail {i} ' in q
  for i in range(4,12): assert f'message-{i}' not in q+p.stdout
  before=q; p=run(h,'poll'); assert p.returncode==0 and contents(h,'.wake-queue')==before
  p=run(h,'poll',{'FM_MAIL_SOURCE_ALLOW':'@gmail.com,@nevilleweb.sk,@im3.sk,@evil.test'}); assert p.returncode==0 and contents(h,'.wake-queue')==before
 scenario('Read and poll allow exact addresses/domains; hostile headers stay redacted and never re-wake',matching)
 def disabled():
  messages.clear(); messages[1]=msg('outsider@evil.test','unfiltered'); failures.clear()
  for name,allow in [('unset',None),('blank','   ')]:
   h=home(name,allow); p=run(h,'read'); assert p.returncode==0 and 'Subj: unfiltered' in p.stdout
   p=run(h,'poll'); assert p.returncode==0 and 'check: mail 1 ' in contents(h,'.wake-queue')
 scenario('Unset or blank allow list preserves all-sender read and wake behavior',disabled)
 def malformed():
  for i,allow in enumerate(['nevilleweb.sk','*@gmail.com','user name@gmail.com',',,,']):
   h=home('bad-'+str(i),allow); before=len(requests)
   for command in ['read','poll']:
    p=run(h,command); assert p.returncode!=0 and 'FM_MAIL_SOURCE_ALLOW' in p.stderr
   assert len(requests)==before and not contents(h,'.wake-queue')
 scenario('Malformed allow lists fail read/poll clearly before connecting or publishing wakes',malformed)
 def progress():
  messages.clear(); messages.update({i:msg('allowed@nevilleweb.sk',f'prefix-{i}') for i in range(1,82)})
  failures.clear(); failures.update(range(1,81)); h=home('held','@nevilleweb.sk')
  p=run(h,'poll'); assert p.returncode==0 and not contents(h,'.wake-queue')
  assert set(contents(h,'.mail-retry').splitlines())==set(map(str,range(1,81)))
  p=run(h,'poll'); assert p.returncode==0 and 'check: mail 81 ' in contents(h,'.wake-queue')
  trans.append('Queue beyond unfetchable prefix:\n'+contents(h,'.wake-queue'))
  failures.remove(80)
  for _ in range(4):
   p=run(h,'poll'); assert p.returncode==0
   if 'check: mail 80 ' in contents(h,'.wake-queue'): break
  q=contents(h,'.wake-queue'); assert 'check: mail 80 ' in q and len(q.splitlines())==2
  trans.append('Recovered tail queue:\n'+q)
  failures.remove(79); messages[79]=msg('outsider@evil.test','PRIVATE-BLOCKED')
  for _ in range(5):
   p=run(h,'poll'); assert p.returncode==0
   if '79' not in contents(h,'.mail-retry').splitlines(): break
  assert '79' not in contents(h,'.mail-retry').splitlines() and contents(h,'.wake-queue')==q
  trans.append('Retry set after withheld recovery (79 and 80 removed):\n'+contents(h,'.mail-retry'))
 scenario('80 held UIDs cannot starve UID 81; rotating retries wake allowed recovery and discard denied recovery',progress)
 def override():
  messages.clear(); failures.clear(); messages[1]=msg('other@gmail.com','override-allowed')
  h=home('override','@nevilleweb.sk'); p=run(h,'poll',{'FM_MAIL_SOURCE_ALLOW':'other@gmail.com'}); assert p.returncode==0 and 'check: mail 1 ' in contents(h,'.wake-queue')
  p=run(h,'status'); assert p.returncode==0 and 'SOURCE_ALLOW' not in p.stdout and 'nevilleweb.sk' not in p.stdout
 scenario('Environment overrides .env allow list and status omits parsed allow-list reporting',override)
 assert not any('STORE' in r or 'BODY[' in r.replace('BODY.PEEK[','') for r in requests), 'Non-PEEK fetch or seen mutation'
 trans.append('IMAP protocol transcript (LOGIN omitted):\n'+'\n'.join(requests))
finally:
 if 'server' in globals(): server.shutdown(); server.server_close()
 shutil.rmtree(lab)
 (E/'mail-live-transcript.txt').write_text('\n'.join(trans))
 (E/'mail-live-results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
sys.exit(1 if any(x['result']=='fail' for x in results) else 0)
