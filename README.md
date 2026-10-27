# Nochmal

Nochmal is a mobile web app for learning German through short audio lessons.
The app served to learners is the static site in `web/dist/`. Python in this
repository prepares, validates, and releases lesson content for that site.

## Run the mobile app locally

```bash
python3 -m http.server 8000 --directory web
```

Open `http://localhost:8000/dist/` in a browser. The app reads
`web/dist/lessons.json`; its lesson data and audio live beside that catalog.

## Lesson workflow

The A1 publication manifest lists lessons 001–048. The A2 publication manifest
lists lessons 001–024. Authored A2 lessons 025–072 remain in the curriculum
source for future review. The A2 and B1 blueprints are planning inputs.

Ask Codex for specific lesson numbers to create or curate, then request an
independent Sol High audit. Audio, publication, mobile installation, and live
deployment are separate gated actions. See [the lesson workflow](docs/lesson-workflow.md)
for the commands and checks. The entry point is `scripts/lesson_flow.py`.

Before changing a lesson, read the complete
[grammar breakdown rulebook](docs/grammar-breakdown-rulebook.md) and
[lesson format](docs/lesson-format.md). A lesson enters the mobile catalog only
after its release evidence, audio, tests, and local mobile preview pass.

## Development checks

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -q
```

## Repository layout

- `web/dist/` — mobile app and installed lesson assets; the mobile app is included in this repository.
- `web/prepared/` — temporary local mobile previews, excluded from Git.
- `curriculum/a1_staging/` and `curriculum/a2_course/` — authored lesson records.
- `curriculum/*_candidates/` — candidate sources, compiled cards, and review evidence.
- `curriculum/*_published/` — reviewed sources and explicit publication manifests.
- `assets/audio/` — staged, candidate, and published audio for the release pipeline.
- `nochmal/content/` — typed lesson models and shared compiler.
- `nochmal/validation/` — release gate.
- `nochmal/workflows/` — internal lesson and audio steps.
- `scripts/lesson_flow.py` — the command entry point.
- `tests/content/` — lesson, release, and mobile export checks.
