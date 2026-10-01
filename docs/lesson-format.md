# Nochmal lesson format

This file defines the production data and visual format used by every lesson.
The pedagogical audit and release gate are in
[grammar-breakdown-rulebook.md](grammar-breakdown-rulebook.md).

## Fixed lesson page

The lesson page is always rendered in this order:

1. title, German title, level and audio state;
2. complete paragraph and full audio;
3. sentence-by-sentence study cards;
4. speaking practice when enabled; and
5. completion controls.

There is no lesson-specific “goals and grammar” panel. Explanations appear only
on the word, phrase or form they describe.

## Fixed sentence card

Each sentence card contains:

1. sentence number;
2. sentence audio when available;
3. exact German;
4. natural English;
5. ordered word cards; and
6. phrase-result cards positioned after their inputs.

Cards follow German source order. A phrase may appear after its final component
even when that produces a small nested flow.

## Pydantic object map

| Object | Required shape |
|---|---|
| `Sentence` | `text`, `natural_meaning`, `breakdown_groups`, `audio_path` |
| `SentenceAnnotations` | controlled `word_tags`, `base_forms`, contextual `word_meanings`, audited phrase/tag exclusions, and authored `phrases` |
| `BreakdownGroup` | ordered `items` |
| `BreakdownItem` | `german`, natural/contextual `english`, optional `literal_meaning`, `kind`, `tags`, `source_forms`, optional typed help |
| `GrammarTag` | controlled `label` and matching `category` |
| `VerbHelp` | infinitive, meaning, tense and complete conjugation data |
| `InflectionHelp` | surface, base, kind, paradigm, case and grammatical slot |

Use `kind="word"` for reusable vocabulary and `kind="phrase"` for a
composed result.

## Word items

### Nouns

- German: dictionary article plus dictionary noun.
- English: noun meaning without an unnecessary English article.
- Tags: noun, gender, and plural when applicable.
- `source_forms`: every exact sentence token represented by the card.

### Verbs

- German: exact sentence form on the visible card.
- English: exact contextual meaning.
- Tags: only controlled verb/tense facts.
- `verb_help`: mandatory complete `VerbHelp`.

### Adjectives

- German: uninflected base.
- English: contextual meaning.
- Tags: `adjective` when used adjectivally.
- `source_forms`: declined surface form when different.

### Other words

Use the reusable form and contextual English meaning. Add only controlled tags
that are true in the current sentence.

When a reusable dictionary gloss would be misleading for the exact surface in
context, author the concise visible meaning in `SentenceAnnotations.word_meanings`.
This field changes only the word card's contextual English; it does not replace
the shared dictionary form, verb table, or grammar metadata.

## Phrase items

A phrase item:

- uses exact German source tokens;
- supplies one natural contextual English meaning;
- supplies `literal_meaning` when a natural translation hides structure that is useful to the learner;
- adds structural value beyond its word cards;
- has controlled tags; and
- contains `inflection_help` when it exposes case morphology.

Useful phrase types include noun phrases, prepositional phrases, contractions,
fixed expressions, question order, inversion, separated verbs, modal
constructions, perfect-tense brackets and subordinate clauses.

Do not create a phrase merely to repeat an article+noun dictionary card.

## Grammar tags

Tags are controlled metadata, never prose.

- Labels must exist in `TAG_KEYWORDS`.
- Categories must match `TAG_KEYWORDS`.
- Definitions come only from `TAG_DESCRIPTIONS`.
- The tag hover always shows label, category and fixed definition.
- Lesson data cannot add or override a definition.
- One pill represents one fact.
- Do not combine case and a redundant object-role tag.

## Verb reference hover

The renderer always uses this structure:

```text
Dictionary form
  infinitive | English

Simple present
  pronoun | German | English
  ... six rows

Form in this sentence
  surface | contextual English

Relevant tense (when not present)
  pronoun | German | English
```

Every verb uses the same sections and column order.

## Inflection reference hover

The renderer always uses this structure:

```text
Reference type

Base form | Sentence form | Contraction (when present)

case | gender/person | number

Paradigm name
  case | complete paradigm columns
  ... current cell highlighted
```

Allowed `kind` and `paradigm` combinations are enforced by
`InflectionHelp`:

| kind | allowed paradigm |
|---|---|
| definite article | definite |
| indefinite article | indefinite |
| possessive determiner | possessive |
| adjective | weak, mixed or strong adjective |
| personal pronoun | personal pronoun |

The full tables come from `grammar_reference.py`; lesson data never stores a
partial table or explanatory sentence.

## Source-form linkage

`source_forms` connects a reusable card to exact source text:

- noun dictionary form to a declined/plural source;
- adjective base to declined adjective;
- preposition base to a contraction;
- verb card to all source tokens in a discontinuous construction.

Every source token must be represented exactly once among word-card source
forms. Phrase cards reuse those tokens as composed results.

## Shared-code boundary

Shared code may contain:

- controlled vocabularies;
- complete paradigms;
- reusable matching and validation;
- fixed rendering functions; and
- accessibility behavior.

Shared code must not contain:

- a branch matching one full lesson sentence;
- a custom tooltip sentence for one lesson;
- a special layout for one grammar point; or
- generated lesson-description prose.

Sentence-specific tags, base-form corrections, contextual word meanings,
audited exclusions of invalid automatic phrases or tags, and extra phrases belong in the
sentence's `annotations` object in curriculum JSON. The compiler consumes that
same schema for every lesson; it must not keep a parallel sentence lookup
table in Python.

When context cannot be determined safely, add structured lesson metadata or
extend the model. Do not guess.

## Accessibility

Every hover target must:

- support pointer hover and keyboard focus;
- provide a useful aria label;
- keep the reference card inside the viewport;
- support vertical scrolling;
- allow wide tables to scroll horizontally on narrow screens; and
- use the same content for hover and focus.

## Required tests

Before publishing a lesson, test:

- Pydantic rejects invalid model combinations;
- every source token is represented;
- every verb has complete bilingual tables;
- every case-bearing phrase has the required typed help;
- each help surface exists inside its phrase;
- the help case matches the phrase case tag;
- every reference table has all four cases;
- the current table cell is highlighted;
- no lesson-description panel is rendered; and
- the complete lesson-library validator passes.

Run:

```bash
python -m unittest discover -s tests -q
```

Then run `python scripts/validate_release.py LESSON_ID` and inspect the running
app before adding the lesson ID to `curriculum/a1_course/publication.json`.
