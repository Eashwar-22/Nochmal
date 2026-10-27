import json
import unittest

from nochmal.content import A2_COURSE_LESSONS
from nochmal.content.candidates import (
    candidate_directory,
    candidate_errors,
    load_candidate_artifact,
)
from nochmal.content.catalog import load_publication_catalog


class A2ModuleOneCandidateTests(unittest.TestCase):
    @staticmethod
    def _items(number: int, sentence_index: int):
        sentence = load_candidate_artifact(f"a2-course-{number:03d}").lesson.sentences[
            sentence_index
        ]
        return [item for group in sentence.breakdown_groups for item in group.items]

    def test_module_one_candidates_are_current_reviewed_unpublished_artifacts(self) -> None:
        published_ids = set(load_publication_catalog().published_lesson_ids)
        course_lessons = {lesson.id: lesson for lesson in A2_COURSE_LESSONS}

        for number in range(1, 7):
            lesson_id = f"a2-course-{number:03d}"
            with self.subTest(lesson=lesson_id):
                artifact = load_candidate_artifact(lesson_id)
                self.assertEqual([], candidate_errors(lesson_id, artifact))
                candidate_data = artifact.lesson.model_dump(mode="json")
                candidate_data["audio_status"] = "pending"
                candidate_data["audio_path"] = None
                for sentence in candidate_data["sentences"]:
                    sentence["audio_path"] = None
                self.assertEqual(
                    course_lessons[lesson_id].model_dump(mode="json"),
                    candidate_data,
                )
                if lesson_id in published_ids:
                    self.assertEqual("ready", artifact.lesson.audio_status)
                    self.assertIsNotNone(artifact.lesson.audio_path)

                review = json.loads(
                    (candidate_directory(lesson_id) / "review.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(lesson_id, review["lesson_id"])
                self.assertEqual(artifact.source_sha256, review["source_sha256"])
                self.assertEqual("pass", review["overall_verdict"])

    def test_audited_forms_and_contextual_cards(self) -> None:
        forgotten = next(
            item for item in self._items(1, 1) if item.german == "vergessen" and item.kind == "word"
        )
        self.assertEqual("vergisst", forgotten.verb_help.present_forms[2].verb)
        self.assertEqual(
            "he/she/it has forgotten", forgotten.verb_help.current_english_forms[2]
        )

        returned = next(
            item for item in self._items(1, 2) if item.german == "zurückgefahren" and item.kind == "word"
        )
        self.assertEqual("fährst zurück", returned.verb_help.present_forms[1].verb)
        self.assertEqual("I have traveled back", returned.verb_help.current_english_forms[0])

        rained = next(
            item for item in self._items(5, 1) if item.german == "geregnet" and item.kind == "word"
        )
        self.assertEqual("regnet", rained.verb_help.present_forms[2].verb)

        was = next(item for item in self._items(2, 0) if item.german == "war" and item.kind == "word")
        self.assertEqual("you were", was.verb_help.current_english_forms[1])

        hats = [item for item in self._items(2, 4) if item.german == "hat" and item.kind == "word"]
        self.assertEqual(2, len(hats))
        self.assertNotIn("auxiliary", {tag.label for tag in hats[0].tags})
        self.assertIn("auxiliary", {tag.label for tag in hats[1].tags})

        zu_cards = [item for item in self._items(3, 0) if item.german == "zu" and item.kind == "word"]
        self.assertEqual(2, len(zu_cards))
        self.assertIn("particle", {tag.label for tag in zu_cards[0].tags})
        self.assertIn("preposition", {tag.label for tag in zu_cards[1].tags})

        self.assertEqual(
            "to tomorrow",
            next(item.english for item in self._items(4, 3) if item.german == "auf morgen"),
        )
        self.assertEqual(
            "they",
            next(item.english for item in self._items(6, 3) if item.german == "sie" and item.kind == "word"),
        )

    def test_attributive_endings_have_case_explanations(self) -> None:
        cases = [
            (1, 4, "neuen", "accusative"),
            (2, 0, "kleines", "accusative"),
            (2, 4, "gute", "accusative"),
            (4, 0, "große", "accusative"),
            (4, 4, "welche", "nominative"),
            (5, 4, "ganze", "nominative"),
        ]
        for lesson, sentence, surface, case in cases:
            with self.subTest(lesson=lesson, sentence=sentence, surface=surface):
                self.assertTrue(
                    any(
                        help.surface == surface and help.case == case
                        for item in self._items(lesson, sentence)
                        for help in item.inflection_help
                    )
                )
