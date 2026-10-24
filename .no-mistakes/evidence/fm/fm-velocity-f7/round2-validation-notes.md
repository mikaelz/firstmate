Live validation of 6a3b900a289eebc74cc3c859ab99fe07634257bb

The real fm-pr-park, fm-control, fm-procevent-when, fm-procevent and fm-teardown scripts ran in disposable marked lab homes under the gate worktree, with private 120-column x 40-row tmux sessions. The real gh CLI read deterministic PR responses from a disposable local TLS API fixture. No GitHub PR was changed.

Full running-worker proof used the installed authenticated Cursor CLI with its invocation-scoped --trust option. Transcript round2-cursor-live.txt records stopped, fired, relaunched, and the worker-created resumed.txt content RESUMED. round2-cursor-after.txt captures its actual editing output and the preserved uncommitted.txt content. Neither the worker CLI nor the lifecycle scripts were substituted. Initial Codex attempts, including invocation-only project trust settings and --no-daemon, stopped at folder trust; they are setup limitations, superseded for the required runtime-independent proof by the successful Cursor run. No persistent trust was approved manually.

Targeted regression command completed exit 0:
  bin/fm-test-run.sh tests/fm-pr-park.test.sh tests/fm-brief.test.sh tests/fm-teardown.test.sh

Additional executed evidence drivers (all completed exit 0 after correcting disposable setup):
  python3 <evidence>/round2-driver-cursor.py
  python3 <evidence>/round2-driver-diagnostic.py
  python3 <evidence>/round2-driver-cleanup.py
  python3 <evidence>/round2-driver-default.py

The default-home driver copies the unchanged real bin directory into a marked lab home and invokes its park script with FM_HOME unset; no lifecycle substitutes are used. Its initial attempt lacked a worktree identity and safely rolled back; adding a real disposable git repository resolved that setup error.

The generated scout brief is retained as the emitted public instruction contract. The task scope changes command-line behavior and generated instructions, with no visual layout change.

Every driver stopped its private server/API endpoint and removed its lab home in finally cleanup. Transient certificate, API and wrapper directories were then removed from the worktree. No source modifications were made.
