import json
import tempfile
import unittest
from pathlib import Path

from nochmal.services.storage import ProgressStore


class ProgressStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "progress.db"
        self.store = ProgressStore(database_path)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_attempt_can_be_resumed_and_completed(self) -> None:
        audio_hash = "same-audio-hash"
        attempt_id = self.store.start_attempt(
            "lesson-one",
            "My first answer",
            metadata={"audio_sha256": audio_hash},
        )

        saved_attempt = self.store.latest_incomplete_attempt("lesson-one")
        self.assertIsNotNone(saved_attempt)
        self.assertEqual(saved_attempt["id"], attempt_id)
        self.assertEqual(saved_attempt["stage"], "study")
        self.assertEqual(saved_attempt["initial_answer"], "My first answer")

        self.store.set_stage(
            attempt_id,
            "final",
            event_type="study_completed",
        )
        self.store.complete_attempt(
            attempt_id,
            "My final answer",
            metadata={"audio_sha256": audio_hash},
        )

        self.assertIsNone(self.store.latest_incomplete_attempt("lesson-one"))
        completed = self.store.recent_attempts()[0]
        self.assertEqual(completed["stage"], "complete")
        self.assertEqual(completed["final_answer"], "My final answer")
        self.assertIsNotNone(completed["completed_at"])
        self.assertEqual(self.store.completed_lesson_ids(), {"lesson-one"})

        events = self.store.events_for_attempt(attempt_id)
        self.assertEqual(
            [event["event_type"] for event in events],
            [
                "initial_answer_submitted",
                "study_completed",
                "attempt_completed",
            ],
        )
        first_hash = json.loads(events[0]["metadata_json"])["audio_sha256"]
        final_hash = json.loads(events[-1]["metadata_json"])["audio_sha256"]
        self.assertEqual(first_hash, final_hash)

    def test_abandoned_attempt_is_not_resumed(self) -> None:
        attempt_id = self.store.start_attempt("lesson-one", "An answer")
        self.store.abandon_attempt(attempt_id)

        self.assertIsNone(self.store.latest_incomplete_attempt("lesson-one"))
        self.assertEqual(self.store.recent_attempts()[0]["stage"], "abandoned")
        self.assertEqual(self.store.completed_lesson_ids(), set())

    def test_direct_completion_and_full_progress_reset(self) -> None:
        attempt_id = self.store.mark_lesson_complete(
            "lesson-one",
            metadata={"source": "direct-study"},
        )

        self.assertEqual(self.store.completed_lesson_ids(), {"lesson-one"})
        attempt = self.store.recent_attempts()[0]
        self.assertEqual(attempt["stage"], "complete")
        self.assertEqual(attempt["initial_answer"], "")
        self.assertEqual(attempt["final_answer"], "")
        events = self.store.events_for_attempt(attempt_id)
        self.assertEqual([event["event_type"] for event in events], ["lesson_completed"])

        self.store.clear_all_progress()

        self.assertEqual(self.store.recent_attempts(), [])
        self.assertEqual(self.store.events_for_attempt(attempt_id), [])
        self.assertEqual(self.store.completed_lesson_ids(), set())


if __name__ == "__main__":
    unittest.main()
