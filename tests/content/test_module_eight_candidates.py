import hashlib
import json
import re
import unittest
from collections import Counter

from nochmal.content.candidates import candidate_errors, load_candidate_artifact, source_path
from nochmal.content.grammar_reference import selected_column_for_help, table_for_help
from nochmal.content.ordering import ordered_breakdown_items
from nochmal.paths import PROJECT_ROOT
from nochmal.content.catalog import load_publication_catalog

PUBLISHED_LESSON_IDS = load_publication_catalog().published_lesson_ids
from nochmal.validation.models import LessonReviewReport


class ModuleEightCandidateTests(unittest.TestCase):
    def test_final_a1_candidates_are_reviewed_current_and_published(self) -> None:
        staged = json.loads(
            (
                PROJECT_ROOT / "curriculum" / "a1_staging" / "lessons" / "module_08.json"
            ).read_text(encoding="utf-8")
        )
        for lesson_number, draft in zip(range(43, 49), staged, strict=True):
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
                [{"de": sentence["de"], "en": sentence["en"]} for sentence in source["sentences"]],
            )
            self.assertEqual("pass", review.overall_verdict)
            self.assertEqual(
                hashlib.sha256(source_file.read_bytes()).hexdigest(),
                review.source_sha256,
            )

            for sentence in artifact.lesson.sentences:
                expected = Counter(
                    token.casefold()
                    for token in re.findall(r"\w+(?:[-’']\w+)*", sentence.text)
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

                for group in sentence.breakdown_groups:
                    for item in group.items:
                        if item.kind != "phrase":
                            continue
                        self.assertEqual(item.german.count("„"), item.german.count("“"))
                        self.assertEqual(item.english.count("“"), item.english.count("”"))
                        labels = {tag.label for tag in item.tags}
                        for help_card in item.inflection_help:
                            self.assertIn(help_card.case, labels)
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

    def test_audited_module_eight_grammar_regressions(self) -> None:
        lessons = {
            number: load_candidate_artifact(f"a1-course-{number:03d}").lesson
            for number in range(43, 49)
        }

        def word(lesson_number: int, surface: str):
            return next(
                item
                for sentence in lessons[lesson_number].sentences
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word" and surface in item.source_forms
            )

        self.assertEqual("fahren", word(43, "gefahren").verb_help.infinitive)
        self.assertEqual("haben", word(43, "hat").verb_help.infinitive)
        self.assertEqual("antworten", word(44, "antworte").verb_help.infinitive)
        self.assertEqual("die Seite", word(45, "Seite").german)
        self.assertEqual(
            "Perfekt (conversational past)",
            word(47, "angerufen").verb_help.tense,
        )
        self.assertEqual("sich treffen", word(48, "Treffen").verb_help.infinitive)
        self.assertEqual("fahren", word(48, "Fährt").verb_help.infinitive)


if __name__ == "__main__":
    unittest.main()
