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

    def test_library_contains_only_numbered_course_lessons(self) -> None:
        self.assertEqual(120, len(LESSONS))
        self.assertEqual(
            [*range(1, 121)],
            [lesson.sequence for lesson in LESSONS],
        )
        self.assertTrue(all(lesson.id.startswith(("a1-course-", "a2-course-")) for lesson in LESSONS))


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
