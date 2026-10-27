"""Storage compaction must preserve published bytes during later edits."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from nochmal.workflows.attach_candidate_audio import copy_verified
from nochmal.workflows.compact_lesson_audio import compact_pair
from nochmal.workflows.generate_staged_elevenlabs_audio import write_pcm_wav


class CompactLessonAudioTests(unittest.TestCase):
    def test_matching_clips_share_storage_and_mismatch_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            published = root / "published.wav"
            candidate = root / "candidate.wav"
            different = root / "different.wav"
            published.write_bytes(b"same audio")
            candidate.write_bytes(b"same audio")
            different.write_bytes(b"other audio")
            self.assertEqual(len(b"same audio"), compact_pair(published, candidate, apply=False))
            self.assertNotEqual(published.stat().st_ino, candidate.stat().st_ino)
            self.assertEqual(len(b"same audio"), compact_pair(published, candidate, apply=True))
            self.assertTrue(os.path.samefile(published, candidate))
            self.assertEqual(0, compact_pair(published, different, apply=True))
            self.assertEqual(b"other audio", different.read_bytes())

    def test_audio_writers_detach_shared_clip_before_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            published = root / "published.wav"
            staged = root / "staged.wav"
            candidate = root / "candidate.wav"
            replacement = root / "replacement.wav"
            write_pcm_wav(published, b"\x00\x00")
            os.link(published, staged)
            os.link(published, candidate)
            original = published.read_bytes()
            write_pcm_wav(staged, b"\x01\x00")
            replacement.write_bytes(b"other audio")
            copy_verified(replacement, candidate, force=True)
            self.assertEqual(original, published.read_bytes())
            self.assertEqual(b"other audio", candidate.read_bytes())
            self.assertFalse(os.path.samefile(published, staged))
            self.assertFalse(os.path.samefile(published, candidate))


if __name__ == "__main__":
    unittest.main()
