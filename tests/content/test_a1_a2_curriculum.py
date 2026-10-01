import json
import re
import unittest
from collections import Counter
from pathlib import Path

from curriculum.a1_a2.validate import validate
from nochmal.content import A1_A2_LESSONS, LESSONS
from nochmal.content.a1_a2_glossary import TARGET_GLOSSES
from nochmal.content.a1_a2_lessons import _present_forms


CURRICULUM_ROOT = Path(__file__).resolve().parents[2] / "curriculum" / "a1_a2"


class A1A2CurriculumTests(unittest.TestCase):
    def test_complete_curriculum_passes_the_offline_contract(self):
        self.assertEqual([], validate())

    def test_every_deliberate_target_has_one_controlled_english_gloss(self):
        lessons = []
        for path in sorted((CURRICULUM_ROOT / "lessons").glob("*.json")):
            lessons.extend(json.loads(path.read_text(encoding="utf-8")))
        targets = [target for lesson in lessons for target in lesson["new_targets"]]

        self.assertEqual(set(targets), set(TARGET_GLOSSES))
        self.assertTrue(all(TARGET_GLOSSES[target].strip() for target in targets))

    def test_all_eighty_legacy_lessons_remain_preserved_before_extension_lessons(self):
        self.assertEqual(80, len(A1_A2_LESSONS))
        self.assertEqual(list(range(1, 81)), [lesson.sequence for lesson in A1_A2_LESSONS])
        self.assertEqual(A1_A2_LESSONS, LESSONS[1:81])
        self.assertEqual(
            Counter({"A1.1": 20, "A1.2": 17, "A2.1": 23, "A2.2": 20}),
            Counter(lesson.level for lesson in A1_A2_LESSONS),
        )

    def test_audio_status_matches_authored_metadata(self):
        for lesson in A1_A2_LESSONS:
            with self.subTest(lesson=lesson.id):
                has_audio = bool(lesson.audio_path) and all(
                    sentence.audio_path for sentence in lesson.sentences
                )
                expected_status = "ready" if has_audio else "pending"
                self.assertEqual(expected_status, lesson.audio_status)
                if expected_status == "ready":
                    self.assertIsNotNone(lesson.audio_path)
                    self.assertTrue(all(sentence.audio_path for sentence in lesson.sentences))
                else:
                    self.assertIsNone(lesson.audio_path)
                    self.assertTrue(all(sentence.audio_path is None for sentence in lesson.sentences))
                self.assertNotIn("grammar_explanation", type(lesson).model_fields)
                self.assertNotIn("communicative_goal", type(lesson).model_fields)
                self.assertTrue(lesson.initial_answer)
                self.assertTrue(all(sentence.breakdown_groups for sentence in lesson.sentences))

    def test_every_source_token_has_one_ordered_word_definition(self):
        token_pattern = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)
        for lesson in A1_A2_LESSONS:
            for sentence in lesson.sentences:
                expected = [token.casefold() for token in token_pattern.findall(sentence.text)]
                actual = [
                    source_form.casefold()
                    for group in sentence.breakdown_groups
                    for item in group.items
                    if item.kind == "word"
                    for source_form in item.source_forms
                ]
                with self.subTest(lesson=lesson.id, sentence=sentence.text):
                    self.assertEqual(Counter(expected), Counter(actual))

    def test_generated_verb_cards_are_bilingual_and_contextual(self):
        particles = {"ab", "an", "auf", "aus", "ein", "mit", "statt", "teil", "um", "vor"}
        tense_names = set()
        for lesson in A1_A2_LESSONS:
            for sentence in lesson.sentences:
                for group in sentence.breakdown_groups:
                    for item in group.items:
                        if not item.verb_help:
                            continue
                        help_card = item.verb_help
                        tense_names.add(help_card.tense)
                        self.assertNotIn(item.german.casefold(), particles)
                        self.assertEqual(6, len(help_card.present_forms or []))
                        self.assertEqual(6, len(help_card.present_english_forms or []))
                        self.assertEqual(len(help_card.forms), len(help_card.current_english_forms or []))
        self.assertTrue(
            {
                "Präsens (present)",
                "Perfekt (conversational past)",
                "Präteritum (simple past)",
                "Imperativ (command/request)",
                "Konjunktiv II (polite/conditional)",
            }
            <= tense_names
        )

    def test_separability_is_lexical_not_guessed_from_initial_letters(self):
        self.assertEqual(
            (
                "antworte",
                "antwortest",
                "antwortet",
                "antworten",
                "antwortet",
                "antworten",
            ),
            _present_forms("antworten"),
        )
        self.assertEqual(
            ("rufe an", "rufst an", "ruft an", "rufen an", "ruft an", "rufen an"),
            _present_forms("anrufen"),
        )

    def test_reflexive_pronoun_precedes_a_separated_prefix(self):
        lesson = next(lesson for lesson in A1_A2_LESSONS if lesson.id == "a2-045")
        ausruhen = next(
            item
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if item.verb_help and item.verb_help.infinitive == "sich ausruhen"
        )
        self.assertEqual(
            [
                "ruhe mich aus",
                "ruhst dich aus",
                "ruht sich aus",
                "ruhen uns aus",
                "ruht euch aus",
                "ruhen sich aus",
            ],
            [form.verb for form in ausruhen.verb_help.present_forms or []],
        )

    def test_lesson_two_authors_natural_speaking_alternatives(self):
        lesson = next(lesson for lesson in A1_A2_LESSONS if lesson.id == "a1-002")

        self.assertEqual(
            {alternative.accepted_phrase for alternative in lesson.speech_alternatives},
            {"am Morgen", "morgens"},
        )

    def test_first_four_lessons_explain_every_introduced_case_pattern(self):
        first_four = A1_A2_LESSONS[:4]

        def item_for(lesson_id: str, german: str):
            lesson = next(lesson for lesson in first_four if lesson.id == lesson_id)
            return next(
                item
                for sentence in lesson.sentences
                for group in sentence.breakdown_groups
                for item in group.items
                if item.german == german
            )

        self.assertEqual(
            {"noun", "plural", "nominative", "subject"},
            {tag.label for tag in item_for("a1-003", "die Eltern").tags},
        )
        self.assertEqual(
            {"adverb", "frequency", "time"},
            {tag.label for tag in item_for("a1-004", "morgens").tags},
        )
        self.assertEqual(
            "there is / there are",
            item_for("a1-004", "gibt").english,
        )
        self.assertEqual(
            {"genitive"},
            {tag.label for tag in item_for("a1-004", "meiner Schwester").tags},
        )
        self.assertEqual(
            {"dative", "place"},
            {
                tag.label
                for tag in item_for("a1-004", "in einem kleinen Haus").tags
            },
        )
        city_phrase = item_for("a1-003", "in einer kleinen Stadt")
        self.assertEqual(
            {"indefinite-article", "adjective"},
            {help_card.kind for help_card in city_phrase.inflection_help},
        )
        self.assertTrue(
            all(help_card.case == "dative" for help_card in city_phrase.inflection_help)
        )

    def test_reviewed_lessons_use_sentence_owned_annotations(self):
        records = json.loads(
            (CURRICULUM_ROOT / "lessons" / "001_020.json").read_text(
                encoding="utf-8"
            )
        )
        reviewed = records[:4]
        self.assertTrue(
            all(
                "annotations" in sentence
                for lesson in reviewed
                for sentence in lesson["sentences"]
            )
        )
        compiler = (
            Path(__file__).resolve().parents[2]
            / "nochmal"
            / "content"
            / "a1_a2_lessons.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("EARLY_SENTENCE_WORD_TAGS", compiler)
        self.assertNotIn("EARLY_SENTENCE_PHRASE_TAGS", compiler)
        self.assertNotIn("EARLY_EXTRA_PHRASES", compiler)

    def test_inversion_annotations_cover_each_fronting_pattern(self):
        inversion_items = [
            (lesson, sentence, item)
            for lesson in A1_A2_LESSONS
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if any(tag.label == "inversion" for tag in item.tags)
        ]
        self.assertTrue(all(item.kind == "phrase" for _, _, item in inversion_items))
        self.assertFalse(
            any(
                item.kind == "word"
                and any(tag.label == "inversion" for tag in item.tags)
                for lesson in A1_A2_LESSONS
                for sentence in lesson.sentences
                for group in sentence.breakdown_groups
                for item in group.items
            )
        )
        expected = {
            # W-questions keep the question word first and put the finite verb
            # before the subject.
            (
                "a1-002",
                "Im Deutschkurs fragt Leo: „Wie heißt du und woher kommst du?“",
                "heisst",
            ),
            (
                "a1-002",
                "Im Deutschkurs fragt Leo: „Wie heißt du und woher kommst du?“",
                "kommst",
            ),
            # Fronted time and place fields.
            ("a1-006", "Am Morgen stehe ich um sieben Uhr auf.", "stehe"),
            ("a1-004", "In der Küche trinkt die Familie morgens Kaffee.", "trinkt"),
            (
                "a1-013",
                "Die Sonne scheint nicht, draußen fällt viel Regen, und der Wind ist stark.",
                "fällt",
            ),
            # A connector beginning a later main clause.
            (
                "a1-009",
                "Zu Hause hat sie kein Wasser mehr, deshalb nimmt sie zwei Flaschen.",
                "nimmt",
            ),
            # A fronted object.
            (
                "a2-057",
                "Die Bedeutung sucht sie im Wörterbuch, danach spricht sie das Wort mehrmals laut aus.",
                "sucht",
            ),
            (
                "a1-025",
                "Ein Geschenk musst du nicht kaufen. Liebe Grüße, Mina.",
                "musst",
            ),
            # A fronted role or situation expression.
            (
                "a2-059",
                "Sehr geehrte Damen und Herren, als Kundin möchte ich mich über den Service in Ihrem Hotel beschweren.",
                "möchte",
            ),
            (
                "a2-066",
                "Mina denkt, dass der neue Krimi zu lang ist, und Leo sagt: „Da hast du recht.“",
                "hast",
            ),
            (
                "a2-067",
                "Der Verkehr ist stark, und zurzeit gibt es vor ihrer Wohnung auch eine laute Baustelle.",
                "gibt",
            ),
            # The subject can also be delayed by another element.
            (
                "a2-055",
                "Um achtzehn Uhr findet dort eine Lesung mit einer bekannten Autorin statt.",
                "findet",
            ),
            # A complete subordinate clause in the first field.
            (
                "a2-061",
                "Als sie jung war, hat sie mit ihrer Familie in einem kleinen Dorf gelebt.",
                "hat",
            ),
        }

        for lesson_id, sentence_text, finite_verb in expected:
            with self.subTest(lesson=lesson_id, verb=finite_verb):
                self.assertTrue(
                    any(
                        lesson.id == lesson_id
                        and sentence.text == sentence_text
                        and finite_verb
                        in {
                            token.casefold()
                            for token in re.findall(
                                r"\w+(?:[-’']\w+)*", item.german, flags=re.UNICODE
                            )
                        }
                        for lesson, sentence, item in inversion_items
                    )
                )
        self.assertEqual(146, len(inversion_items))

        shopping = next(
            item
            for lesson, sentence, item in inversion_items
            if lesson.id == "a1-030"
            and sentence.text == "Gestern hat Mina nach der Arbeit eingekauft."
        )
        self.assertEqual("Gestern hat Mina … eingekauft", shopping.german)
        self.assertEqual(
            "Yesterday Mina went shopping after work", shopping.english
        )
        exact_chunks = {
            item.german: item.english
            for _, _, item in inversion_items
        }
        self.assertEqual(
            "Later she watched television for another hour",
            exact_chunks["Später hat sie … ferngesehen"],
        )
        self.assertEqual(
            "I would therefore like part of my money back",
            exact_chunks["Deshalb möchte ich einen Teil meines Geldes zurück"],
        )
        self.assertEqual(
            "At the end of this course Mina has achieved almost all her goals",
            exact_chunks["Am Ende dieses Kurses hat Mina … geschafft"],
        )

        directions = next(
            sentence
            for lesson in A1_A2_LESSONS
            for sentence in lesson.sentences
            if sentence.text == "Dann gehen Sie nach links und an der nächsten Haltestelle nach rechts."
        )
        gehen = next(
            item
            for group in directions.breakdown_groups
            for item in group.items
            if "gehen" in {form.casefold() for form in item.source_forms}
        )
        self.assertNotIn("inversion", {tag.label for tag in gehen.tags})
        self.assertFalse(
            any(
                item.kind == "phrase"
                and any(tag.label == "inversion" for tag in item.tags)
                for group in directions.breakdown_groups
                for item in group.items
            )
        )

    def test_every_sentence_has_level_appropriate_meaning_chunks(self):
        token_pattern = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)
        bare_articles = {
            "der", "die", "das", "den", "dem", "des", "ein", "eine",
            "einen", "einem", "einer", "eines",
        }
        for lesson in A1_A2_LESSONS:
            required_count = 2 if lesson.level.startswith("A2") else 1
            for sentence in lesson.sentences:
                phrases = [
                    item
                    for group in sentence.breakdown_groups
                    for item in group.items
                    if item.kind == "phrase"
                ]
                source_tokens = [
                    token.casefold() for token in token_pattern.findall(sentence.text)
                ]
                source = " ".join(source_tokens)
                with self.subTest(lesson=lesson.id, sentence=sentence.text):
                    self.assertGreaterEqual(len(phrases), required_count)
                    for phrase in phrases:
                        phrase_tokens = token_pattern.findall(phrase.german)
                        normalized_phrase = " ".join(
                            token.casefold() for token in phrase_tokens
                        )
                        if "…" in phrase.german or "..." in phrase.german:
                            cursor = 0
                            for token in (
                                token.casefold() for token in phrase_tokens
                            ):
                                cursor = source_tokens.index(token, cursor) + 1
                        else:
                            self.assertIn(normalized_phrase, source)
                        if source == normalized_phrase:
                            self.assertIn(
                                "inversion", {tag.label for tag in phrase.tags}
                            )
                        self.assertFalse(
                            len(phrase_tokens) == 2
                            and phrase_tokens[0].casefold() in bare_articles
                            and phrase_tokens[1][:1].isupper()
                        )

    def test_only_real_names_and_places_use_the_proper_noun_fallback(self):
        proper_nouns = {
            item.german
            for lesson in A1_A2_LESSONS
            for sentence in lesson.sentences
            for group in sentence.breakdown_groups
            for item in group.items
            if any(tag.label == "proper noun" for tag in item.tags)
        }
        self.assertEqual(
            {
                "Ana", "Bonn", "Deutschland", "Hamburg", "Köln", "Leo",
                "Luis", "Madrid", "Mina", "Minas", "Paul", "Sara", "Spanien",
            },
            proper_nouns,
        )


if __name__ == "__main__":
    unittest.main()
