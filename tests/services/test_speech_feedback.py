import unittest

from nochmal.services.speech_feedback import (
    AcceptedAlternative,
    PacingComparison,
    SpeechFeedback,
    compare_transcript,
    normalize_text,
    revise_transcript,
)


class SpeechFeedbackTests(unittest.TestCase):
    def test_normalization_preserves_german_letters_and_ignores_punctuation(self) -> None:
        self.assertEqual(
            normalize_text("Grüße, aus Köln! Weißt du's?"),
            "grüße aus köln weißt du s",
        )

    def test_spoken_and_numeric_beginner_numbers_are_equivalent(self) -> None:
        result = compare_transcript(
            "Ich bin achtundzwanzig Jahre alt.",
            "Ich bin 28 Jahre alt.",
        )

        self.assertEqual(result.match_percent, 100)
        self.assertEqual(result.differences, ())

    def test_lesson_authored_alternative_is_accepted_and_explained(self) -> None:
        alternative = AcceptedAlternative(
            lesson_phrase="am Vormittag",
            accepted_phrase="am Morgen",
            explanation="Both fit the English cue.",
        )
        result = compare_transcript(
            "Sie arbeitet am Vormittag.",
            "Sie arbeitet am Morgen.",
            (alternative,),
        )

        self.assertEqual(result.match_percent, 100)
        self.assertEqual(result.differences, ())
        self.assertEqual(result.accepted_alternatives, (alternative,))

    def test_reviewed_transcript_replaces_asr_errors_but_preserves_raw_text(self) -> None:
        raw = "Sie wohnt in Wohnen und versteht in gut."
        feedback = SpeechFeedback(
            raw_transcript=raw,
            transcript=compare_transcript(
                "Sie wohnt in Bonn und versteht ihn gut.",
                raw,
            ),
            pacing=PacingComparison(10.0, 11.0, 10 / 11, 0.02, 0.9),
        )

        revised = revise_transcript(
            feedback,
            reference_text="Sie wohnt in Bonn und versteht ihn gut.",
            corrected_transcript="Sie wohnt in Bonn und versteht ihn gut.",
        )

        self.assertEqual(revised.raw_transcript, raw)
        self.assertEqual(revised.transcript.match_percent, 100)
        self.assertEqual(revised.pacing, feedback.pacing)

    def test_comparison_matches_the_lesson_one_sample(self) -> None:
        reference = (
            "Hallo, ich heiße Mina. Ich komme aus Spanien und wohne jetzt in Bonn. "
            "Die Stadt ist schön, und ich spreche ein bisschen Deutsch."
        )
        transcript = (
            "Hallo, mein Name ist Mina. Ich komme aus Spanien und wohne jetzt in "
            "Bohnen. Die Stadt ist schön und ich spreche ein bisschen Deutsch."
        )

        result = compare_transcript(reference, transcript)

        self.assertEqual(result.substitutions, 3)
        self.assertEqual(result.deletions, 0)
        self.assertEqual(result.insertions, 1)
        self.assertAlmostEqual(result.word_error_rate, 4 / 23)
        self.assertEqual(result.match_percent, 83)
        self.assertEqual(
            [(item.kind, item.reference, item.heard) for item in result.differences],
            [
                ("extra", "", "mein"),
                ("different", "ich heiße", "name ist"),
                ("different", "bonn", "bohnen"),
            ],
        )

    def test_missing_transcript_reports_each_reference_word(self) -> None:
        result = compare_transcript("Hallo aus Bonn", "")

        self.assertEqual(result.deletions, 3)
        self.assertEqual(result.match_percent, 0)
        self.assertEqual(len(result.differences), 1)
        self.assertEqual(result.differences[0].reference, "hallo aus bonn")

    def test_empty_reference_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Reference text"):
            compare_transcript("...", "Hallo")


if __name__ == "__main__":
    unittest.main()
