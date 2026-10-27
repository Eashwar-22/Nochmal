import json
import re
import unittest
from collections import Counter

from nochmal.content import A2_COURSE_LESSONS
from nochmal.content.grammar_reference import selected_column_for_help, table_for_help
from nochmal.content.ordering import ordered_breakdown_items
from nochmal.content.source_models import CourseLessonSource
from nochmal.content.validation import validate_lesson_library
from nochmal.paths import PROJECT_ROOT


TOKEN_PATTERN = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)
A2_ROOT = PROJECT_ROOT / "curriculum" / "a2_course"


def source_records() -> list[CourseLessonSource]:
    records: list[CourseLessonSource] = []
    for path in sorted((A2_ROOT / "lessons").glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        records.extend(
            CourseLessonSource.model_validate(item)
            for item in (payload if isinstance(payload, list) else [payload])
        )
    return sorted(records, key=lambda item: item.sequence)


class A2CourseTests(unittest.TestCase):
    def test_complete_numbering_and_level_split(self) -> None:
        self.assertEqual(72, len(A2_COURSE_LESSONS))
        self.assertEqual(
            [f"a2-course-{number:03d}" for number in range(1, 73)],
            [lesson.id for lesson in A2_COURSE_LESSONS],
        )
        self.assertEqual(
            list(range(49, 121)),
            [lesson.sequence for lesson in A2_COURSE_LESSONS],
        )
        self.assertEqual(
            ["A2.1"] * 36 + ["A2.2"] * 36,
            [lesson.level for lesson in A2_COURSE_LESSONS],
        )

    def test_sources_are_strict_production_lessons_with_checkpoint_cadence(self) -> None:
        records = source_records()
        self.assertEqual(72, len(records))
        for number, source in enumerate(records, start=1):
            with self.subTest(lesson=source.id):
                self.assertEqual(f"a2-course-{number:03d}", source.id)
                self.assertEqual(f"a2-draft-{number:03d}", source.source_draft_id)
                self.assertEqual(48 + number, source.sequence)
                self.assertEqual(len(source.new_targets), len(set(source.new_targets)))
                self.assertGreaterEqual(len(source.sentences), 5)
                self.assertLessEqual(len(source.sentences), 7)
                if number % 6 == 0:
                    self.assertTrue(
                        {"consolidation", "retrieval"}
                        & set(source.grammar_focus.casefold().split())
                    )
                    self.assertEqual(5, len(source.new_targets))

    def test_course_passes_the_full_non_audio_contract(self) -> None:
        self.assertEqual(
            [],
            validate_lesson_library(A2_COURSE_LESSONS, project_root=PROJECT_ROOT),
        )

    def test_authored_a2_sources_keep_audio_pending(self) -> None:
        for lesson in A2_COURSE_LESSONS:
            with self.subTest(lesson=lesson.id):
                self.assertEqual("pending", lesson.audio_status)
                self.assertIsNone(lesson.audio_path)
                self.assertTrue(all(sentence.audio_path is None for sentence in lesson.sentences))

    def test_every_source_token_has_exactly_one_word_card_owner(self) -> None:
        for lesson in A2_COURSE_LESSONS:
            for sentence_number, sentence in enumerate(lesson.sentences, start=1):
                with self.subTest(lesson=lesson.id, sentence=sentence_number):
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
                        source.casefold()
                        for item in words
                        for source in item.source_forms
                    )
                    self.assertEqual(expected, actual)

    def test_nouns_verbs_and_inflection_cards_are_self_contained(self) -> None:
        conflicting_nonverb_tags = {
            "noun", "article", "determiner", "possessive", "personal pronoun",
            "reflexive pronoun", "adjective", "adverb", "preposition", "conjunction",
        }
        for lesson in A2_COURSE_LESSONS:
            for sentence in lesson.sentences:
                for group in sentence.breakdown_groups:
                    for item in group.items:
                        labels = {grammar_tag.label for grammar_tag in item.tags}
                        if item.kind == "word" and labels & {
                            "noun", "compound noun", "masc.", "fem.", "neuter"
                        }:
                            self.assertRegex(item.german, r"(?i)^(der|die|das)\s")
                        if item.kind == "word" and "verb" in labels:
                            self.assertIsNotNone(item.verb_help)
                        if item.verb_help is not None:
                            self.assertFalse(labels & conflicting_nonverb_tags)
                            self.assertEqual(6, len(item.verb_help.present_forms or []))
                            self.assertEqual(6, len(item.verb_help.present_english_forms or []))
                            self.assertEqual(
                                len(item.verb_help.forms),
                                len(item.verb_help.current_english_forms or []),
                            )
                        for help_card in item.inflection_help:
                            self.assertEqual("phrase", item.kind)
                            self.assertIn(help_card.case, labels)
                            table = table_for_help(help_card)
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
                                self.assertIn(
                                    visible.casefold(),
                                    {
                                        option.strip().casefold()
                                        for option in expected_form.split("/")
                                    },
                                )

    def test_a2_tense_and_form_regressions(self) -> None:
        lessons = {lesson.id: lesson for lesson in A2_COURSE_LESSONS}

        def word(lesson_number: int, surface: str, occurrence: int = 1):
            matches = [
                item
                for sentence in lessons[f"a2-course-{lesson_number:03d}"].sentences
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word" and surface in item.source_forms
            ]
            return matches[occurrence - 1]

        self.assertEqual("Perfekt (conversational past)", word(1, "bekommen").verb_help.tense)
        polite_request = word(13, "Könnten").verb_help
        self.assertEqual(
            ["könnte", "könntest", "könnte", "könnten", "könntet", "könnten"],
            [form.verb for form in polite_request.forms],
        )
        self.assertEqual(
            ["I could", "you could", "he/she/it could", "we could", "you could", "they/you could"],
            polite_request.current_english_forms,
        )
        apology = word(13, "tut").verb_help
        self.assertEqual("to cause regret / make someone feel sorry", apology.english)
        self.assertEqual("he/she/it causes regret", apology.present_english_forms[2])
        self.assertEqual("he/she/it causes regret", apology.current_english_forms[2])
        apology_card = word(13, "tut")
        self.assertEqual(["tut", "leid"], apology_card.source_forms)
        self.assertFalse(
            any(
                item.kind == "word" and item.source_forms == ["leid"]
                for sentence in lessons["a2-course-013"].sentences
                for group in sentence.breakdown_groups
                for item in group.items
            )
        )
        annoyance = word(14, "geärgert").verb_help
        self.assertEqual(
            ["ärgere mich", "ärgerst dich", "ärgert sich", "ärgern uns", "ärgert euch", "ärgern sich"],
            [form.verb for form in annoyance.present_forms],
        )
        promise = word(14, "verspreche").verb_help
        self.assertEqual("versprichst", promise.present_forms[1].verb)
        self.assertEqual("verspricht", promise.present_forms[2].verb)
        calming = word(14, "beruhigen").verb_help
        self.assertEqual("he/she/it calms down", calming.present_english_forms[2])
        self.assertEqual("Perfekt (conversational past)", word(20, "begonnen").verb_help.tense)
        self.assertEqual("Konjunktiv II (polite/conditional)", word(24, "würde").verb_help.tense)
        self.assertEqual("would", word(24, "würde").english)
        self.assertEqual("Präsens (present)", word(33, "erfahren").verb_help.tense)
        self.assertEqual(
            "Partizip II with bekommen (recipient passive)",
            word(39, "erstattet").verb_help.tense,
        )
        self.assertTrue(word(39, "bekommen").verb_help.tense.startswith("Infinitiv"))
        self.assertTrue(word(49, "nachzusehen").verb_help.tense.startswith("Infinitiv"))
        self.assertEqual("Präteritum (simple past)", word(53, "fand").verb_help.tense)
        self.assertEqual("Imperativ (command/request)", word(61, "überweisen").verb_help.tense)
        self.assertEqual(
            "Präteritum Passiv (simple-past passive)",
            word(62, "verletzt").verb_help.tense,
        )
        self.assertEqual("Perfekt (conversational past)", word(71, "erfahren").verb_help.tense)
        self.assertEqual(
            "Präteritum Passiv (simple-past passive)",
            word(71, "geändert").verb_help.tense,
        )
        self.assertTrue(word(71, "einreichen").verb_help.tense.startswith("Infinitiv"))
        self.assertTrue(word(71, "geklärt").verb_help.tense.startswith("Partizip II"))
        self.assertTrue(word(16, "leihen").verb_help.tense.startswith("Infinitiv"))
        self.assertTrue(word(16, "helfen").verb_help.tense.startswith("Infinitiv"))

    def test_only_intended_names_and_labels_are_proper_nouns(self) -> None:
        allowed = {
            "B1", "Berlin", "Bonn", "Gartenstraße", "Hamburg", "Hannover",
            "Braun", "Frau", "Herr", "Keller", "Klein", "Koch", "Köln", "Leo", "Lina", "Mara", "Mina", "Nord", "Nordwind",
            "Roth", "Sara", "West",
        }
        actual = {
            item.source_forms[-1]
            for lesson in A2_COURSE_LESSONS
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "word"
            and any(grammar_tag.label == "proper noun" for grammar_tag in item.tags)
        }
        self.assertEqual(allowed, actual)

    def test_checkpoint_formal_references_and_imperative(self) -> None:
        lesson = next(lesson for lesson in A2_COURSE_LESSONS if lesson.id == "a2-course-018")
        items = [item for sentence in lesson.sentences for group in sentence.breakdown_groups for item in group.items]
        formal_pronoun = next(
            help_card for item in items if item.kind == "phrase"
            for help_card in item.inflection_help
            if help_card.surface == "Ihnen"
        )
        self.assertEqual("Sie", formal_pronoun.base)
        formal_possessive = next(
            help_card for item in items if item.kind == "phrase"
            for help_card in item.inflection_help
            if help_card.surface == "Ihr"
        )
        self.assertEqual("Ihr", formal_possessive.base)
        command = next(
            item for item in items
            if item.kind == "word" and "Geben" in item.source_forms
        )
        self.assertEqual("Imperativ (command/request)", command.verb_help.tense)


if __name__ == "__main__":
    unittest.main()
