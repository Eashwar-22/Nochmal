import hashlib
import json
import re
import unittest
import wave
from collections import Counter
from pathlib import Path

from pydantic import ValidationError

from nochmal.content import A1_PUBLISHED_LESSONS, LESSONS
from nochmal.content.catalog import load_publication_catalog, published_lessons
from nochmal.content.models import SentenceAnnotations
from nochmal.content.source_models import CourseLessonSource
from nochmal.content.validation import validate_lesson_library
from nochmal.paths import PROJECT_ROOT
from nochmal.validation.release import release_errors


STAGED_PATH = PROJECT_ROOT / "curriculum" / "a1_staging" / "lessons" / "module_01.json"
PRODUCTION_PATH = PROJECT_ROOT / "curriculum" / "a1_published" / "lessons" / "001.json"
AUDIO_ROOT = PROJECT_ROOT / "assets" / "audio" / "a1_published" / "a1-course-001"
PUBLISHED_LESSON_IDS = load_publication_catalog().published_lesson_ids


class A1CourseReferenceLessonTests(unittest.TestCase):
    def test_complete_release_gate_passes_for_every_published_lesson(self) -> None:
        for lesson_id in PUBLISHED_LESSON_IDS:
            with self.subTest(lesson_id=lesson_id):
                self.assertEqual([], release_errors(lesson_id))

    def test_authored_schemas_reject_unknown_fields(self) -> None:
        with self.assertRaises(ValidationError):
            SentenceAnnotations.model_validate({"word_meaningz": {"bin": "am"}})

        source = json.loads(PRODUCTION_PATH.read_text(encoding="utf-8"))
        source["sentences"][0]["annotations"]["word_tagz"] = {}
        with self.assertRaises(ValidationError):
            CourseLessonSource.model_validate(source)

    def test_published_course_lessons_match_the_manifest(self) -> None:
        self.assertEqual(
            tuple(f"a1-course-{sequence:03d}" for sequence in range(1, 49)),
            tuple(lesson_id for lesson_id in PUBLISHED_LESSON_IDS if lesson_id.startswith("a1-")),
        )
        self.assertEqual(
            list(PUBLISHED_LESSON_IDS),
            [lesson.id for lesson in published_lessons(LESSONS)],
        )

    def test_recycled_targets_compile_in_later_published_lessons(self) -> None:
        lessons = {lesson.id: lesson for lesson in A1_PUBLISHED_LESSONS}
        lesson_two_words = {
            item.german
            for sentence in lessons["a1-course-002"].sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "word"
        }
        self.assertIn("kommst", lesson_two_words)

    def test_production_text_matches_the_corrected_staged_draft(self) -> None:
        staged = json.loads(STAGED_PATH.read_text(encoding="utf-8"))[0]
        production = json.loads(PRODUCTION_PATH.read_text(encoding="utf-8"))
        self.assertEqual(staged["draft_id"], production["source_draft_id"])
        self.assertEqual(staged["sentences"], [
            {"de": item["de"], "en": item["en"]}
            for item in production["sentences"]
        ])

    def test_audio_manifest_binds_v4_files_to_the_exact_lesson_text(self) -> None:
        production = json.loads(PRODUCTION_PATH.read_text(encoding="utf-8"))
        manifest = json.loads(
            (AUDIO_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual("eleven_v4", manifest["model_id"])
        self.assertEqual(
            [sentence["de"] for sentence in production["sentences"]],
            manifest["sentence_texts"],
        )
        for file_name, expected_hash in manifest["sentence_sha256"].items():
            self.assertEqual(
                expected_hash,
                hashlib.sha256((AUDIO_ROOT / file_name).read_bytes()).hexdigest(),
            )
        self.assertEqual(
            manifest["paragraph_sha256"],
            hashlib.sha256((AUDIO_ROOT / manifest["paragraph_file"]).read_bytes()).hexdigest(),
        )

    def test_paragraph_audio_is_the_exact_sentence_join(self) -> None:
        manifest = json.loads(
            (AUDIO_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        sentence_pcm: list[bytes] = []
        for file_name in manifest["sentence_files"]:
            with wave.open(str(AUDIO_ROOT / file_name), "rb") as source:
                self.assertEqual((1, 2, 44_100), (
                    source.getnchannels(),
                    source.getsampwidth(),
                    source.getframerate(),
                ))
                sentence_pcm.append(source.readframes(source.getnframes()))
        with wave.open(str(AUDIO_ROOT / manifest["paragraph_file"]), "rb") as source:
            paragraph_pcm = source.readframes(source.getnframes())
        pause = b"\x00" * round(44_100 * 2 * manifest["pause_seconds"])
        self.assertEqual(pause.join(sentence_pcm), paragraph_pcm)

    def test_reference_lesson_passes_the_full_contract(self) -> None:
        self.assertEqual(
            [],
            validate_lesson_library(A1_PUBLISHED_LESSONS, project_root=PROJECT_ROOT),
        )

    def test_every_source_token_is_represented_once_in_ordered_word_cards(self) -> None:
        token_pattern = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)
        lesson = A1_PUBLISHED_LESSONS[0]
        for sentence in lesson.sentences:
            expected = [token.casefold() for token in token_pattern.findall(sentence.text)]
            actual = [
                source.casefold()
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word"
                for source in item.source_forms
            ]
            self.assertEqual(Counter(expected), Counter(actual))

    def test_reference_lesson_exposes_required_form_changes(self) -> None:
        lesson = A1_PUBLISHED_LESSONS[0]
        phrases = {
            item.german: item
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertEqual(
            [("im", "der", "dative", "definite")],
            [
                (help_.surface, help_.base, help_.case, help_.paradigm)
                for help_ in phrases["im Kurs"].inflection_help
            ],
        )
        self.assertEqual(
            [("Guten", "gut", "accusative", "strong-adjective")],
            [
                (help_.surface, help_.base, help_.case, help_.paradigm)
                for help_ in phrases["Guten Tag"].inflection_help
            ],
        )
        self.assertEqual(
            [("mich", "ich", "accusative", "personal-pronoun")],
            [
                (help_.surface, help_.base, help_.case, help_.paradigm)
                for help_ in phrases["Freut mich"].inflection_help
            ],
        )

    def test_every_verb_has_complete_bilingual_help(self) -> None:
        verbs = [
            item
            for sentence in A1_PUBLISHED_LESSONS[0].sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.verb_help
        ]
        self.assertEqual({"heißen", "sein", "freuen"}, {item.verb_help.infinitive for item in verbs})
        for item in verbs:
            self.assertEqual(6, len(item.verb_help.present_forms or []))
            self.assertEqual(6, len(item.verb_help.present_english_forms or []))
            self.assertEqual(len(item.verb_help.forms), len(item.verb_help.current_english_forms or []))

    def test_every_word_has_the_audited_meaning_and_grammar_tags(self) -> None:
        expected = [
            [
                ("Hallo", "hello", {"interjection"}),
                ("ich", "I", {"personal pronoun", "nominative", "subject"}),
                ("heiße", "am called", {"verb", "present"}),
                ("Mina", "Mina", {"proper noun"}),
                ("und", "and", {"conjunction", "coordinating"}),
                ("bin", "am", {"verb", "present"}),
                ("neu", "new", {"adjective", "predicate"}),
                ("in", "in", {"preposition", "dative", "place"}),
                ("der Kurs", "course", {"noun", "masc."}),
            ],
            [
                ("gut", "good", {"adjective"}),
                ("der Tag", "day", {"noun", "masc."}),
                ("Mina", "Mina", {"proper noun"}),
                ("ich", "I", {"personal pronoun", "nominative", "subject"}),
                ("bin", "am", {"verb", "present"}),
                ("Leo", "Leo", {"proper noun", "nominative", "predicate"}),
            ],
            [
                ("Freut", "pleases", {"verb", "present"}),
                ("mich", "me", {"personal pronoun", "accusative"}),
                ("Mina", "Mina", {"proper noun"}),
                ("und", "and", {"conjunction", "coordinating"}),
                ("willkommen", "welcome", {"adjective", "predicate"}),
                ("in", "in", {"preposition", "dative", "place"}),
                ("der Kurs", "course", {"noun", "masc."}),
            ],
            [
                ("Auf", "until", {"preposition", "accusative"}),
                ("das Wiedersehen", "seeing one another again", {"noun", "neuter"}),
                ("Leo", "Leo", {"proper noun"}),
            ],
        ]
        actual = []
        for sentence in A1_PUBLISHED_LESSONS[0].sentences:
            actual.append([
                (item.german, item.english, {tag.label for tag in item.tags})
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word"
            ])
        self.assertEqual(expected, actual)

    def test_every_phrase_has_the_audited_meaning_and_grammar_tags(self) -> None:
        expected = [
            [
                ("im Kurs", "in the class", {"contraction", "dative", "place"}),
                (
                    "ich heiße Mina und bin neu im Kurs",
                    "my name is Mina and I am new to the course",
                    {"main clause", "verb-second"},
                ),
                ("ich heiße Mina", "my name is Mina", {"main clause", "verb-second"}),
            ],
            [
                ("Guten Tag", "Hello", {"fixed phrase", "accusative"}),
                ("ich bin Leo", "I’m Leo", {"main clause", "verb-second"}),
            ],
            [
                ("im Kurs", "in the class", {"contraction", "dative", "place"}),
                (
                    "Freut mich",
                    "Nice to meet you",
                    {"fixed phrase", "ellipsis", "accusative"},
                ),
                (
                    "willkommen im Kurs",
                    "welcome to the course",
                    {"fixed phrase", "ellipsis"},
                ),
            ],
            [("Auf Wiedersehen", "Goodbye", {"fixed phrase", "accusative"})],
        ]
        actual = []
        for sentence in A1_PUBLISHED_LESSONS[0].sentences:
            actual.append([
                (item.german, item.english, {tag.label for tag in item.tags})
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "phrase"
            ])
        self.assertEqual(expected, actual)

    def test_idiomatic_phrases_preserve_natural_and_literal_meanings(self) -> None:
        phrases = {
            item.german: (item.english, item.literal_meaning)
            for sentence in A1_PUBLISHED_LESSONS[0].sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertEqual(("my name is Mina", "I am called Mina"), phrases["ich heiße Mina"])
        self.assertEqual(("Hello", "Good day"), phrases["Guten Tag"])
        self.assertEqual(("Nice to meet you", "Pleases me"), phrases["Freut mich"])
        self.assertEqual(
            ("Goodbye", "Until we see each other again"),
            phrases["Auf Wiedersehen"],
        )


if __name__ == "__main__":
    unittest.main()
