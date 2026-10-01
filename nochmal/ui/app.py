from html import escape
import re

import streamlit as st

from nochmal.content import LESSONS, models
from nochmal.content.candidates import load_active_preview_lessons
from nochmal.content.catalog import load_publication_catalog, published_lessons
from nochmal.content.ordering import ordered_breakdown_items
from nochmal.content.grammar_reference import (
    columns_for_help,
    inflections_for_phrase,
    selected_column_for_help,
    table_for_help,
)
from nochmal.content.verb_reference import (
    english_current_forms,
    english_infinitive,
    english_present_forms,
    present_forms,
    reference_for,
)
from nochmal.paths import PROJECT_ROOT
from nochmal.services import speech_feedback, storage, vocabulary
from nochmal.ui.audio_player import render_audio_player


PUBLICATION_CATALOG = load_publication_catalog()
PUBLISHED_LESSON_IDS = PUBLICATION_CATALOG.published_lesson_ids
PUBLISHED_COURSE_LESSONS = published_lessons(LESSONS)
PREVIEW_LESSONS = load_active_preview_lessons()
PREVIEW_LESSON_IDS = frozenset(lesson.id for lesson in PREVIEW_LESSONS)
COURSE_LESSONS = (
    *PUBLISHED_COURSE_LESSONS,
    *(
        lesson
        for lesson in PREVIEW_LESSONS
        if lesson.id not in PUBLISHED_LESSON_IDS
    ),
)
LESSON_BY_ID = {lesson.id: lesson for lesson in COURSE_LESSONS}
SPEAKING_PRACTICE_LESSON_IDS = PUBLICATION_CATALOG.speaking_practice_lesson_ids
PRACTICE_RECORDINGS_DIR = PROJECT_ROOT / "data" / "practice-recordings"
SPEECH_MODEL_CACHE_DIR = PROJECT_ROOT / "data" / "faster-whisper-cache"
SPEECH_MODEL_NAME = "small"

APP_STYLES = """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(
        to right,
        #f3f3f3 0,
        #f3f3f3 calc(50% - 425px),
        #ffffff calc(50% - 425px),
        #ffffff calc(50% + 425px),
        #f3f3f3 calc(50% + 425px),
        #f3f3f3 100%
    );
    background-attachment: local;
}
.stApp {
    background: transparent;
}
header[data-testid="stHeader"] {
    display: none;
}
.block-container {
    max-width: 850px;
    min-height: 100vh;
    padding: 4.5rem 4rem 6rem;
    background: transparent;
}
.st-key-lesson_selector {
    max-width: 25rem;
    margin: 0 auto 1.4rem;
}
.st-key-lesson_selector label p {
    color: #444444;
    font-weight: 700;
}
.st-key-lesson_selector [data-baseweb="select"] > div {
    border-color: #111111 !important;
    border-radius: 9px !important;
    background: #ffffff !important;
}
.lesson-heading {
    position: relative;
    margin: 0 0 1rem;
    text-align: center;
}
.page-heading {
    margin: 1.15rem 0 0.2rem;
    color: var(--ink);
    font-size: 1.75rem;
    font-weight: 780;
    letter-spacing: -0.035em;
}
.lesson-heading h1 {
    margin: 0;
    color: #111111;
    font-size: 1.55rem;
    font-weight: 780;
    letter-spacing: -0.035em;
}
.lesson-mark {
    position: absolute;
    top: 50%;
    right: 0.25rem;
    color: #bdbdbd;
    font-size: 1.7rem;
    transform: translateY(-50%);
}
.st-key-dictation_input {
    margin-top: 1.15rem;
}
.st-key-dictation_input textarea {
    min-height: 190px !important;
    padding: 1rem 1.15rem !important;
    border: 1.5px solid #111111 !important;
    border-radius: 10px !important;
    background: #fafafa !important;
    color: #171717 !important;
    font-size: 1.12rem !important;
    line-height: 1.45 !important;
    box-shadow: none !important;
}
.st-key-dictation_input textarea::placeholder {
    color: #a9a9a9 !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}
.st-key-dictation_input [data-baseweb="textarea"] {
    border: 0 !important;
    background: transparent !important;
}
.st-key-solution_button {
    width: fit-content;
    margin-right: auto;
    margin-left: auto;
    padding: 1.2rem 0 1.55rem;
}
.st-key-solution_button .stButton {
    display: flex;
    justify-content: center;
}
.st-key-solution_button button {
    min-width: 145px;
    min-height: 48px;
    border: 1.5px solid #111111 !important;
    border-radius: 10px !important;
    background: #a9dfae !important;
    color: #111111 !important;
    font-size: 1.15rem !important;
    font-weight: 780 !important;
    box-shadow: none !important;
}
.st-key-solution_button button p {
    font-size: 1.15rem !important;
    font-weight: 780 !important;
}
.st-key-solution_button button:hover {
    background: #98d5a0 !important;
}
.st-key-solution_card {
    min-height: 270px;
    padding: 1.35rem 1.2rem 1.2rem;
    border: 1.5px solid #111111;
    border-radius: 11px;
    background: #eefaf5;
}
.solution-german,
.solution-english {
    text-align: center;
    font-size: 1.25rem;
    font-weight: 760;
    line-height: 1.3;
}
.solution-german {
    color: #bc4c4a;
}
.solution-english {
    margin-top: 0.55rem;
    color: #0969d8;
}
.solution-passage {
    margin-top: 0.65rem;
    color: #111111;
    font-size: 1.12rem;
    line-height: 1.42;
}
[class*="st-key-sentence_card_"] {
    margin-top: 1.25rem;
    padding: 1rem 0.8rem 1.35rem;
    border: 1.5px solid #111111;
    border-radius: 11px;
    background: #ebfaf8;
}
.sentence-card-header {
    position: relative;
    margin: 0 0 0.75rem;
}
.sentence-card-header h2 {
    margin: 0;
    color: #111111;
    font-size: 1.35rem;
    font-weight: 780;
}
.sentence-card-mark {
    position: absolute;
    top: 50%;
    right: 0.1rem;
    color: #b9c4c3;
    font-size: 1.55rem;
    transform: translateY(-50%);
}
.sentence-source {
    margin: 0.9rem 0 1.15rem;
    color: #111111;
    font-size: 1.13rem;
    line-height: 1.4;
}
.translation-heading {
    margin-bottom: 0.85rem;
    color: #111111;
    font-size: 1.2rem;
    font-weight: 780;
}
.sentence-translation {
    margin-bottom: 1.05rem;
    color: #111111;
    font-size: 1.08rem;
    line-height: 1.4;
}
.breakdown-group {
    margin-top: 1.75rem;
}
.breakdown-group + .breakdown-group {
    margin-top: 2.25rem;
}
.breakdown-item + .breakdown-item {
    margin-top: 1.15rem;
}
.breakdown-item.phrase {
    margin-top: 1.55rem;
}
.breakdown-expression {
    color: #111111;
    font-size: 1.2rem;
    line-height: 1.35;
    letter-spacing: -0.012em;
}
.breakdown-item.phrase .breakdown-expression {
    color: #696a77;
}
.breakdown-arrow {
    display: inline-block;
    margin: 0 0.25rem;
    font-weight: 400;
}
.breakdown-term {
    position: relative;
    display: inline-block;
    font-weight: 780;
}
.breakdown-meaning {
    font-weight: 400;
}
.breakdown-term.has-verb-help {
    cursor: help;
}
.breakdown-term.has-verb-help {
    text-decoration: underline dotted;
    text-underline-offset: 0.2rem;
}
.grammar-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.38rem;
    margin-top: 0.42rem;
}
.grammar-tag {
    position: relative;
    display: inline-flex;
    align-items: center;
    min-height: 1.55rem;
    padding: 0.12rem 0.62rem;
    border: 1.5px solid;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 560;
    line-height: 1.15;
    white-space: nowrap;
    cursor: help;
}
.grammar-tag:focus {
    outline: 2px solid #111827;
    outline-offset: 2px;
}
.grammar-tag-tooltip {
    visibility: hidden;
    position: absolute;
    z-index: 1200;
    bottom: calc(100% + 0.5rem);
    left: 0;
    width: max-content;
    max-width: min(16rem, calc(100vw - 3rem));
    padding: 0.55rem 0.65rem;
    border-radius: 0.5rem;
    background: #111827;
    box-shadow: 0 0.45rem 1rem rgba(0, 0, 0, 0.24);
    color: #f9fafb;
    font-size: 0.78rem;
    font-weight: 450;
    line-height: 1.35;
    text-align: left;
    white-space: normal;
    opacity: 0;
    pointer-events: none;
    transition: opacity 120ms ease;
}
.grammar-tags .grammar-tag:last-child .grammar-tag-tooltip {
    right: 0;
    left: auto;
}
.grammar-tag:hover .grammar-tag-tooltip,
.grammar-tag:focus .grammar-tag-tooltip {
    visibility: visible;
    opacity: 1;
}
.tag-time {
    border-color: #16a36a;
    background: #d8f1c9;
    color: #286b22;
}
.tag-verb {
    border-color: #8929a5;
    background: #ddb3eb;
    color: #6e2089;
}
.tag-tense {
    border-color: #202020;
    background: #ffffff;
    color: #171717;
}
.tag-role {
    border-color: #ce3c3c;
    background: #f5c2bf;
    color: #a22d2d;
}
.tag-word-class {
    border-color: #b3c43d;
    background: #f0f5cd;
    color: #708f36;
}
.tag-structure {
    border-color: #28aeb4;
    background: #bce8e8;
    color: #176f74;
}
.tag-case {
    border-color: #4f7fc5;
    background: #d8e6fb;
    color: #315f9e;
}
.tag-form {
    border-color: #d18a18;
    background: #ffe7bb;
    color: #8b5a08;
}
.tag-noun {
    border-color: #4774b8;
    background: #dce7fa;
    color: #2f568e;
}
.tag-connector {
    border-color: #d06b31;
    background: #f8dbc6;
    color: #97451f;
}
.verb-tooltip {
    display: block;
    visibility: hidden;
    position: absolute;
    z-index: 1000;
    bottom: calc(100% + 0.6rem);
    left: 0;
    width: 19rem;
    padding: 0.75rem;
    border-radius: 0.6rem;
    background: #111827;
    box-shadow: 0 0.5rem 1.25rem rgba(0, 0, 0, 0.28);
    color: #f9fafb;
    font-size: 0.82rem;
    font-weight: 400;
    line-height: 1.35;
    text-align: left;
    opacity: 0;
    pointer-events: none;
    transition: opacity 120ms ease;
}
.breakdown-term.has-verb-help:hover .verb-tooltip,
.breakdown-term.has-verb-help:focus .verb-tooltip {
    visibility: visible;
    opacity: 1;
}
@media (max-width: 700px) {
    [data-testid="stAppViewContainer"] {
        background: #ffffff;
    }
    .block-container {
        padding: 2rem 1rem 4rem;
    }
    .lesson-heading h1 {
        padding-right: 2rem;
        padding-left: 2rem;
        font-size: 1.35rem;
    }
    .solution-german,
    .solution-english {
        font-size: 1.08rem;
    }
    .breakdown-expression {
        font-size: 1.08rem;
    }
    .grammar-tag-tooltip,
    .grammar-tags .grammar-tag:last-child .grammar-tag-tooltip {
        position: fixed;
        z-index: 2000;
        right: 1rem;
        bottom: 1rem;
        left: 1rem;
        width: auto;
        max-width: none;
    }
}
</style>
"""

MODERN_STYLES = """
<style>
:root {
    --page: #edf1f4;
    --paper: #ffffff;
    --paper-soft: #f5f7f9;
    --ink: #14222d;
    --muted: #687680;
    --line: #d9e0e5;
    --line-strong: #aebbc4;
    --coral: #ed6a4d;
    --coral-soft: #ffebe5;
    --blue: #285f8f;
    --blue-soft: #e9f1f8;
    --green: #2f7357;
    --green-soft: #e4f3eb;
    --navy: #132733;
    --navy-light: #1e3b49;
    --shadow: 0 18px 46px rgba(23, 43, 54, 0.09);
}
[data-testid="stAppViewContainer"] {
    background: var(--page);
    color: var(--ink);
    font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
}
.block-container {
    position: relative;
    max-width: 1020px;
    min-height: 100vh;
    padding: 0.9rem 2.5rem 6rem;
    background: transparent;
}
.st-key-app_toolbar {
    position: absolute;
    z-index: 20;
    top: 3.1rem;
    right: 2.5rem;
    width: 11rem;
    margin: 0;
}
.st-key-app_toolbar .stButton {
    display: flex;
    justify-content: flex-end;
}
.st-key-reset_progress_trigger button {
    min-height: 36px;
    border: 1px solid var(--line) !important;
    border-radius: 999px !important;
    background: var(--paper) !important;
    color: var(--muted) !important;
    box-shadow: none !important;
}
.st-key-reset_progress_trigger button:hover {
    border-color: #b75a4b !important;
    color: #a34335 !important;
}
.st-key-reset_confirmation {
    margin: 0.25rem 0 1.2rem;
    padding: 1rem 1.1rem;
    border: 1px solid #e4b8ae;
    border-radius: 14px;
    background: #fff7f5;
}
[data-testid="stTabs"] [role="tablist"] {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: min(28rem, calc(100% - 12.5rem));
    gap: 0.35rem;
    padding: 0.38rem;
    border: 1px solid #c8d3da;
    border-radius: 16px;
    background: #dde5ea;
    box-shadow:
        inset 0 1px 2px rgba(23, 43, 54, 0.08),
        0 6px 18px rgba(23, 43, 54, 0.06);
}
[data-testid="stTabs"] [data-testid="stTab"] {
    width: 100% !important;
    min-width: 0 !important;
    min-height: 3rem;
    justify-content: center !important;
    margin: 0;
    padding: 0.65rem 1rem !important;
    border: 0 !important;
    border-radius: 11px !important;
    background: transparent !important;
    color: var(--muted) !important;
    font-size: 1rem !important;
    font-weight: 720 !important;
    letter-spacing: -0.01em;
    transition:
        color 140ms ease,
        background 140ms ease,
        box-shadow 140ms ease,
        transform 140ms ease;
}
[data-testid="stTabs"] [data-testid="stTab"] p {
    font-size: inherit !important;
    font-weight: inherit !important;
}
[data-testid="stTabs"] [data-testid="stTab"]:hover:not([aria-selected="true"]) {
    background: rgba(255, 255, 255, 0.62) !important;
    color: var(--ink) !important;
}
[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] {
    background: var(--navy) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 14px rgba(23, 43, 54, 0.22);
}
[data-testid="stTabs"] .react-aria-SelectionIndicator {
    display: none !important;
}
.st-key-lesson_picker {
    margin: 1rem 0 1.15rem;
    padding: 0.9rem 1rem 1rem;
    border: 1px solid var(--line);
    border-radius: 16px;
    background: var(--paper);
    box-shadow: 0 6px 20px rgba(23, 43, 54, 0.045);
}
.st-key-lesson_selector {
    max-width: none;
    margin: 0;
}
.st-key-lesson_selector label p {
    color: var(--ink);
    font-size: 0.9rem;
    font-weight: 740;
}
.st-key-lesson_selector [data-baseweb="select"] > div {
    min-height: 3rem;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    background: var(--paper-soft) !important;
    box-shadow: none !important;
}
.st-key-lesson_selector [role="group"] {
    min-height: 2.75rem;
    border: 0 !important;
    border-radius: 10px !important;
    background: var(--paper-soft) !important;
}
.lesson-heading {
    margin: 0;
    text-align: left;
}
.lesson-heading a {
    display: none !important;
}
.lesson-heading h1 {
    color: #ffffff;
    font-size: clamp(1.75rem, 3.5vw, 2.2rem);
    font-weight: 780;
    letter-spacing: -0.04em;
}
.lesson-introduction {
    margin: 0 0 1.35rem;
}
.lesson-introduction h1 {
    margin: 0.65rem 0 0.18rem;
}
.lesson-introduction p {
    margin: 0;
    color: #c0ccd3;
    font-size: 1rem;
}
.lesson-level {
    display: inline-flex;
    align-items: center;
    min-height: 1.65rem;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.12);
    color: #d9e6ec;
    font-size: 0.78rem;
    font-weight: 760;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.lesson-mark,
.sentence-card-mark {
    display: none;
}
.st-key-dictation_input {
    margin-top: 1rem;
}
.st-key-dictation_input textarea {
    min-height: 165px !important;
    padding: 1.1rem 1.2rem !important;
    border: 1px solid var(--line) !important;
    border-radius: 16px !important;
    background: var(--paper) !important;
    color: var(--ink) !important;
    font-size: 1.05rem !important;
    line-height: 1.55 !important;
    box-shadow: 0 12px 30px rgba(71, 61, 43, 0.05) !important;
}
.st-key-dictation_input textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(49, 93, 148, 0.12) !important;
}
.st-key-dictation_input textarea::placeholder {
    color: #aaa79f !important;
    font-weight: 500 !important;
}
.st-key-solution_button {
    width: fit-content;
    margin: 0 0 0 auto;
    padding: 0.65rem 0 1.8rem;
}
.st-key-solution_button .stButton {
    justify-content: flex-end;
}
.st-key-solution_button button {
    min-width: 0;
    min-height: 44px;
    padding: 0.6rem 1.1rem;
    border: 0 !important;
    border-radius: 12px !important;
    background: var(--coral) !important;
    color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 650 !important;
    box-shadow: 0 8px 18px rgba(207, 99, 78, 0.2) !important;
}
.st-key-solution_button button p {
    font-size: 0.95rem !important;
    font-weight: 650 !important;
}
.st-key-solution_button button:hover {
    background: #bd5744 !important;
    transform: translateY(-1px);
}
.st-key-solution_card {
    min-height: 0;
    padding: 1.75rem;
    border: 0;
    border-radius: 26px;
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
    box-shadow: 0 24px 60px rgba(19, 39, 51, 0.2);
}
.listen-label {
    margin-bottom: 0.5rem;
    color: #afbec7;
    font-size: 0.78rem;
    font-weight: 720;
    letter-spacing: 0.075em;
    text-transform: uppercase;
}
.st-key-solution_card [data-testid="stCaptionContainer"],
.st-key-solution_card [data-testid="stCaptionContainer"] p {
    margin: 0.35rem 0 0.85rem;
    color: #d5e0e6 !important;
    font-size: 0.9rem !important;
}
.solution-german,
.solution-english {
    text-align: left;
    line-height: 1.35;
}
.solution-german {
    color: var(--coral);
    font-size: 1.25rem;
    font-weight: 720;
}
.solution-english {
    margin-top: 0.25rem;
    color: var(--blue);
    font-size: 1rem;
    font-weight: 600;
}
.solution-passage {
    margin-top: 0.75rem;
    padding: 1.2rem 1.25rem 0;
    border-top: 1px solid rgba(255, 255, 255, 0.14);
    color: #f3f7f9;
    font-size: 1.06rem;
    line-height: 1.62;
}
.section-heading {
    margin: 2.5rem 0 0.4rem;
}
.section-heading span {
    color: var(--ink);
    font-size: 1.4rem;
    font-weight: 760;
    letter-spacing: -0.025em;
}
.section-heading p {
    margin: 0.25rem 0 0;
    color: var(--muted);
    font-size: 0.9rem;
}
.st-key-lesson_completion {
    margin-top: 1.5rem;
    padding: 1.15rem;
    border: 1px solid var(--line);
    border-radius: 16px;
    background: var(--paper);
}
.st-key-lesson_completion button {
    border: 0 !important;
    border-radius: 11px !important;
    background: var(--ink) !important;
    color: #ffffff !important;
    box-shadow: none !important;
}
.st-key-speaking_practice {
    margin-top: 1.5rem;
    padding: 1.5rem;
    border: 1px solid #cfe2d8;
    border-radius: 22px;
    background: linear-gradient(135deg, #f4fbf7 0%, #edf6f1 100%);
}
.speaking-practice-heading {
    margin: 0 0 0.3rem;
    color: var(--green);
    font-size: 1.3rem;
    font-weight: 760;
    letter-spacing: -0.025em;
}
.speaking-practice-intro {
    margin: 0 0 1rem;
    color: var(--muted);
    font-size: 0.92rem;
    line-height: 1.5;
}
.speaking-reference-list {
    display: grid;
    gap: 0.55rem;
    margin: 1rem 0 1.15rem;
}
.speaking-reference-line {
    padding: 0.75rem 0.85rem;
    border: 1px solid #d5e1ec;
    border-radius: 12px;
    background: var(--blue-soft);
    color: var(--blue);
    font-size: 0.96rem;
    line-height: 1.45;
}
.speaking-reference-line strong {
    margin-right: 0.35rem;
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 760;
}
/*
Keep recall practice honest while Streamlit's recorder is active. The audio
widget changes its action label from "Record" to "Stop recording", which lets
CSS enter and leave focus mode immediately without waiting for a Python rerun.
The English cue and the stop control remain usable above the blur layer.
*/
body:has(
    .st-key-speaking_practice
    [data-testid="stAudioInputActionButton"][aria-label="Stop recording"]
) [data-testid="stMain"] {
    overflow: hidden !important;
    overscroll-behavior: none;
}
body:has(
    .st-key-speaking_practice
    [data-testid="stAudioInputActionButton"][aria-label="Stop recording"]
) [data-testid="stMain"]::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 999;
    background: rgba(238, 246, 242, 0.38);
    backdrop-filter: blur(14px) saturate(0.72);
    -webkit-backdrop-filter: blur(14px) saturate(0.72);
    pointer-events: auto;
}
body:has(
    .st-key-speaking_practice
    [data-testid="stAudioInputActionButton"][aria-label="Stop recording"]
) .speaking-reference-list,
body:has(
    .st-key-speaking_practice
    [data-testid="stAudioInputActionButton"][aria-label="Stop recording"]
) [class*="st-key-speaking_recorder_"] {
    position: relative;
    z-index: 1000;
}
body:has(
    .st-key-speaking_practice
    [data-testid="stAudioInputActionButton"][aria-label="Stop recording"]
) .speaking-reference-list {
    padding: 0.7rem;
    border: 1px solid #bfd7ca;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.97);
    box-shadow: 0 18px 48px rgba(31, 54, 46, 0.2);
}
.speaking-audio-label {
    display: block;
    margin: 1.05rem 0 0.4rem;
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 760;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.st-key-speaking_reveal button {
    border: 1px solid #a7c4b3 !important;
    border-radius: 10px !important;
    background: transparent !important;
    color: var(--green) !important;
    font-weight: 700 !important;
}
.speaking-german-reveal {
    margin-top: 0.8rem;
    padding: 0.95rem 1rem;
    border: 1px solid #d5e6dc;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.78);
}
.speaking-german-reveal strong {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--green);
    font-size: 0.72rem;
    font-weight: 760;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.speaking-german-reveal p {
    margin: 0.35rem 0;
    color: var(--ink);
    font-size: 1rem;
    line-height: 1.5;
}
.st-key-speaking_analysis_action {
    margin-top: 1rem;
}
.st-key-speaking_analysis_action button {
    width: 100%;
    min-height: 44px;
    border: 0 !important;
    border-radius: 12px !important;
    background: var(--green) !important;
    color: #ffffff !important;
    font-weight: 720 !important;
    box-shadow: 0 8px 18px rgba(47, 115, 87, 0.18) !important;
}
.st-key-speaking_analysis_action button:disabled {
    background: #a9b9b1 !important;
    color: #eef3f0 !important;
}
.speech-feedback {
    margin-top: 1rem;
    padding: 1rem;
    border: 1px solid #c8ddd1;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.86);
}
.speech-feedback h3 {
    margin: 0 0 0.75rem;
    color: var(--ink);
    font-size: 1.05rem;
}
.speech-feedback-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.55rem;
}
.speech-feedback-stat {
    padding: 0.75rem;
    border-radius: 11px;
    background: var(--paper-soft);
}
.speech-feedback-stat strong,
.speech-feedback-stat span {
    display: block;
}
.speech-feedback-stat strong {
    color: var(--green);
    font-size: 1.02rem;
}
.speech-feedback-stat span {
    margin-top: 0.18rem;
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 650;
    text-transform: uppercase;
}
.speech-transcript {
    margin: 0.9rem 0;
    padding: 0.8rem;
    border-left: 3px solid var(--blue);
    border-radius: 0 10px 10px 0;
    background: var(--blue-soft);
    color: var(--ink);
    line-height: 1.5;
}
.speech-transcript strong {
    display: block;
    margin-bottom: 0.25rem;
    color: var(--blue);
    font-size: 0.72rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.speech-differences {
    display: grid;
    gap: 0.45rem;
    margin: 0.75rem 0;
}
.speech-difference {
    padding: 0.6rem 0.7rem;
    border: 1px solid #e6d8b7;
    border-radius: 9px;
    background: #fff9ec;
    color: #5b4a28;
    font-size: 0.88rem;
    line-height: 1.4;
}
.speech-alternative {
    padding: 0.7rem 0.8rem;
    border: 1px solid #b8d9c6;
    border-radius: 10px;
    background: #edf8f1;
    color: #285c44;
    font-size: 0.88rem;
    line-height: 1.45;
}
.speech-alternative + .speech-alternative {
    margin-top: 0.45rem;
}
.speech-reviewed-transcript {
    margin-top: 0.65rem;
    padding: 0.8rem;
    border-left: 3px solid var(--green);
    border-radius: 0 10px 10px 0;
    background: var(--green-soft);
    color: var(--ink);
    line-height: 1.5;
}
.speech-reviewed-transcript strong {
    display: block;
    margin-bottom: 0.25rem;
    color: var(--green);
    font-size: 0.72rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.st-key-speech_transcript_review {
    margin-top: 1rem;
    padding: 1rem;
    border: 1px solid #c8ddd1;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.72);
}
.st-key-speech_transcript_review textarea {
    min-height: 125px !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    background: #ffffff !important;
}
.st-key-speech_transcript_update button {
    border: 1px solid #a7c4b3 !important;
    border-radius: 10px !important;
    background: #ffffff !important;
    color: var(--green) !important;
    font-weight: 700 !important;
}
.speech-feedback-note {
    margin: 0.8rem 0 0;
    color: var(--muted);
    font-size: 0.8rem;
    line-height: 1.45;
}
@media (max-width: 700px) {
    .speech-feedback-grid {
        grid-template-columns: 1fr;
    }
}
[class*="st-key-sentence_card_"] {
    margin-top: 1.15rem;
    padding: 1.65rem;
    border: 0;
    border-radius: 22px;
    background: var(--paper);
    box-shadow: var(--shadow);
}
.sentence-card-header {
    margin: 0 0 0.85rem;
}
.sentence-card-header h2 {
    display: inline-flex;
    min-height: 1.65rem;
    align-items: center;
    padding: 0.18rem 0.58rem;
    border-radius: 999px;
    background: var(--coral-soft);
    color: #b84732;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.075em;
    text-transform: uppercase;
}
.sentence-copy {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.55rem;
    margin-top: 0.75rem;
}
.sentence-language {
    min-width: 0;
    padding: 1rem 1.05rem;
    border: 1px solid var(--line);
    border-radius: 14px;
    background: var(--paper-soft);
}
.sentence-language.translation {
    border-color: #d5e1ec;
    background: var(--blue-soft);
}
.copy-label {
    display: block;
    margin-bottom: 0.38rem;
    color: var(--muted);
    font-size: 0.7rem;
    font-weight: 760;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.sentence-source {
    margin: 0;
    color: var(--ink);
    font-size: 1.08rem;
    font-weight: 650;
    line-height: 1.5;
}
.translation-heading {
    display: none;
}
.sentence-translation {
    margin: 0;
    color: var(--blue);
    font-size: 1.02rem;
    line-height: 1.5;
}
.meaning-map-heading {
    display: flex;
    gap: 0.65rem;
    align-items: baseline;
    margin-top: 1.25rem;
    color: var(--ink);
}
.meaning-map-heading strong {
    font-size: 0.92rem;
}
.meaning-map-heading span {
    color: var(--muted);
    font-size: 0.8rem;
}
.breakdown-group {
    margin-top: 0.65rem;
}
.breakdown-group + .breakdown-group {
    margin-top: 0.8rem;
}
.meaning-list {
    display: grid;
    gap: 0.55rem;
}
.meaning-row {
    position: relative;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 0.9fr);
    gap: 1rem;
    align-items: start;
    padding: 0.78rem 0.9rem;
    border: 1px solid var(--line);
    border-radius: 12px;
    background: var(--paper-soft);
}
.meaning-row.phrase {
    margin: 0.12rem 0 0.28rem 1.1rem;
    border-color: #c7d8e7;
    background: var(--blue-soft);
}
.meaning-row.phrase::before {
    position: absolute;
    top: 0.9rem;
    left: -0.75rem;
    color: #6c8ca7;
    content: "↳";
    font-size: 0.9rem;
    font-weight: 750;
}
.meaning-german,
.meaning-english {
    min-width: 0;
}
.meaning-english {
    color: #415d72;
}
.literal-meaning {
    margin-top: 0.18rem;
    color: var(--muted);
    font-size: 0.78rem;
}
.meaning-row.phrase .meaning-german,
.meaning-row.phrase .meaning-english {
    color: var(--blue);
}
.meaning-label {
    display: block;
    margin-bottom: 0.18rem;
    color: var(--muted);
    font-size: 0.67rem;
    font-weight: 730;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
.standalone-words,
.loose-word-list {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 62px minmax(0, 0.92fr);
    gap: 0.65rem;
}
.standalone-words .breakdown-node,
.loose-word-list .breakdown-node {
    grid-column: 1;
}
.loose-word-list {
    margin-top: 0.8rem;
}
.breakdown-node {
    position: relative;
    min-width: 0;
    padding: 0.8rem 0.85rem;
    border: 1px solid var(--line);
    border-radius: 13px;
    background: var(--paper-soft);
}
.breakdown-node.phrase-source {
    border-color: #cad7e7;
    background: var(--blue-soft);
}
.breakdown-node.phrase-result {
    align-self: center;
    padding: 1rem;
    border-color: #b9cce2;
    background: var(--blue-soft);
    box-shadow: 0 10px 24px rgba(49, 93, 148, 0.08);
}
.breakdown-node.phrase-result .breakdown-term,
.breakdown-node.phrase-result .breakdown-meaning {
    color: var(--blue);
}
.breakdown-expression {
    color: var(--ink);
    font-size: 1rem;
    line-height: 1.4;
}
.breakdown-term {
    font-weight: 720;
}
.breakdown-arrow {
    margin: 0 0.28rem;
    color: var(--muted);
}
.flow-group {
    display: grid;
    gap: 0.9rem;
}
.breakdown-stage {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 62px minmax(0, 0.92fr);
    align-items: stretch;
    gap: 0;
}
.flow-source-list {
    position: relative;
    display: grid;
    align-content: center;
    gap: 0.55rem;
}
.flow-source-list .breakdown-node::after {
    content: "";
    position: absolute;
    top: 50%;
    right: -31px;
    width: 31px;
    height: 2px;
    background: var(--line-strong);
    transform: translateY(-50%);
}
.flow-source-list.has-multiple::before {
    content: "";
    position: absolute;
    z-index: 1;
    top: calc(1.15rem + 2px);
    right: -31px;
    bottom: calc(1.15rem + 2px);
    width: 2px;
    background: var(--line-strong);
}
.flow-connector {
    position: relative;
    display: grid;
    place-items: center end;
    color: var(--blue);
}
.flow-connector::before {
    content: "";
    position: absolute;
    top: 50%;
    left: 31px;
    right: 7px;
    height: 2px;
    background: var(--line-strong);
    transform: translateY(-50%);
}
.flow-connector span {
    position: relative;
    z-index: 2;
    display: grid;
    place-items: center;
    width: 1.35rem;
    height: 1.35rem;
    border-radius: 50%;
    background: var(--blue);
    color: #ffffff;
    font-size: 1.1rem;
    line-height: 1;
}
.muted-node {
    color: var(--muted);
    font-style: italic;
}
.grammar-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.32rem;
    margin-top: 0.48rem;
}
.grammar-tag {
    min-height: 1.45rem;
    padding: 0.14rem 0.52rem;
    border-width: 1px;
    font-size: 0.72rem;
    font-weight: 600;
}
.verb-tooltip,
.grammar-tag-tooltip {
    border: 1px solid #343a46;
    border-radius: 10px;
    background: #1e2430;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
}
.grammar-tag-tooltip strong,
.grammar-tag-tooltip span,
.grammar-tag-tooltip p {
    display: block;
}
.grammar-tag-tooltip strong {
    color: #ffffff;
    font-size: 0.82rem;
    text-transform: capitalize;
}
.grammar-tag-tooltip span {
    margin-top: 0.12rem;
    color: #9fb1bd;
    font-size: 0.62rem;
    font-weight: 760;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
.grammar-tag-tooltip p {
    margin: 0.42rem 0 0;
    color: #d7e1e7;
}
.verb-tooltip {
    position: fixed;
    z-index: 2200;
    top: 50%;
    bottom: auto;
    left: 50%;
    width: 32rem;
    max-width: min(32rem, calc(100vw - 3rem));
    max-height: calc(100vh - 3rem);
    padding: 1rem;
    overflow-y: auto;
    border-color: #40505e;
    border-radius: 14px;
    background: #17232d;
    font-size: 0.8rem;
    line-height: 1.35;
    pointer-events: auto;
    transform: translate(-50%, -50%);
}
.verb-dictionary-label,
.verb-section-label {
    display: block;
    color: #9fb1bd;
    font-size: 0.67rem;
    font-weight: 760;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.verb-dictionary {
    display: grid;
    grid-template-columns: minmax(0, auto) minmax(0, 1fr);
    gap: 0.7rem;
    align-items: baseline;
    margin-top: 0.22rem;
}
.verb-dictionary strong {
    color: #ffffff;
    font-size: 1.05rem;
}
.verb-dictionary span {
    color: #c6d7e1;
    font-size: 0.88rem;
}
.verb-section {
    display: block;
    margin-top: 0.85rem;
    padding-top: 0.8rem;
    border-top: 1px solid #3a4955;
}
.verb-current-form {
    display: flex;
    flex-wrap: wrap;
    gap: 0.32rem;
    align-items: baseline;
    margin-top: 0.32rem;
    color: #f3f7f9;
    font-size: 0.88rem;
}
.verb-current-form strong {
    color: #ffffff;
}
.verb-current-form .arrow {
    color: #8fa6b5;
}
.verb-tense-name {
    margin-top: 0.65rem;
    color: #d6e2e9;
    font-size: 0.76rem;
    font-weight: 700;
}
.verb-table {
    display: grid;
    gap: 0.18rem;
    margin-top: 0.38rem;
}
.verb-table-row {
    display: grid;
    grid-template-columns: 4.6rem minmax(0, 1fr) minmax(0, 1.15fr);
    gap: 0.55rem;
    padding: 0.25rem 0.35rem;
    border-radius: 6px;
}
.verb-table-row:nth-child(odd) {
    background: rgba(255, 255, 255, 0.045);
}
.verb-pronoun {
    color: #9fb1bd;
}
.verb-german-form {
    color: #ffffff;
    font-weight: 680;
}
.verb-english-form {
    color: #bed0db;
}
.case-shift {
    position: relative;
    display: inline-block;
    border-radius: 3px;
    text-decoration-line: underline;
    text-decoration-color: var(--coral);
    text-decoration-thickness: 2px;
    text-underline-offset: 0.2rem;
    cursor: help;
}
.case-shift:focus {
    outline: 2px solid var(--coral);
    outline-offset: 2px;
}
.case-shift-tooltip {
    visibility: hidden;
    position: fixed;
    z-index: 2200;
    top: 50%;
    bottom: auto;
    left: 50%;
    width: 40rem;
    max-width: min(40rem, calc(100vw - 3rem));
    max-height: calc(100vh - 3rem);
    padding: 1rem;
    overflow-y: auto;
    border: 1px solid #40505e;
    border-radius: 14px;
    background: #17232d;
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
    color: #f8fafc;
    font-size: 0.8rem;
    font-weight: 450;
    line-height: 1.35;
    text-align: left;
    white-space: normal;
    opacity: 0;
    pointer-events: none;
    transform: translate(-50%, -50%);
    transition: opacity 120ms ease;
}
.case-shift-tooltip span {
    display: block;
}
.case-reference-title {
    color: #ffffff;
    font-size: 1rem;
    font-weight: 760;
}
.case-reference-fields {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.55rem;
    margin-top: 0.7rem;
}
.case-reference-field {
    padding: 0.55rem 0.62rem;
    border: 1px solid #3a4955;
    border-radius: 7px;
    background: rgba(255, 255, 255, 0.035);
}
.case-reference-field > span {
    color: #9fb1bd;
    font-size: 0.65rem;
    font-weight: 760;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}
.case-reference-field strong {
    display: block;
    margin-top: 0.18rem;
    color: #ffffff;
    font-size: 0.9rem;
}
.case-reference-context {
    display: flex !important;
    flex-wrap: wrap;
    gap: 0.35rem;
    margin-top: 0.65rem;
}
.case-reference-context span {
    padding: 0.16rem 0.48rem;
    border: 1px solid #4b5d6a;
    border-radius: 999px;
    color: #d8e5ec;
    font-size: 0.7rem;
    font-weight: 680;
}
.case-reference-section {
    margin-top: 0.8rem;
    padding-top: 0.75rem;
    border-top: 1px solid #3a4955;
}
.case-reference-section > span:first-child {
    color: #9fb1bd;
    font-size: 0.67rem;
    font-weight: 760;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.case-table {
    display: grid !important;
    gap: 0.18rem;
    margin-top: 0.4rem;
}
.case-table-row {
    display: grid !important;
    grid-template-columns: 5.4rem repeat(4, minmax(0, 1fr));
    gap: 0.25rem;
    align-items: center;
}
.case-table.columns-8 {
    overflow-x: auto;
}
.case-table.columns-8 .case-table-row {
    grid-template-columns: 5.4rem repeat(8, minmax(3.3rem, 1fr));
    min-width: 42rem;
}
.case-table-header {
    padding-bottom: 0.2rem;
    border-bottom: 1px solid #3a4955;
}
.case-table-case,
.case-table-heading,
.case-table-cell {
    padding: 0.28rem 0.32rem;
}
.case-table-case,
.case-table-heading {
    color: #9fb1bd;
    font-size: 0.68rem;
    font-weight: 700;
}
.case-table-cell {
    border-radius: 5px;
    color: #ffffff;
    font-weight: 650;
}
.case-table-row:not(.case-table-header):nth-child(even) .case-table-cell,
.case-table-row:not(.case-table-header):nth-child(even) .case-table-case {
    background: rgba(255, 255, 255, 0.04);
}
.case-table-cell.is-current {
    background: #d87355 !important;
    color: #ffffff;
}
.case-shift:hover .case-shift-tooltip,
.case-shift:focus .case-shift-tooltip {
    visibility: visible;
    opacity: 1;
}

.lesson-progress {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.55rem;
    margin: 0 auto 2.2rem;
}
.lesson-step {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    color: #aaa59a;
}
.lesson-step::after {
    flex: 1;
    height: 2px;
    margin-left: 0.15rem;
    background: #dedbd3;
    content: "";
}
.lesson-step:last-child::after {
    display: none;
}
.lesson-step span {
    display: grid;
    width: 1.8rem;
    height: 1.8rem;
    place-items: center;
    border: 1.5px solid currentColor;
    border-radius: 50%;
    font-size: 0.78rem;
    font-weight: 800;
}
.lesson-step small {
    font-size: 0.76rem;
    font-weight: 720;
    white-space: nowrap;
}
.lesson-step.is-active {
    color: #cf634e;
}
.lesson-step.is-done {
    color: #397b51;
}
.lesson-step.is-done span {
    background: #e3f3e8;
}

@media (max-width: 760px) {
    [data-testid="stAppViewContainer"] {
        background: var(--page);
    }
    .block-container {
        padding: 1.25rem 0.85rem 4rem;
    }
    .st-key-app_toolbar {
        top: 3.55rem;
        right: 0.85rem;
        width: 9rem;
    }
    [data-testid="stTabs"] [role="tablist"] {
        width: calc(100% - 9.75rem);
        gap: 0.2rem;
        padding: 0.3rem;
        border-radius: 14px;
    }
    [data-testid="stTabs"] [data-testid="stTab"] {
        min-height: 2.75rem;
        padding: 0.55rem 0.4rem !important;
        border-radius: 10px !important;
        font-size: 1rem !important;
    }
    .lesson-heading h1 {
        padding: 0;
    }
    .st-key-lesson_selector {
        margin-bottom: 1.5rem;
    }
    [class*="st-key-sentence_card_"],
    .st-key-solution_card {
        padding: 1rem;
        border-radius: 16px;
    }
    .sentence-copy {
        grid-template-columns: 1fr;
        gap: 0.65rem;
    }
    .meaning-row {
        grid-template-columns: 1fr;
        gap: 0.35rem;
    }
    .meaning-row.phrase {
        margin-left: 0.75rem;
    }
    .solution-passage {
        padding-right: 0.25rem;
        padding-left: 0.25rem;
    }
    .breakdown-stage {
        grid-template-columns: minmax(0, 1fr) 38px minmax(0, 0.95fr);
    }
    .flow-source-list .breakdown-node::after {
        right: -19px;
        width: 19px;
    }
    .flow-source-list.has-multiple::before {
        right: -19px;
    }
    .flow-connector::before {
        left: 19px;
        right: 5px;
    }
    .breakdown-node {
        padding: 0.7rem;
        border-radius: 11px;
    }
    .breakdown-expression {
        font-size: 0.9rem;
    }
    .standalone-words,
    .loose-word-list {
        grid-template-columns: minmax(0, 1fr) 38px minmax(0, 0.95fr);
    }
    .grammar-tag-tooltip,
    .grammar-tags .grammar-tag:last-child .grammar-tag-tooltip,
    .case-shift-tooltip,
    .verb-tooltip {
        position: fixed;
        z-index: 2000;
        top: auto;
        right: 1rem;
        bottom: 1rem;
        left: 1rem;
        width: auto;
        max-width: none;
        max-height: calc(100vh - 2rem);
        transform: none;
    }
    .verb-table-row {
        grid-template-columns: 4rem minmax(0, 1fr);
    }
    .verb-english-form {
        grid-column: 2;
    }
}

@media (max-width: 520px) {
    .lesson-progress {
        gap: 0.2rem;
    }
    .lesson-step {
        justify-content: center;
    }
    .lesson-step::after,
    .lesson-step small {
        display: none;
    }
    .breakdown-stage {
        grid-template-columns: 1fr;
        gap: 0;
    }
    .standalone-words,
    .loose-word-list {
        grid-template-columns: 1fr;
    }
    .flow-source-list .breakdown-node::after,
    .flow-source-list.has-multiple::before {
        display: none;
    }
    .flow-connector {
        min-height: 2.4rem;
        place-items: end center;
    }
    .flow-connector::before {
        top: 0;
        bottom: 0.35rem;
        left: 50%;
        right: auto;
        width: 2px;
        height: auto;
        transform: translateX(-50%);
    }
    .flow-connector span {
        transform: rotate(90deg);
    }
}
</style>
"""


def article_changes_for_phrase(
    phrase: models.BreakdownItem,
    group: models.BreakdownGroup,
) -> list[models.InflectionHelp]:
    return [
        help_card
        for help_card in case_changes_for_phrase(phrase, group)
        if help_card.kind != "adjective"
    ]


def adjective_changes_for_phrase(
    phrase: models.BreakdownItem,
    group: models.BreakdownGroup,
) -> list[models.InflectionHelp]:
    return [
        help_card
        for help_card in case_changes_for_phrase(phrase, group)
        if help_card.kind == "adjective"
    ]
def case_changes_for_phrase(
    phrase: models.BreakdownItem,
    group: models.BreakdownGroup,
) -> list[models.InflectionHelp]:
    """Return the phrase's validated inflection records.

    Compiled lessons store these records directly.  The fallback keeps older
    prepared lessons compatible while still producing the same typed schema.
    """
    return phrase.inflection_help or inflections_for_phrase(phrase, group)


def render_inflection_table(help_card: models.InflectionHelp) -> str:
    table = table_for_help(help_card)
    columns = columns_for_help(help_card)
    selected_column = selected_column_for_help(help_card)
    header = "".join(
        f"<span class='case-table-heading'>{escape(column)}</span>"
        for column in columns
    )
    rows = []
    for case, forms in table.items():
        cells = "".join(
            "<span class='case-table-cell"
            + (
                " is-current"
                if case == help_card.case and column == selected_column
                else ""
            )
            + f"'>{escape(form)}</span>"
            for column, form in enumerate(forms)
        )
        rows.append(
            "<span class='case-table-row'>"
            f"<span class='case-table-case'>{escape(case)}</span>{cells}</span>"
        )
    return (
        f"<span class='case-table columns-{len(columns)}'>"
        "<span class='case-table-row case-table-header'>"
        "<span class='case-table-case'>case</span>"
        f"{header}</span>{''.join(rows)}</span>"
    )


def render_inflection_tooltip(help_card: models.InflectionHelp) -> str:
    kind_labels = {
        "definite-article": "Definite article",
        "indefinite-article": "Indefinite article",
        "possessive-determiner": "Possessive determiner",
        "adjective": "Adjective ending",
        "personal-pronoun": "Personal pronoun",
    }
    paradigm_labels = {
        "definite": "Definite-article forms",
        "indefinite": "Indefinite-article forms",
        "possessive": "Possessive forms",
        "weak-adjective": "Weak adjective endings",
        "mixed-adjective": "Mixed adjective endings",
        "strong-adjective": "Strong adjective endings",
        "personal-pronoun": "Personal-pronoun forms",
    }
    sentence_form = help_card.resolved_form or help_card.surface
    contraction = (
        "<span class='case-reference-field'>"
        "<span>Contraction</span>"
        f"<strong>{escape(help_card.surface)} = {escape(help_card.contraction or '')}</strong>"
        "</span>"
        if help_card.contraction
        else ""
    )
    context_values = [help_card.case]
    if help_card.gender:
        context_values.append(help_card.gender)
    if help_card.pronoun_slot:
        context_values.append(help_card.pronoun_slot.replace("-", " "))
    context_values.append(help_card.number)
    context_chips = "".join(
        f"<span>{escape(value)}</span>" for value in context_values
    )
    return (
        "<span class='case-shift-tooltip' role='tooltip'>"
        f"<span class='case-reference-title'>{kind_labels[help_card.kind]}</span>"
        "<span class='case-reference-fields'>"
        "<span class='case-reference-field'><span>Base form</span>"
        f"<strong>{escape(help_card.base)}</strong></span>"
        "<span class='case-reference-field'><span>Sentence form</span>"
        f"<strong>{escape(sentence_form)}</strong></span>"
        f"{contraction}"
        "</span>"
        "<span class='case-reference-context'>"
        f"{context_chips}"
        "</span>"
        "<span class='case-reference-section'>"
        f"<span>{paradigm_labels[help_card.paradigm]}</span>"
        f"{render_inflection_table(help_card)}"
        "</span>"
        "</span>"
    )


def render_phrase_german(
    item: models.BreakdownItem,
    article_changes: list[models.InflectionHelp],
) -> str:
    if not article_changes:
        return escape(item.german)

    positioned: list[tuple[int, int, models.InflectionHelp]] = []
    cursor_by_surface: dict[str, int] = {}
    for help_card in article_changes:
        start_at = cursor_by_surface.get(help_card.surface.casefold(), 0)
        match = re.search(
            rf"(?<!\w){re.escape(help_card.surface)}(?!\w)",
            item.german[start_at:],
            flags=re.IGNORECASE,
        )
        if match is None:
            continue
        start = start_at + match.start()
        end = start_at + match.end()
        cursor_by_surface[help_card.surface.casefold()] = end
        positioned.append((start, end, help_card))

    fragments: list[str] = []
    cursor = 0
    for start, end, help_card in sorted(positioned, key=lambda item: item[0]):
        fragments.append(escape(item.german[cursor:start]))
        visible = escape(item.german[start:end])
        sentence_form = help_card.resolved_form or help_card.surface
        grammar_slot = help_card.gender or (help_card.pronoun_slot or "")
        aria_label = (
            f"{help_card.base} to {sentence_form}; {help_card.case}, "
            f"{grammar_slot}, {help_card.number}."
        )
        fragments.append(
            "<span class='case-shift' tabindex='0' "
            f"aria-label='{escape(aria_label)}'>"
            f"{visible}"
            f"{render_inflection_tooltip(help_card)}</span>"
        )
        cursor = end
    fragments.append(escape(item.german[cursor:]))
    return "".join(fragments)


def render_conjugation_rows(
    forms: list[models.ConjugationForm],
    english_forms: tuple[str, ...],
) -> str:
    return "".join(
        "<span class='verb-table-row'>"
        f"<span class='verb-pronoun'>{escape(form.pronoun)}</span>"
        f"<span class='verb-german-form'>{escape(form.verb)}</span>"
        f"<span class='verb-english-form'>{escape(english)}</span>"
        "</span>"
        for form, english in zip(forms, english_forms, strict=True)
    )


def render_verb_tooltip(item: models.BreakdownItem) -> str:
    help_card = item.verb_help
    if help_card is None:
        return ""

    present_rows = render_conjugation_rows(
        present_forms(help_card),
        english_present_forms(help_card),
    )
    tense_is_present = (
        "präsens" in help_card.tense.casefold()
        or "present" in help_card.tense.casefold()
    )
    current_table = ""
    if not tense_is_present:
        current_rows = render_conjugation_rows(
            help_card.forms,
            english_current_forms(help_card),
        )
        current_table = (
            f"<div class='verb-tense-name'>{escape(help_card.tense)}</div>"
            f"<span class='verb-table'>{current_rows}</span>"
        )
    else:
        current_table = (
            f"<div class='verb-tense-name'>{escape(help_card.tense)} · "
            "conjugation shown above</div>"
        )

    return (
        "<span class='verb-tooltip' role='tooltip'>"
        "<span class='verb-dictionary-label'>Dictionary form</span>"
        "<span class='verb-dictionary'>"
        f"<strong>{escape(help_card.infinitive)}</strong>"
        f"<span>{escape(english_infinitive(help_card))}</span>"
        "</span>"
        "<span class='verb-section'>"
        "<span class='verb-section-label'>Simple present</span>"
        f"<span class='verb-table'>{present_rows}</span>"
        "</span>"
        "<span class='verb-section'>"
        "<span class='verb-section-label'>Form in this sentence</span>"
        "<span class='verb-current-form'>"
        f"<strong>{escape(item.german)}</strong>"
        "<span class='arrow'>→</span>"
        f"<span>{escape(item.english)}</span>"
        "</span>"
        f"{current_table}"
        "</span>"
        "</span>"
    )


def render_breakdown_item(
    item: models.BreakdownItem,
    *,
    role: str = "word",
    article_changes: list[models.InflectionHelp] | None = None,
) -> str:
    tooltip = ""
    tooltip_class = ""
    keyboard_attributes = ""
    if item.verb_help:
        tooltip_class = " has-verb-help"
        keyboard_attributes = " tabindex='0'"
        tooltip = render_verb_tooltip(item)

    tags = "".join(
        f"<span class='grammar-tag tag-{escape(tag.category)}' "
        f"tabindex='0' aria-label='"
        f"{escape(tag.label)}: "
        f"{escape(models.TAG_DESCRIPTIONS[tag.label])}'>"
        f"{escape(tag.label)}"
        "<span class='grammar-tag-tooltip' aria-hidden='true'>"
        f"<strong>{escape(tag.label)}</strong>"
        f"<span>{escape(tag.category)}</span>"
        f"<p>{escape(models.TAG_DESCRIPTIONS[tag.label])}</p>"
        "</span>"
        "</span>"
        for tag in item.tags
    )
    tag_row = f"<div class='grammar-tags'>{tags}</div>" if tags else ""
    rendered_german = (
        render_phrase_german(item, article_changes)
        if article_changes
        else escape(item.german)
    )
    phrase_label = (
        "<span class='meaning-label'>Combined phrase</span>"
        if role == "phrase"
        else ""
    )
    literal_meaning = (
        "<div class='literal-meaning'>"
        f"Literally: {escape(item.literal_meaning)}</div>"
        if item.literal_meaning
        else ""
    )
    return (
        f"<div class='meaning-row {escape(role)}'>"
        "<div class='meaning-german'>"
        f"{phrase_label}"
        "<div class='breakdown-expression'>"
        f"<span class='breakdown-term{tooltip_class}'{keyboard_attributes}>"
        f"{rendered_german}{tooltip}</span>"
        "</div>"
        f"{tag_row}"
        "</div>"
        "<div class='meaning-english'>"
        f"<div class='breakdown-expression'>{escape(item.english)}</div>"
        f"{literal_meaning}"
        "</div>"
        "</div>"
    )


def render_breakdown_group(
    group: models.BreakdownGroup,
    sentence_text: str,
) -> None:
    cards: list[str] = []
    for item in ordered_breakdown_items(group, sentence_text):
        article_changes = (
            case_changes_for_phrase(item, group)
            if item.kind == "phrase"
            else None
        )
        cards.append(
            render_breakdown_item(
                item,
                role=item.kind,
                article_changes=article_changes,
            )
        )
    st.markdown(
        "<div class='breakdown-group meaning-list'>"
        f"{''.join(cards)}</div>",
        unsafe_allow_html=True,
    )


def render_sentence_study(sentence: models.Sentence, index: int) -> None:
    with st.container(key=f"sentence_card_{index}"):
        st.markdown(
            f"<div class='sentence-card-header'>"
            f"<h2>Sentence {index}</h2>"
            "<span class='sentence-card-mark' aria-hidden='true'>◇</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        sentence_audio_path = (
            PROJECT_ROOT / sentence.audio_path if sentence.audio_path else None
        )
        if sentence_audio_path and sentence_audio_path.exists():
            render_audio_player(
                sentence_audio_path.read_bytes(),
                label=f"Replay sentence {index}",
                compact=True,
            )
        elif sentence.audio_path:
            st.warning(f"Sentence audio not found: {sentence_audio_path}")

        st.markdown(
            "<div class='sentence-copy'>"
            "<div class='sentence-language'>"
            "<span class='copy-label'>German</span>"
            f"<div class='sentence-source'>{escape(sentence.text)}</div>"
            "</div>"
            "<div class='sentence-language translation'>"
            "<span class='copy-label'>English</span>"
            f"<div class='sentence-translation'>{escape(sentence.natural_meaning)}</div>"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='meaning-map-heading'>"
            "<strong>Meaning map</strong>"
            "<span>German and English, in sentence order</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        for group in sentence.breakdown_groups:
            render_breakdown_group(group, sentence.text)


@st.cache_resource(show_spinner=False)
def local_speech_model():
    """Load Whisper once per app process instead of once per button click."""
    SPEECH_MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return speech_feedback.create_whisper_model(
        SPEECH_MODEL_NAME,
        download_root=SPEECH_MODEL_CACHE_DIR,
    )


def practice_recording_path(lesson_id: str):
    """Return the local full-paragraph recording location for speaking practice."""
    return PRACTICE_RECORDINGS_DIR / lesson_id / "paragraph.wav"


def accepted_speech_alternatives(
    lesson: models.Lesson,
) -> tuple[speech_feedback.AcceptedAlternative, ...]:
    return tuple(
        speech_feedback.AcceptedAlternative(
            lesson_phrase=item.lesson_phrase,
            accepted_phrase=item.accepted_phrase,
            explanation=item.explanation,
        )
        for item in lesson.speech_alternatives
    )


def render_speech_feedback(result: speech_feedback.SpeechFeedback) -> None:
    """Render cautious model observations without claiming pronunciation grading."""
    transcript = result.transcript
    pacing = result.pacing
    if transcript.differences:
        difference_rows = []
        for difference in transcript.differences:
            if difference.kind == "different":
                description = (
                    f"Check this phrase: lesson <strong>{escape(difference.reference)}</strong>"
                    f" · transcript <strong>{escape(difference.heard)}</strong>"
                )
            elif difference.kind == "missing":
                description = (
                    f"Not detected: <strong>{escape(difference.reference)}</strong>"
                )
            else:
                description = f"Additional wording: <strong>{escape(difference.heard)}</strong>"
            difference_rows.append(
                f"<div class='speech-difference'>{description}</div>"
            )
        differences_markup = (
            "<div class='speech-differences'>" + "".join(difference_rows) + "</div>"
        )
    else:
        differences_markup = (
            "<div class='speech-differences'>"
            "<div class='speech-difference'>No unchecked wording differences remain.</div>"
            "</div>"
        )

    accepted_markup = ""
    if transcript.accepted_alternatives:
        accepted_rows = "".join(
            "<div class='speech-alternative'>"
            f"Accepted alternative: <strong>{escape(item.accepted_phrase)}</strong>"
            f" · lesson wording <strong>{escape(item.lesson_phrase)}</strong><br>"
            f"{escape(item.explanation)}"
            "</div>"
            for item in transcript.accepted_alternatives
        )
        accepted_markup = (
            "<strong>Accepted alternatives</strong>"
            f"<div class='speech-differences'>{accepted_rows}</div>"
        )

    reviewed_markup = ""
    if result.raw_transcript.strip() != transcript.transcript.strip():
        reviewed_markup = (
            "<div class='speech-reviewed-transcript'>"
            "<strong>Reviewed transcript used for comparison</strong>"
            f"{escape(transcript.transcript)}</div>"
        )

    st.markdown(
        "<div class='speech-feedback'>"
        "<h3>Experimental speech check</h3>"
        "<div class='speech-feedback-grid'>"
        f"<div class='speech-feedback-stat'><strong>{transcript.match_percent}%</strong>"
        "<span>Lesson match</span></div>"
        f"<div class='speech-feedback-stat'><strong>{escape(pacing.label)}</strong>"
        "<span>Overall timing</span></div>"
        f"<div class='speech-feedback-stat'><strong>{pacing.learner_duration:.1f}s</strong>"
        f"<span>Yours · lesson {pacing.reference_duration:.1f}s</span></div>"
        "</div>"
        "<div class='speech-transcript'><strong>What the local model heard</strong>"
        f"{escape(result.raw_transcript)}</div>"
        + reviewed_markup
        + accepted_markup
        + "<strong>Words to check</strong>"
        + differences_markup
        + "<p class='speech-feedback-note'>"
        "The lesson match uses the reviewed transcript and accepts alternatives authored "
        "for this lesson. Timing still comes from the original recording. This is not a "
        "pronunciation or accent grade."
        "</p></div>",
        unsafe_allow_html=True,
    )


def render_speaking_practice(lesson: models.Lesson) -> None:
    """Offer a stored-recording experiment for selected audio-ready lessons."""
    if lesson.id not in SPEAKING_PRACTICE_LESSON_IDS:
        return

    with st.container(key="speaking_practice"):
        st.markdown(
            "<h2 class='speaking-practice-heading'>Speak it yourself</h2>"
            "<p class='speaking-practice-intro'>"
            "Use the English cues to recall and say the lesson paragraph in German. "
            "The check compares with the lesson wording, so natural alternatives may differ. "
            "Your latest recording is saved only on this device; recording again replaces it."
            "</p>",
            unsafe_allow_html=True,
        )
        english_cues = "".join(
            "<div class='speaking-reference-line'>"
            f"<strong>{index}.</strong>{escape(sentence.natural_meaning)}"
            "</div>"
            for index, sentence in enumerate(lesson.sentences, start=1)
        )
        st.markdown(
            "<div class='speaking-reference-list'>" + english_cues + "</div>",
            unsafe_allow_html=True,
        )

        recording_path = practice_recording_path(lesson.id)
        feedback_key = f"speech_feedback_v2_{lesson.id}"
        error_key = f"speech_feedback_error_v2_{lesson.id}"
        editor_key = f"speech_transcript_editor_v2_{lesson.id}"
        reference_text = " ".join(sentence.text for sentence in lesson.sentences)
        alternatives = accepted_speech_alternatives(lesson)
        recording = st.audio_input(
            "Record your complete German paragraph",
            sample_rate=16_000,
            key=f"speaking_recorder_{lesson.id}",
        )
        if recording is not None:
            recording_bytes = recording.getvalue()
            existing_bytes = (
                recording_path.read_bytes() if recording_path.is_file() else None
            )
            if recording_bytes and recording_bytes != existing_bytes:
                recording_path.parent.mkdir(parents=True, exist_ok=True)
                recording_path.write_bytes(recording_bytes)
                st.session_state.pop(feedback_key, None)
                st.session_state.pop(error_key, None)
                st.session_state.pop(editor_key, None)

        reference_audio_path = (
            PROJECT_ROOT / lesson.audio_path if lesson.audio_path else None
        )
        if reference_audio_path and reference_audio_path.is_file():
            st.markdown(
                "<span class='speaking-audio-label'>Original lesson audio</span>",
                unsafe_allow_html=True,
            )
            render_audio_player(
                reference_audio_path.read_bytes(),
                label="Play the original German paragraph",
                compact=True,
            )

        can_analyse = bool(
            recording_path.is_file()
            and reference_audio_path
            and reference_audio_path.is_file()
        )
        with st.container(key="speaking_analysis_action"):
            analyse_clicked = st.button(
                "Check my recording",
                key=f"analyse_speaking_{lesson.id}",
                disabled=not can_analyse,
            )
        if not recording_path.is_file():
            st.caption("Record the paragraph to unlock the experimental speech check.")
        elif not reference_audio_path or not reference_audio_path.is_file():
            st.caption("The lesson audio is required for timing feedback.")
        else:
            st.caption(
                "Runs locally. The first check can take longer while the speech model loads."
            )

        if analyse_clicked and reference_audio_path:
            try:
                with st.spinner("Transcribing and comparing your recording locally..."):
                    result = speech_feedback.analyse_recording(
                        reference_text=reference_text,
                        reference_audio_path=reference_audio_path,
                        learner_audio_path=recording_path,
                        model=local_speech_model(),
                        accepted_alternatives=alternatives,
                    )
                st.session_state[feedback_key] = result
                st.session_state[editor_key] = result.raw_transcript
                st.session_state.pop(error_key, None)
            except (
                speech_feedback.SpeechDependencyError,
                speech_feedback.SpeechAnalysisError,
            ) as error:
                st.session_state[error_key] = str(error)
                st.session_state.pop(feedback_key, None)
                st.session_state.pop(editor_key, None)

        if st.session_state.get(error_key):
            st.error(st.session_state[error_key])
            if "requirements-speech.txt" in st.session_state[error_key]:
                st.code("pip install -r requirements-speech.txt", language="bash")
        result = st.session_state.get(feedback_key)
        if result:
            with st.container(key="speech_transcript_review"):
                st.markdown("**Review the transcript before judging your words**")
                st.caption(
                    "Correct only places where the speech model misheard you. "
                    "Keep wording you actually used, such as am Morgen."
                )
                reviewed_transcript = st.text_area(
                    "Transcript used for comparison",
                    key=editor_key,
                    label_visibility="collapsed",
                )
                with st.container(key="speech_transcript_update"):
                    update_clicked = st.button(
                        "Use reviewed transcript",
                        key=f"update_speech_transcript_{lesson.id}",
                    )
            if update_clicked:
                try:
                    result = speech_feedback.revise_transcript(
                        result,
                        reference_text=reference_text,
                        corrected_transcript=reviewed_transcript,
                        accepted_alternatives=alternatives,
                    )
                    st.session_state[feedback_key] = result
                    st.session_state.pop(error_key, None)
                except speech_feedback.SpeechAnalysisError as error:
                    st.session_state[error_key] = str(error)
                    st.error(str(error))
            render_speech_feedback(result)

        reveal_key = f"show_german_reference_{lesson.id}"
        reveal_text = (
            "Hide the German text"
            if st.session_state.get(reveal_key)
            else "Click here to reveal the German text"
        )
        with st.container(key="speaking_reveal"):
            if st.button(reveal_text, key=f"toggle_german_reference_{lesson.id}"):
                st.session_state[reveal_key] = not st.session_state.get(reveal_key, False)
                st.rerun()

        if st.session_state.get(reveal_key):
            german_text = "".join(
                f"<p>{index}. {escape(sentence.text)}</p>"
                for index, sentence in enumerate(lesson.sentences, start=1)
            )
            st.markdown(
                "<div class='speaking-german-reveal'>"
                "<strong>German text</strong>"
                + german_text
                + "</div>",
                unsafe_allow_html=True,
            )


def render_recent_progress() -> None:
    attempts = [
        attempt
        for attempt in STORE.recent_attempts(limit=100)
        if attempt["lesson_id"] in LESSON_BY_ID
    ][:5]
    if not attempts:
        st.caption("No lessons completed yet.")
        return
    with st.expander("Recent progress", expanded=False):
        for attempt in attempts:
            lesson = LESSON_BY_ID.get(attempt["lesson_id"])
            title = lesson.english_title if lesson else attempt["lesson_id"]
            status = attempt["stage"].replace("_", " ").title()
            st.markdown(f"**{escape(title)}** · {escape(status)}")


def render_reset_confirmation() -> None:
    if not st.session_state.get("confirm_progress_reset"):
        return

    with st.container(key="reset_confirmation"):
        st.markdown("**Remove all local progress?**")
        st.caption(
            "This permanently deletes every saved lesson attempt, completion, "
            "and learned-vocabulary state from this device. Lessons and audio "
            "will stay intact."
        )
        reset_column, cancel_column, _ = st.columns([1, 1, 3])
        if reset_column.button(
            "Yes, reset all",
            type="primary",
            key="confirm_reset_all_progress",
        ):
            STORE.clear_all_progress()
            st.session_state.confirm_progress_reset = False
            st.session_state.progress_reset_notice = True
            st.rerun()
        if cancel_column.button("Cancel", key="cancel_progress_reset"):
            st.session_state.confirm_progress_reset = False
            st.rerun()


DATA_PATH = PROJECT_ROOT / "data" / "nochmal.db"
STORE = storage.ProgressStore(DATA_PATH)

def render_lesson_tab() -> None:
    if st.session_state.get("lesson_selector") not in {None, *LESSON_BY_ID}:
        st.session_state.pop("lesson_selector", None)
    with st.container(key="lesson_picker"):
        lesson_id = st.selectbox(
            "Lesson",
            options=list(LESSON_BY_ID),
            format_func=lambda item_id: (
                f"{'PREVIEW · ' if item_id in PREVIEW_LESSON_IDS else ''}"
                f"{f'{LESSON_BY_ID[item_id].sequence:02d} · ' if LESSON_BY_ID[item_id].sequence else ''}"
                f"{LESSON_BY_ID[item_id].level} · {LESSON_BY_ID[item_id].english_title} · "
                f"{LESSON_BY_ID[item_id].title}"
            ),
            key="lesson_selector",
        )

    active_lesson = LESSON_BY_ID[lesson_id]
    audio_path = (
        PROJECT_ROOT / active_lesson.audio_path if active_lesson.audio_path else None
    )
    audio_bytes = (
        audio_path.read_bytes() if audio_path and audio_path.exists() else None
    )

    full_passage = " ".join(sentence.text for sentence in active_lesson.sentences)
    lesson_mode = (
        "Local preview · audio pending"
        if active_lesson.id in PREVIEW_LESSON_IDS
        else "Text lesson · audio pending"
        if active_lesson.audio_status == "pending"
        else "Listening lesson"
    )
    with st.container(key="solution_card"):
        st.markdown(
            f"""
            <div class="lesson-heading lesson-introduction">
              <span class="lesson-level">{escape(active_lesson.level)} · {lesson_mode}</span>
              <h1>{escape(active_lesson.english_title)}</h1>
              <p>{escape(active_lesson.title)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='listen-label'>"
            + ("Full text" if active_lesson.audio_status == "pending" else "Full paragraph")
            + "</div>",
            unsafe_allow_html=True,
        )
        if audio_bytes:
            render_audio_player(audio_bytes, label="Play full paragraph")
        elif active_lesson.audio_status == "pending":
            st.caption("Audio will be added later. The complete text lesson is available now.")
        else:
            st.error(f"Audio file not found: {audio_path}")
        st.markdown(
            f"<div class='solution-passage'>{escape(full_passage)}</div>",
            unsafe_allow_html=True,
        )

    section_hint = (
        "Read each sentence, then explore its meaning and building blocks."
        if active_lesson.audio_status == "pending"
        else "Listen again, then explore the meaning and building blocks."
    )
    st.markdown(
        f"""
        <div class="section-heading">
          <span>Sentence by sentence</span>
          <p>{section_hint}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for index, sentence in enumerate(active_lesson.sentences, start=1):
        render_sentence_study(sentence, index)

    completed_ids = STORE.completed_lesson_ids()
    with st.container(key="lesson_completion"):
        if lesson_id in completed_ids:
            st.success("Completed — this lesson is in your learned vocabulary.")
        elif st.button(
            "Mark lesson as complete",
            type="primary",
            key="mark_lesson_complete",
        ):
            STORE.mark_lesson_complete(
                lesson_id,
                metadata={"source": "direct-study"},
            )
            st.rerun()

    render_recent_progress()
    render_speaking_practice(active_lesson)


def render_vocabulary_tab() -> None:
    st.markdown(
        "<h1 class='page-heading'>Vocabulary</h1>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Words come from the lesson breakdowns. Completing a lesson marks "
        "its vocabulary as learned."
    )

    completed_ids = STORE.completed_lesson_ids()
    learned_scope = "__all_learned__"
    options = [lesson.id for lesson in COURSE_LESSONS] + [learned_scope]
    if st.session_state.get("vocabulary_lesson_selector") not in {None, *options}:
        st.session_state.pop("vocabulary_lesson_selector", None)

    def format_vocabulary_scope(scope: str) -> str:
        if scope == learned_scope:
            return f"All learned vocabulary · {len(completed_ids)} lessons"
        lesson = LESSON_BY_ID[scope]
        marker = "Learned" if scope in completed_ids else "Not learned yet"
        return f"{lesson.english_title} · {marker}"

    selected_scope = st.selectbox(
        "Choose a lesson",
        options=options,
        format_func=format_vocabulary_scope,
        key="vocabulary_lesson_selector",
    )

    if selected_scope == learned_scope:
        completed_lessons = [
            lesson for lesson in COURSE_LESSONS if lesson.id in completed_ids
        ]
        if not completed_lessons:
            st.info("Complete a lesson to start your learned vocabulary list.")
            return
        entries = vocabulary.vocabulary_for_lessons(completed_lessons)
        groups = vocabulary.group_entries(entries)
        st.success(
            f"{len(entries)} unique words learned across "
            f"{len(completed_lessons)} lessons."
        )
    else:
        lesson = LESSON_BY_ID[selected_scope]
        groups = vocabulary.grouped_vocabulary(lesson)
        word_count = sum(len(entries) for entries in groups.values())
        if selected_scope in completed_ids:
            st.success(f"Learned · {word_count} vocabulary words")
        else:
            st.info(
                f"{word_count} vocabulary words available. Complete this "
                "lesson to add them to your learned list."
            )

    for category, entries in groups.items():
        st.subheader(f"{category} ({len(entries)})")
        for entry in entries:
            german_column, meaning_column = st.columns([2, 3])
            german_column.markdown(f"**{entry.german}**")
            meaning_column.write(entry.english)
            if entry.tags:
                meaning_column.caption(" · ".join(entry.tags))


def main() -> None:
    st.set_page_config(page_title="Nochmal", page_icon="🎧", layout="wide")
    st.markdown(APP_STYLES + MODERN_STYLES, unsafe_allow_html=True)

    with st.container(key="app_toolbar"):
        if st.button(
            "Reset progress",
            key="reset_progress_trigger",
            use_container_width=True,
        ):
            st.session_state.confirm_progress_reset = True

    if st.session_state.pop("progress_reset_notice", False):
        st.success("Lesson and vocabulary progress have been reset.")
    render_reset_confirmation()

    lesson_tab, vocabulary_tab = st.tabs(["Learn", "Vocabulary"])
    with lesson_tab:
        render_lesson_tab()
    with vocabulary_tab:
        render_vocabulary_tab()
