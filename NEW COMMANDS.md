# Lesson commands

Create a lesson candidate by asking Codex in chat, for example: “Create A2
lesson 019.” If a later audit finds problems, paste those findings in chat and
ask Codex to fix the candidate. Codex edits the lesson source and rebuilds it.
You do not edit review files or set workflow flags.

From the project folder, run one command after chat creation or repair:

```bash
.venv/bin/python scripts/lesson_flow.py ready a2-course-019
```

`ready` rebuilds a stale candidate, runs an independent audit when needed,
generates matching audio after a passing audit, prepares a local preview, and
starts a temporary local web server. Open the URL printed in the terminal and
check desktop width, mobile width, and every audio clip. Type `REVIEWED` only
after doing so. The command records that inspection, runs the full test suite,
and prints `Ready for release`.

If the audit fails, `ready` stops before generating audio and prints precise
findings. Ask Codex in chat to fix them, then rerun the same `ready` command.
It reuses current passing audit and audio evidence, so rerunning it does not
repeat paid steps that are still valid. No `audit-fix`, manual `review.json`,
or `--desktop-reviewed` flags are part of this path.

After `ready` succeeds, run:

```bash
.venv/bin/python scripts/lesson_flow.py release a2-course-019
```

`release` publishes locally, uploads the published audio, and prepares the
mobile build. Open the URL it prints and inspect desktop and mobile widths.
Type `DEPLOY` to install and deploy. If you pause, rerun `release` to resume.
This last command changes the live app.

For a read-only status check:

```bash
.venv/bin/python scripts/lesson_flow.py status a2-course-019
```

Replace `a2-course-019` with the lesson you are working on. Work through
release one lesson at a time.
