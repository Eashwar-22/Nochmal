"""Behavioral checks for the numbered A2 orchestration entry point."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import lesson_flow


class LessonFlowTests(unittest.TestCase):
    def test_prepare_refuses_to_replace_a_published_lesson(self) -> None:
        with patch.object(lesson_flow, "published_ids", return_value={"a2-course-012"}):
            with self.assertRaisesRegex(ValueError, "already published"):
                lesson_flow.prepare("a2-course-012")

    def test_preflight_requires_current_candidate_and_suite_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            receipt = Path(directory) / "preflight.json"
            expected = {
                "lesson_id": "a2-course-013",
                "source_sha256": "source",
                "compiled_lesson_sha256": "compiled",
                "review_sha256": "review",
                "suite_inputs_sha256": "suite",
            }
            receipt.write_text(json.dumps({**expected, "passed_at": "now"}), encoding="utf-8")
            with (
                patch.object(lesson_flow, "preflight_path", return_value=receipt),
                patch.object(lesson_flow, "preflight_inputs", return_value=expected),
            ):
                lesson_flow.require_preflight("a2-course-013")
                expected["suite_inputs_sha256"] = "changed"
                with self.assertRaisesRegex(ValueError, "stale"):
                    lesson_flow.require_preflight("a2-course-013")

    def test_ready_stops_at_failed_audit_before_audio(self) -> None:
        with (
            patch.object(lesson_flow, "published_ids", return_value=set()),
            patch.object(lesson_flow, "rebuild_after_repair_if_needed"),
            patch.object(lesson_flow, "passing_review", side_effect=ValueError("stale")),
            patch.object(lesson_flow, "audit", return_value=False) as audit,
            patch.object(lesson_flow, "review_findings", return_value="- sentence 2: wrong case"),
            patch.object(lesson_flow, "audio") as audio,
        ):
            with self.assertRaisesRegex(ValueError, "sentence 2: wrong case"):
                lesson_flow.ready(["a2-course-016"], model="gpt-6.1-sol", reasoning_effort="high")
            audit.assert_called_once_with("a2-course-016", model="gpt-6.1-sol", reasoning_effort="high")
            audio.assert_not_called()

    def test_ready_reuses_current_evidence_without_repeating_paid_steps(self) -> None:
        with (
            patch.object(lesson_flow, "published_ids", return_value=set()),
            patch.object(lesson_flow, "rebuild_after_repair_if_needed"),
            patch.object(lesson_flow, "passing_review"),
            patch.object(lesson_flow, "audit") as audit,
            patch.object(lesson_flow, "load_candidate_source"),
            patch.object(lesson_flow, "load_verified_audio"),
            patch.object(lesson_flow, "audio") as audio,
            patch.object(lesson_flow, "step") as step,
            patch.object(lesson_flow, "require_preflight"),
            patch.object(lesson_flow, "run_preflight") as preflight,
        ):
            lesson_flow.ready(["a2-course-016"], model="gpt-6.1-sol", reasoning_effort="high")
            audit.assert_not_called()
            audio.assert_not_called()
            step.assert_called_once_with("mobile_lesson", "prepare-candidate", "a2-course-016")
            preflight.assert_not_called()

    def test_ready_prepares_preview_and_preflights_without_confirmation(self) -> None:
        with (
            patch.object(lesson_flow, "published_ids", return_value=set()),
            patch.object(lesson_flow, "rebuild_after_repair_if_needed"),
            patch.object(lesson_flow, "passing_review"),
            patch.object(lesson_flow, "load_candidate_source"),
            patch.object(lesson_flow, "load_verified_audio"),
            patch.object(lesson_flow, "step") as step,
            patch.object(lesson_flow, "require_preflight", side_effect=ValueError("missing")),
            patch.object(lesson_flow, "run_preflight") as preflight,
        ):
            lesson_flow.ready(["a2-course-016"], model="gpt-6.1-sol", reasoning_effort="high")
            step.assert_called_once_with("mobile_lesson", "prepare-candidate", "a2-course-016")
            preflight.assert_called_once_with(["a2-course-016"])

    def test_independent_audit_is_read_only_and_bound_to_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "lesson-source.json"
            source.write_text('{"id":"a2-course-013"}', encoding="utf-8")

            def fake_codex(command, *, input, text, cwd, check):
                self.assertEqual(["codex", "exec"], command[:2])
                self.assertEqual("read-only", command[command.index("--sandbox") + 1])
                self.assertEqual("gpt-6.1-sol", command[command.index("--model") + 1])
                self.assertIn("model_reasoning_effort=high", command)
                self.assertIn("independently audit", input.lower())
                self.assertIn("uses `sentences`, with `de`", input)
                output = Path(command[command.index("--output-last-message") + 1])
                output.write_text(json.dumps({
                    "overall_verdict": "pass",
                    "audits": [{
                        "kind": kind,
                        "verdict": "pass",
                        "checks": ["Sentence-by-sentence review"],
                        "findings": [],
                    } for kind in ("rulebook", "language", "translation-pedagogy")],
                }), encoding="utf-8")

            with (
                patch.object(lesson_flow, "source_path", return_value=source),
                patch.object(lesson_flow, "candidate_directory", return_value=root),
                patch.object(lesson_flow, "load_candidate_source"),
                patch.object(lesson_flow, "load_candidate_artifact"),
                patch.object(lesson_flow.subprocess, "run", side_effect=fake_codex),
            ):
                lesson_flow.audit("a2-course-013", model="gpt-6.1-sol")
            report = json.loads((root / "review.json").read_text(encoding="utf-8"))
            self.assertEqual(lesson_flow.digest(source), report["source_sha256"])
            self.assertEqual("pass", report["overall_verdict"])

    def test_release_installs_and_deploys_without_confirmation(self) -> None:
        with (
            patch.object(lesson_flow, "published_ids", return_value=set()),
            patch.object(lesson_flow, "ready") as ready,
            patch.object(lesson_flow, "passing_review"),
            patch.object(lesson_flow, "require_preflight"),
            patch.object(lesson_flow, "step") as step,
            patch.object(lesson_flow, "upload"),
            patch.object(lesson_flow, "deploy") as deploy,
        ):
            lesson_flow.release(["a2-course-016"])
        ready.assert_called_once_with(
            ["a2-course-016"],
            model=lesson_flow.DEFAULT_AUDIT_MODEL,
            reasoning_effort=lesson_flow.DEFAULT_AUDIT_REASONING_EFFORT,
        )
        self.assertEqual(
            [
                ("publish_candidate", "a2-course-016"),
                ("validate_release", "a2-course-016"),
                ("compact_lesson_audio", "a2-course-016", "--apply"),
                ("mobile_lesson", "prepare", "a2-course-016"),
                ("mobile_lesson", "install", "a2-course-016"),
                ("compact_lesson_audio", "a2-course-016", "--apply"),
            ],
            [call.args for call in step.call_args_list],
        )
        deploy.assert_called_once_with(["a2-course-016"])


if __name__ == "__main__":
    unittest.main()
