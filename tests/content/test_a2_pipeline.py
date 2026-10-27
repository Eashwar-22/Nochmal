import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from nochmal.content.candidates import load_candidate_source
from nochmal.content.catalog import load_publication_catalog
from nochmal.content.course_paths import (
    candidate_audio_root,
    published_audio_root,
    published_root,
    staged_audio_root,
)
from nochmal.validation.release import release_errors
from nochmal.workflows import attach_candidate_audio, generate_staged_elevenlabs_audio
from nochmal.workflows import publish_candidate
from scripts import lesson_flow


class A2PipelineTests(unittest.TestCase):
    def test_a2_audio_and_publication_paths_are_separate_from_a1(self) -> None:
        lesson_id = "a2-course-001"
        self.assertEqual("a2_candidates", candidate_audio_root(lesson_id).name)
        self.assertEqual("a2_staging", staged_audio_root("a2-draft-001").name)
        self.assertEqual("a2_published", published_root(lesson_id).name)
        self.assertEqual("a2_published", published_audio_root(lesson_id).name)
        self.assertNotEqual(published_root(lesson_id), published_root("a1-course-001"))

    def test_a2_audio_uses_exact_authored_sentence_text(self) -> None:
        source = load_candidate_source("a2-course-001")
        generated = generate_staged_elevenlabs_audio.find_lesson(source.source_draft_id)
        staged = attach_candidate_audio.staged_record(source.source_draft_id)
        expected = [{"de": sentence.de, "en": sentence.en} for sentence in source.sentences]
        self.assertEqual(expected, [
            {"de": sentence["de"], "en": sentence["en"]}
            for sentence in generated["sentences"]
        ])
        self.assertEqual(expected, [
            {"de": sentence["de"], "en": sentence["en"]}
            for sentence in staged["sentences"]
        ])

    def test_flow_runs_internal_steps_as_modules(self) -> None:
        with patch.object(lesson_flow, "run") as run:
            lesson_flow.step("publish_candidate", "a2-course-001")
        self.assertEqual(
            (lesson_flow.sys.executable, "-m", "nochmal.workflows.publish_candidate", "a2-course-001"),
            run.call_args.args,
        )

    def test_published_a2_audio_paths_are_level_specific(self) -> None:
        source = load_candidate_source("a2-course-001")
        candidate_prefix = "assets/audio/a2_candidates/a2-course-001/"
        source = source.model_copy(update={
            "audio_path": candidate_prefix + "paragraph.wav",
            "sentences": [
                sentence.model_copy(update={"audio_path": candidate_prefix + f"sentence-{index:02d}.wav"})
                for index, sentence in enumerate(source.sentences, start=1)
            ],
        })
        manifest = SimpleNamespace(
            paragraph_file="paragraph.wav",
            sentence_files=[f"sentence-{index:02d}.wav" for index in range(1, 6)],
        )
        published = publish_candidate.published_source(source, source.id, manifest)
        self.assertEqual(
            "assets/audio/a2_published/a2-course-001/paragraph.wav",
            published.audio_path,
        )
        self.assertTrue(all(
            sentence.audio_path.startswith("assets/audio/a2_published/a2-course-001/")
            for sentence in published.sentences
        ))

    def test_catalog_aggregates_a1_and_a2_without_cross_level_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            a1_root = root / "a1_published"
            a2_root = root / "a2_published"
            a1_root.mkdir()
            a2_root.mkdir()
            a1_path = a1_root / "publication.json"
            a2_path = a2_root / "publication.json"
            a1_path.write_text(json.dumps({
                "published_lesson_ids": ["a1-course-001"],
            }), encoding="utf-8")
            a2_path.write_text(json.dumps({
                "published_lesson_ids": ["a2-course-001"],
            }), encoding="utf-8")
            def catalog_root(lesson_id: str) -> Path:
                return a1_root if lesson_id.startswith("a1-") else a2_root

            with patch("nochmal.content.catalog.discovered_levels", return_value=("a1", "a2")), patch(
                "nochmal.content.catalog.published_root", side_effect=catalog_root
            ):
                catalog = load_publication_catalog()
            self.assertEqual(
                ("a1-course-001", "a2-course-001"), catalog.published_lesson_ids
            )

    def test_a2_release_gate_reads_a2_storage(self) -> None:
        lesson_id = "a2-course-001"
        if lesson_id in load_publication_catalog().published_lesson_ids:
            self.assertEqual([], release_errors(lesson_id))
        else:
            self.assertIn(
                f"source: no production lesson exists for {lesson_id}",
                release_errors(lesson_id),
            )


if __name__ == "__main__":
    unittest.main()
