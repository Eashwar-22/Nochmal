import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Content-authoring rules for these models live in docs/lesson-format.md.


class StrictModel(BaseModel):
    """Reject misspelled or obsolete authored fields instead of ignoring them."""

    model_config = ConfigDict(extra="forbid")


class ConjugationForm(StrictModel):
    pronoun: str
    verb: str


class VerbHelp(StrictModel):
    infinitive: str
    tense: str
    forms: list[ConjugationForm]
    usage: str
    english: str | None = None
    present_forms: list[ConjugationForm] | None = None
    present_english_forms: list[str] | None = None
    current_english_forms: list[str] | None = None

    @model_validator(mode="after")
    def require_complete_embedded_reference(self) -> "VerbHelp":
        """Keep generated verb cards self-contained when a shared entry is absent."""
        embedded = (
            self.english,
            self.present_forms,
            self.present_english_forms,
            self.current_english_forms,
        )
        if any(value is not None for value in embedded):
            if (
                not self.english
                or self.present_forms is None
                or self.present_english_forms is None
                or self.current_english_forms is None
                or len(self.present_forms) != 6
                or len(self.present_english_forms) != 6
                or not self.forms
                or len(self.current_english_forms) != len(self.forms)
            ):
                raise ValueError(
                    "Embedded verb references require an English meaning and "
                    "six present-tense forms and matching German/English forms "
                    "for the sentence tense"
                )
        return self


GrammarCase = Literal["nominative", "accusative", "dative", "genitive"]
GrammarGender = Literal["masculine", "feminine", "neuter", "plural"]
InflectionKind = Literal[
    "definite-article",
    "indefinite-article",
    "possessive-determiner",
    "adjective",
    "personal-pronoun",
]
InflectionParadigm = Literal[
    "definite",
    "indefinite",
    "possessive",
    "weak-adjective",
    "mixed-adjective",
    "strong-adjective",
    "personal-pronoun",
]
PronounSlot = Literal[
    "first-singular",
    "second-singular",
    "third-masculine",
    "third-feminine",
    "third-neuter",
    "first-plural",
    "second-plural",
    "third-plural-formal",
]


class InflectionHelp(StrictModel):
    """Typed input for one fixed-layout case or adjective reference card.

    The UI derives its labels and complete reference table from these fields.
    Lesson data cannot inject free-form tooltip prose.
    """

    surface: str
    base: str
    kind: InflectionKind
    paradigm: InflectionParadigm
    case: GrammarCase
    gender: GrammarGender | None = None
    number: Literal["singular", "plural"] = "singular"
    pronoun_slot: PronounSlot | None = None
    resolved_form: str | None = None
    contraction: str | None = None

    @model_validator(mode="after")
    def require_coherent_reference(self) -> "InflectionHelp":
        if not self.surface.strip() or not self.base.strip():
            raise ValueError("Inflection help requires a surface and base form")

        expected_paradigms = {
            "definite-article": {"definite"},
            "indefinite-article": {"indefinite"},
            "possessive-determiner": {"possessive"},
            "adjective": {
                "weak-adjective",
                "mixed-adjective",
                "strong-adjective",
            },
            "personal-pronoun": {"personal-pronoun"},
        }
        if self.paradigm not in expected_paradigms[self.kind]:
            raise ValueError(
                f"{self.kind} cannot use the {self.paradigm} paradigm"
            )
        if self.kind == "personal-pronoun":
            if self.pronoun_slot is None:
                raise ValueError("Personal-pronoun help requires a pronoun slot")
        elif self.gender is None:
            raise ValueError(f"{self.kind} help requires grammatical gender")
        if self.kind != "personal-pronoun":
            if self.gender == "plural" and self.number != "plural":
                raise ValueError("Plural inflection help must use number='plural'")
            if self.gender != "plural" and self.number != "singular":
                raise ValueError("Singular genders must use number='singular'")
        elif self.pronoun_slot:
            plural_slot = self.pronoun_slot in {
                "first-plural",
                "second-plural",
                "third-plural-formal",
            }
            if plural_slot != (self.number == "plural"):
                raise ValueError("Pronoun slot and grammatical number disagree")
        if self.contraction and (
            self.kind != "definite-article" or not self.resolved_form
        ):
            raise ValueError(
                "A contraction requires a resolved definite-article form"
            )
        return self


TagCategory = Literal[
    "case",
    "connector",
    "form",
    "noun",
    "role",
    "structure",
    "tense",
    "time",
    "verb",
    "word-class",
]


TAG_KEYWORDS: dict[str, TagCategory] = {
    "noun": "word-class",
    "compound noun": "noun",
    "proper noun": "noun",
    "masc.": "noun",
    "fem.": "noun",
    "neuter": "noun",
    "singular": "form",
    "plural": "form",
    "verb": "verb",
    "modal verb": "verb",
    "auxiliary": "verb",
    "reflexive": "verb",
    "separable": "verb",
    "inseparable": "verb",
    "regular": "verb",
    "irregular": "verb",
    "infinitive": "verb",
    "past participle": "verb",
    "imperative": "verb",
    "present": "tense",
    "simple past": "tense",
    "perfect": "tense",
    "pluperfect": "tense",
    "future": "tense",
    "adjective": "word-class",
    "adverb": "word-class",
    "interjection": "word-class",
    "article": "word-class",
    "determiner": "word-class",
    "personal pronoun": "word-class",
    "reflexive pronoun": "word-class",
    "relative pronoun": "word-class",
    "possessive": "word-class",
    "preposition": "word-class",
    "conjunction": "word-class",
    "particle": "word-class",
    "numeral": "word-class",
    "nominative": "case",
    "accusative": "case",
    "dative": "case",
    "genitive": "case",
    "subject": "role",
    "direct object": "role",
    "indirect object": "role",
    "predicate": "role",
    "main clause": "structure",
    "subordinate clause": "structure",
    "verb-second": "structure",
    "verb-final": "structure",
    "inversion": "structure",
    "negation": "structure",
    "fixed phrase": "structure",
    "idiom": "structure",
    "ellipsis": "structure",
    "contraction": "form",
    "comparative": "form",
    "superlative": "form",
    "time": "time",
    "place": "time",
    "direction": "time",
    "frequency": "time",
    "manner": "time",
    "reason": "time",
    "connector": "connector",
    "coordinating": "connector",
    "subordinating": "connector",
    "formal": "form",
    "informal": "form",
    "colloquial": "form",
    "subjunctive": "form",
}


TAG_DESCRIPTIONS: dict[str, str] = {
    "noun": "A word for a person, place, thing, or idea.",
    "compound noun": "A noun formed by joining two or more words.",
    "proper noun": "The specific name of a person, place, or organization.",
    "masc.": "A noun with masculine grammatical gender.",
    "fem.": "A noun with feminine grammatical gender.",
    "neuter": "A noun with neuter grammatical gender.",
    "singular": "A form referring to one person or thing.",
    "plural": "A form referring to more than one person or thing.",
    "verb": "A word expressing an action, process, or state.",
    "modal verb": "A verb expressing ability, permission, need, or intention.",
    "auxiliary": "A helping verb used to build a tense or voice.",
    "reflexive": "A verb used with a pronoun that refers back to the subject.",
    "separable": "A verb whose prefix separates in some sentence patterns.",
    "inseparable": "A prefixed verb whose prefix stays attached.",
    "regular": "A verb that follows the standard conjugation pattern.",
    "irregular": "A verb with a stem or form that changes irregularly.",
    "infinitive": "The unconjugated dictionary form of a verb.",
    "past participle": "A verb form used in perfect tenses and the passive.",
    "imperative": "A verb form used for commands or requests.",
    "present": "A tense for current actions, habits, or general facts.",
    "simple past": "A tense for completed past events, especially in writing.",
    "perfect": "A past tense formed with haben or sein and a past participle.",
    "pluperfect": "A tense for an event completed before another past event.",
    "future": "A tense commonly formed with werden and an infinitive.",
    "adjective": "A word describing a noun or a state.",
    "adverb": "A word modifying a verb, adjective, or whole sentence.",
    "interjection": "A standalone word used for a greeting, reaction, or brief response.",
    "article": "A noun companion that can show gender, number, and case.",
    "determiner": "A word that specifies quantity or reference before a noun.",
    "personal pronoun": "A word such as ich or mir that refers to a participant.",
    "reflexive pronoun": "A pronoun that refers back to the subject of its clause.",
    "relative pronoun": "A pronoun that introduces a relative clause and refers back to a noun.",
    "possessive": "A form expressing ownership or another close relationship.",
    "preposition": "A word showing a relationship and governing a case.",
    "conjunction": "A word joining words, phrases, or clauses.",
    "particle": "A small word that changes meaning, emphasis, or tone.",
    "numeral": "A word expressing number, quantity, or order.",
    "nominative": "The case normally used for the subject.",
    "accusative": "The case often used for a direct object.",
    "dative": "The case often used for a recipient or indirect object.",
    "genitive": "The case commonly expressing possession or belonging.",
    "subject": "The person or thing performing an action or being described.",
    "direct object": "The person or thing directly affected by the action.",
    "indirect object": "The recipient or beneficiary of the action.",
    "predicate": "A word or phrase describing what the subject is or does.",
    "main clause": "A complete clause that can stand on its own.",
    "subordinate clause": "A dependent clause that supports a main clause.",
    "verb-second": "The finite verb occupies the second sentence position.",
    "verb-final": "The finite verb appears at the end of the clause.",
    "inversion": "The verb comes before the subject after another first element.",
    "negation": "A form that makes a word, phrase, or sentence negative.",
    "fixed phrase": "A common expression usually learned as one stable unit.",
    "idiom": "A phrase whose meaning is not fully predictable from its words.",
    "ellipsis": "An understood word or phrase is omitted because the meaning is clear in context.",
    "contraction": "A shortened form made by combining two words.",
    "comparative": "An adjective or adverb form used to compare two things.",
    "superlative": "A form expressing the highest degree of a quality.",
    "time": "Shows when something happens.",
    "place": "Shows where something happens.",
    "direction": "Shows movement toward or away from a place.",
    "frequency": "Shows how often something happens.",
    "manner": "Shows how an action happens.",
    "reason": "Shows why something happens.",
    "connector": "Links one idea or sentence to another.",
    "coordinating": "Joins elements that have equal grammatical status.",
    "subordinating": "Introduces a clause that depends on another clause.",
    "formal": "Used mainly in polite, official, or professional contexts.",
    "informal": "Used mainly in relaxed or familiar contexts.",
    "colloquial": "Typical of everyday spoken language.",
    "subjunctive": "A verb form used for hypothetical, reported, or politely distanced statements.",
}


if TAG_KEYWORDS.keys() != TAG_DESCRIPTIONS.keys():
    missing = TAG_KEYWORDS.keys() - TAG_DESCRIPTIONS.keys()
    extra = TAG_DESCRIPTIONS.keys() - TAG_KEYWORDS.keys()
    raise RuntimeError(
        "Grammar keyword descriptions are out of sync. "
        f"Missing: {sorted(missing)}; extra: {sorted(extra)}"
    )


class GrammarTag(StrictModel):
    label: str
    category: TagCategory

    @model_validator(mode="after")
    def require_controlled_keyword(self) -> "GrammarTag":
        expected_category = TAG_KEYWORDS.get(self.label)
        if expected_category is None:
            raise ValueError(f"Unknown grammar keyword: {self.label}")
        if self.category != expected_category:
            raise ValueError(
                f"Keyword {self.label!r} must use category "
                f"{expected_category!r}, not {self.category!r}"
            )
        return self


class BreakdownItem(StrictModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    german: str
    english: str
    literal_meaning: str | None = None
    tags: list[GrammarTag] = Field(default_factory=list)
    kind: Literal["word", "phrase"] = "word"
    verb_help: VerbHelp | None = None
    inflection_help: list[InflectionHelp] = Field(default_factory=list)
    source_forms: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_dictionary_article_for_nouns(self) -> "BreakdownItem":
        if (
            self.kind == "word"
            and any(
                tag.label in {"noun", "compound noun", "masc.", "fem.", "neuter"}
                for tag in self.tags
            )
            and not re.match(r"^(der|die|das)\s", self.german, flags=re.IGNORECASE)
        ):
            raise ValueError(
                "Noun breakdowns must start with their dictionary article "
                f"(der/die/das): {self.german}"
            )
        return self

    @model_validator(mode="after")
    def reject_redundant_tags(self) -> "BreakdownItem":
        labels = {tag.label for tag in self.tags}
        redundant_pairs = [
            {"accusative", "direct object"},
            {"dative", "indirect object"},
        ]
        for pair in redundant_pairs:
            if pair <= labels:
                raise ValueError(
                    "Use the case tag without the redundant object-role tag: "
                    f"{', '.join(sorted(pair))}"
                )
        return self

    @model_validator(mode="after")
    def validate_inflection_help(self) -> "BreakdownItem":
        if self.inflection_help and self.kind != "phrase":
            raise ValueError("Inflection help belongs on a phrase result")
        labels = {tag.label for tag in self.tags}
        for help_card in self.inflection_help:
            if not re.search(
                rf"(?<!\w){re.escape(help_card.surface)}(?!\w)",
                self.german,
                flags=re.IGNORECASE,
            ):
                raise ValueError(
                    f"Inflection surface {help_card.surface!r} is absent from "
                    f"phrase {self.german!r}"
                )
            if help_card.case not in labels:
                raise ValueError(
                    f"Inflection case {help_card.case!r} must also be a phrase tag"
                )
        return self


class BreakdownGroup(StrictModel):
    items: list[BreakdownItem]


class AuthoredPhrase(StrictModel):
    german: str
    english: str | None = None
    literal_meaning: str | None = None
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_controlled_tags(self) -> "AuthoredPhrase":
        unknown = set(self.tags) - TAG_KEYWORDS.keys()
        if unknown:
            raise ValueError(f"Unknown authored phrase tags: {sorted(unknown)}")
        return self


class SentenceAnnotations(StrictModel):
    """Structured, sentence-owned inputs consumed by the generic compiler."""

    word_tags: dict[str, list[str]] = Field(default_factory=dict)
    base_forms: dict[str, str] = Field(default_factory=dict)
    word_meanings: dict[str, str] = Field(default_factory=dict)
    excluded_phrases: list[str] = Field(default_factory=list)
    excluded_phrase_tags: dict[str, list[str]] = Field(default_factory=dict)
    phrases: list[AuthoredPhrase] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_controlled_word_tags(self) -> "SentenceAnnotations":
        unknown = {
            label
            for labels in self.word_tags.values()
            for label in labels
            if label not in TAG_KEYWORDS
        }
        if unknown:
            raise ValueError(f"Unknown authored word tags: {sorted(unknown)}")
        unknown_excluded = {
            label
            for labels in self.excluded_phrase_tags.values()
            for label in labels
            if label not in TAG_KEYWORDS
        }
        if unknown_excluded:
            raise ValueError(
                f"Unknown excluded phrase tags: {sorted(unknown_excluded)}"
            )
        return self


class Sentence(StrictModel):
    text: str
    natural_meaning: str
    breakdown_groups: list[BreakdownGroup]
    audio_path: str | None

    @model_validator(mode="after")
    def require_a_gloss_for_every_word(self) -> "Sentence":
        """Keep every source form represented by a vocabulary breakdown."""
        word_pattern = r"\w+(?:[-’']\w+)*"
        source_words = {
            word.casefold()
            for word in re.findall(word_pattern, self.text, flags=re.UNICODE)
        }
        vocabulary_items = [
            item
            for group in self.breakdown_groups
            for item in group.items
            if item.kind == "word"
        ]
        glossed_words = {
            word.casefold()
            for item in vocabulary_items
            for word in (
                re.findall(word_pattern, item.german, flags=re.UNICODE)
                + item.source_forms
            )
        }
        missing = sorted(source_words - glossed_words)
        if missing:
            raise ValueError(
                "Every sentence word needs its own breakdown; missing: "
                f"{', '.join(missing)}"
            )

        return self


class SpeechAlternative(StrictModel):
    """A meaning-preserving phrase accepted by a speaking-practice lesson."""

    lesson_phrase: str
    accepted_phrase: str
    explanation: str


class Lesson(StrictModel):
    id: str
    title: str
    english_title: str
    level: Literal["A1.1", "A1.2", "A1", "A2.1", "A2.2", "A2", "A2-B1", "B1", "B1-B2", "B2"]
    sentences: list[Sentence]
    audio_path: str | None
    initial_question: str
    initial_answer: str | None = None
    audio_status: Literal["ready", "pending"] = "ready"
    sequence: int | None = None
    lesson_format: Literal[
        "narrative",
        "description",
        "dialogue",
        "message",
        "announcement",
        "instructions",
    ] | None = None
    topic: str | None = None
    new_targets: list[str] = Field(default_factory=list)
    recycled_targets: list[str] = Field(default_factory=list)
    speech_alternatives: list[SpeechAlternative] = Field(default_factory=list)
