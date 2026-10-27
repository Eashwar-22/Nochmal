import hashlib
import json
import re
import unittest
from collections import Counter

from nochmal.content.candidates import (
    candidate_errors,
    load_candidate_artifact,
    source_path,
)
from nochmal.content.grammar_reference import selected_column_for_help, table_for_help
from nochmal.content.ordering import ordered_breakdown_items
from nochmal.paths import PROJECT_ROOT
from nochmal.content.catalog import load_publication_catalog

PUBLISHED_LESSON_IDS = load_publication_catalog().published_lesson_ids
from nochmal.validation.models import LessonReviewReport


TOKEN_PATTERN = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)


class ModulesSixAndSevenCandidateTests(unittest.TestCase):
    def test_candidates_are_reviewed_current_and_active(self) -> None:
        for module, first_lesson in ((6, 31), (7, 37)):
            staged = json.loads(
                (
                    PROJECT_ROOT
                    / "curriculum"
                    / "a1_staging"
                    / "lessons"
                    / f"module_{module:02d}.json"
                ).read_text(encoding="utf-8")
            )
            for lesson_number, draft in zip(
                range(first_lesson, first_lesson + 6), staged, strict=True
            ):
                lesson_id = f"a1-course-{lesson_number:03d}"
                artifact = load_candidate_artifact(lesson_id)
                source_file = source_path(lesson_id)
                source = json.loads(source_file.read_text(encoding="utf-8"))
                review = LessonReviewReport.model_validate_json(
                    source_file.with_name("review.json").read_text(encoding="utf-8")
                )

                self.assertEqual([], candidate_errors(lesson_id, artifact))
                self.assertEqual("ready", artifact.lesson.audio_status)
                self.assertIn(lesson_id, PUBLISHED_LESSON_IDS)
                self.assertEqual(draft["draft_id"], source["source_draft_id"])
                self.assertEqual(
                    draft["sentences"],
                    [
                        {"de": sentence["de"], "en": sentence["en"]}
                        for sentence in source["sentences"]
                    ],
                )
                self.assertEqual("pass", review.overall_verdict)
                self.assertEqual(
                    hashlib.sha256(source_file.read_bytes()).hexdigest(),
                    review.source_sha256,
                )

                for sentence in artifact.lesson.sentences:
                    expected = Counter(
                        token.casefold() for token in TOKEN_PATTERN.findall(sentence.text)
                    )
                    words = [
                        item
                        for group in sentence.breakdown_groups
                        for item in ordered_breakdown_items(group, sentence.text)
                        if item.kind == "word"
                    ]
                    actual = Counter(
                        form.casefold() for item in words for form in item.source_forms
                    )
                    self.assertEqual(expected, actual)
                    for item in words:
                        labels = {tag.label for tag in item.tags}
                        if "verb" in labels:
                            self.assertIsNotNone(item.verb_help)
                            self.assertIn(item.german, item.source_forms)

                    for group in sentence.breakdown_groups:
                        for item in group.items:
                            if item.kind != "phrase":
                                continue
                            labels = {tag.label for tag in item.tags}
                            for help_card in item.inflection_help:
                                self.assertIn(help_card.case, labels)
                                self.assertRegex(
                                    item.german,
                                    rf"(?i)(?<!\w){re.escape(help_card.surface)}(?!\w)",
                                )
                                table = table_for_help(help_card)
                                self.assertEqual(
                                    {"nominative", "accusative", "dative", "genitive"},
                                    set(table),
                                )
                                expected_form = table[help_card.case][
                                    selected_column_for_help(help_card)
                                ]
                                visible = help_card.resolved_form or help_card.surface
                                if help_card.kind == "adjective":
                                    self.assertTrue(
                                        visible.casefold().endswith(
                                            expected_form.removeprefix("-").casefold()
                                        )
                                    )
                                else:
                                    self.assertEqual(
                                        visible.casefold(), expected_form.casefold()
                                    )

    def test_audited_grammar_regressions(self) -> None:
        lessons = {
            number: load_candidate_artifact(f"a1-course-{number:03d}").lesson
            for number in range(31, 43)
        }

        def word(lesson_number: int, surface: str):
            return next(
                item
                for sentence in lessons[lesson_number].sentences
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word" and surface in item.source_forms
            )

        self.assertEqual("anprobieren", word(33, "probiert").verb_help.infinitive)
        self.assertEqual("abgeben", word(34, "gibt").verb_help.infinitive)
        self.assertIsNone(word(34, "Stellen").verb_help)
        self.assertEqual("annehmen", word(36, "nimmt").verb_help.infinitive)
        self.assertEqual("er", word(36, "ihm").german)
        self.assertEqual("treffen", word(39, "trifft").verb_help.infinitive)
        self.assertEqual("fernsehen", word(39, "sieht").verb_help.infinitive)
        self.assertEqual("mitkommen", word(41, "kommst").verb_help.infinitive)
        self.assertIn(
            "denn ich muss lange arbeiten",
            {
                item.german
                for group in lessons[42].sentences[1].breakdown_groups
                for item in group.items
                if item.kind == "phrase"
            },
        )


if __name__ == "__main__":
    unittest.main()
