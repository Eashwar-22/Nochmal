# Nochmal

Nochmal is a local German learning prototype. A learner chooses a short passage
and studies it sentence by sentence with translations, ordered vocabulary,
meaning chunks, grammar guidance, and detailed verb help. The currently
published reference lesson includes complete audio and speaking practice.

The complete product concept, original prototype roadmap, and longer-term ML
direction are preserved in
[`docs/project-vision.md`](docs/project-vision.md).

## Run locally

No API key is required for the prepared lessons.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit, normally
`http://localhost:8501`.

The reference lesson also contains an experimental, entirely local speech
check. To enable transcript and broad timing feedback, install the optional
speech packages:

```bash
pip install -r requirements-speech.txt
```

The first check loads the local `small` Whisper model and may take longer while
the model is downloaded and cached under `data/`. Learners can correct words
the model misheard before the comparison is updated. Lessons can also author
meaning-preserving alternatives, such as `am Morgen` for `am Vormittag`, which
do not reduce the lesson match. The result is not a pronunciation or accent
grade.

## Demo flow

1. Choose **Hello, I’m Mina**.
2. Play the full paragraph from the audio bar while following the passage.
3. Review each sentence's audio, translation, vocabulary, grammar tags, and
   verb help.
4. Record the German paragraph and optionally run the
   experimental local speech check.
5. Mark the lesson complete to add its words to learned vocabulary.
6. Open the **Vocabulary** tab to browse words by category or review vocabulary
   from completed lessons.
7. Use **Reset progress** when you want to permanently clear all local lesson
   completions and attempts.

## Lesson library

The app currently publishes one reviewed A1.1 reference lesson promoted from
the new 48-lesson staged curriculum. The remaining drafts stay unpublished
under `curriculum/a1_staging/` until they pass the complete grammar, audio,
test, and visual-review gate. The previous 80-lesson A1-A2 curriculum remains
preserved under `curriculum/a1_a2/`; it has not been deleted. Fourteen older
A2–B2 listening paragraphs also remain preserved but hidden from the picker.

Lesson 2 is available as a prebuilt, unpublished experiment under
`curriculum/a1_candidates/a1-course-002/`. Its `preview.md` shows the exact
compiled cards before app activation. Push that existing artifact into your
local app with:

```bash
.venv/bin/python scripts/push_lesson.py a1-course-002
```

Refresh Streamlit and select the item prefixed `PREVIEW`. No AI runs during
this command, and the production publication list is unchanged. Remove it with:

```bash
.venv/bin/python scripts/push_lesson.py a1-course-002 --remove
```

The reference lesson audio was generated sentence by sentence with Eleven v4,
then assembled locally so the full playback uses the exact accepted sentence
clips. Reviewed files live under `assets/audio/a1_course/a1-course-001/`.
With `ELEVENLABS_API_KEY` stored in a git-ignored `.env`, generate or compare a
staged draft with:

```bash
python3 scripts/generate_staged_elevenlabs_audio.py a1-draft-001 --force
```

Staged generation never overwrites reviewed production audio. After a lesson's
source, structured semantic review, and audio manifest are promoted, run its
fail-closed release gate before adding it to `curriculum/a1_course/publication.json`:

```bash
python scripts/validate_release.py a1-course-001
```

The preserved legacy audio is generated locally with the quantized Qwen3-TTS VoiceDesign
model through MLX (Apple Silicon) and does not use an API. Its voice direction is a
clear, warm female German narrator for adult learners. Create the one-purpose TTS
environment and regenerate the audio with:

```bash
python3.12 -m venv .venv-tts
.venv-tts/bin/pip install -r requirements-tts.txt
.venv-tts/bin/python scripts/generate_prepared_audio.py --isolate-lessons --force
```

The voice direction asks for slower, deliberate speech at A2 and gradually moves
toward natural pacing at B2. Every full recording is built from the exact sentence
clips used for replays, with a 0.35-second silent pause between sentences.
The isolated mode releases the model between lessons, which is recommended on
8 GB Apple Silicon machines.

Lesson completions are stored in `data/nochmal.db`. Progress stays on the local
device, can be completely reset from the interface, and is excluded from Git.

## Tests

```bash
python -m unittest discover -s tests -v
```

The shared lesson contract runs against every paragraph exported by the content
library, including future additions. It checks ready-versus-pending audio, phrase/source agreement,
preposition and contraction results, noun/article composition, and complete
six-form hover help for every verb card. The suite also covers the SQLite
attempt lifecycle, vocabulary grouping, and the breakdown-column layout.

Before adding or publishing a paragraph, read the complete
[`grammar breakdown rulebook`](docs/grammar-breakdown-rulebook.md), then follow
[`docs/lesson-format.md`](docs/lesson-format.md) and run the focused contract:

```bash
python -m unittest tests.content.test_lesson_contract -v
```

## Project structure

- `app.py` — stable, minimal Streamlit entry point.
- `nochmal/content/` — lesson models, authored paragraphs, and the reusable
  content validator.
- `curriculum/a1_candidates/` — prebuilt unpublished lesson packages and
  human-readable card previews.
- `nochmal/validation/` — strict review evidence and publication release gate.
- `nochmal/services/` — SQLite persistence and vocabulary derivation.
- `nochmal/services/speech_feedback.py` — optional local transcript and pacing
  comparison for selected speaking-practice lessons.
- `nochmal/ui/` — Streamlit workflow and reusable audio controls.
- `nochmal/paths.py` — shared project paths for UI, scripts, and tests.
- `assets/audio/` — prepared full-paragraph and sentence recordings.
- `curriculum/a1_course/publication.json` — explicit ordered list of lessons
  allowed into the app after release validation.
- `data/` — ignored local progress and speech-model caches.
- `docs/` — product vision, lesson-authoring rules, and project status.
- `scripts/generate_prepared_audio.py` — reproducible local German audio.
- `tests/content/`, `tests/services/`, `tests/ui/` — tests mirroring the package
  boundaries.
