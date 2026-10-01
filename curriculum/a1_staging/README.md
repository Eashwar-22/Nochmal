# A1 staged lesson drafts

> **UNPUBLISHED. DO NOT IMPORT INTO THE APP.**

This directory holds passage drafts derived from `curriculum/a1_blueprint.md`.
It is deliberately outside `curriculum/a1_a2/lessons/` and is not consumed by
the production lesson compiler.

Each draft contains only:

- a staging-only ID and blueprint lesson number;
- a title, module, format, and explicit `draft_unpublished` status;
- German sentences with natural English meanings; and
- one first-listen comprehension check.

The following publication blockers intentionally remain:

- sentence-by-sentence grammar audit;
- authored word and phrase cards;
- complete `VerbHelp` and `InflectionHelp`;
- reviewed speaking alternatives;
- sentence and full-passage audio;
- production Pydantic validation and tests;
- linguistic and in-app review; and
- addition to any published-lesson list.

Run the staging-only structural check with:

```bash
python3 curriculum/a1_staging/validate.py
```

Passing this check means only that the draft corpus has the expected lesson
order, bilingual sentence alignment, and planned sentence/word ranges. It does
not establish grammatical accuracy or publication readiness.
