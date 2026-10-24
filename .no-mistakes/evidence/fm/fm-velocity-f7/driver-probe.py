import os, ssl, socketserver, threading, json, subprocess, pathlib
root=pathlib.Path.cwd(); d=root/'.live-park'
ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.load_cert_chain(d/'cert.pem',d/'key.pem')
pr={'state':'OPEN','headRefOid':'a'*40,'reviewDecision':'','reviews':{'nodes':[]},'comments':{'nodes':[]},'statusCheckRollup':{'contexts':{'nodes':[{'__typename':'CheckRun','name':'test','status':'QUEUED','conclusion':''}]}}}
class H(socketserver.StreamRequestHandler):
 def handle(self):
  line=self.rfile.readline()
  while self.rfile.readline().strip():pass
  self.wfile.write(b'HTTP/1.1 200 Connection established\r\n\r\n');self.wfile.flush()
  s=ctx.wrap_socket(self.connection,server_side=True); f=s.makefile('rb'); line=f.readline();headers={}
  while True:
   l=f.readline().strip()
   if not l:break
   k,v=l.decode().split(':',1);headers[k.lower()]=v.strip()
  body=f.read(int(headers.get('content-length','0')))
  (d/'request.json').write_bytes(body)
  data=json.dumps({'errors':[{'message':'disposable API unavailable'}]} if (d/'api-fail').exists() else {'data':{'repository':{'pullRequest':pr}}}).encode()
  s.sendall(b'HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: '+str(len(data)).encode()+b'\r\nConnection: close\r\n\r\n'+data);s.close()
server=socketserver.ThreadingTCPServer(('127.0.0.1',0),H);threading.Thread(target=server.serve_forever,daemon=True).start()
env=os.environ.copy();env.update(GH_TOKEN='disposable-fixture-token',GH_CONFIG_DIR=str(d/'gh'),SSL_CERT_FILE=str(d/'cert.pem'),HTTPS_PROXY='http://127.0.0.1:'+str(server.server_address[1]),NO_PROXY='')
r=subprocess.run(['gh','pr','view','https://github.com/acme/widget/pull/42','--json','state,headRefOid,reviewDecision,statusCheckRollup,comments,reviews'],env=env,capture_output=True,text=True);print(r.returncode,r.stdout,r.stderr)
(d/'env.json').write_text(json.dumps({k:env[k] for k in ['GH_TOKEN','GH_CONFIG_DIR','SSL_CERT_FILE','HTTPS_PROXY','NO_PROXY']}))
server.shutdown()
