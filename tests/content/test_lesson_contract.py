import unittest

from pydantic import ValidationError

from nochmal.content import LESSONS
from nochmal.content.models import InflectionHelp
from nochmal.content.validation import validate_lesson_library
from nochmal.paths import PROJECT_ROOT


class LessonLibraryContractTests(unittest.TestCase):
    """Run automatically against every paragraph exported in LESSONS."""

    def test_every_published_paragraph_passes_the_authoring_contract(self) -> None:
        self.assertEqual(
            validate_lesson_library(LESSONS, project_root=PROJECT_ROOT),
            [],
        )

    def test_library_remains_progressive_from_a2_to_b2(self) -> None:
        levels = [lesson.level for lesson in LESSONS]
        self.assertGreaterEqual(len(LESSONS), 14)
        self.assertGreaterEqual(levels.count("A2"), 3)
        self.assertGreaterEqual(levels.count("B1"), 4)
        self.assertGreaterEqual(levels.count("B2"), 2)

    def test_rainy_picnic_teaches_word_order_and_contractions(self) -> None:
        lesson = next(lesson for lesson in LESSONS if lesson.id == "rainy-picnic")
        sentence = lesson.sentences[0]
        phrases = {
            item.german: {tag.label for tag in item.tags}
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertEqual(
            sentence.natural_meaning,
            "We originally wanted to have a picnic in the park on Saturday.",
        )
        self.assertIn("am Samstag", phrases)
        self.assertIn("im Park", phrases)
        self.assertEqual(
            phrases["Eigentlich wollten wir ... picknicken"],
            {"inversion"},
        )

    def test_advanced_lessons_build_meaningful_intermediate_phrases(self) -> None:
        advanced_ids = {"team-meeting", "digital-break", "car-free-centre"}
        advanced_lessons = [
            lesson for lesson in LESSONS if lesson.id in advanced_ids
        ]

        for lesson in advanced_lessons:
            for sentence in lesson.sentences:
                with self.subTest(lesson=lesson.id, sentence=sentence.text):
                    self.assertGreaterEqual(len(sentence.breakdown_groups), 2)
                    self.assertTrue(
                        any(
                            sum(item.kind == "phrase" for item in group.items) >= 2
                            for group in sentence.breakdown_groups
                        )
                    )

        phrases = {
            item.german
            for lesson in advanced_lessons
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertTrue(
            {
                "unter Druck stehen würde",
                "ihre Bedenken erklärt hatten",
                "beschloss sie, eine digitale Pause einzulegen",
                "schaltete sie abends alle Benachrichtigungen aus",
                "bewusster mit ihrer Zeit umging",
                "die Luft sauberer und das Viertel ruhiger werden",
                "sollen die Anwohner ihre Erfahrungen und Vorschläge einbringen",
            }
            <= phrases
        )

    def test_every_b1_or_higher_sentence_has_multiple_phrase_steps(self) -> None:
        higher_levels = {"B1", "B1-B2", "B2"}
        for lesson in LESSONS:
            if lesson.level not in higher_levels:
                continue
            for sentence in lesson.sentences:
                phrase_count = sum(
                    item.kind == "phrase"
                    for group in sentence.breakdown_groups
                    for item in group.items
                )
                with self.subTest(lesson=lesson.id, sentence=sentence.text):
                    self.assertGreaterEqual(phrase_count, 3)

        phrases = {
            item.german
            for lesson in LESSONS
            if lesson.level in higher_levels
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertTrue(
            {
                "wartet er gespannt auf ihre Antwort",
                "sich die Wörter besser merken",
                "erst kurz vor der Abfahrt",
                "ein ungenutztes Grundstück voller Müll",
            }
            <= phrases
        )


class LessonValidatorRegressionTests(unittest.TestCase):
    def test_inflection_schema_rejects_mismatched_paradigms(self) -> None:
        with self.assertRaises(ValidationError):
            InflectionHelp(
                surface="dem",
                base="der",
                kind="definite-article",
                paradigm="mixed-adjective",
                case="dative",
                gender="masculine",
            )

    def test_duplicate_lesson_ids_are_rejected(self) -> None:
        duplicate = LESSONS[0].model_copy(deep=True)
        errors = validate_lesson_library([LESSONS[0], duplicate])
        self.assertTrue(any("duplicate lesson id" in error for error in errors))

    def test_missing_hover_conjugation_is_rejected(self) -> None:
        lesson = LESSONS[0].model_copy(deep=True)
        verb = next(
            item
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.verb_help is not None
        )
        verb.verb_help = None

        errors = validate_lesson_library([lesson])
        self.assertTrue(any("verb help is missing" in error for error in errors))

    def test_phrase_words_absent_from_source_are_rejected(self) -> None:
        lesson = LESSONS[0].model_copy(deep=True)
        phrase = next(
            item
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        )
        phrase.german += " Fantasiewort"

        errors = validate_lesson_library([lesson])
        self.assertTrue(
            any(
                "phrase contains words absent from the source" in error
                for error in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
