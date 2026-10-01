# Example: Adding lesson a1-002

## 1. Generate the audio

From the repository root:

```
cd /Users/eashwar/Documents/GitHub/nochmal

.venv-tts/bin/python scripts/generate_prepared_audio.py \
  --lesson a1-002 \
  --isolate-lessons \
  --force
```

Do not add `--full-only`; without it, you get both full and sentence audio.

Expected files:

```
assets/audio/a1-002.wav
assets/audio/sentences/a1-002-1.wav
assets/audio/sentences/a1-002-2.wav
assets/audio/sentences/a1-002-3.wav
assets/audio/sentences/a1-002-4.wav
```

Verify:

```
find assets/audio -maxdepth 2 -name 'a1-002*.wav' -print | sort
```

### 2. Add the full audio path to the JSON lesson

Open:

[curriculum/a1_a2/lessons/001_020.json](/Users/eashwar/Documents/GitHub/nochmal/curriculum/a1_a2/lessons/001_020.json)

Inside the `a1-002` object, change:

```
"recycles_from": [1],
```

to:

```
"recycles_from": [1],
"audio_path": "assets/audio/a1-002.wav",
```

### 3. Add each sentence audio path

Update the four `a1-002` sentence objects like this:

```
{
  "de": "Im Deutschkurs fragt Leo: „Wie heißt du und woher kommst du?“",
  "en": "In the German course Leo asks, “What is your name and where are you from?”",
  "audio_path": "assets/audio/sentences/a1-002-1.wav"
},
{
  "de": "Mina antwortet: „Ich bin achtundzwanzig Jahre alt und wohne in Bonn.“",
  "en": "Mina answers, “I am twenty-eight years old and live in Bonn.”",
  "audio_path": "assets/audio/sentences/a1-002-2.wav"
},
{
  "de": "Sie arbeitet am Vormittag und lernt am Abend Deutsch.",
  "en": "She works in the morning and learns German in the evening.",
  "audio_path": "assets/audio/sentences/a1-002-3.wav"
},
{
  "de": "Leo spricht langsam, und Mina versteht ihn gut.",
  "en": "Leo speaks slowly, and Mina understands him well.",
  "audio_path": "assets/audio/sentences/a1-002-4.wav"
}
```

The compiler already supports these optional metadata fields in:

[nochmal/content/a1_a2_lessons.py](/Users/eashwar/Documents/GitHub/nochmal/nochmal/content/a1_a2_lessons.py)

If all paths are present, it automatically marks the lesson as `ready`.

### 4. Validate the curriculum

```
.venv-tts/bin/python -m curriculum.a1_a2.validate
```

Expected:

```
Validated 80 ordered A1-A2 passage lessons.
```

### 5. Restart the app

Stop Streamlit with `Ctrl+C`, then run:

```
streamlit run app.py
```

Lesson `a1-002` should then have full-paragraph audio and four sentence-level audio players.

One test detail: the current test assumes only `a1-001` is ready. If you run the full unit tests after adding `a1-002`, change the test’s hardcoded check from:

```
expected_status = "ready" if lesson.id == "a1-001" else "pending"
```

to:

```
has_audio = bool(lesson.audio_path) and all(
    sentence.audio_path for sentence in lesson.sentences
)
expected_status = "ready" if has_audio else "pending"
```
