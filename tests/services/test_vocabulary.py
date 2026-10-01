import unittest

from nochmal.content import LESSONS
from nochmal.services.vocabulary import (
    CATEGORY_ORDER,
    grouped_vocabulary,
    vocabulary_for_lesson,
)


class VocabularyTests(unittest.TestCase):
    def test_vocabulary_contains_only_unique_word_items(self) -> None:
        for lesson in LESSONS:
            with self.subTest(lesson=lesson.id):
                entries = vocabulary_for_lesson(lesson)
                normalized = [entry.german.casefold() for entry in entries]
                self.assertTrue(entries)
                self.assertEqual(len(normalized), len(set(normalized)))

    def test_categories_use_the_documented_order(self) -> None:
        category_positions = {
            category: index for index, category in enumerate(CATEGORY_ORDER)
        }
        for lesson in LESSONS:
            with self.subTest(lesson=lesson.id):
                groups = grouped_vocabulary(lesson)
                positions = [category_positions[category] for category in groups]
                self.assertEqual(positions, sorted(positions))

    def test_known_words_are_categorized(self) -> None:
        missed_train = next(lesson for lesson in LESSONS if lesson.id == "missed-train")
        entries = {
            entry.german: entry.category
            for entry in vocabulary_for_lesson(missed_train)
        }
        self.assertEqual(entries["die U-Bahn"], "Nouns")
        self.assertEqual(entries["wollte"], "Verbs")
        self.assertEqual(entries["pünktlich"], "Adjectives")
        self.assertEqual(entries["deshalb"], "Adverbs")


if __name__ == "__main__":
    unittest.main()
