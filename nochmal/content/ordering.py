"""Shared source-order layout for compiled word and phrase cards."""

from __future__ import annotations

import re

from .models import BreakdownGroup, BreakdownItem


def _tokenize(text: str) -> list[str]:
    return [
        token.casefold()
        for token in re.findall(r"\w+(?:[-’']\w+)*", text, flags=re.UNICODE)
    ]


def _find_sequence(
    source: list[str], candidate: list[str], *, start: int = 0
) -> tuple[int, int] | None:
    if not candidate:
        return None
    for index in range(start, len(source) - len(candidate) + 1):
        if source[index : index + len(candidate)] == candidate:
            return index, index + len(candidate) - 1
    return None


def _word_candidates(item: BreakdownItem) -> list[list[str]]:
    candidates: list[list[str]] = []
    for form in [item.german, *item.source_forms]:
        tokens = _tokenize(form)
        if tokens and tokens not in candidates:
            candidates.append(tokens)
    german_tokens = _tokenize(item.german)
    if german_tokens and german_tokens[0] in {"der", "die", "das"}:
        noun_tokens = german_tokens[1:]
        if noun_tokens and noun_tokens not in candidates:
            candidates.append(noun_tokens)
    if german_tokens and [german_tokens[-1]] not in candidates:
        candidates.append([german_tokens[-1]])
    return sorted(candidates, key=len, reverse=True)


def _word_spans(
    words: list[BreakdownItem], sentence_text: str
) -> dict[int, tuple[int, int]]:
    source = _tokenize(sentence_text)
    spans: dict[int, tuple[int, int]] = {}
    claimed: set[int] = set()

    def find_unclaimed(candidate: list[str]) -> tuple[int, int] | None:
        for index in range(len(source) - len(candidate) + 1):
            end = index + len(candidate) - 1
            if source[index : end + 1] == candidate and not (
                set(range(index, end + 1)) & claimed
            ):
                return index, end
        return None

    for item in words:
        matches = [
            match
            for candidate in _word_candidates(item)
            if (match := find_unclaimed(candidate))
        ]
        if matches:
            match = min(matches, key=lambda span: (span[0], -span[1]))
            spans[id(item)] = match
            claimed.update(range(match[0], match[1] + 1))
            # A dictionary noun card can represent an article and a declined
            # noun that are separated by an adjective. Reserve all of its
            # concrete source forms, while using the first source position for
            # visual order. This keeps both token ownership and the rendered
            # German order intact.
            for source_form in item.source_forms:
                tokens = _tokenize(source_form)
                if _find_sequence(source[match[0] : match[1] + 1], tokens):
                    continue
                if additional_match := find_unclaimed(tokens):
                    claimed.update(range(additional_match[0], additional_match[1] + 1))
    return spans


def _phrase_span(
    phrase: BreakdownItem, sentence_text: str
) -> tuple[int, int] | None:
    source = _tokenize(sentence_text)
    chunks = [
        _tokenize(chunk)
        for chunk in re.split(r"\.{3}|…", phrase.german)
        if _tokenize(chunk)
    ]
    if not chunks:
        return None
    cursor = 0
    first_start: int | None = None
    last_end: int | None = None
    for chunk in chunks:
        match = _find_sequence(source, chunk, start=cursor)
        if match is None:
            return None
        if first_start is None:
            first_start = match[0]
        last_end = match[1]
        cursor = match[1] + 1
    if first_start is None or last_end is None:
        return None
    return first_start, last_end


def is_redundant_noun_phrase(
    phrase: BreakdownItem, words: list[BreakdownItem]
) -> bool:
    """Reject article+noun restatements that add no grammatical information."""
    if phrase.tags:
        return False
    phrase_tokens = _tokenize(phrase.german)
    if phrase_tokens and phrase_tokens[0] in {
        "der", "die", "das", "ein", "eine", "einen", "einem", "einer", "eines",
    }:
        phrase_tokens = phrase_tokens[1:]
    if not phrase_tokens:
        return False
    noun_labels = {"noun", "compound noun", "masc.", "fem.", "neuter"}
    for word in words:
        labels = {tag.label for tag in word.tags}
        if not labels & noun_labels or "plural" in labels:
            continue
        candidates = {
            tuple(tokens[1:] if tokens and tokens[0] in {"der", "die", "das"} else tokens)
            for tokens in _word_candidates(word)
        }
        if tuple(phrase_tokens) in candidates:
            return True
    return False


def ordered_breakdown_items(
    group: BreakdownGroup, sentence_text: str
) -> list[BreakdownItem]:
    """Place each phrase after its final component, matching the app layout."""
    words = [item for item in group.items if item.kind == "word"]
    phrases = [
        item
        for item in group.items
        if item.kind == "phrase" and not is_redundant_noun_phrase(item, words)
    ]
    word_spans = _word_spans(words, sentence_text)
    source_length = len(_tokenize(sentence_text))
    decorated: list[tuple[tuple[int, int, int, int, int], BreakdownItem]] = []
    for original_index, item in enumerate([*words, *phrases]):
        span = (
            word_spans.get(id(item))
            if item.kind == "word"
            else _phrase_span(item, sentence_text)
        )
        if span is None:
            sort_key = (
                source_length + original_index,
                item.kind == "phrase",
                0,
                source_length,
                original_index,
            )
        else:
            start, end = span
            # Word cards start where their source form begins. Phrase-result
            # cards remain after their final component, which allows a noun
            # card that includes an article to precede an intervening adjective.
            placement = end if item.kind == "phrase" else start
            sort_key = (
                placement,
                item.kind == "phrase",
                end - start,
                start,
                original_index,
            )
        decorated.append((sort_key, item))
    return [item for _, item in sorted(decorated, key=lambda entry: entry[0])]
