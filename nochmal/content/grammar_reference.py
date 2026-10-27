"""Reusable German inflection paradigms and typed phrase annotations.

This module is the single source of truth for case-reference tables.  Lesson
content supplies context through controlled tags; the renderer never receives
lesson-authored tooltip prose.
"""

from __future__ import annotations

import re

from .models import BreakdownGroup, BreakdownItem, GrammarCase, InflectionHelp


CASES: tuple[GrammarCase, ...] = (
    "nominative",
    "accusative",
    "dative",
    "genitive",
)
GENDERS = ("masculine", "feminine", "neuter", "plural")
PRONOUN_COLUMNS = (
    "ich",
    "du",
    "er",
    "sie",
    "es",
    "wir",
    "ihr",
    "sie / Sie",
)
PRONOUN_SLOTS = (
    "first-singular",
    "second-singular",
    "third-masculine",
    "third-feminine",
    "third-neuter",
    "first-plural",
    "second-plural",
    "third-plural-formal",
)

DEFINITE_ARTICLES = {
    "nominative": ("der", "die", "das", "die"),
    "accusative": ("den", "die", "das", "die"),
    "dative": ("dem", "der", "dem", "den"),
    "genitive": ("des", "der", "des", "der"),
}
INDEFINITE_ARTICLES = {
    "nominative": ("ein", "eine", "ein", "—"),
    "accusative": ("einen", "eine", "ein", "—"),
    "dative": ("einem", "einer", "einem", "—"),
    "genitive": ("eines", "einer", "eines", "—"),
}
NEGATIVE_DETERMINERS = {
    "nominative": ("kein", "keine", "kein", "keine"),
    "accusative": ("keinen", "keine", "kein", "keine"),
    "dative": ("keinem", "keiner", "keinem", "keinen"),
    "genitive": ("keines", "keiner", "keines", "keiner"),
}
POSSESSIVE_ENDINGS = {
    "nominative": ("", "e", "", "e"),
    "accusative": ("en", "e", "", "e"),
    "dative": ("em", "er", "em", "en"),
    "genitive": ("es", "er", "es", "er"),
}
DER_WORD_ENDINGS = {
    "nominative": ("er", "e", "es", "e"),
    "accusative": ("en", "e", "es", "e"),
    "dative": ("em", "er", "em", "en"),
    "genitive": ("es", "er", "es", "er"),
}
DER_WORD_BASES = {
    "dieser": "dies",
    "jeder": "jed",
    "welcher": "welch",
}
ADJECTIVE_ENDINGS = {
    "weak-adjective": {
        "nominative": ("-e", "-e", "-e", "-en"),
        "accusative": ("-en", "-e", "-e", "-en"),
        "dative": ("-en", "-en", "-en", "-en"),
        "genitive": ("-en", "-en", "-en", "-en"),
    },
    "mixed-adjective": {
        "nominative": ("-er", "-e", "-es", "-en"),
        "accusative": ("-en", "-e", "-es", "-en"),
        "dative": ("-en", "-en", "-en", "-en"),
        "genitive": ("-en", "-en", "-en", "-en"),
    },
    "strong-adjective": {
        "nominative": ("-er", "-e", "-es", "-e"),
        "accusative": ("-en", "-e", "-es", "-e"),
        "dative": ("-em", "-er", "-em", "-en"),
        "genitive": ("-en", "-er", "-en", "-er"),
    },
}
PERSONAL_PRONOUNS = {
    "nominative": ("ich", "du", "er", "sie", "es", "wir", "ihr", "sie / Sie"),
    "accusative": ("mich", "dich", "ihn", "sie", "es", "uns", "euch", "sie / Sie"),
    "dative": ("mir", "dir", "ihm", "ihr", "ihm", "uns", "euch", "ihnen / Ihnen"),
    "genitive": ("meiner", "deiner", "seiner", "ihrer", "seiner", "unser", "euer", "ihrer / Ihrer"),
}

CONTRACTIONS = {
    "am": ("an + dem", "dem"),
    "ans": ("an + das", "das"),
    "aufs": ("auf + das", "das"),
    "beim": ("bei + dem", "dem"),
    "durchs": ("durch + das", "das"),
    "fürs": ("für + das", "das"),
    "im": ("in + dem", "dem"),
    "ins": ("in + das", "das"),
    "ums": ("um + das", "das"),
    "vom": ("von + dem", "dem"),
    "zum": ("zu + dem", "dem"),
    "zur": ("zu + der", "der"),
}
POSSESSIVE_STEMS = ("unser", "euer", "mein", "dein", "sein", "ihr")
TOKEN_RE = re.compile(r"\w+(?:[-’']\w+)*", flags=re.UNICODE)


def table_for_help(help_card: InflectionHelp) -> dict[str, tuple[str, ...]]:
    """Return the complete immutable-layout table selected by typed metadata."""
    if help_card.paradigm == "definite":
        return DEFINITE_ARTICLES
    if help_card.paradigm == "indefinite":
        return INDEFINITE_ARTICLES
    if help_card.paradigm == "negative":
        return NEGATIVE_DETERMINERS
    if help_card.paradigm == "possessive":
        stem = help_card.base.rstrip("-")
        return {
            case: tuple(
                "—" if ending == "—" else f"{stem}{ending}"
                for ending in endings
            )
            for case, endings in POSSESSIVE_ENDINGS.items()
        }
    if help_card.paradigm == "der-word":
        stem = DER_WORD_BASES[help_card.base.casefold()]
        return {
            case: tuple(f"{stem}{ending}" for ending in endings)
            for case, endings in DER_WORD_ENDINGS.items()
        }
    if help_card.paradigm == "personal-pronoun":
        return PERSONAL_PRONOUNS
    return ADJECTIVE_ENDINGS[help_card.paradigm]


def columns_for_help(help_card: InflectionHelp) -> tuple[str, ...]:
    return PRONOUN_COLUMNS if help_card.kind == "personal-pronoun" else GENDERS


def selected_column_for_help(help_card: InflectionHelp) -> int:
    if help_card.kind == "personal-pronoun":
        if help_card.pronoun_slot is None:
            raise ValueError("Personal-pronoun help is missing its slot")
        return PRONOUN_SLOTS.index(help_card.pronoun_slot)
    if help_card.gender is None:
        raise ValueError("Inflection help is missing grammatical gender")
    return GENDERS.index(help_card.gender)


def _noun_gender(item: BreakdownItem, article: str) -> str:
    labels = {tag.label for tag in item.tags}
    if "plural" in labels:
        return "plural"
    if "masc." in labels:
        return "masculine"
    if "fem." in labels:
        return "feminine"
    if "neuter" in labels:
        return "neuter"
    return {"der": "masculine", "das": "neuter"}.get(article, "feminine")


def _table_cases(
    table: dict[str, tuple[str, ...]], gender: str, surface: str
) -> set[str]:
    column = GENDERS.index(gender)
    return {
        case
        for case, row in table.items()
        if row[column].casefold() == surface.casefold()
    }


def _possessive_stem(surface: str) -> str | None:
    key = surface.casefold()
    for stem in POSSESSIVE_STEMS:
        normalized_stem = "eur" if stem == "euer" and key.startswith("eur") else stem
        if not key.startswith(normalized_stem):
            continue
        if any(
            key == f"{normalized_stem}{ending}"
            for endings in POSSESSIVE_ENDINGS.values()
            for ending in endings
            if ending != "—"
        ):
            return stem
    return None


def _der_word_base(surface: str) -> str | None:
    key = surface.casefold()
    for base, stem in DER_WORD_BASES.items():
        if any(
            key == f"{stem}{ending}"
            for endings in DER_WORD_ENDINGS.values()
            for ending in endings
        ):
            return base
    return None


def _determiner_help(
    surface: str,
    *,
    dictionary_article: str,
    case: GrammarCase,
    gender: str,
    possessive_base: str | None = None,
) -> InflectionHelp | None:
    key = surface.casefold()
    number = "plural" if gender == "plural" else "singular"
    if key in CONTRACTIONS:
        contraction, resolved = CONTRACTIONS[key]
        if case not in _table_cases(DEFINITE_ARTICLES, gender, resolved):
            return None
        return InflectionHelp(
            surface=surface,
            base=dictionary_article,
            kind="definite-article",
            paradigm="definite",
            case=case,
            gender=gender,
            number=number,
            resolved_form=resolved,
            contraction=contraction,
        )
    if case in _table_cases(DEFINITE_ARTICLES, gender, key):
        return InflectionHelp(
            surface=surface,
            base=dictionary_article,
            kind="definite-article",
            paradigm="definite",
            case=case,
            gender=gender,
            number=number,
        )
    if case in _table_cases(INDEFINITE_ARTICLES, gender, key):
        return InflectionHelp(
            surface=surface,
            base="ein",
            kind="indefinite-article",
            paradigm="indefinite",
            case=case,
            gender=gender,
            number=number,
        )
    if case in _table_cases(NEGATIVE_DETERMINERS, gender, key):
        return InflectionHelp(
            surface=surface,
            base="kein",
            kind="negative-determiner",
            paradigm="negative",
            case=case,
            gender=gender,
            number=number,
        )
    stem = _possessive_stem(key)
    if stem:
        base = possessive_base or stem
        help_card = InflectionHelp(
            surface=surface,
            base=base,
            kind="possessive-determiner",
            paradigm="possessive",
            case=case,
            gender=gender,
            number=number,
        )
        if table_for_help(help_card)[case][GENDERS.index(gender)].casefold() == key:
            return help_card
    der_word_base = _der_word_base(key)
    if der_word_base:
        help_card = InflectionHelp(
            surface=surface,
            base=der_word_base,
            kind="der-word-determiner",
            paradigm="der-word",
            case=case,
            gender=gender,
            number=number,
        )
        if table_for_help(help_card)[case][GENDERS.index(gender)].casefold() == key:
            return help_card
    return None


def _pronoun_help(
    surface: str,
    case: GrammarCase,
    *,
    nominative_base: str | None = None,
    formal: bool = False,
    singular: bool = False,
) -> InflectionHelp | None:
    key = surface.casefold()
    candidates = []
    for column, form in enumerate(PERSONAL_PRONOUNS[case]):
        variants = {part.strip().casefold() for part in form.split("/")}
        if key in variants:
            candidates.append(column)
    if formal:
        candidates = [column for column in candidates if column == 7]
    elif singular:
        candidates = [column for column in candidates if column < 5]
    if len(candidates) > 1 and nominative_base:
        base_key = nominative_base.casefold()
        candidates = [
            column
            for column in candidates
            if base_key
            in {
                part.strip().casefold()
                for part in PERSONAL_PRONOUNS["nominative"][column].split("/")
            }
        ]
    if len(candidates) != 1:
        return None
    column = candidates[0]
    slot = PRONOUN_SLOTS[column]
    base = (
        "Sie"
        if formal and column == 7
        else PERSONAL_PRONOUNS["nominative"][column].split("/")[0].strip()
    )
    number = "plural" if column >= 5 else "singular"
    gender = {
        2: "masculine",
        3: "feminine",
        4: "neuter",
    }.get(column)
    return InflectionHelp(
        surface=surface,
        base=base,
        kind="personal-pronoun",
        paradigm="personal-pronoun",
        case=case,
        gender=gender,
        number=number,
        pronoun_slot=slot,
    )


def inflections_for_phrase(
    phrase: BreakdownItem, group: BreakdownGroup
) -> list[InflectionHelp]:
    """Build typed inflection cards from an explicitly case-tagged phrase.

    Case is never guessed from an ending: a phrase must already carry one
    controlled case tag.  Ambiguous or incomplete phrases produce no card.
    """
    phrase_case = next(
        (
            tag.label
            for tag in phrase.tags
            if tag.label in {"nominative", "accusative", "dative", "genitive"}
        ),
        None,
    )
    if phrase_case is None:
        return []

    matches = list(TOKEN_RE.finditer(phrase.german))
    noun_details: dict[str, tuple[str, str]] = {}
    for item in group.items:
        if item.kind != "word":
            continue
        noun_match = re.match(
            r"^(der|die|das)\s+(.+)$", item.german, flags=re.IGNORECASE
        )
        if noun_match is None:
            continue
        noun_tokens = TOKEN_RE.findall(noun_match.group(2))
        if noun_tokens:
            details = (
                noun_match.group(1).casefold(),
                _noun_gender(item, noun_match.group(1).casefold()),
            )
            noun_details[noun_tokens[-1].casefold()] = details
            # The reusable noun card uses a dictionary form while source_forms
            # can hold a declined or plural form.  Record that source form too
            # so a case-tagged phrase such as "ihren Namen" can find its noun
            # and attach the determiner reference without a lesson-specific
            # exception.
            for source_form in item.source_forms:
                source_tokens = TOKEN_RE.findall(source_form)
                if source_tokens and source_tokens[-1].casefold() not in {
                    "der",
                    "die",
                    "das",
                }:
                    noun_details.setdefault(source_tokens[-1].casefold(), details)

    result: list[InflectionHelp] = []
    used_surfaces: set[str] = set()

    def authored_possessive_base(surface: str) -> str | None:
        if surface.startswith("Ihr") and any(
            item.kind == "word"
            and surface in item.source_forms
            and {"possessive", "formal"} <= {tag.label for tag in item.tags}
            for item in group.items
        ):
            return "Ihr"
        return next(
            (
                item.german
                for item in group.items
                if item.kind == "word"
                and "possessive" in {tag.label for tag in item.tags}
                and surface in item.source_forms
                and item.german.casefold().rstrip("-") in POSSESSIVE_STEMS
                and item.german.casefold() != surface.casefold()
            ),
            None,
        )

    for noun_index, noun_match in enumerate(matches):
        noun = noun_details.get(noun_match.group(0).casefold())
        if noun is None:
            continue
        dictionary_article, gender = noun
        candidates = matches[max(0, noun_index - 3) : noun_index]
        for candidate in reversed(candidates):
            help_card = _determiner_help(
                candidate.group(0),
                dictionary_article=dictionary_article,
                case=phrase_case,
                gender=gender,
                possessive_base=authored_possessive_base(candidate.group(0)),
            )
            if help_card is not None:
                key = help_card.surface.casefold()
                if key not in used_surfaces:
                    result.append(help_card)
                    used_surfaces.add(key)
                break

        for item in group.items:
            labels = {tag.label for tag in item.tags}
            if item.kind != "word" or "adjective" not in labels:
                continue
            source_forms = {form.casefold() for form in item.source_forms}
            adjective_match = next(
                (
                    match
                    for match in candidates
                    if match.group(0).casefold() in source_forms
                    and match.group(0).casefold() != item.german.casefold()
                ),
                None,
            )
            if adjective_match is None:
                continue
            preceding = matches[max(0, matches.index(adjective_match) - 2) : matches.index(adjective_match)]
            determiner = next(
                (
                    _determiner_help(
                        match.group(0),
                        dictionary_article=dictionary_article,
                        case=phrase_case,
                        gender=gender,
                        possessive_base=authored_possessive_base(match.group(0)),
                    )
                    for match in reversed(preceding)
                ),
                None,
            )
            if determiner and determiner.kind in {
                "definite-article",
                "der-word-determiner",
            }:
                paradigm = "weak-adjective"
            elif determiner:
                paradigm = "mixed-adjective"
            else:
                paradigm = "strong-adjective"
            result.append(
                InflectionHelp(
                    surface=adjective_match.group(0),
                    base=item.german,
                    kind="adjective",
                    paradigm=paradigm,
                    case=phrase_case,
                    gender=gender,
                    number="plural" if gender == "plural" else "singular",
                )
            )
            used_surfaces.add(adjective_match.group(0).casefold())

    pronoun_items = [
        item
        for item in group.items
        if item.kind == "word"
        and "personal pronoun" in {tag.label for tag in item.tags}
    ]
    pronoun_spellings: dict[str, set[str]] = {}
    explicitly_disambiguated: set[str] = set()
    for item in pronoun_items:
        labels = {tag.label for tag in item.tags}
        for form in {item.german, *item.source_forms}:
            pronoun_spellings.setdefault(form.casefold(), set()).add(form)
            if "singular" in labels or "plural" in labels:
                explicitly_disambiguated.add(form.casefold())
    capitalization_distinguishes = {
        key
        for key, forms in pronoun_spellings.items()
        if len(forms) > 1 and key in explicitly_disambiguated
    }

    for item in pronoun_items:
        labels = {tag.label for tag in item.tags}
        visible_forms = {
            item.german,
            *item.source_forms,
        }
        for match in matches:
            matched = match.group(0)
            if matched.casefold() in capitalization_distinguishes:
                belongs_to_item = matched in visible_forms
            else:
                belongs_to_item = matched.casefold() in {
                    form.casefold() for form in visible_forms
                }
            if not belongs_to_item:
                continue
            help_card = _pronoun_help(
                match.group(0),
                phrase_case,
                nominative_base=item.german,
                formal="formal" in labels,
                singular="singular" in labels,
            )
            if help_card and help_card.surface.casefold() not in used_surfaces:
                result.append(help_card)
                used_surfaces.add(help_card.surface.casefold())
                break
    return result


def attach_inflection_help(group: BreakdownGroup) -> BreakdownGroup:
    """Populate every phrase with validated, fixed-schema inflection help."""
    for item in group.items:
        if item.kind == "phrase":
            item.inflection_help = inflections_for_phrase(item, group)
    return group
