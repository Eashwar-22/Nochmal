import json
import re
import unittest
from pathlib import Path

from nochmal.content.candidates import (
    artifact_path,
    candidate_errors,
    load_candidate_artifact,
    source_path,
)
from nochmal.paths import PROJECT_ROOT
from nochmal.ui.app import PUBLISHED_LESSON_IDS


STAGED_PATH = PROJECT_ROOT / "curriculum" / "a1_staging" / "lessons" / "module_01.json"
PREVIEW_PATH = PROJECT_ROOT / "curriculum" / "a1_candidates" / "a1-course-002" / "preview.md"


class LessonCandidateTests(unittest.TestCase):
    def test_lesson_two_is_prebuilt_but_not_published(self) -> None:
        artifact = load_candidate_artifact("a1-course-002")
        self.assertEqual([], candidate_errors("a1-course-002", artifact))
        self.assertEqual("pending", artifact.lesson.audio_status)
        self.assertNotIn("a1-course-002", PUBLISHED_LESSON_IDS)
        self.assertTrue(source_path("a1-course-002").is_file())
        self.assertTrue(artifact_path("a1-course-002").is_file())
        self.assertTrue(PREVIEW_PATH.is_file())

    def test_candidate_text_matches_staged_lesson_two(self) -> None:
        staged = json.loads(STAGED_PATH.read_text(encoding="utf-8"))[1]
        source = json.loads(source_path("a1-course-002").read_text(encoding="utf-8"))
        self.assertEqual("a1-draft-002", staged["draft_id"])
        self.assertEqual(staged["draft_id"], source["source_draft_id"])
        self.assertEqual(staged["sentences"], [
            {"de": sentence["de"], "en": sentence["en"]}
            for sentence in source["sentences"]
        ])

    def test_candidate_has_exact_ordered_word_coverage(self) -> None:
        artifact = load_candidate_artifact("a1-course-002")
        token_pattern = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)
        for sentence in artifact.lesson.sentences:
            expected = [
                token.casefold() for token in token_pattern.findall(sentence.text)
            ]
            actual = [
                form.casefold()
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word"
                for form in item.source_forms
            ]
            self.assertEqual(expected, actual)

    def test_candidate_contains_the_reviewed_learning_phrases(self) -> None:
        artifact = load_candidate_artifact("a1-course-002")
        phrases = {
            item.german: (item.english, item.literal_meaning)
            for sentence in artifact.lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertEqual(
            ("Where are you from?", "Where from do you come?"),
            phrases["Woher kommst du"],
        )
        self.assertEqual(("from Spain", None), phrases["aus Spanien"])
        self.assertEqual(("in the city", None), phrases["in der Stadt"])
        self.assertEqual(("And you?", None), phrases["Und du"])

    def test_push_command_only_validates_and_copies_the_prebuilt_artifact(self) -> None:
        command_source = (PROJECT_ROOT / "scripts" / "push_lesson.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("load_candidate_artifact", command_source)
        self.assertIn("shutil.copyfile", command_source)
        self.assertIn('if __name__ == "__main__":', command_source)
        self.assertNotIn("compile_candidate", command_source)
        self.assertNotIn("urllib", command_source)
        self.assertNotIn("openai", command_source.casefold())


if __name__ == "__main__":
    unittest.main()
