# Numbered lesson workflow

Candidate creation and repair happen in Codex chat. Ask for a lesson number,
for example “Create A2 lesson 019.” Codex reads the blueprint and lesson rules,
edits the authored and candidate source, builds the candidate, and runs focused
validation. The candidate remains outside the published app.

From the repository root, the user runs:

```bash
.venv/bin/python scripts/lesson_flow.py release a2-course-019
```

This is the only command needed after chat has created or fixed the candidate.

## What happens before publication

1. Rebuilds the candidate if its compiled artifact is stale.
2. Reuses a passing audit tied to the current source hash, or launches one
   independent, read-only Sol High audit and records its verdict.
3. Stops with sentence and card findings if the audit fails. Paste those
   findings in chat and ask Codex to fix the candidate; then rerun `release`.
4. Generates or reuses matching ElevenLabs audio only after the audit passes.
   New audio may consume ElevenLabs credits.
5. Builds an unpublished mobile preview as a package-integrity check. No local
   review prompt or confirmation is required.
6. Runs the full unit suite once and records a preflight receipt tied to the
   current candidate and code. A later source or code change makes it stale.

Reruns skip a current passing audit, matching audio, and preflight. There are
no manual status flags, confirmation prompts, or hand-edited review files. The
independent audit is intentionally a command step; chat never creates a passing
receipt.

## What `release` does

After the audit, audio, package, and preflight steps above pass, `release`
publishes the lesson locally; validates and compacts published audio; uploads it
to R2; prepares and verifies the mobile package; installs it; and deploys to
Cloudflare Pages. It does not pause for a local review or request a confirmation
token.

Release one lesson at a time. Publishing and deployment are separate from
creating or fixing a candidate in chat.

## Other commands

`status LESSON_ID` shows the current state. `prepare` is an internal helper for
chat creation. `audit`, `audio`, `preview`, `preflight`, `publish`, `upload`,
and the `mobile-*` commands remain available for diagnosis or custom workflows.
`ready` remains available when you want to prepare a lesson without publishing;
the normal path is `release`; the old nested
`audit-fix` command has been removed.
