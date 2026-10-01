"""Stable Streamlit entry point for local development."""

from importlib import reload

# Keeping this tiny wrapper preserves the familiar `streamlit run app.py`
# command while application code lives in the package. Refresh generated lesson
# content and presentation modules on every Streamlit rerun so local edits appear
# immediately and an older cached module can never leave the page stale or blank.
from nochmal import content
from nochmal.content import (
    a1_a2_lessons,
    a1_course_lessons,
    grammar_reference,
    models,
)
from nochmal.services import speech_feedback
from nochmal.ui import app as ui_app
from nochmal.ui import audio_player
from nochmal.validation import release

audio_player = reload(audio_player)
models = reload(models)
grammar_reference = reload(grammar_reference)
a1_a2_lessons = reload(a1_a2_lessons)
a1_course_lessons = reload(a1_course_lessons)
content = reload(content)
release = reload(release)
speech_feedback = reload(speech_feedback)
ui_app = reload(ui_app)

ui_app.main()
