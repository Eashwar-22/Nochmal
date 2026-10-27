import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

from nochmal.content.candidates import (
    artifact_path,
    candidate_errors,
    load_candidate_artifact,
    source_path,
)
from nochmal.content.catalog import load_publication_catalog
from nochmal.content.grammar_reference import selected_column_for_help, table_for_help
from nochmal.content.source_models import CourseSentenceSource
from nochmal.content.ordering import ordered_breakdown_items
from nochmal.paths import PROJECT_ROOT
from nochmal.validation.models import LessonReviewReport


STAGED_PATH = PROJECT_ROOT / "curriculum" / "a1_staging" / "lessons" / "module_01.json"
MODULE_TWO_STAGED_PATH = (
    PROJECT_ROOT / "curriculum" / "a1_staging" / "lessons" / "module_02.json"
)
MODULE_THREE_STAGED_PATH = (
    PROJECT_ROOT / "curriculum" / "a1_staging" / "lessons" / "module_03.json"
)
MODULE_FOUR_STAGED_PATH = (
    PROJECT_ROOT / "curriculum" / "a1_staging" / "lessons" / "module_04.json"
)
MODULE_FIVE_STAGED_PATH = (
    PROJECT_ROOT / "curriculum" / "a1_staging" / "lessons" / "module_05.json"
)
LESSON_ONE_PREVIEW_PATH = (
    PROJECT_ROOT / "curriculum" / "a1_candidates" / "a1-course-001" / "preview.md"
)
PREVIEW_PATH = PROJECT_ROOT / "curriculum" / "a1_candidates" / "a1-course-002" / "preview.md"
PUBLISHED_LESSON_IDS = load_publication_catalog().published_lesson_ids
LESSON_THREE_PREVIEW_PATH = (
    PROJECT_ROOT / "curriculum" / "a1_candidates" / "a1-course-003" / "preview.md"
)
LESSON_FOUR_PREVIEW_PATH = (
    PROJECT_ROOT / "curriculum" / "a1_candidates" / "a1-course-004" / "preview.md"
)


class LessonCandidateTests(unittest.TestCase):
    def test_authored_word_gloss_does_not_replace_sentence_meaning_in_generated_phrases(self) -> None:
        lesson = load_candidate_artifact("a2-course-015").lesson
        phrases = {
            item.german: item.english
            for group in lesson.sentences[2].breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertEqual(
            "The building rules say",
            phrases["In der Hausordnung steht"],
        )

    def test_lesson_one_is_available_through_the_same_candidate_workflow(self) -> None:
        artifact = load_candidate_artifact("a1-course-001")
        self.assertEqual([], candidate_errors("a1-course-001", artifact))
        self.assertEqual("ready", artifact.lesson.audio_status)
        self.assertIn("a1-course-001", PUBLISHED_LESSON_IDS)
        self.assertTrue(source_path("a1-course-001").is_file())
        self.assertTrue(artifact_path("a1-course-001").is_file())
        self.assertTrue(LESSON_ONE_PREVIEW_PATH.is_file())

    def test_lesson_two_corrected_candidate_is_audio_ready(self) -> None:
        artifact = load_candidate_artifact("a1-course-002")
        self.assertEqual([], candidate_errors("a1-course-002", artifact))
        self.assertEqual("ready", artifact.lesson.audio_status)
        self.assertEqual(
            "assets/audio/a1_candidates/a1-course-002/paragraph.wav",
            artifact.lesson.audio_path,
        )
        self.assertIn("a1-course-002", PUBLISHED_LESSON_IDS)
        self.assertTrue(source_path("a1-course-002").is_file())
        self.assertTrue(artifact_path("a1-course-002").is_file())
        self.assertTrue(PREVIEW_PATH.is_file())

    def test_lesson_two_has_a_current_passing_review_report(self) -> None:
        review_path = source_path("a1-course-002").with_name("review.json")
        review = LessonReviewReport.model_validate_json(
            review_path.read_text(encoding="utf-8")
        )
        self.assertEqual("a1-course-002", review.lesson_id)
        self.assertEqual("pass", review.overall_verdict)
        self.assertEqual(
            hashlib.sha256(source_path("a1-course-002").read_bytes()).hexdigest(),
            review.source_sha256,
        )

    def test_lesson_three_is_a_complete_reviewed_candidate(self) -> None:
        artifact = load_candidate_artifact("a1-course-003")
        self.assertEqual([], candidate_errors("a1-course-003", artifact))
        self.assertEqual("ready", artifact.lesson.audio_status)
        self.assertIn("a1-course-003", PUBLISHED_LESSON_IDS)
        self.assertTrue(LESSON_THREE_PREVIEW_PATH.is_file())

        review_path = source_path("a1-course-003").with_name("review.json")
        review = LessonReviewReport.model_validate_json(
            review_path.read_text(encoding="utf-8")
        )
        self.assertEqual("pass", review.overall_verdict)
        self.assertEqual(
            hashlib.sha256(source_path("a1-course-003").read_bytes()).hexdigest(),
            review.source_sha256,
        )
        staged = json.loads(STAGED_PATH.read_text(encoding="utf-8"))[2]
        source = json.loads(source_path("a1-course-003").read_text(encoding="utf-8"))
        self.assertEqual(staged["draft_id"], source["source_draft_id"])
        self.assertEqual(
            staged["sentences"],
            [
                {"de": sentence["de"], "en": sentence["en"]}
                for sentence in source["sentences"]
            ],
        )

    def test_lesson_three_repair_phrases_are_precise(self) -> None:
        artifact = load_candidate_artifact("a1-course-003")
        phrases = {
            item.german: (item.english, item.literal_meaning)
            for sentence in artifact.lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertEqual(("Pardon?", "How, please?"), phrases["Wie bitte"])
        self.assertEqual(
            ("Please say that again.", "Once again, please."),
            phrases["Noch einmal, bitte"],
        )
        self.assertNotIn("Wie bitte? Noch einmal", phrases)
        self.assertNotIn("Jetzt versteht Mina alles und sagt", phrases)

    def test_lesson_four_is_a_complete_audio_ready_candidate(self) -> None:
        artifact = load_candidate_artifact("a1-course-004")
        self.assertEqual([], candidate_errors("a1-course-004", artifact))
        self.assertEqual("ready", artifact.lesson.audio_status)
        self.assertIn("a1-course-004", PUBLISHED_LESSON_IDS)
        self.assertTrue(LESSON_FOUR_PREVIEW_PATH.is_file())

        review_path = source_path("a1-course-004").with_name("review.json")
        review = LessonReviewReport.model_validate_json(
            review_path.read_text(encoding="utf-8")
        )
        self.assertEqual("pass", review.overall_verdict)
        self.assertEqual(
            hashlib.sha256(source_path("a1-course-004").read_bytes()).hexdigest(),
            review.source_sha256,
        )

        staged = json.loads(STAGED_PATH.read_text(encoding="utf-8"))[3]
        source = json.loads(source_path("a1-course-004").read_text(encoding="utf-8"))
        self.assertEqual(staged["draft_id"], source["source_draft_id"])
        self.assertEqual(
            staged["sentences"],
            [{"de": sentence["de"], "en": sentence["en"]} for sentence in source["sentences"]],
        )

    def test_lesson_four_exposes_every_audited_form_change(self) -> None:
        artifact = load_candidate_artifact("a1-course-004")
        phrase_help = {
            item.german: {
                help_card.surface: (
                    help_card.base,
                    help_card.kind,
                    help_card.paradigm,
                    help_card.case,
                    help_card.gender,
                    help_card.contraction,
                )
                for help_card in item.inflection_help
            }
            for sentence in artifact.lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertEqual(
            ("der", "definite-article", "definite", "dative", "masculine", "in + dem"),
            phrase_help["Im Kurs"]["Im"],
        )
        self.assertEqual(
            ("ihr", "possessive-determiner", "possessive", "accusative", "feminine", None),
            phrase_help["ihre Telefonnummer"]["ihre"],
        )
        self.assertEqual(
            ("letzt", "adjective", "weak-adjective", "nominative", "feminine", None),
            phrase_help["die letzte Zahl"]["letzte"],
        )
        self.assertEqual(
            ("ihr", "possessive-determiner", "possessive", "accusative", "masculine", None),
            phrase_help["ihren Namen"]["ihren"],
        )
        sentence_two_words = {
            item.german: (item.english, item.spoken_form)
            for group in artifact.lesson.sentences[1].breakdown_groups
            for item in group.items
            if item.kind == "word"
        }
        self.assertEqual(
            ("zero one seven six", "null eins sieben sechs"),
            sentence_two_words["0176"],
        )
        self.assertEqual(
            ("four two zero eight", "vier zwei null acht"),
            sentence_two_words["4208"],
        )

        token_pattern = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)
        for sentence in artifact.lesson.sentences:
            expected = [
                token.casefold() for token in token_pattern.findall(sentence.text)
            ]
            actual = [
                source_form.casefold()
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word"
                for source_form in item.source_forms
            ]
            self.assertEqual(Counter(expected), Counter(actual))
            for group in sentence.breakdown_groups:
                for item in group.items:
                    if item.kind != "phrase":
                        continue
                    labels = {tag.label for tag in item.tags}
                    phrase_tokens = {
                        token.casefold()
                        for token in token_pattern.findall(item.german)
                    }
                    for help_card in item.inflection_help:
                        self.assertIn(help_card.case, labels)
                        self.assertIn(help_card.surface.casefold(), phrase_tokens)
                        table = table_for_help(help_card)
                        self.assertEqual(
                            {"nominative", "accusative", "dative", "genitive"},
                            set(table),
                        )
                        visible_form = help_card.resolved_form or help_card.surface
                        table_form = table[help_card.case][
                            selected_column_for_help(help_card)
                        ]
                        if help_card.kind == "adjective":
                            self.assertTrue(
                                visible_form.casefold().endswith(
                                    table_form.removeprefix("-").casefold()
                                )
                            )
                        else:
                            self.assertEqual(
                                visible_form.casefold(), table_form.casefold()
                            )

        sentence = artifact.lesson.sentences[2]
        ordered = ordered_breakdown_items(sentence.breakdown_groups[0], sentence.text)
        self.assertLess(
            [item.german for item in ordered].index("die Zahl"),
            [item.german for item in ordered].index("letzt"),
        )

    def test_lessons_five_and_six_are_reviewed_published_candidates(self) -> None:
        staged_records = json.loads(STAGED_PATH.read_text(encoding="utf-8"))
        for lesson_id, staged_index in (("a1-course-005", 4), ("a1-course-006", 5)):
            artifact = load_candidate_artifact(lesson_id)
            self.assertEqual([], candidate_errors(lesson_id, artifact))
            self.assertEqual("ready", artifact.lesson.audio_status)
            self.assertIn(lesson_id, PUBLISHED_LESSON_IDS)

            source = json.loads(source_path(lesson_id).read_text(encoding="utf-8"))
            self.assertEqual(
                staged_records[staged_index]["sentences"],
                [{"de": sentence["de"], "en": sentence["en"]} for sentence in source["sentences"]],
            )
            review = LessonReviewReport.model_validate_json(
                source_path(lesson_id).with_name("review.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("pass", review.overall_verdict)
            self.assertEqual(
                hashlib.sha256(source_path(lesson_id).read_bytes()).hexdigest(),
                review.source_sha256,
            )

    def test_lesson_eight_personal_details_cards_are_contextually_correct(self) -> None:
        lesson = load_candidate_artifact("a1-course-008").lesson
        words = {
            item.german: item
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "word"
        }
        self.assertEqual("you (formal)", words["Sie"].english)
        self.assertIn("accusative", {tag.label for tag in words["der Geburtstag"].tags})
        self.assertEqual("born", words["geboren"].english)
        self.assertIn("past participle", {tag.label for tag in words["geboren"].tags})
        self.assertEqual("gebären", words["geboren"].verb_help.infinitive)
        self.assertEqual("sechsten", words["6"].spoken_form)
        self.assertEqual("fünf drei eins eins eins", words["53111"].spoken_form)
        phrases = {
            item.german
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertIn("am 6. Mai", phrases)
        self.assertFalse(any("…" in phrase for phrase in phrases))

    def test_lessons_nine_and_twelve_use_aufstehen_and_der_word_help(self) -> None:
        for lesson_id, phrase_text in (
            ("a1-course-009", "jeden Morgen"),
            ("a1-course-012", "jeden Tag"),
        ):
            lesson = load_candidate_artifact(lesson_id).lesson
            words = [
                item
                for sentence in lesson.sentences
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word"
            ]
            steht = next(item for item in words if item.german == "steht")
            self.assertEqual("aufstehen", steht.verb_help.infinitive)
            self.assertEqual("get up", steht.english)
            self.assertTrue(any(item.german == "der Morgen" for item in words))
            phrase = next(
                item
                for sentence in lesson.sentences
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "phrase" and item.german == phrase_text
            )
            self.assertEqual(1, len(phrase.inflection_help))
            help_card = phrase.inflection_help[0]
            self.assertEqual(
                ("jeder", "jeden", "der-word-determiner", "der-word", "accusative"),
                (
                    help_card.base,
                    help_card.surface,
                    help_card.kind,
                    help_card.paradigm,
                    help_card.case,
                ),
            )

    def test_lesson_ten_time_cards_and_losfahren_are_precise(self) -> None:
        lesson = load_candidate_artifact("a1-course-010").lesson
        items = [
            item
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
        ]
        self.assertNotIn("viel Uhr", {item.german for item in items})
        self.assertNotIn("Um Viertel", {item.german for item in items})
        self.assertEqual(
            "quarter",
            next(item for item in items if item.german == "das Viertel").english,
        )
        fahren = next(item for item in items if item.german == "fährt")
        self.assertEqual("losfahren", fahren.verb_help.infinitive)
        self.assertEqual("set off", fahren.english)
        for phrase_text in ("Um Viertel nach sechs", "nicht um halb sieben"):
            phrase = next(item for item in items if item.german == phrase_text)
            self.assertNotIn("main clause", {tag.label for tag in phrase.tags})

    def test_lesson_eleven_modal_question_and_reflexive_pronoun_are_correct(self) -> None:
        lesson = load_candidate_artifact("a1-course-011").lesson
        self.assertIn("work long hours", lesson.sentences[1].natural_meaning)
        items = [
            item
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
        ]
        uns = next(item for item in items if item.german == "uns")
        self.assertEqual(
            {"reflexive pronoun", "accusative"},
            {tag.label for tag in uns.tags},
        )
        self.assertNotIn("uns am Dienstag", {item.german for item in items})
        modal_phrase = next(
            item
            for item in items
            if item.german == "Können wir uns am Dienstag um fünf Uhr treffen"
        )
        modal_tags = {tag.label for tag in modal_phrase.tags}
        self.assertIn("inversion", modal_tags)
        self.assertNotIn("verb-second", modal_tags)

    def test_lesson_twelve_reflexive_checkpoint_is_direct_and_audited(self) -> None:
        lesson = load_candidate_artifact("a1-course-012").lesson
        self.assertEqual("When do Mina and Leo meet?", lesson.initial_question)
        self.assertEqual("On Sunday at three o’clock.", lesson.initial_answer)
        items = [
            item
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
        ]
        sich = next(item for item in items if item.german == "sich")
        self.assertEqual(
            {"reflexive pronoun", "accusative"},
            {tag.label for tag in sich.tags},
        )
        coordinated = next(item for item in items if item.german == "und geht zur Arbeit")
        self.assertEqual(
            {"connector", "ellipsis"},
            {tag.label for tag in coordinated.tags},
        )

    def test_lessons_eight_through_twelve_have_current_passing_reviews(self) -> None:
        for sequence in range(8, 13):
            lesson_id = f"a1-course-{sequence:03d}"
            review = LessonReviewReport.model_validate_json(
                source_path(lesson_id).with_name("review.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("pass", review.overall_verdict)
            self.assertEqual(
                hashlib.sha256(source_path(lesson_id).read_bytes()).hexdigest(),
                review.source_sha256,
            )

    def test_lessons_eight_through_twelve_match_the_preserved_staging_text(self) -> None:
        staged_records = json.loads(MODULE_TWO_STAGED_PATH.read_text(encoding="utf-8"))
        for sequence in range(8, 13):
            lesson_id = f"a1-course-{sequence:03d}"
            source = json.loads(source_path(lesson_id).read_text(encoding="utf-8"))
            staged = staged_records[sequence - 7]
            self.assertEqual(source["source_draft_id"], staged["draft_id"])
            self.assertEqual(
                staged["sentences"],
                [
                    {"de": sentence["de"], "en": sentence["en"]}
                    for sentence in source["sentences"]
                ],
            )
            self.assertEqual(
                source["comprehension"],
                {
                    "question_en": staged["first_listen_check"]["prompt"],
                    "answer_en": staged["first_listen_check"]["answer"],
                },
            )

    def test_module_three_candidates_preserve_staging_and_are_published_audio_ready(self) -> None:
        staged_records = json.loads(MODULE_THREE_STAGED_PATH.read_text(encoding="utf-8"))
        for sequence, staged in enumerate(staged_records, start=13):
            lesson_id = f"a1-course-{sequence:03d}"
            artifact = load_candidate_artifact(lesson_id)
            self.assertEqual([], candidate_errors(lesson_id, artifact))
            self.assertEqual("ready", artifact.lesson.audio_status)
            self.assertIn(lesson_id, PUBLISHED_LESSON_IDS)

            source = json.loads(source_path(lesson_id).read_text(encoding="utf-8"))
            self.assertEqual(staged["draft_id"], source["source_draft_id"])
            self.assertEqual(
                staged["sentences"],
                [{"de": sentence["de"], "en": sentence["en"]} for sentence in source["sentences"]],
            )
            self.assertEqual(
                {
                    "question_en": staged["first_listen_check"]["prompt"],
                    "answer_en": staged["first_listen_check"]["answer"],
                },
                source["comprehension"],
            )
            review = LessonReviewReport.model_validate_json(
                source_path(lesson_id).with_name("review.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("pass", review.overall_verdict)
            self.assertEqual(
                hashlib.sha256(source_path(lesson_id).read_bytes()).hexdigest(),
                review.source_sha256,
            )

        negative_help = {
            card.surface: (card.kind, card.paradigm, card.case, card.gender)
            for group in load_candidate_artifact("a1-course-016").lesson.sentences[1].breakdown_groups
            for item in group.items
            if item.kind == "phrase"
            for card in item.inflection_help
        }
        self.assertEqual(
            ("negative-determiner", "negative", "accusative", "feminine"),
            negative_help["keine"],
        )
        self.assertEqual(
            ("negative-determiner", "negative", "accusative", "neuter"),
            negative_help["kein"],
        )

    def test_module_three_audit_repairs_are_preserved(self) -> None:
        price_sentence = load_candidate_artifact("a1-course-014").lesson.sentences[2]
        euro_cards = [
            item
            for group in price_sentence.breakdown_groups
            for item in group.items
            if item.kind == "word" and item.german == "der Euro"
        ]
        self.assertEqual(2, len(euro_cards))
        self.assertIn("plural", {tag.label for tag in euro_cards[0].tags})
        self.assertNotIn("plural", {tag.label for tag in euro_cards[1].tags})
        self.assertIn("accusative", {tag.label for tag in euro_cards[1].tags})

        lesson_fourteen_phrases = {
            item.german: item
            for sentence in load_candidate_artifact("a1-course-014").lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertNotIn("Die Verkäuferin antwortet: „Drei Euro", lesson_fourteen_phrases)
        self.assertNotIn("Auf dem Markt möchte Leo Äpfel", lesson_fourteen_phrases)
        self.assertNotIn("und Wasser kaufen", lesson_fourteen_phrases)
        self.assertNotIn("zwei Flaschen", lesson_fourteen_phrases)
        self.assertEqual(
            {"plural"},
            {tag.label for tag in lesson_fourteen_phrases["Drei Euro"].tags},
        )
        self.assertIn(
            "connector",
            {
                tag.label
                for tag in lesson_fourteen_phrases[
                    "und eine Flasche Wasser kostet einen Euro"
                ].tags
            },
        )
        for phrase in ("ein Kilo Äpfel", "einen Euro"):
            self.assertTrue(lesson_fourteen_phrases[phrase].inflection_help)

        how_much_sentence = load_candidate_artifact("a1-course-014").lesson.sentences[1]
        much_card = next(
            item
            for group in how_much_sentence.breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["viel"]
        )
        self.assertIn("numeral", {tag.label for tag in much_card.tags})

        excluded_generated_phrases = {
            "a1-course-013": {
                "Mina nimmt nur den Käse, bezahlt",
                "und sagt freundlich Danke",
            },
            "a1-course-015": {"heute essen sie lieber Käse"},
            "a1-course-016": {"kein Gemüse", "vier Äpfel"},
        }
        for lesson_id, excluded in excluded_generated_phrases.items():
            compiled_phrases = {
                item.german
                for sentence in load_candidate_artifact(lesson_id).lesson.sentences
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "phrase"
            }
            self.assertTrue(excluded.isdisjoint(compiled_phrases))

        lesson_eighteen = load_candidate_artifact("a1-course-018").lesson
        lesson_eighteen_phrases = {
            item.german: item
            for sentence in lesson_eighteen.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "phrase"
        }
        self.assertTrue(lesson_eighteen_phrases["ein Kilo Tomaten"].inflection_help)
        self.assertNotIn(
            "main clause",
            {tag.label for tag in lesson_eighteen_phrases["Sonst noch etwas"].tags},
        )
        self.assertNotIn("zwei Äpfel", lesson_eighteen_phrases)
        what_card = next(
            item
            for group in lesson_eighteen.sentences[0].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["Was"]
        )
        self.assertIn("interrogative pronoun", {tag.label for tag in what_card.tags})
        that_card = next(
            item
            for group in lesson_eighteen.sentences[4].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["das"]
        )
        self.assertIn("demonstrative pronoun", {tag.label for tag in that_card.tags})
        self.assertNotIn("personal pronoun", {tag.label for tag in that_card.tags})

        for lesson_id, sentence_index, surface, meaning in (
            ("a1-course-013", 1, "Sie", "she"),
            ("a1-course-015", 3, "sie", "they"),
            ("a1-course-016", 3, "sie", "they"),
            ("a1-course-018", 1, "Sie", "she"),
            ("a1-course-018", 2, "sie", "she"),
        ):
            sentence = load_candidate_artifact(lesson_id).lesson.sentences[sentence_index]
            card = next(
                item
                for group in sentence.breakdown_groups
                for item in group.items
                if item.kind == "word" and surface in item.source_forms
            )
            self.assertEqual(meaning, card.english)

    def test_occurrence_annotations_reject_an_out_of_range_token(self) -> None:
        with self.assertRaises(ValueError):
            CourseSentenceSource.model_validate(
                {
                    "de": "Ein Euro kostet einen Euro.",
                    "en": "One euro costs one euro.",
                    "annotations": {
                        "word_occurrences": [
                            {"surface": "Euro", "occurrence": 3, "tags": ["plural"]}
                        ]
                    },
                }
            )

    def test_lesson_six_preserves_colloquial_contraction_and_repeated_bitte_order(self) -> None:
        artifact = load_candidate_artifact("a1-course-006")
        greeting_words = {
            item.german: item.english
            for group in artifact.lesson.sentences[1].breakdown_groups
            for item in group.items
            if item.kind == "word"
        }
        self.assertEqual("goes", greeting_words["geht’s"])

        repair_sentence = artifact.lesson.sentences[3]
        ordered = ordered_breakdown_items(
            repair_sentence.breakdown_groups[0], repair_sentence.text
        )
        word_forms = [
            source.casefold()
            for item in ordered
            if item.kind == "word"
            for source in item.source_forms
        ]
        token_pattern = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)
        self.assertEqual(
            [token.casefold() for token in token_pattern.findall(repair_sentence.text)],
            word_forms,
        )

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

    def test_audio_attachment_command_is_deterministic_and_requires_v4(self) -> None:
        command_source = (
            PROJECT_ROOT / "nochmal" / "workflows" / "attach_candidate_audio.py"
        ).read_text(encoding="utf-8")
        self.assertIn("require_matching_audio", command_source)
        self.assertIn('manifest.get("model_id") != "eleven_v4"', command_source)
        self.assertIn("shutil.copy2", command_source)
        self.assertIn("compile_candidate(updated_source)", command_source)
        self.assertIn("rebound_review", command_source)
        self.assertNotIn("urllib", command_source)
        self.assertNotIn("openai", command_source.casefold())

    def test_publish_command_requires_review_and_release_gate(self) -> None:
        command_source = (
            PROJECT_ROOT / "nochmal" / "workflows" / "publish_candidate.py"
        ).read_text(encoding="utf-8")
        self.assertIn("load_passing_review", command_source)
        self.assertIn("load_verified_audio", command_source)
        self.assertIn("release.release_errors", command_source)
        self.assertIn("published_lesson_ids", command_source)
        self.assertNotIn("urllib", command_source)
        self.assertNotIn("openai", command_source.casefold())

    def test_single_flow_command_routes_internal_steps(self) -> None:
        flow_source = (PROJECT_ROOT / "scripts" / "lesson_flow.py").read_text(encoding="utf-8")
        self.assertIn('step("build_lesson_candidate"', flow_source)
        self.assertIn('step("generate_staged_elevenlabs_audio"', flow_source)
        self.assertIn('step("attach_candidate_audio"', flow_source)
        self.assertIn('step("publish_candidate"', flow_source)
        self.assertNotIn("run_lesson_pipeline", flow_source)

    def test_module_four_candidates_are_current_reviewed_active_artifacts(self) -> None:
        staged_records = json.loads(
            MODULE_FOUR_STAGED_PATH.read_text(encoding="utf-8")
        )
        for lesson_number, staged in zip(range(19, 25), staged_records, strict=True):
            lesson_id = f"a1-course-{lesson_number:03d}"
            artifact = load_candidate_artifact(lesson_id)
            source = json.loads(source_path(lesson_id).read_text(encoding="utf-8"))
            review = LessonReviewReport.model_validate_json(
                source_path(lesson_id).with_name("review.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual([], candidate_errors(lesson_id, artifact))
            self.assertEqual("ready", artifact.lesson.audio_status)
            self.assertIn(lesson_id, PUBLISHED_LESSON_IDS)
            self.assertEqual(staged["draft_id"], source["source_draft_id"])
            self.assertEqual(
                staged["sentences"],
                [
                    {"de": sentence["de"], "en": sentence["en"]}
                    for sentence in source["sentences"]
                ],
            )
            self.assertEqual("pass", review.overall_verdict)
            self.assertEqual(
                hashlib.sha256(source_path(lesson_id).read_bytes()).hexdigest(),
                review.source_sha256,
            )

    def test_module_four_audit_regressions_stay_fixed(self) -> None:
        lesson_nineteen = load_candidate_artifact("a1-course-019").lesson
        has_card = next(
            item
            for group in lesson_nineteen.sentences[1].breakdown_groups
            for item in group.items
            if item.kind == "word" and "hat" in item.source_forms
        )
        self.assertEqual("haben", has_card.verb_help.infinitive)

        lesson_twenty = load_candidate_artifact("a1-course-020").lesson
        standing_cards = [
            item
            for sentence in lesson_twenty.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.kind == "word" and "steht" in item.source_forms
        ]
        self.assertTrue(standing_cards)
        self.assertTrue(
            all(item.verb_help.infinitive == "stehen" for item in standing_cards)
        )
        mina = next(
            item
            for group in lesson_twenty.sentences[0].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["Mina"]
        )
        self.assertIn("dative", {tag.label for tag in mina.tags})

        lesson_twenty_one = load_candidate_artifact("a1-course-021").lesson
        repair = next(
            item
            for group in lesson_twenty_one.sentences[2].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["reparieren"]
        )
        self.assertIn("infinitive", {tag.label for tag in repair.tags})
        self.assertIn("Infinitiv", repair.verb_help.tense)

        lesson_twenty_two = load_candidate_artifact("a1-course-022").lesson
        gibt = next(
            item
            for group in lesson_twenty_two.sentences[0].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["gibt"]
        )
        self.assertEqual("there is / there are", gibt.english)

        lesson_twenty_three = load_candidate_artifact("a1-course-023").lesson
        sehen = next(
            item
            for group in lesson_twenty_three.sentences[3].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["sehen"]
        )
        self.assertNotIn("imperative", {tag.label for tag in sehen.tags})
        self.assertIn("present", {tag.label for tag in sehen.tags})

        lesson_twenty_four = load_candidate_artifact("a1-course-024").lesson
        visitor = next(
            item
            for group in lesson_twenty_four.sentences[0].breakdown_groups
            for item in group.items
            if item.kind == "word" and "Besucher" in item.source_forms
        )
        self.assertEqual("der Besucher", visitor.german)

    def test_module_five_candidates_are_current_reviewed_active_artifacts(self) -> None:
        staged_records = json.loads(
            MODULE_FIVE_STAGED_PATH.read_text(encoding="utf-8")
        )
        token_pattern = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)
        for lesson_number, staged in zip(range(25, 31), staged_records, strict=True):
            lesson_id = f"a1-course-{lesson_number:03d}"
            artifact = load_candidate_artifact(lesson_id)
            source = json.loads(source_path(lesson_id).read_text(encoding="utf-8"))
            review = LessonReviewReport.model_validate_json(
                source_path(lesson_id).with_name("review.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual([], candidate_errors(lesson_id, artifact))
            self.assertEqual("ready", artifact.lesson.audio_status)
            self.assertIn(lesson_id, PUBLISHED_LESSON_IDS)
            self.assertIsNotNone(source.get("audio_path"))
            self.assertEqual(staged["draft_id"], source["source_draft_id"])
            self.assertEqual(
                staged["sentences"],
                [
                    {"de": sentence["de"], "en": sentence["en"]}
                    for sentence in source["sentences"]
                ],
            )
            self.assertEqual("pass", review.overall_verdict)
            self.assertEqual(
                hashlib.sha256(source_path(lesson_id).read_bytes()).hexdigest(),
                review.source_sha256,
            )
            self.assertTrue(source_path(lesson_id).with_name("preview.md").is_file())

            for sentence in artifact.lesson.sentences:
                expected = [
                    token.casefold()
                    for token in token_pattern.findall(sentence.text)
                ]
                actual = [
                    form.casefold()
                    for group in sentence.breakdown_groups
                    for item in ordered_breakdown_items(group, sentence.text)
                    if item.kind == "word"
                    for form in item.source_forms
                ]
                self.assertEqual(Counter(expected), Counter(actual))

    def test_module_five_audit_regressions_stay_fixed(self) -> None:
        ticket = load_candidate_artifact("a1-course-025").lesson
        scheduled_train = next(
            item
            for group in ticket.sentences[2].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["fährt"]
        )
        self.assertEqual("fahren", scheduled_train.verb_help.infinitive)
        self.assertEqual("runs", scheduled_train.english)

        platform = load_candidate_artifact("a1-course-026").lesson
        departure = next(
            item
            for group in platform.sentences[1].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["fährt"]
        )
        self.assertEqual("abfahren", departure.verb_help.infinitive)
        self.assertEqual("depart", departure.english)
        formal_imperative = next(
            item
            for group in platform.sentences[3].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["halten"]
        )
        self.assertEqual("keep", formal_imperative.english)

        reception = load_candidate_artifact("a1-course-027").lesson
        reservation_have = next(
            item
            for group in reception.sentences[1].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["habe"]
        )
        self.assertEqual("haben", reservation_have.verb_help.infinitive)
        formal_possessive = next(
            item
            for group in reception.sentences[2].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["Ihr"]
        )
        self.assertNotIn(
            "personal pronoun", {tag.label for tag in formal_possessive.tags}
        )
        booked = next(
            item
            for group in reception.sentences[1].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["bestellt"]
        )
        self.assertEqual("booked", booked.english)

        message = load_candidate_artifact("a1-course-028").lesson
        request_words = {
            source: item
            for group in message.sentences[3].breakdown_groups
            for item in group.items
            if item.kind == "word"
            for source in item.source_forms
        }
        self.assertEqual("anrufen", request_words["ruf"].verb_help.infinitive)
        self.assertIn("imperative", {tag.label for tag in request_words["ruf"].tags})
        self.assertNotIn("present", {tag.label for tag in request_words["ruf"].tags})
        self.assertEqual("works", request_words["Geht"].english)
        longer = next(
            item
            for group in message.sentences[1].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["länger"]
        )
        self.assertIn("comparative", {tag.label for tag in longer.tags})
        reflexive_phrase = next(
            item
            for group in message.sentences[2].breakdown_groups
            for item in group.items
            if item.kind == "phrase" and item.german == "uns ... treffen"
        )
        reflexive_help = reflexive_phrase.inflection_help[0]
        self.assertEqual(
            ("wir", "uns", "personal-pronoun", "accusative", "first-plural"),
            (
                reflexive_help.base,
                reflexive_help.surface,
                reflexive_help.kind,
                reflexive_help.case,
                reflexive_help.pronoun_slot,
            ),
        )
        heard = next(
            item
            for group in message.sentences[4].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["hört"]
        )
        self.assertEqual("hören", heard.verb_help.infinitive)

        day_trip = load_candidate_artifact("a1-course-029").lesson
        drink = next(
            item
            for group in day_trip.sentences[2].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["trinken"]
        )
        self.assertIn("infinitive", {tag.label for tag in drink.tags})
        self.assertNotIn("present", {tag.label for tag in drink.tags})
        home = next(
            item
            for group in day_trip.sentences[3].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["Hause"]
        )
        self.assertEqual("home", home.english)

        checkpoint = load_candidate_artifact("a1-course-030").lesson
        checkpoint_departure = next(
            item
            for group in checkpoint.sentences[0].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["fährt"]
        )
        self.assertEqual("abfahren", checkpoint_departure.verb_help.infinitive)
        checkpoint_travel = next(
            item
            for group in checkpoint.sentences[4].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["fahren"]
        )
        self.assertEqual("fahren", checkpoint_travel.verb_help.infinitive)
        meeting_time = next(
            item
            for group in checkpoint.sentences[3].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["erst"]
        )
        self.assertEqual("not until / only", meeting_time.english)
        meeting = next(
            item
            for group in checkpoint.sentences[3].breakdown_groups
            for item in group.items
            if item.kind == "word" and item.source_forms == ["treffen"]
        )
        self.assertIn("reflexive", {tag.label for tag in meeting.tags})


if __name__ == "__main__":
    unittest.main()
