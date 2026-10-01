import unittest

from nochmal.content import LESSONS
from nochmal.content.verb_reference import (
    english_current_forms,
    english_present_forms,
    present_forms,
)
from nochmal.paths import PROJECT_ROOT
from nochmal.ui.app import (
    COURSE_LESSONS,
    PRACTICE_RECORDINGS_DIR,
    PUBLISHED_COURSE_LESSONS,
    PUBLISHED_LESSON_IDS,
    SPEAKING_PRACTICE_LESSON_IDS,
    adjective_changes_for_phrase,
    article_changes_for_phrase,
    ordered_breakdown_items,
    practice_recording_path,
    render_inflection_tooltip,
    render_verb_tooltip,
)


class BreakdownLayoutTests(unittest.TestCase):
    def test_primary_tabs_use_a_large_segmented_control(self) -> None:
        app_source = (PROJECT_ROOT / "nochmal" / "ui" / "app.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "grid-template-columns: repeat(2, minmax(0, 1fr));",
            app_source,
        )
        self.assertIn("min-height: 3rem;", app_source)
        self.assertIn("background: var(--navy) !important;", app_source)

    def test_translation_is_stacked_below_the_german_sentence(self) -> None:
        app_source = (PROJECT_ROOT / "nochmal" / "ui" / "app.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            ".sentence-copy {\n    display: grid;\n    grid-template-columns: 1fr;",
            app_source,
        )

    def test_speaking_practice_is_enabled_for_the_reference_lesson_and_saves_locally(self) -> None:
        app_source = (PROJECT_ROOT / "nochmal" / "ui" / "app.py").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            frozenset({"a1-course-001"}),
            SPEAKING_PRACTICE_LESSON_IDS,
        )
        self.assertEqual(
            ("a1-course-001",),
            PUBLISHED_LESSON_IDS,
        )
        self.assertEqual(
            list(PUBLISHED_LESSON_IDS),
            [lesson.id for lesson in PUBLISHED_COURSE_LESSONS],
        )
        self.assertTrue(
            set(PUBLISHED_LESSON_IDS) <= {lesson.id for lesson in COURSE_LESSONS}
        )
        self.assertEqual(
            PRACTICE_RECORDINGS_DIR / "a1-course-001" / "paragraph.wav",
            practice_recording_path("a1-course-001"),
        )
        self.assertIn("if lesson.id not in SPEAKING_PRACTICE_LESSON_IDS:", app_source)
        self.assertIn("st.audio_input(", app_source)
        self.assertIn("Record your complete German paragraph", app_source)
        self.assertIn("reference_audio_path", app_source)
        self.assertIn("Play the original German paragraph", app_source)
        self.assertIn("Check my recording", app_source)
        self.assertIn("Experimental speech check", app_source)
        self.assertIn("Review the transcript before judging your words", app_source)
        self.assertIn("Use reviewed transcript", app_source)
        self.assertIn("pronunciation or accent grade.", app_source)
        self.assertIn("Click here to reveal the German text", app_source)
        self.assertIn('[aria-label="Stop recording"]', app_source)
        self.assertIn('backdrop-filter: blur(14px)', app_source)
        self.assertIn('overflow: hidden !important;', app_source)
        self.assertIn('[class*="st-key-speaking_recorder_"]', app_source)
        self.assertNotIn("Play your full-paragraph recording", app_source)

    def test_early_case_changes_cover_indefinite_and_possessive_determiners(self) -> None:
        expected = {
            "in einer kleinen Stadt": ("ein", "einer", "dative", "feminine"),
            "in einem kleinen Haus": ("ein", "einem", "dative", "neuter"),
            "meiner Schwester": ("mein", "meiner", "genitive", "feminine"),
        }
        found = {}
        for lesson in LESSONS:
            for sentence in lesson.sentences:
                for group in sentence.breakdown_groups:
                    for item in group.items:
                        if item.german not in expected:
                            continue
                        changes = article_changes_for_phrase(item, group)
                        self.assertEqual(1, len(changes))
                        change = changes[0]
                        found[item.german] = (
                            change.base,
                            change.surface.casefold(),
                            change.case,
                            change.gender,
                        )

        self.assertEqual(expected, found)

        apartment = next(
            lesson for lesson in LESSONS if lesson.id == "a1-004"
        )
        kitchen = next(
            item
            for sentence in apartment.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.german == "In der Küche"
        )
        kitchen_help = article_changes_for_phrase(
            kitchen, apartment.sentences[-1].breakdown_groups[0]
        )
        self.assertEqual("der", kitchen_help[0].surface.casefold())

    def test_declined_adjectives_explain_their_case_endings(self) -> None:
        expected = {
            "in einer kleinen Stadt": ("klein", "kleinen", "dative", "feminine"),
            "in einer hellen Wohnung": ("hell", "hellen", "dative", "feminine"),
            "in einem kleinen Haus": ("klein", "kleinen", "dative", "neuter"),
        }
        found = {}
        paradigms = {}
        for lesson in LESSONS:
            for sentence in lesson.sentences:
                for group in sentence.breakdown_groups:
                    for item in group.items:
                        if item.german not in expected:
                            continue
                        changes = adjective_changes_for_phrase(item, group)
                        self.assertEqual(1, len(changes))
                        change = changes[0]
                        found[item.german] = (
                            change.base,
                            change.surface.casefold(),
                            change.case,
                            change.gender,
                        )
                        paradigms[item.german] = change.paradigm

        self.assertEqual(expected, found)
        self.assertEqual("mixed-adjective", paradigms["in einer kleinen Stadt"])
        self.assertEqual("mixed-adjective", paradigms["in einem kleinen Haus"])

    def test_case_hovers_use_one_complete_static_table_layout(self) -> None:
        lesson = next(lesson for lesson in LESSONS if lesson.id == "a1-004")
        phrase = next(
            item
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.german == "neben dem Bad"
        )
        markup = render_inflection_tooltip(phrase.inflection_help[0])

        self.assertIn("Definite article", markup)
        self.assertIn("Definite-article forms", markup)
        for case in ("nominative", "accusative", "dative", "genitive"):
            self.assertIn(case, markup)
        for gender in ("masculine", "feminine", "neuter", "plural"):
            self.assertIn(gender, markup)
        self.assertIn("is-current", markup)
        self.assertNotIn("uses -", markup)

        family = next(lesson for lesson in LESSONS if lesson.id == "a1-003")
        pronoun_phrase = next(
            item
            for sentence in family.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.german == "mit mir"
        )
        pronoun_markup = render_inflection_tooltip(
            pronoun_phrase.inflection_help[0]
        )
        self.assertIn("Personal pronoun", pronoun_markup)
        self.assertIn("Personal-pronoun forms", pronoun_markup)
        self.assertIn("first singular", pronoun_markup)

    def test_lesson_specific_grammar_description_is_not_rendered(self) -> None:
        app_source = (PROJECT_ROOT / "nochmal" / "ui" / "app.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("Lesson goals & grammar", app_source)
        self.assertNotIn("active_lesson.grammar_explanation", app_source)

    def test_meanings_follow_sentence_order_and_drop_empty_noun_restatements(self) -> None:
        lesson = next(lesson for lesson in LESSONS if lesson.id == "lost-wallet")
        sentence = lesson.sentences[2]
        ordered = ordered_breakdown_items(
            sentence.breakdown_groups[0], sentence.text
        )
        german = [item.german for item in ordered]

        self.assertEqual(
            german,
            [
                "zu",
                "das Glück",
                "Zum Glück",
                "hatte",
                "die Mitarbeiterin",
                "ihn",
                "gefunden",
                "und",
                "sicher",
                "aufbewahrt",
                "hatte ... gefunden und ... aufbewahrt",
            ],
        )
        self.assertNotIn("eine Mitarbeiterin", german)

    def test_every_verb_card_has_bilingual_present_and_current_forms(self) -> None:
        verbs = [
            item
            for lesson in LESSONS
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.verb_help is not None
        ]
        self.assertTrue(verbs)
        for item in verbs:
            with self.subTest(verb=item.german):
                help_card = item.verb_help
                self.assertIsNotNone(help_card)
                self.assertEqual(len(present_forms(help_card)), 6)
                self.assertEqual(len(english_present_forms(help_card)), 6)
                self.assertEqual(
                    len(english_current_forms(help_card)),
                    len(help_card.forms),
                )

                markup = render_verb_tooltip(item)
                self.assertLess(
                    markup.index("Dictionary form"),
                    markup.index("Simple present"),
                )
                self.assertLess(
                    markup.index("Simple present"),
                    markup.index("Form in this sentence"),
                )
                self.assertNotIn("verb-tooltip-usage", markup)


if __name__ == "__main__":
    unittest.main()
