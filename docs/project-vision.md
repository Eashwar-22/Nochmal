# Nochmal mobile product direction

Nochmal helps learners understand a short piece of spoken German that was
difficult on the first listen. The mobile web app starts with the audio, then
reveals the German passage, natural English, and sentence-by-sentence cards.
Learners can replay the passage and individual sentences, inspect word and
phrase meanings, and open structured grammar references.

The current product is the static site in `web/dist/`. Its visible lessons
come from `web/dist/lessons.json`. Python tooling validates authored A1 and
A2 records, builds the cards, verifies matching audio, and installs reviewed
lessons into the mobile site. Unpublished A2 records remain in the curriculum
source until requested, audited, and released. The A2 and B1 blueprints remain
planning inputs.

The learning loop is:

1. Hear the complete German audio before reading the passage.
2. Reveal the passage and study each sentence with its translation and cards.
3. Open full verb and form tables where the visible German changes.
4. Replay the same complete recording and notice what is now understandable.

Keep lesson rules explicit and mechanically tested. Treat linguistic review
and schema validation as separate requirements. Do not publish a lesson until
its sentence audit, cards, audio, release checks, and mobile preview pass.
Favor a maintainable one-person workflow and keep API keys out of source
control and logs.
