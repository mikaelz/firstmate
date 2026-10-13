import http.server
import json
import os
from pathlib import Path
import queue
import shlex
import shutil
import subprocess
import sys
import threading
import time

root, lab, version = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
lab.mkdir()
wrapper = json.loads((root / '.codex/hooks.json').read_text())['hooks']['Stop'][0]['hooks'][0]['command']
base_wrapper = json.loads(subprocess.check_output(['git', 'show', '6407052f4c521e39401ce2305dfa45d201249827:.codex/hooks.json'], cwd=root))['hooks']['Stop'][0]['hooks'][0]['command']
emitter = lab / 'emit.py'
emitter.write_text('''import json,sys
mode=sys.argv[1]
active=json.load(sys.stdin).get('stop_hook_active',False)
outputs={
 'empty': ('','',0), 'json': ('{}\\n','',0),
 'mixed': ('diagnostic\\n{}\\n','',0), 'syntax': ('{','',0),
 'schema': ('{"continue":"yes"}','',0), 'two-objects': ('{}\\n{}','',0),
 'stderr': ('{}\\n','diagnostic\\n',0), 'error': ('','fixture error\\n',7)}
if mode=='continue':
 out,err,code=('', 'fixture continuation\\n', 2) if not active else ('{}\\n','',0)
else: out,err,code=outputs[mode]
sys.stdout.write(out);sys.stderr.write(err);sys.exit(code)
''')
primary = lab / 'primary'
for name in ['bin', 'state', 'docs', '.codex']:
    (primary / name).mkdir(parents=True, exist_ok=True)
(primary / 'AGENTS.md').write_text('Isolated Stop parser fixture.\n')
(primary / '.codex/hooks.json').write_text(json.dumps({'hooks': {'Stop': [{'hooks': [
    {'type': 'command', 'command': 'fm-turnend-guard.sh'}]}]}}))
for name in ['fm-turnend-guard.sh', 'fm-operational-input.sh', 'fm-supervision-instructions.sh',
             'fm-harness.sh', 'fm-primary-scope-lib.sh', 'fm-supervision-lib.sh',
             'fm-supervision-engine-lib.sh', 'fm-wake-lib.sh', 'fm-path-lib.sh',
             'fm-hook-host-lib.sh', 'fm-session-lock-lib.sh', 'fm-cursor-lib.sh']:
    shutil.copy2(root / 'bin' / name, primary / 'bin' / name)
shutil.copytree(root / 'docs/supervision-protocols', primary / 'docs/supervision-protocols')
subprocess.run(['git', 'init', '-q', str(primary)], check=True)

class Responses(http.server.BaseHTTPRequestHandler):
    requests = 0

    def log_message(self, *args):
        pass

    def do_POST(self):
        self.rfile.read(int(self.headers.get('Content-Length', '0')))
        Responses.requests += 1
        message = {'id': 'msg_fixture', 'type': 'message', 'role': 'assistant',
                   'status': 'completed', 'phase': 'final_answer', 'content': [
                       {'type': 'output_text', 'text': 'fixture complete', 'annotations': []}]}
        events = [
            {'type': 'response.created', 'response': {'id': 'resp_fixture', 'status': 'in_progress', 'output': []}},
            {'type': 'response.output_item.added', 'output_index': 0,
             'item': {**message, 'status': 'in_progress', 'content': []}},
            {'type': 'response.output_item.done', 'output_index': 0, 'item': message},
            {'type': 'response.completed', 'response': {'id': 'resp_fixture', 'status': 'completed',
             'output': [message], 'usage': {'input_tokens': 1, 'output_tokens': 1, 'total_tokens': 2}}},
        ]
        data = ''.join('event: ' + event['type'] + '\ndata: ' + json.dumps(event) + '\n\n'
                       for event in events).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Responses)
server_thread = threading.Thread(target=server.serve_forever, daemon=True)
server_thread.start()

def check(mode, expected):
    case = lab / mode
    case.mkdir()
    fixture_home = case / 'login'
    fixture_home.mkdir()
    (fixture_home / '.bash_profile').write_text(':\n')
    (fixture_home / '.bash_logout').write_text("printf '\\033[H\\033[2J\\033[3J'\n")
    codex_data = case / 'codex'
    codex_data.mkdir()
    command = wrapper if mode.startswith('wrapper-') else shlex.join([sys.executable, str(emitter), mode])
    if mode == 'wrapper-before': command = base_wrapper
    if mode == 'wrapper-json-only': command = base_wrapper[:-1] + '; code=$?; if [ "$code" -eq 0 ]; then printf "{}\\n"; fi; exit "$code"' + chr(39)
    (codex_data / 'hooks.json').write_text(json.dumps({'hooks': {'Stop': [{'hooks': [
        {'type': 'command', 'command': command, 'timeout': 10}]}]}}))
    (codex_data / 'config.toml').write_text(f'''model="fixture"
model_provider="fixture"
[model_providers.fixture]
name="Loopback Stop fixture"
base_url="http://127.0.0.1:{server.server_port}/v1"
wire_api="responses"
requires_openai_auth=false
[features]
hooks=true
shell_snapshot=false
[analytics]
enabled=false
''')
    # Keep the inherited PATH, but no operator config, tokens, hook startup
    # overrides, or fleet paths enter the child app-server or its hooks.
    env = {key: os.environ[key] for key in ['PATH', 'LANG', 'LC_ALL', 'DISABLE_AUTOUPDATER'] if key in os.environ}
    env.update({'HOME': str(fixture_home), 'CODEX_HOME': str(codex_data),
                'SHELL': '/bin/sh', 'TMPDIR': str(lab), 'OTEL_SDK_DISABLED': 'true'})
    cwd = primary if mode in ['wrapper-idle', 'wrapper-block'] else case
    (primary / 'state/task.meta').unlink(missing_ok=True)
    if mode == 'wrapper-block':
        (primary / 'state/task.meta').touch()
    notifications = []
    messages = queue.Queue()
    deadline = time.monotonic() + 40
    before = Responses.requests
    with (case / 'stderr').open('w') as stderr:
        process = subprocess.Popen(['codex', 'app-server', '--stdio'], cwd=case, env=env,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr, text=True)
        def read_lines():
            for line in process.stdout:
                messages.put(json.loads(line))
            messages.put(None)
        reader = threading.Thread(target=read_lines, daemon=True)
        reader.start()
        def send(message):
            process.stdin.write(json.dumps(message) + '\n')
            process.stdin.flush()
        def receive():
            message = messages.get(timeout=max(0.1, deadline - time.monotonic()))
            assert message is not None, 'app-server exited before its hook verdict'
            notifications.append(message)
            return message
        def rpc(number, method, params):
            send({'id': number, 'method': method, 'params': params})
            while True:
                message = receive()
                if message.get('id') == number:
                    assert 'error' not in message, message
                    return message['result']
        try:
            rpc(1, 'initialize', {'clientInfo': {'name': 'isolated-stop-test', 'version': '1'},
                                 'capabilities': {'experimentalApi': True}})
            send({'method': 'initialized'})
            listed = rpc(2, 'hooks/list', {'cwds': [str(case)]})
            hooks = [hook for entry in listed['data'] for hook in entry['hooks']
                     if hook['eventName'] == 'stop' and hook['sourcePath'] == str(codex_data / 'hooks.json')]
            assert len(hooks) == 1, listed
            hook = hooks[0]
            thread = rpc(3, 'thread/start', {'cwd': str(cwd), 'model': 'fixture', 'modelProvider': 'fixture',
                'approvalPolicy': 'never', 'sandbox': 'read-only', 'ephemeral': True,
                'config': {'hooks.state': {hook['key']: {'trusted_hash': hook['currentHash']}}}})
            rpc(4, 'turn/start', {'threadId': thread['thread']['id'],
                                 'input': [{'type': 'text', 'text': 'fixture', 'text_elements': []}]})
            while receive().get('method') != 'turn/completed':
                pass
            runs = [message['params']['run'] for message in notifications
                    if message.get('method') == 'hook/completed' and message['params']['run']['eventName'] == 'stop']
            print(json.dumps({'mode': mode, 'codex_version': version, 'model_requests': Responses.requests-before, 'hooks': runs}), flush=True)
            assert [run['status'] for run in runs] == expected, (mode, runs)
            assert Responses.requests - before == len(expected), (mode, Responses.requests - before)
            if mode in ['mixed', 'syntax', 'schema', 'two-objects']:
                assert runs[0]['entries'] == [{'kind': 'error', 'text': 'hook returned invalid stop hook JSON output'}], runs
            if mode == 'error':
                assert runs[0]['entries'] == [{'kind': 'error', 'text': 'hook exited with code 7'}], runs
            if mode == 'wrapper-block':
                assert any('TURN WOULD END BLIND' in entry['text'] for entry in runs[0]['entries']), runs
        finally:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            reader.join(timeout=1)

try:
    for mode in ['wrapper-before', 'wrapper-json-only']:
        check(mode, ['failed'])
    for mode in ['empty', 'json', 'stderr', 'wrapper-noop', 'wrapper-idle']:
        check(mode, ['completed'])
    for mode in ['mixed', 'syntax', 'schema', 'two-objects', 'error']:
        check(mode, ['failed'])
    for mode in ['continue', 'wrapper-block']:
        check(mode, ['blocked', 'completed'])
    print(f'ok - codex {version}: Stop parser checked 12 isolated cases with clean wrapper JSON and bounded continuation')
except Exception as error:
    raise SystemExit(f'not ok - codex {version}: isolated Stop parser failed: {error!r}') from error
finally:
    server.shutdown()
    server.server_close()
    server_thread.join()