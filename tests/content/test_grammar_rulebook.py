import unittest

from nochmal.paths import PROJECT_ROOT


class GrammarRulebookTests(unittest.TestCase):
    def test_rulebook_is_required_by_repository_instructions(self) -> None:
        agent_instructions = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/grammar-breakdown-rulebook.md", agent_instructions)
        self.assertIn("mandatory", agent_instructions.casefold())

    def test_rulebook_contains_the_publication_contract(self) -> None:
        rulebook = (
            PROJECT_ROOT / "docs" / "grammar-breakdown-rulebook.md"
        ).read_text(encoding="utf-8")
        required_sections = (
            "Typed content contract",
            "Required sentence audit",
            "Word-card contract",
            "Phrase-result contract",
            "Fixed hover layouts",
            "Case analysis",
            "Inflection rules",
            "Automation boundary",
            "Publication gate",
            "Required integration sequence",
        )
        for heading in required_sections:
            with self.subTest(heading=heading):
                self.assertIn(heading, rulebook)

        self.assertIn("complete paradigm table", rulebook)
        self.assertIn("Pydantic", rulebook)
        self.assertIn("Do not add a “Lesson goals”", rulebook)
        self.assertIn("Every declined attributive adjective", rulebook)


if __name__ == "__main__":
    unittest.main()
