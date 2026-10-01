# Nochmal reviewed A1 course

This directory contains lessons promoted from `curriculum/a1_staging` only
after the complete grammar, audio, validation, and rendering review described
in `docs/grammar-breakdown-rulebook.md` and `docs/lesson-format.md`.

The source record is not itself a publication switch. The app exposes only
lesson IDs named in `publication.json`, and each listed lesson must pass the
fail-closed release gate in `nochmal/validation/release.py`. The gate requires
strict source validation, the deterministic lesson contract, a current
structured review report, and matching ElevenLabs v4 audio evidence.
