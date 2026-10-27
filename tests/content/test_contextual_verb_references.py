import unittest

from nochmal.content.lesson_compiler import _english_rows, _present_forms, _sentence_groups
from nochmal.content.models import SentenceAnnotations


class ContextualVerbReferenceTests(unittest.TestCase):
    @staticmethod
    def _word(text, surface, annotations):
        groups = _sentence_groups(text, "", [], annotations)
        return next(
            item for group in groups for item in group.items
            if item.kind == "word" and surface in item.source_forms
        )

    def test_all_polite_moegen_forms_keep_the_dictionary_present(self):
        present = ["mag", "magst", "mag", "mögen", "mögt", "mögen"]
        subjunctive = ["möchte", "möchtest", "möchte", "möchten", "möchtet", "möchten"]
        subjects = ["Ich", "Du", "Er", "Wir", "Ihr", "Sie"]
        for subject, surface in zip(subjects, subjunctive, strict=True):
            with self.subTest(subject=subject, surface=surface):
                item = self._word(
                    f"{subject} {surface} gehen.", surface,
                    SentenceAnnotations(base_forms={surface: "mögen"}),
                )
                help_ = item.verb_help
                self.assertEqual("mögen", help_.infinitive)
                self.assertEqual("to like", help_.english)
                self.assertEqual(present, [row.verb for row in help_.present_forms])
                self.assertEqual(subjunctive, [row.verb for row in help_.forms])
                self.assertEqual("he/she/it likes", help_.present_english_forms[2])
                self.assertEqual("he/she/it would like", help_.current_english_forms[2])
                self.assertEqual("would like", item.english)
                self.assertIn("subjunctive", [tag.label for tag in item.tags])
                self.assertNotIn("present", [tag.label for tag in item.tags])

    def test_contextual_perfect_senses_preserve_dictionary_references(self):
        cases = [
            ("Ich habe nachgeholt.", "nachgeholt", "nachholen", "to celebrate belatedly", "celebrated belatedly"),
            ("Ich habe gearbeitet.", "gearbeitet", "arbeiten", "to work late", "worked late"),
        ]
        subjects = ["I", "you", "he/she/it", "we", "you", "they/you"]
        for text, surface, infinitive, meaning, participle in cases:
            with self.subTest(surface=surface):
                baseline = self._word(
                    text, surface, SentenceAnnotations(base_forms={surface: infinitive})
                )
                contextual = self._word(
                    text, surface,
                    SentenceAnnotations(
                        base_forms={surface: infinitive},
                        verb_meanings={surface: meaning},
                    ),
                )
                original = baseline.verb_help.model_dump()
                changed = contextual.verb_help.model_dump()
                original.pop("current_english_forms")
                changed.pop("current_english_forms")
                self.assertEqual(original, changed)
                self.assertEqual(
                    [
                        f"{subject} {'has' if index == 2 else 'have'} {participle}"
                        for index, subject in enumerate(subjects)
                    ],
                    contextual.verb_help.current_english_forms,
                )

    def test_koennt_is_present_not_conditional(self):
        item = self._word(
            "Ihr könnt helfen.", "könnt",
            SentenceAnnotations(base_forms={"könnt": "können"}),
        )
        self.assertEqual("Präsens (present)", item.verb_help.tense)
        self.assertIn("present", [tag.label for tag in item.tags])
        self.assertNotIn("subjunctive", [tag.label for tag in item.tags])

    def test_separable_verb_references_show_split_present_forms(self):
        for infinitive, surface, prefix in (
            ("aufbauen", "baut", "auf"),
            ("weitergeben", "gibt", "weiter"),
        ):
            with self.subTest(infinitive=infinitive):
                item = self._word(
                    f"Er {surface} es {prefix}.", surface,
                    SentenceAnnotations(
                        base_forms={surface: infinitive},
                        verb_components={surface: [prefix]},
                    ),
                )
                self.assertEqual(infinitive, item.verb_help.infinitive)
                self.assertTrue(all(
                    row.verb.endswith(f" {prefix}")
                    for row in item.verb_help.present_forms
                ))

    def test_formal_geben_command_has_actual_imperative_forms(self):
        item = self._word(
            "Geben Sie ihr das Paket.", "Geben",
            SentenceAnnotations(base_forms={"Geben": "geben"}),
        )
        self.assertEqual("Imperativ (command/request)", item.verb_help.tense)
        self.assertEqual(
            ["gib", "gebt", "geben Sie"],
            [row.verb for row in item.verb_help.forms],
        )

    def test_unterschrieben_is_a_perfect_participle(self):
        item = self._word(
            "Ich habe unterschrieben.", "unterschrieben",
            SentenceAnnotations(base_forms={"unterschrieben": "unterschreiben"}),
        )
        self.assertEqual("Perfekt (conversational past)", item.verb_help.tense)

    def test_module_four_strong_and_separable_present_forms(self):
        self.assertEqual("bewirbst", _present_forms("bewerben")[1])
        self.assertEqual("bewirbt", _present_forms("bewerben")[2])
        self.assertEqual("berätst", _present_forms("beraten")[1])
        self.assertEqual("berät", _present_forms("beraten")[2])
        self.assertEqual("lerne kennen", _present_forms("kennenlernen")[0])
        self.assertEqual("übernimmst", _present_forms("übernehmen")[1])
        self.assertEqual("übernimmt", _present_forms("übernehmen")[2])

    def test_reflexive_english_rows_agree_with_subject(self):
        self.assertEqual(
            ["I introduce myself", "you introduce yourself", "he/she/it introduces himself/herself/itself"],
            _english_rows("to introduce oneself", "present")[:3],
        )
        self.assertEqual("I have introduced myself", _english_rows("to introduce oneself", "perfect")[0])


if __name__ == "__main__":
    unittest.main()
