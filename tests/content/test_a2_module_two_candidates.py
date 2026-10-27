import json
import unittest

from nochmal.content.course_library import compiled_published_lesson, published_records
from nochmal.content.ordering import ordered_breakdown_items
from nochmal.paths import PROJECT_ROOT


class A2ModuleTwoPublishedLessonTests(unittest.TestCase):
    @staticmethod
    def _items(number: int, sentence_index: int):
        lesson = compiled_published_lesson(f"a2-course-{number:03d}")
        assert lesson is not None
        sentence = lesson.sentences[sentence_index]
        return [item for group in sentence.breakdown_groups for item in group.items]

    @staticmethod
    def _without_release_audio(record: dict) -> dict:
        """Compare authored curriculum data without candidate-only audio paths."""

        copied = json.loads(json.dumps(record))
        copied["audio_path"] = None
        for sentence in copied["sentences"]:
            sentence["audio_path"] = None
        return copied

    def test_six_published_lessons_match_the_authored_module(self) -> None:
        module = json.loads(
            (PROJECT_ROOT / "curriculum/a2_course/lessons/module-02.json").read_text(
                encoding="utf-8"
            )
        )
        published = {record.id: record for record in published_records("a2")}
        for record in module:
            with self.subTest(lesson=record["id"]):
                lesson_id = record["id"]
                source = published[lesson_id]
                lesson = compiled_published_lesson(lesson_id)
                assert lesson is not None
                self.assertEqual(
                    self._without_release_audio(record),
                    self._without_release_audio(source.model_dump(mode="json")),
                )
                self.assertEqual("ready", lesson.audio_status)

    def test_compared_forms_and_superlatives_have_correct_cards(self) -> None:
        travel = next(
            item for item in self._items(7, 3)
            if item.kind == "word" and "fahre" in item.source_forms
        )
        self.assertEqual("fahren", travel.verb_help.infinitive)
        short_walk = next(
            item for item in self._items(7, 3)
            if item.kind == "phrase" and item.german == "der kurze Weg"
        )
        self.assertTrue(
            any(help_.surface == "kurze" and help_.paradigm == "weak-adjective"
                for help_ in short_walk.inflection_help)
        )
        lesson = compiled_published_lesson("a2-course-008")
        assert lesson is not None
        for sentence in lesson.sentences:
            phrases = [
                item.german for group in sentence.breakdown_groups
                for item in group.items if item.kind == "phrase"
            ]
            self.assertTrue(
                {"am günstigsten aber dort", "am kürzesten und die",
                 "am ruhigsten und dort"}.isdisjoint(phrases)
            )

    def test_adjective_and_location_forms_have_typed_help(self) -> None:
        infinitive = next(
            item for item in self._items(9, 1)
            if item.kind == "word" and item.german == "haben"
        )
        self.assertTrue(infinitive.verb_help.tense.startswith("Infinitiv"))
        expected = (
            (9, 1, "moderne", "nominative"),
            (10, 2, "dem", "dative"),
            (10, 3, "ins", "accusative"),
            (11, 4, "seinen", "accusative"),
            (12, 1, "Ihnen", "dative"),
            (12, 2, "Mir", "dative"),
        )
        for lesson, sentence, surface, case in expected:
            with self.subTest(lesson=lesson, sentence=sentence, surface=surface):
                self.assertTrue(
                    any(
                        help_.surface.casefold() == surface.casefold()
                        and help_.case == case
                        for item in self._items(lesson, sentence)
                        for help_ in item.inflection_help
                    )
                )

    def test_every_declined_attributive_adjective_has_its_own_help(self) -> None:
        for number in range(7, 13):
            lesson = compiled_published_lesson(f"a2-course-{number:03d}")
            assert lesson is not None
            for sentence_number, sentence in enumerate(lesson.sentences, start=1):
                items = [item for group in sentence.breakdown_groups for item in group.items]
                helped = {
                    help_.surface.casefold()
                    for item in items for help_ in item.inflection_help
                    if help_.kind == "adjective"
                }
                for item in items:
                    if item.kind != "word" or not any(
                        tag.label == "adjective" for tag in item.tags
                    ):
                        continue
                    for surface in item.source_forms:
                        if surface.casefold() != item.german.casefold():
                            with self.subTest(lesson=number, sentence=sentence_number,
                                              surface=surface):
                                self.assertIn(surface.casefold(), helped)

    def test_repeated_nouns_precede_phrases_that_use_them(self) -> None:
        for number, phrase in (
            (7, "größer als die Wohnung am Markt"),
            (12, "aber die Wohnung im Zentrum liegt näher an meiner Arbeit"),
        ):
            with self.subTest(lesson=number):
                lesson = compiled_published_lesson(f"a2-course-{number:03d}")
                assert lesson is not None
                sentence = lesson.sentences[0]
                ordered = [
                    item for group in sentence.breakdown_groups
                    for item in ordered_breakdown_items(group, sentence.text)
                ]
                noun_positions = [
                    index for index, item in enumerate(ordered)
                    if item.kind == "word" and item.german == "die Wohnung"
                ]
                phrase_position = next(
                    index for index, item in enumerate(ordered)
                    if item.kind == "phrase" and item.german == phrase
                )
                self.assertEqual(2, len(noun_positions))
                self.assertLess(noun_positions[1], phrase_position)

    def test_reviewed_case_forms_have_reference_cards(self) -> None:
        expected = (
            (7, 0, "in der Gartenstraße", "der", "dative"),
            (7, 2, "einen Balkon", "einen", "accusative"),
            (9, 0, "Guten Tag", "Guten", "accusative"),
            (9, 3, "mit einem kleinen Balkon", "kleinen", "dative"),
            (11, 3, "am Ende", "am", "dative"),
        )
        for lesson, sentence, phrase, surface, case in expected:
            with self.subTest(lesson=lesson, sentence=sentence, phrase=phrase):
                item = next(
                    item for item in self._items(lesson, sentence)
                    if item.kind == "phrase" and item.german == phrase
                )
                self.assertTrue(
                    any(help_.surface.casefold() == surface.casefold()
                        and help_.case == case for help_ in item.inflection_help)
                )


if __name__ == "__main__":
    unittest.main()
