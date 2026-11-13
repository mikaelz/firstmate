import json,os,pathlib,subprocess
root=pathlib.Path.cwd(); settings=json.loads((root/'.augment/settings.json').read_text())
regs=settings['hooks']['PreToolUse']
assert regs and all(r['matcher']=='bash' for r in regs)
print('Normalized hook registration: only bash, with',sum(len(r['hooks']) for r in regs),'command hooks.')
env=os.environ.copy()
for name in ['FM_ROOT_OVERRIDE','FM_STATE_OVERRIDE','FM_DATA_OVERRIDE','FM_CONFIG_OVERRIDE','FM_PROJECTS_OVERRIDE']:
    env.pop(name,None)
env.update(FM_HOME=str(root/'.live-auggie/home'),AUGMENT_PROJECT_DIR=str(root))
for r in regs:
    for hook in r['hooks']:
        for command in ['printf hello','bin/fm-watch-arm.sh &','exec bin/fm-watch-arm.sh']:
            payload={'hook_event_name':'PreToolUse','tool_name':'bash','tool_input':{'command':command}}
            p=subprocess.run(['bash','-c',hook['command']],env=env,input=json.dumps(payload),text=True,capture_output=True,timeout=10)
            print(f'\nRegistered hook command: {hook["command"]}\nTool input: {command}\nExit={p.returncode}\nstdout={p.stdout}\nstderr={p.stderr}')
            is_arm='fm-arm-pretool-check' in hook['command']
            expected=2 if is_arm and command=='bin/fm-watch-arm.sh &' else 0
            assert p.returncode==expected
print('\nThe registered bash hooks allow safe commands and refuse backgrounded arming.')
