# Nochmal grammar breakdown rulebook

This is the mandatory, lesson-independent contract for integrating learning
content into Nochmal. Read it together with [lesson-format.md](lesson-format.md)
before changing a lesson.

The purpose of this document is consistency. Every lesson uses the same data
types, card types, hover layouts, validation rules, and publication process.
Lesson-specific grammar essays are not part of the product.

## 1. Product rule

The learning interface contains:

1. the German passage and audio;
2. sentence-level German and natural English;
3. ordered word cards;
4. ordered phrase-result cards;
5. controlled grammar tags;
6. fixed-layout reference hovers; and
7. speaking practice when the lesson has reviewed audio.

Do not add a “Lesson goals”, “Grammar explanation”, “What to notice”, or
similar lesson-description panel. Grammar belongs beside the exact word or
phrase where the learner encounters it.

Internal curriculum-planning fields may remain in the source corpus, but they
must not generate learner-facing prose.

## 2. Typed content contract

Production lesson content is validated with Pydantic. Use the existing models;
do not pass unstructured dictionaries into the renderer.

| Model | One responsibility |
|---|---|
| `Lesson` | identity, sequence, titles, sentences, audio and practice data |
| `Sentence` | exact German, natural English, audio and breakdown groups |
| `SentenceAnnotations` | sentence-owned tags, base forms, contextual word meanings, audited phrase/tag exclusions and authored phrases |
| `BreakdownGroup` | one ordered collection of learning cards |
| `BreakdownItem` | one word card or one phrase-result card |
| `GrammarTag` | one controlled label and category |
| `VerbHelp` | the fixed verb-reference data |
| `InflectionHelp` | the fixed case/declension-reference data |
| `SpeechAlternative` | one deliberately accepted speaking alternative |
| `PerformanceActivity` | one typed retrieval task with concrete prompts |

### 2.1 No free-form hover fields

A lesson cannot author tooltip prose. It supplies controlled fields, and the
shared renderer supplies the wording and layout.

`InflectionHelp` contains only:

- exact surface form;
- base form;
- controlled kind;
- controlled paradigm;
- case;
- gender when applicable;
- number;
- pronoun slot when applicable;
- resolved article form for a contraction; and
- contraction expansion when applicable.

Pydantic must reject incompatible combinations, such as a definite article
using an adjective paradigm or a plural slot marked singular.

### 2.2 One source of truth

Keep each fact in one place:

- curriculum JSON: passage text, translation, sequence, audio paths,
  `SentenceAnnotations` inputs (including concise contextual word meanings
  and numbered context for repeated surface forms, including contextual verb senses)
  and deliberate speaking alternatives;
- Pydantic models: allowed fields and combinations;
- `grammar_reference.py`: complete reusable paradigms;
- `models.py`: controlled grammar tags and fixed definitions;
- renderer: shared HTML structure;
- this rulebook: authoring and publication policy.

Never add a full sentence as a special branch in shared rendering or grammar
reference code. Sentence-specific analysis is content data; paradigms and
layouts are shared code.

## 3. Required sentence audit

Before building cards, audit every sentence from left to right.

| Surface | Base | Class | Role | Case/tense | Trigger | Visible change | Card/help |
|---|---|---|---|---|---|---|---|
| exact token or phrase | reusable form | controlled class | contextual role | exact value | governing construction | exact form change | word, phrase, verb or inflection |

Check every:

- noun and noun gender;
- singular or plural form;
- article and determiner;
- adjective and whether it is attributive, predicate or adverbial;
- pronoun and contextual case;
- preposition and governed case;
- finite verb, infinitive, participle, prefix and tense;
- contraction;
- clause boundary and finite-verb position;
- conjunction, adverb and particle; and
- fixed expression whose meaning is not compositional.

The audit is complete only when every source token has a word card and every
meaningful transformation has the required structured help.

## 4. Word-card contract

A word card always represents a reusable item.

### Nouns

- Use the dictionary article: `der`, `die` or `das`.
- Use the singular dictionary form unless the noun is plural-only.
- Keep noun gender separate from sentence case.
- Do not infer feminine gender from plural `die`.

### Verbs

- Use the correct lexical infinitive.
- Treat separability and reflexivity as lexical facts.
- Use the contextual English meaning on the visible word card.
- Attach `VerbHelp` to every verb card.

### Adjectives

- Store the reusable uninflected form.
- Put the visible declined form in `source_forms`.
- Mark attributive adjectives as adjectives.
- Do not give predicate or adverbial adjectives a declension card.

### Function words

- Classify the word by its actual sentence function.
- A preposition is not a separated prefix.
- A sentence-initial adverb is not automatically a conjunction.
- A capitalized token is not automatically a noun.

## 5. Phrase-result contract

A phrase card shows what selected word cards produce together.

A valid phrase:

- uses exact source wording;
- has a natural contextual English meaning;
- contains a useful learning unit;
- appears after its component word cards;
- has only controlled tags;
- carries the contextual case tag when it contains case morphology; and
- carries typed `InflectionHelp` for each inspectable case form.

Do not create:

- a second bare article+noun card that merely repeats the noun card;
- a whole-clause case tag because one noun phrase inside it has a case;
- a phrase containing words absent from the source;
- a phrase that crosses an unrelated noun or clause boundary; or
- a free-form explanation disguised as a phrase.

## 6. Fixed hover layouts

All hovers are renderer-owned. Lessons select content through typed fields;
they never select layout or wording.

### 6.1 Grammar-tag hover

Every tag hover has exactly:

1. tag label;
2. tag category; and
3. the fixed definition from `TAG_DESCRIPTIONS`.

The lesson cannot override the definition.

### 6.2 Verb hover

Every verb hover has exactly:

1. **Dictionary form** — infinitive and English meaning;
2. **Simple present** — a six-row bilingual table;
3. **Form in this sentence** — visible German and contextual English; and
4. a complete table for another relevant tense when applicable.

No lesson-authored usage paragraph is displayed in the hover.

### 6.3 Case and declension hover

Every case-bearing surface form uses the same reference-card shell:

1. reference type;
2. base form;
3. sentence form;
4. contraction expansion when applicable;
5. case, gender/person and number chips;
6. paradigm name; and
7. the complete paradigm table with the current cell highlighted.

The table is mandatory. A bare statement such as `der → dem` or
`klein → kleinen` is not sufficient.

Supported shared tables are:

- definite articles;
- indefinite articles;
- possessive determiners;
- der-word determiners such as `jeder`;
- negative determiners such as `kein`;
- weak adjective endings;
- mixed adjective endings;
- strong adjective endings; and
- personal pronouns.

If a lesson needs a paradigm that the typed model does not support, extend the
shared model, reference table, renderer and tests before publishing the lesson.

## 7. Case analysis

Determine the grammatical trigger first. Never infer case only from an ending.

### Nominative

Use for a subject or a relevant predicate-noun construction.

### Accusative

Common triggers are a direct object, an accusative preposition, or a two-way
preposition expressing a destination or placement.

### Dative

Common triggers are a dative preposition, recipient/complement, or a two-way
preposition expressing a fixed location.

### Genitive

Use for genuine possession or a genitive-governing construction. Do not call a
feminine `-er` form genitive unless the phrase function establishes genitive.

### Two-way prepositions

Choose by the phrase’s meaning:

- fixed location / **where?** → normally dative;
- destination or placement / **where to?** → normally accusative.

Do not use the unreliable shortcut “movement means accusative.”

### Invisible case

A proper place name may carry governed case without displaying an ending. Tag
the governing preposition and phrase, but do not invent an inflection card when
no visible form exists.

## 8. Inflection rules

### Articles and determiners

For each visible article or determiner in a case-tagged noun phrase:

- identify its controlled paradigm;
- identify case, gender and number;
- attach one `InflectionHelp`;
- show the complete paradigm table; and
- highlight the current cell.

A contraction also stores the expanded preposition+article and the resolved
article form.

### Adjectives

Only attributive adjectives decline. Select the paradigm from the determiner
context:

- definite article → weak adjective endings;
- `ein`-word or possessive determiner → mixed adjective endings;
- no determiner → strong adjective endings.

The adjective gets its own hover. An article hover never substitutes for the
adjective hover.

### Personal pronouns

A case-changed personal pronoun gets its own `InflectionHelp` with:

- nominative base;
- sentence form;
- exact case;
- person/number slot; and
- the complete personal-pronoun case table.

If the visible form is ambiguous and context metadata does not resolve it,
fail closed and require an authored choice.

## 9. Word order and verbal constructions

Add a phrase result when the learner needs to see:

- finite verb in second position;
- W-question or yes/no-question order;
- time/place/object fronting;
- separated prefix;
- modal plus final infinitive;
- auxiliary plus participle;
- reflexive-pronoun placement; or
- verb-final subordinate clause.

Use controlled structure tags. Do not add an explanatory paragraph.

## 10. Automation boundary

Automation may:

- match an authored surface to a reusable base;
- apply a complete tested paradigm;
- render typed hover data;
- expand a known contraction;
- verify every token and structured transformation; and
- reject incomplete lesson data.

Automation must not:

- guess case from an ending;
- guess noun gender from an article that may be plural;
- guess separability from the first letters of a verb;
- attach a determiner across another noun or clause;
- invent a grammar explanation;
- invent a speaking alternative; or
- silently omit an unsupported form.

Ambiguous analysis requires structured authored metadata. The fallback is an
unpublished lesson, not guessed UI.

## 11. Rendering and accessibility

Before publication, verify:

- hover and focus open the same card;
- every underlined form is keyboard reachable;
- tables remain readable at desktop and mobile widths;
- the highlighted cell matches the sentence form;
- repeated forms open the correct card;
- no tooltip is clipped by the card or page;
- German, English and audio agree; and
- the rendered card order follows the source sentence.

## 12. Publication gate

A lesson may enter the published lesson list only when all of these pass.

### Structure

- [ ] Every production object validates through Pydantic.
- [ ] Every source token has a word card.
- [ ] Every noun has a correct dictionary article or plural-only treatment.
- [ ] Every useful phrase uses exact source wording.
- [ ] Every tag is a controlled `GrammarTag`.

### Hovers

- [ ] Every verb has complete `VerbHelp`.
- [ ] Every visible article/determiner case form has `InflectionHelp`.
- [ ] Every declined attributive adjective has separate `InflectionHelp`.
- [ ] Every changed personal pronoun has `InflectionHelp`.
- [ ] Every inflection card displays a full table and highlighted current cell.
- [ ] No hover contains lesson-authored prose.

### Accuracy

- [ ] Case is justified by a governing construction or sentence role.
- [ ] Gender, number, person and paradigm are correct.
- [ ] Separable/reflexive verb identity is correct.
- [ ] Phrase boundaries do not cross unrelated syntax.
- [ ] Translation and audio match the exact German source.

### Verification

- [ ] Curriculum validation passes.
- [ ] The complete unit-test suite passes.
- [ ] New paradigms have model, table and rendering tests.
- [ ] The generated mobile package and installed files pass their integrity checks.
- [ ] The lesson remains hidden until every blocking item passes.

## 13. Required integration sequence

For every new lesson:

1. Read this rulebook and `lesson-format.md`.
2. Complete the sentence audit.
3. Create typed word and phrase items.
4. Add `VerbHelp` and `InflectionHelp`; do not write tooltip prose.
5. Validate the Pydantic objects.
6. Run curriculum and unit tests.
7. Build and verify the mobile package.
8. Run the release validator, then use the publish command to add the lesson
   ID to its level's `curriculum/a1_published/publication.json` or
   `curriculum/a2_published/publication.json` only after all checks pass.

This sequence is the reusable learning-content system. Do not replace it with
lesson-specific UI, sentence-string branches in shared code, or generated
grammar essays.
