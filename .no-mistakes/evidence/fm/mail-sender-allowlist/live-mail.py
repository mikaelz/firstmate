import json, os, pathlib, re, socketserver, ssl, subprocess, tempfile, threading
ROOT=pathlib.Path.cwd()
EVID=pathlib.Path('/home/mike/.no-mistakes/evidence/01M4Q810K754CCBGRC4RNVDGNM')
log=[]; results=[]
def record(s): log.append(s); print(s,flush=True)
with tempfile.TemporaryDirectory(prefix='.mail-live-',dir=ROOT) as td:
    lab=pathlib.Path(td)
    subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(lab/'key.pem'),'-out',str(lab/'cert.pem'),'-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain(lab/'cert.pem',lab/'key.pem')
    mailbox={}; commands=[]
    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            def send(s): self.wfile.write(s.encode() if isinstance(s,str) else s); self.wfile.flush()
            send('* OK disposable IMAP ready\r\n')
            while True:
                raw=self.rfile.readline()
                if not raw: break
                line=raw.decode().strip(); tag,cmd,*args=line.split(); cmd=cmd.upper()
                # Do not persist LOGIN credentials.
                commands.append(cmd+' '+(' '.join(args) if cmd!='LOGIN' else '[redacted]'))
                if cmd=='CAPABILITY': send('* CAPABILITY IMAP4rev1\r\n')
                elif cmd=='LOGIN': pass
                elif cmd=='SELECT': send(f'* {len(mailbox)} EXISTS\r\n* 0 RECENT\r\n* FLAGS (\\Seen)\r\n* OK [UIDVALIDITY 90009] generation\r\n')
                elif cmd=='UID' and args[0].upper()=='SEARCH': send('* SEARCH '+ ' '.join(str(u) for u in mailbox)+'\r\n')
                elif cmd=='UID' and args[0].upper()=='FETCH':
                    uid=int(args[1]); data=mailbox.get(uid)
                    if data is None:
                        send(tag+' NO temporarily unfetchable\r\n'); continue
                    body=data if 'HEADER' not in line else data.split(b'\r\n\r\n')[0]+b'\r\n\r\n'
                    send(f'* 1 FETCH (UID {uid} BODY[] {{{len(body)}}}\r\n'); send(body); send(')\r\n')
                elif cmd=='LOGOUT': send('* BYE goodbye\r\n'+tag+' OK logout\r\n'); break
                else: send(tag+' BAD unsupported\r\n'); continue
                send(tag+' OK complete\r\n')
    class Server(socketserver.ThreadingTCPServer):
        allow_reuse_address=True; daemon_threads=True
        def get_request(self):
            sock,addr=super().get_request(); return ctx.wrap_socket(sock,server_side=True),addr
    srv=Server(('127.0.0.1',0),Handler); thread=threading.Thread(target=srv.serve_forever,daemon=True); thread.start()
    base={k:v for k,v in os.environ.items() if not k.startswith(('FM_','NO_MISTAKES'))}
    base['SSL_CERT_FILE']=str(lab/'cert.pem')
    def home(name,allow=None):
        h=lab/name; h.mkdir(); values={'FM_MAIL_USER':'lab@example.test','FM_MAIL_PASS':'disposable-password','FM_IMAP_HOST':'localhost','FM_IMAP_PORT':str(srv.server_address[1]),'FM_SMTP_HOST':'localhost','FM_MAIL_TIMEOUT':'3'}
        if allow is not None: values['FM_MAIL_SOURCE_ALLOW']=allow
        (h/'.env').write_text(''.join(k+'='+v+'\n' for k,v in values.items())); return h
    def run(h,cmd,**extra):
        env=dict(base,FM_HOME=str(h),**extra)
        p=subprocess.run([str(ROOT/'bin/fm-mail.sh'),cmd],env=env,capture_output=True,text=True,timeout=30)
        record(f'$ FM_HOME=<{h.name}> bin/fm-mail.sh {cmd} '+str(extra)+'\n'+p.stdout+p.stderr+f'exit={p.returncode}')
        return p
    def state(h,name):
        p=h/'state'/name; return p.read_text() if p.exists() else ''
    def uids(h): return [int(x) for x in re.findall(r'check: mail (\d+)',state(h,'.wake-queue'))]
    def msg(sender,subject,body='preview',additional=''):
        return (('From: '+sender+'\r\n' if sender is not None else '')+additional+'Subject: '+subject+'\r\nDate: Mon, 12 Oct 2026 12:00:00 +0000\r\n\r\n'+body+'\r\n').encode()
    def scenario(name,f):
        try: f(); results.append({'name':name,'result':'pass','live':True,'reason':'','evidence':'live-mail-transcript.txt'}); record('PASS: '+name)
        except Exception as e: results.append({'name':name,'result':'fail','live':True,'reason':str(e),'evidence':'live-mail-transcript.txt'}); record('FAIL: '+name+' '+repr(e))
    def matching():
        mailbox.clear(); mailbox.update({1:msg('Alice <USER@NEVILLEWEB.SK>','allowed-domain'),2:msg('USERNAME@GMAIL.COM','allowed-address'),3:msg('username@im3.sk','second-address'),4:msg('"username@gmail.com" <attacker@evil.test>','SECRET-display'),5:msg('a@nevilleweb.sk.evil.test','SECRET-suffix'),6:msg('a@sub.nevilleweb.sk','SECRET-subdomain'),7:msg('other@gmail.com','SECRET-other'),8:msg('username@gmail.com, evil@evil.test','SECRET-multiple'),9:msg(None,'SECRET-missing'),10:msg('username@gmail.com','SECRET-duplicate',additional='From: evil@evil.test\r\n'),11:msg('not-an-address','SECRET-malformed'),12:None})
        h=home('matching',' @NEVILLEWEB.SK , username@gmail.com,username@im3.sk ')
        p=run(h,'poll'); assert p.returncode==0; assert sorted(uids(h))==[1,2,3],uids(h)
        assert 'withheld 8' in p.stdout and 'held 1' in p.stdout
        assert 'SECRET' not in p.stdout+state(h,'.wake-queue') and 'evil.test' not in p.stdout+state(h,'.wake-queue')
        before=len(commands); p=run(h,'poll'); assert p.returncode==0 and sorted(uids(h))==[1,2,3]
        assert [x for x in commands[before:] if x.startswith('UID FETCH')]==['UID FETCH 12 (BODY.PEEK[HEADER])']
        p=run(h,'read'); assert p.returncode==0 and 'SECRET' not in p.stdout and '8 unseen message(s)' in p.stdout and 'Uid: 12' in p.stdout
        for s in ['allowed-domain','allowed-address','second-address']: assert s in p.stdout
        p=run(h,'poll',FM_MAIL_SOURCE_ALLOW='@evil.test'); assert p.returncode==0 and sorted(uids(h))==[1,2,3]
        p=run(h,'status'); assert p.returncode==0 and 'SOURCE_ALLOW' not in p.stdout
        record('Persisted queue:\n'+state(h,'.wake-queue')); record('Cursor:\n'+state(h,'.mail-seen')); record('Retry:\n'+state(h,'.mail-retry'))
    scenario('Configure comma-separated domain/address entries in .env; only matching single From addresses appear in notifications and read output, with redacted counts and no duplicates',matching)
    def invalid():
        h=home('invalid','@ok.test')
        for value in ['nevilleweb.sk','*@nevilleweb.sk','@nev ille.sk','a@b@c','<a@b.c>',', ,']:
            for cmd in ['read','poll']:
                before=len(commands); p=run(h,cmd,FM_MAIL_SOURCE_ALLOW=value); assert p.returncode==1 and 'FM_MAIL_SOURCE_ALLOW' in p.stderr and len(commands)==before
        assert not uids(h)
    scenario('Malformed or entry-less allow lists reject read and poll before contacting IMAP or publishing notifications',invalid)
    def unrestricted():
        mailbox.clear(); mailbox.update({1:msg('any@evil.test','any-sender'),2:None})
        for name,allow in [('unset',None),('blank',' ' )]:
            h=home(name,allow); p=run(h,'poll'); assert p.returncode==0 and sorted(uids(h))==[1,2] and 'unfetchable header' in state(h,'.wake-queue')
            p=run(h,'read'); assert p.returncode==0 and 'any-sender' in p.stdout
    scenario('Unset or whitespace-only allow list preserves unrestricted mail delivery and degraded-header notifications',unrestricted)
    def progress():
        for cap,window in [(20,80),(1,11)]:
            mailbox.clear(); mailbox.update({u:None for u in range(1,window+1)}); mailbox[window+1]=msg('later@nevilleweb.sk','later-allowed')
            h=home('progress-'+str(cap),'@nevilleweb.sk')
            p=run(h,'poll',FM_MAIL_POLL_MAX_WAKES=str(cap)); assert p.returncode==0 and not uids(h)
            assert len(state(h,'.mail-retry').splitlines())==window
            for _ in range(2): assert run(h,'poll',FM_MAIL_POLL_MAX_WAKES=str(cap)).returncode==0
            assert uids(h)==[window+1],uids(h)
            mailbox[1]=msg('blocked@evil.test','SECRET-recovered'); mailbox[window]=msg('recovered@nevilleweb.sk','recovered-allowed')
            for _ in range(5): assert run(h,'poll',FM_MAIL_POLL_MAX_WAKES=str(cap)).returncode==0
            assert sorted(uids(h))==[window,window+1],uids(h)
            assert '1' not in state(h,'.mail-retry').splitlines() and str(window) not in state(h,'.mail-retry').splitlines()
            assert 'SECRET' not in state(h,'.wake-queue')
            record('Recovery queue:\n'+state(h,'.wake-queue')); record('Remaining retry UIDs:\n'+state(h,'.mail-retry'))
    scenario('Persistent unfetchable prefix permits later allowed mail and retries recover allowed senders once while discarding blocked senders, at caps 20 and 1',progress)
    assert not any('STORE' in x or ('FETCH' in x and 'BODY.PEEK' not in x) for x in commands)
    record('IMAP operations use BODY.PEEK only; no STORE or Seen mutation sent.')
    srv.shutdown(); srv.server_close()
    (EVID/'live-imap-protocol.txt').write_text('\n'.join(commands)+'\n')
(EVID/'live-mail-transcript.txt').write_text('\n'.join(log)+'\n')
(EVID/'live-mail-results.json').write_text(json.dumps(results,indent=2)+'\n')
if any(x['result']!='pass' for x in results): raise SystemExit(1)
