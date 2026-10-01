"""Compile the authored A1-A2 curriculum into production lesson objects.

The source passages remain easy-to-review JSON. This module adds the reusable
word meanings, grammar metadata, verb help, and clause-level subphrases needed
by the study interface. Audio is the only deliberately pending component.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .a1_a2_glossary import TARGET_GLOSSES
from .models import (
    BreakdownGroup,
    BreakdownItem,
    ConjugationForm,
    GrammarTag,
    Lesson,
    Sentence,
    SentenceAnnotations,
    TAG_KEYWORDS,
    VerbHelp,
)
from .grammar_reference import attach_inflection_help


CURRICULUM_ROOT = Path(__file__).resolve().parents[2] / "curriculum" / "a1_a2"
WORD_RE = re.compile(r"\b[\wÄÖÜäöüß'-]+\b", flags=re.UNICODE)
PRONOUNS = ("ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie")
ENGLISH_SUBJECTS = ("I", "you", "he/she/it", "we", "you", "they/you")


COMMON_GLOSSES: dict[str, str] = {
    "aber": "but", "achtung": "attention", "alle": "all", "allen": "all", "alles": "everything",
    "als": "as / when / than", "am": "at the / on the", "an": "at / on",
    "andere": "other", "anderen": "other", "auch": "also", "auf": "on / onto",
    "aus": "from / out of", "außerdem": "in addition", "ausserdem": "in addition",
    "ab": "from / off", "bald": "soon", "bei": "at / with", "beide": "both", "beiden": "both",
    "beim": "at the / while", "bereit": "ready", "bis": "until / to",
    "bisschen": "a little", "da": "there / since", "dafür": "for it / in favor",
    "dagegen": "against it", "danach": "afterwards", "dann": "then", "das": "the / that",
    "darin": "in it", "darum": "therefore / about it", "dass": "that",
    "dazu": "in addition / for that", "deine": "your", "dem": "the",
    "den": "the", "der": "the", "dich": "you", "die": "the", "dies": "this",
    "diese": "this / these", "diesem": "this", "dieser": "this", "dieses": "this",
    "doch": "after all / however", "dort": "there", "draußen": "outside",
    "draussen": "outside", "du": "you", "durch": "through", "ebenfalls": "also",
    "ein": "a / an", "eine": "a / an", "einem": "a / an", "einen": "a / an",
    "einer": "a / an", "einige": "some", "einigen": "some", "einmal": "once",
    "er": "he", "es": "it / there", "etwas": "something / somewhat",
    "fast": "almost", "für": "for", "gegen": "against / around", "genau": "exactly",
    "gerade": "just / straight", "gestern": "yesterday", "gibt": "there is / gives",
    "gut": "good / well", "habe": "have", "haben": "have", "hat": "has",
    "hallo": "hello", "hier": "here", "hin": "there / toward", "hinter": "behind", "ich": "I",
    "ihm": "him", "ihn": "him", "ihnen": "them / you", "ihr": "her / you",
    "ihre": "her / their", "ihren": "her / their", "im": "in the", "immer": "always",
    "in": "in / into", "ins": "into the", "ist": "is", "ja": "yes",
    "jede": "every", "jeden": "every", "jeder": "every", "jemand": "someone",
    "jetzt": "now", "kein": "no / not a", "keine": "no / not a",
    "keinen": "no / not a", "kurz": "brief / briefly", "lang": "long",
    "lange": "long / for a long time", "man": "one / people", "mehr": "more",
    "mein": "my", "meine": "my", "meinem": "my", "meinen": "my",
    "meiner": "my", "mich": "me", "mir": "me", "mit": "with / by",
    "nach": "after / to", "neben": "next to", "nicht": "not", "nichts": "nothing",
    "noch": "still / another", "nur": "only", "ob": "whether / if", "oder": "or",
    "oft": "often", "ohne": "without", "pro": "per", "schon": "already",
    "statt": "instead of", "teil": "part",
    "sehr": "very", "seit": "since / for", "selbst": "oneself / even",
    "sie": "she / they / you", "sind": "are", "so": "so / like this",
    "sondern": "but rather", "sonst": "otherwise", "spät": "late", "später": "later",
    "trotzdem": "nevertheless", "über": "over / about", "um": "at / around / in order to",
    "und": "and", "uns": "us", "unser": "our", "unsere": "our", "unter": "under / among",
    "vom": "from the", "von": "from / of", "vor": "before / in front of",
    "war": "was", "waren": "were", "was": "what", "wenn": "if / when",
    "weh": "sore / hurting", "wer": "who", "wie": "how / like", "wieder": "again", "wir": "we",
    "wo": "where", "zum": "to the / for", "zur": "to the", "zu": "to / too",
    "zuerst": "first", "zurück": "back", "zwischen": "between",
    "aktuelle": "current", "angegebene": "specified", "begrenzte": "limited",
    "begrenzt": "limited", "blaue": "blue", "dritten": "third", "einfache": "simple",
    "einzelne": "individual", "entschuldigung": "excuse me / apology", "erst": "only / first", "erste": "first", "ersten": "first",
    "erleichtert": "relieved", "fehlende": "missing", "frische": "fresh", "früh": "early", "fünfzehn": "fifteen",
    "ganze": "whole", "gemütlich": "cozy", "gesünder": "healthier", "guten": "good", "groß": "big / tall",
    "großen": "big / tall", "gute": "good", "günstige": "affordable / favorable",
    "geehrte": "dear / esteemed", "herzlich": "warmly / cordial", "hoch": "high", "hoffentlich": "hopefully",
    "höflich": "polite / politely", "ihrem": "her / their", "ihrer": "her / their",
    "interessante": "interesting", "jedes": "every", "klares": "clear",
    "klein": "small", "kleine": "small", "kleinen": "small", "kleines": "small",
    "kurze": "short", "kurzen": "short", "langsam": "slow / slowly", "leiser": "quieter",
    "leere": "empty", "letzte": "last", "liebe": "dear", "lieber": "preferably / rather", "lustige": "funny",
    "länger": "longer", "manchmal": "sometimes", "mehrere": "several",
    "mehrmals": "several times", "meines": "my", "neu": "new", "neue": "new", "neuen": "new",
    "neuer": "new", "neues": "new", "nun": "now", "nächste": "next",
    "nächsten": "next", "näher": "closer", "oben": "upstairs / above", "obwohl": "although",
    "offen": "open", "passend": "suitable", "per": "per / by", "recht": "right",
    "regelmäßig": "regular / regularly", "regelmässig": "regular / regularly",
    "gross": "big / tall", "grossen": "big / tall", "schnell": "fast / quickly", "schwarzes": "black",
    "schwer": "heavy / difficult", "schweren": "heavy / difficult", "schwierige": "difficult",
    "schön": "beautiful / nice", "sechzehn": "sixteen", "seine": "his", "seinem": "his",
    "seinen": "his", "seiner": "his", "seltener": "less often", "sich": "oneself",
    "siebzehn": "seventeen", "spätem": "late", "stark": "strong", "starker": "strong",
    "starkes": "strong", "technischen": "technical", "täglichen": "daily",
    "ungefähr": "approximately", "unserer": "our", "vegetarisches": "vegetarian",
    "viel": "much / a lot", "viele": "many", "vierzehn": "fourteen", "vierzig": "forty",
    "vorher": "beforehand", "wahrscheinlich": "probably", "warm": "warm", "warme": "warm",
    "welche": "which", "welchen": "which", "wenig": "little / few",
    "wichtigsten": "most important", "wohin": "where to", "zurzeit": "currently",
    "willkommen": "welcome", "zwanzig": "twenty", "zweimal": "twice", "zweite": "second",
}

NUMBER_GLOSSES = {
    "eins": "one", "zwei": "two", "drei": "three", "vier": "four",
    "fünf": "five", "sechs": "six", "sieben": "seven", "acht": "eight",
    "neun": "nine", "zehn": "ten", "elf": "eleven", "zwölf": "twelve",
    "achtzehn": "eighteen", "achtundzwanzig": "twenty-eight",
}

IRREGULAR_PRESENT: dict[str, tuple[str, str, str, str, str, str]] = {
    "sein": ("bin", "bist", "ist", "sind", "seid", "sind"),
    "haben": ("habe", "hast", "hat", "haben", "habt", "haben"),
    "werden": ("werde", "wirst", "wird", "werden", "werdet", "werden"),
    "heißen": ("heiße", "heißt", "heißt", "heißen", "heißt", "heißen"),
    "sprechen": ("spreche", "sprichst", "spricht", "sprechen", "sprecht", "sprechen"),
    "gehen": ("gehe", "gehst", "geht", "gehen", "geht", "gehen"),
    "beginnen": ("beginne", "beginnst", "beginnt", "beginnen", "beginnt", "beginnen"),
    "essen": ("esse", "isst", "isst", "essen", "esst", "essen"),
    "fahren": ("fahre", "fährst", "fährt", "fahren", "fahrt", "fahren"),
    "tragen": ("trage", "trägst", "trägt", "tragen", "tragt", "tragen"),
    "wehtun": ("tue weh", "tust weh", "tut weh", "tun weh", "tut weh", "tun weh"),
    "schlafen": ("schlafe", "schläfst", "schläft", "schlafen", "schlaft", "schlafen"),
    "lesen": ("lese", "liest", "liest", "lesen", "lest", "lesen"),
    "können": ("kann", "kannst", "kann", "können", "könnt", "können"),
    "dürfen": ("darf", "darfst", "darf", "dürfen", "dürft", "dürfen"),
    "helfen": ("helfe", "hilfst", "hilft", "helfen", "helft", "helfen"),
    "müssen": ("muss", "musst", "muss", "müssen", "müsst", "müssen"),
    "wollen": ("will", "willst", "will", "wollen", "wollt", "wollen"),
    "sollen": ("soll", "sollst", "soll", "sollen", "sollt", "sollen"),
    "mögen": ("mag", "magst", "mag", "mögen", "mögt", "mögen"),
    "möchten": ("möchte", "möchtest", "möchte", "möchten", "möchtet", "möchten"),
    "nehmen": ("nehme", "nimmst", "nimmt", "nehmen", "nehmt", "nehmen"),
    "anfangen": ("fange an", "fängst an", "fängt an", "fangen an", "fangt an", "fangen an"),
    "treffen": ("treffe", "triffst", "trifft", "treffen", "trefft", "treffen"),
    "verlieren": ("verliere", "verlierst", "verliert", "verlieren", "verliert", "verlieren"),
    "empfehlen": ("empfehle", "empfiehlst", "empfiehlt", "empfehlen", "empfehlt", "empfehlen"),
    "scheinen": ("scheine", "scheinst", "scheint", "scheinen", "scheint", "scheinen"),
    "werfen": ("werfe", "wirfst", "wirft", "werfen", "werft", "werfen"),
    "backen": ("backe", "bäckst", "bäckt", "backen", "backt", "backen"),
    "denken": ("denke", "denkst", "denkt", "denken", "denkt", "denken"),
    "bitten": ("bitte", "bittest", "bittet", "bitten", "bittet", "bitten"),
    "halten": ("halte", "hältst", "hält", "halten", "haltet", "halten"),
    "geben": ("gebe", "gibst", "gibt", "geben", "gebt", "geben"),
    "sehen": ("sehe", "siehst", "sieht", "sehen", "seht", "sehen"),
    "stehen": ("stehe", "stehst", "steht", "stehen", "steht", "stehen"),
    "liegen": ("liege", "liegst", "liegt", "liegen", "liegt", "liegen"),
    "bleiben": ("bleibe", "bleibst", "bleibt", "bleiben", "bleibt", "bleiben"),
    "bringen": ("bringe", "bringst", "bringt", "bringen", "bringt", "bringen"),
    "schreiben": ("schreibe", "schreibst", "schreibt", "schreiben", "schreibt", "schreiben"),
    "finden": ("finde", "findest", "findet", "finden", "findet", "finden"),
    "abgeben": ("gebe ab", "gibst ab", "gibt ab", "geben ab", "gebt ab", "geben ab"),
    "zurückgeben": ("gebe zurück", "gibst zurück", "gibt zurück", "geben zurück", "gebt zurück", "geben zurück"),
    "einladen": ("lade ein", "lädst ein", "lädt ein", "laden ein", "ladet ein", "laden ein"),
    "fernsehen": ("sehe fern", "siehst fern", "sieht fern", "sehen fern", "seht fern", "sehen fern"),
    "mitnehmen": ("nehme mit", "nimmst mit", "nimmt mit", "nehmen mit", "nehmt mit", "nehmen mit"),
    "vorschlagen": ("schlage vor", "schlägst vor", "schlägt vor", "schlagen vor", "schlagt vor", "schlagen vor"),
    "stattfinden": ("finde statt", "findest statt", "findet statt", "finden statt", "findet statt", "finden statt"),
    "teilnehmen": ("nehme teil", "nimmst teil", "nimmt teil", "nehmen teil", "nehmt teil", "nehmen teil"),
    "wissen": ("weiß", "weißt", "weiß", "wissen", "wisst", "wissen"),
    "lassen": ("lasse", "lässt", "lässt", "lassen", "lasst", "lassen"),
    "waschen": ("wasche", "wäschst", "wäscht", "waschen", "wascht", "waschen"),
}

VERB_ALIASES = {
    "Zeit haben": "haben", "sich treffen": "treffen",
    "Rad fahren": "fahren", "sich bewerben": "bewerben", "sich vorstellen": "vorstellen",
    "sich entschuldigen": "entschuldigen", "sich beschweren": "beschweren",
    "sich ausruhen": "ausruhen", "sich informieren": "informieren",
    "sich bedanken": "bedanken", "sich anmelden": "anmelden", "sich kümmern": "kümmern",
    "sich erinnern": "erinnern", "sich beeilen": "beeilen", "dafür sein": "sein",
    "dagegen sein": "sein", "einverstanden sein": "sein", "recht haben": "haben",
    "fit sein": "sein", "sich eintragen": "eintragen", "sich ärgern": "ärgern",
}

# Separability is lexical: a verb beginning with ``an`` is not automatically an
# ``an-`` verb (notably, antworten never becomes *twortet ... an).  Keep the
# course's separable verbs explicit instead of guessing from their first letters.
SEPARABLE_VERBS: dict[str, str] = {
    "abfahren": "ab",
    "abgeben": "ab",
    "abheben": "ab",
    "anfangen": "an",
    "ankommen": "an",
    "anmelden": "an",
    "anrufen": "an",
    "aufhören": "auf",
    "aufpassen": "auf",
    "aufstehen": "auf",
    "ausfüllen": "aus",
    "auspacken": "aus",
    "ausruhen": "aus",
    "aussprechen": "aus",
    "aussteigen": "aus",
    "einkaufen": "ein",
    "einladen": "ein",
    "eintragen": "ein",
    "einziehen": "ein",
    "fernsehen": "fern",
    "mitbringen": "mit",
    "mitnehmen": "mit",
    "stattfinden": "statt",
    "teilnehmen": "teil",
    "umsteigen": "um",
    "umziehen": "um",
    "vorbereiten": "vor",
    "vorschlagen": "vor",
    "vorstellen": "vor",
    "zurückbekommen": "zurück",
    "zurückgeben": "zurück",
    "zurückgehen": "zurück",
}

ENGLISH_IRREGULAR = {
    "be": ("is", "was", "been"), "have": ("has", "had", "had"),
    "go": ("goes", "went", "gone"), "come": ("comes", "came", "come"),
    "speak": ("speaks", "spoke", "spoken"), "eat": ("eats", "ate", "eaten"),
    "drink": ("drinks", "drank", "drunk"), "take": ("takes", "took", "taken"),
    "read": ("reads", "read", "read"), "write": ("writes", "wrote", "written"),
    "find": ("finds", "found", "found"), "think": ("thinks", "thought", "thought"),
    "bring": ("brings", "brought", "brought"), "meet": ("meets", "met", "met"),
    "lose": ("loses", "lost", "lost"), "begin": ("begins", "began", "begun"),
    "sleep": ("sleeps", "slept", "slept"), "wear": ("wears", "wore", "worn"),
    "hang": ("hangs", "hung", "hung"), "lay": ("lays", "laid", "laid"),
    "shop": ("shops", "shopped", "shopped"),
}


def tag(label: str) -> GrammarTag:
    return GrammarTag(label=label, category=TAG_KEYWORDS[label])


def _verb_infinitive(target: str) -> str:
    return VERB_ALIASES.get(target, target)


def _separable_prefix(infinitive: str) -> str | None:
    return SEPARABLE_VERBS.get(infinitive.removeprefix("sich "))


def _regular_present(infinitive: str) -> tuple[str, str, str, str, str, str]:
    prefix = _separable_prefix(infinitive)
    base = infinitive
    if prefix:
        base = infinitive[len(prefix):]
    stem = base[:-2] if base.endswith("en") else base[:-1]
    needs_e = stem.endswith(("d", "t", "chn", "ffn"))
    sibilant = stem.endswith(("s", "ß", "x", "z", "tz"))
    endings = (
        "e",
        "t" if sibilant else "est" if needs_e else "st",
        "et" if needs_e else "t",
        "en",
        "et" if needs_e else "t",
        "en",
    )
    forms = tuple(stem + ending for ending in endings)
    if prefix:
        forms = tuple(f"{form} {prefix}" for form in forms)
    return forms  # type: ignore[return-value]


def _present_forms(infinitive: str) -> tuple[str, str, str, str, str, str]:
    return IRREGULAR_PRESENT.get(infinitive, _regular_present(infinitive))


def _english_parts(meaning: str) -> tuple[str, str, str, str]:
    base = meaning.split(" / ", 1)[0].removeprefix("to ")
    if base in {"can", "may", "must", "should", "would like"}:
        return base, base, base, base
    first, separator, complement = base.partition(" ")
    irregular = ENGLISH_IRREGULAR.get(first)
    if irregular and separator:
        third, past, participle = tuple(
            f"{form} {complement}" for form in irregular
        )
        return base, third, past, participle
    third, past, participle = ENGLISH_IRREGULAR.get(
        base,
        (
            base + ("es" if base.endswith(("s", "sh", "ch", "x", "z", "o")) else "s"),
            base + ("d" if base.endswith("e") else "ed"),
            base + ("d" if base.endswith("e") else "ed"),
        ),
    )
    return base, third, past, participle


def _verb_help(target: str, meaning: str) -> VerbHelp:
    infinitive = _verb_infinitive(target)
    forms = _present_forms(infinitive)
    base, third, _, _ = _english_parts(meaning)
    english = tuple(
        f"{subject} {third if index == 2 else base}"
        for index, subject in enumerate(ENGLISH_SUBJECTS)
    )
    conjugations = [
        ConjugationForm(pronoun=pronoun, verb=form)
        for pronoun, form in zip(PRONOUNS, forms, strict=True)
    ]
    return VerbHelp(
        infinitive=infinitive,
        english=meaning if meaning.startswith("to ") else meaning,
        tense="Präsens (present)",
        forms=conjugations,
        present_forms=conjugations,
        present_english_forms=list(english),
        current_english_forms=list(english),
        usage=(
            f"The sentence uses a form of {infinitive}. The table shows the "
            "simple present forms used for present actions and routines."
        ),
    )


PAST_FORMS: dict[str, tuple[str, str, str, str, str, str]] = {
    "sein": ("war", "warst", "war", "waren", "wart", "waren"),
    "haben": ("hatte", "hattest", "hatte", "hatten", "hattet", "hatten"),
    "können": ("konnte", "konntest", "konnte", "konnten", "konntet", "konnten"),
    "müssen": ("musste", "musstest", "musste", "mussten", "musstet", "mussten"),
    "sollen": ("sollte", "solltest", "sollte", "sollten", "solltet", "sollten"),
    "wollen": ("wollte", "wolltest", "wollte", "wollten", "wolltet", "wollten"),
    "bitten": ("bat", "batest", "bat", "baten", "batet", "baten"),
}
PAST_SURFACES = {
    form.casefold()
    for forms in PAST_FORMS.values()
    for form in forms
} | {"brauchte", "funktionierte"}
PARTICIPLE_SURFACES = {
    "abgegeben", "angekommen", "aufgestanden", "angerufen", "ausgepackt",
    "beeilt", "bestanden", "bestellt", "besucht", "eingekauft", "eingezogen",
    "erledigt", "erleichtert", "erreicht", "ferngesehen", "gefahren", "gefehlt",
    "gefunden", "gegangen", "gegeben", "geholfen", "gehängt", "gehört", "gekocht",
    "gekümmert", "gelebt", "gelegt", "gelesen", "geliefert", "gemacht", "gemeldet",
    "gesagt", "geschafft", "geschrieben", "gespeichert", "gestellt", "getragen",
    "gewartet", "gezeigt", "geärgert", "reserviert", "stattgefunden", "teilgenommen",
    "untersucht", "verbessert", "verloren", "verschoben", "vorbereitet", "vorgestellt",
    "wehgetan", "zurückbekommen", "zurückgegangen", "übernachtet",
}
SEIN_PERFECT = {"ankommen", "aufstehen", "einziehen", "fahren", "gehen", "zurückgehen"}
STATE_PARTICIPLES = {"geschützt", "organisiert"}


def _past_forms(infinitive: str) -> tuple[str, str, str, str, str, str]:
    if infinitive in PAST_FORMS:
        return PAST_FORMS[infinitive]
    stem = infinitive[:-2] if infinitive.endswith("en") else infinitive[:-1]
    return tuple(stem + ending for ending in ("te", "test", "te", "ten", "tet", "ten"))  # type: ignore[return-value]


def _english_rows(meaning: str, tense: str, *, auxiliary: str = "have") -> list[str]:
    base, third, past, participle = _english_parts(meaning)
    if tense == "present":
        if base == "be" or base.startswith("be "):
            complement = base[2:].strip()
            verbs = [
                f"{verb}{f' {complement}' if complement else ''}"
                for verb in ("am", "are", "is", "are", "are", "are")
            ]
        else:
            verbs = [base, base, third, base, base, base]
    elif tense == "perfect":
        verbs = [f"{('has' if index == 2 else auxiliary)} {participle}" for index in range(6)]
    elif tense == "conditional":
        verbs = [f"would {base}"] * 6
    else:
        verbs = [past] * 6
    return [f"{subject} {verb}" for subject, verb in zip(ENGLISH_SUBJECTS, verbs, strict=True)]


def _used_as_participle(sentence: str, word_index: int) -> bool:
    tokens = [token.casefold() for token in WORD_RE.findall(sentence)]
    auxiliaries = {"bin", "bist", "ist", "sind", "seid", "habe", "hast", "hat", "haben", "habt", "hatte", "hatten"}
    before = tokens[max(0, word_index - 8) : word_index]
    after = tokens[word_index + 1 : word_index + 4]
    return bool(auxiliaries.intersection(before) or auxiliaries.intersection(after))


def _used_as_imperative(sentence: str, surface: str, word_index: int) -> bool:
    key = surface.casefold()
    if key not in IMPERATIVE_SURFACES:
        return False
    tokens = WORD_RE.findall(sentence)
    first = tokens[0].casefold() if tokens else ""
    return bool(
        word_index == 0
        or first in IMPERATIVE_SURFACES
        or surface[:1].isupper()
        or re.search(rf"\bBitte\s+{re.escape(surface)}\b", sentence)
    )


def _used_as_infinitive(sentence: str, surface: str, word_index: int) -> bool:
    key = surface.casefold()
    finite_modals = {
        "kann", "kannst", "könnt", "darf", "darfst", "dürft", "möchte",
        "möchtest", "muss", "musst", "müsst", "soll", "sollst", "sollte",
        "will", "willst", "wollte", "würde",
    }
    if key in finite_modals:
        return False
    if key in {"anzukommen", "aufzupassen", "weiterzulernen"}:
        return True
    matches = list(WORD_RE.finditer(sentence))
    tokens = [match.group().casefold() for match in matches]
    if word_index > 0 and tokens[word_index - 1] in COORDINATING_CONNECTORS:
        if word_index < 2:
            return False
        coordinated_left = tokens[word_index - 2]
        if not coordinated_left.endswith(("en", "ern", "eln")):
            return False
        return _used_as_infinitive(
            sentence, matches[word_index - 2].group(), word_index - 2
        )
    previous: list[str] = []
    for index in range(word_index - 1, -1, -1):
        if tokens[index] in COORDINATING_CONNECTORS:
            break
        gap = sentence[matches[index].end() : matches[index + 1].start()]
        if re.search(r"[,;:.!?]", gap):
            break
        previous.insert(0, tokens[index])
    following: list[str] = []
    for index in range(word_index + 1, len(matches)):
        if tokens[index] in COORDINATING_CONNECTORS:
            break
        gap = sentence[matches[index - 1].end() : matches[index].start()]
        if re.search(r"[,;:.!?]", gap):
            break
        following.append(tokens[index])
    modals = {
        "kann", "kannst", "können", "könnt", "darf", "dürfen", "möchte",
        "möchten", "muss", "musst", "müssen", "soll", "sollen", "sollte",
        "will", "wollen", "wollte", "würde",
    }
    return bool(
        (previous and previous[-1] == "zu")
        or modals.intersection(previous)
        or modals.intersection(following)
    )


def _contextual_verb_help(
    target: str,
    meaning: str,
    surface: str,
    sentence: str,
    word_index: int,
) -> tuple[VerbHelp, str, list[GrammarTag]]:
    infinitive = _verb_infinitive(target)
    present = _present_forms(infinitive)
    reflexive = target.startswith("sich ")
    if reflexive:
        prefix = _separable_prefix(infinitive)
        reflexive_pronouns = ("mich", "dich", "sich", "uns", "euch", "sich")
        if prefix:
            present = tuple(
                f"{form.removesuffix(f' {prefix}')} {pronoun} {prefix}"
                for form, pronoun in zip(present, reflexive_pronouns, strict=True)
            )  # type: ignore[assignment]
        else:
            present = tuple(
                f"{form} {pronoun}"
                for form, pronoun in zip(present, reflexive_pronouns, strict=True)
            )  # type: ignore[assignment]
    present_rows = [ConjugationForm(pronoun=p, verb=f) for p, f in zip(PRONOUNS, present, strict=True)]
    present_english = _english_rows(meaning, "present")
    key = surface.casefold()
    base, _, past, participle = _english_parts(meaning)

    if key in STATE_PARTICIPLES:
        forms = tuple(f"{aux} {key}" for aux in _present_forms("sein"))
        english = [
            f"{subject} {verb} {participle}"
            for subject, verb in zip(
                ENGLISH_SUBJECTS, ("am", "are", "is", "are", "are", "are"), strict=True
            )
        ]
        tense = "Partizip II as a state/passive description"
        item_meaning = participle
        tense_tags = [tag("verb"), tag("past participle")]
        usage = f"The participle {surface} combines with sein here to describe a resulting state or passive condition."
    elif key == "verschoben" and re.search(r"\b(musste|müssen)\b", sentence, re.I):
        forms = tuple(f"{modal} {key} werden" for modal in _past_forms("müssen"))
        english = [f"{subject} had to be postponed" for subject in ENGLISH_SUBJECTS]
        tense = "Präteritum modal + passive infinitive"
        item_meaning = "be postponed"
        tense_tags = [tag("verb"), tag("past participle"), tag("simple past")]
        usage = "The participle appears with werden after the past modal musste, forming a passive construction."
    elif key in PARTICIPLE_SURFACES and _used_as_participle(sentence, word_index):
        auxiliary = "sein" if infinitive in SEIN_PERFECT else "haben"
        if reflexive:
            forms = tuple(
                f"{aux} {pronoun} {key}"
                for aux, pronoun in zip(
                    _present_forms(auxiliary),
                    ("mich", "dich", "sich", "uns", "euch", "sich"),
                    strict=True,
                )
            )
        else:
            forms = tuple(f"{aux} {key}" for aux in _present_forms(auxiliary))
        english = _english_rows(meaning, "perfect")
        if re.search(r"\bhatte\b", sentence, re.I):
            forms = tuple(f"{aux} {key}" for aux in _past_forms(auxiliary))
            english = [f"{subject} had {participle}" for subject in ENGLISH_SUBJECTS]
            tense = "Plusquamperfekt (past perfect)"
            tense_tags = [tag("verb"), tag("past participle"), tag("pluperfect")]
            usage = f"{surface} is the past participle of {infinitive}; hatte + participle marks an event completed before another past point."
        else:
            tense = "Perfekt (conversational past)"
            tense_tags = [tag("verb"), tag("past participle"), tag("perfect")]
            usage = f"{surface} is the past participle of {infinitive}; it combines with {auxiliary} to form the conversational past."
        item_meaning = participle
    elif key in PAST_SURFACES:
        forms = _past_forms(infinitive)
        english = _english_rows(meaning, "past")
        tense = "Präteritum (simple past)"
        item_meaning = past
        tense_tags = [tag("verb"), tag("simple past")]
        usage = "This is a simple-past form. In speech it is especially common with sein, haben, and modal verbs."
    elif key in {"würde", "wäre"} or key.startswith("könnt"):
        forms = (
            ("würde", "würdest", "würde", "würden", "würdet", "würden")
            if infinitive == "werden"
            else ("wäre", "wärst", "wäre", "wären", "wärt", "wären")
            if infinitive == "sein"
            else _present_forms(infinitive)
        )
        english = _english_rows(meaning, "conditional")
        tense = "Konjunktiv II (polite/conditional)"
        item_meaning = f"would {base}"
        tense_tags = [tag("verb"), tag("subjunctive")]
        usage = "This form makes a request or possibility polite or hypothetical."
    elif _used_as_imperative(sentence, surface, word_index):
        forms = (present[1], present[4], f"{present[5]} Sie")
        english = (f"you {base}", f"you all {base}", f"you {base} (formal)")
        tense = "Imperativ (command/request)"
        item_meaning = base
        tense_tags = [tag("verb"), tag("imperative")]
        usage = "The sentence uses a command or instruction; the rows show du, ihr, and formal Sie."
    elif _used_as_infinitive(sentence, surface, word_index):
        forms = (surface.casefold(),)
        english = (f"to {base.removeprefix('to ')}",)
        tense = "Infinitiv (infinitive in this construction)"
        item_meaning = base
        tense_tags = [tag("verb"), tag("infinitive")]
        usage = "This non-finite form follows a modal verb or zu, so it does not change for person in this sentence."
    else:
        forms = present
        english = present_english
        tense = "Präsens (present)"
        item_meaning = base
        tense_tags = [tag("verb"), tag("present")]
        usage = "The sentence uses the present tense for a current action, routine, plan, or general fact."

    pronouns = (
        PRONOUNS
        if len(forms) == 6
        else ("du", "ihr", "Sie")
        if len(forms) == 3
        else ("—",)
    )
    current_rows = [ConjugationForm(pronoun=p, verb=f) for p, f in zip(pronouns, forms, strict=True)]
    return (
        VerbHelp(
            infinitive=target,
            english=meaning,
            tense=tense,
            forms=current_rows,
            present_forms=present_rows,
            present_english_forms=present_english,
            current_english_forms=list(english),
            usage=usage,
        ),
        item_meaning,
        tense_tags,
    )


def _is_verb_target(target: str, meaning: str) -> bool:
    return meaning.startswith("to ") or target in {
        "möchten", "können", "dürfen", "müssen", "wollen", "sollen",
    }


def _noun_parts(target: str) -> tuple[str, str] | None:
    match = re.match(r"^(der|die|das)\s+(.+)$", target, flags=re.I)
    return (match.group(1).casefold(), match.group(2)) if match else None


def _surface_forms_for_target(target: str, meaning: str) -> set[str]:
    noun = _noun_parts(target)
    if noun:
        lemma = noun[1].casefold()
        stem = lemma[:-1] if lemma.endswith("e") else lemma
        return {lemma, *(stem + ending for ending in ("e", "en", "n", "er", "s", "es"))}
    if _is_verb_target(target, meaning):
        infinitive = _verb_infinitive(target)
        # A separable prefix is not itself a verb.  For "ruft ... an", for
        # example, only "ruft" should receive the verb card.
        forms = {form.split()[0] for form in _present_forms(infinitive)}
        stem = infinitive[:-2] if infinitive.endswith("en") else infinitive[:-1]
        forms.update({infinitive, f"ge{stem}t", f"ge{stem}en", f"zu{infinitive}"})
        prefix = _separable_prefix(infinitive)
        if prefix:
            base = infinitive[len(prefix):]
            base_stem = base[:-2] if base.endswith("en") else base[:-1]
            forms.update({f"{prefix}ge{base_stem}t", f"{prefix}ge{base_stem}en"})
        return {form.casefold() for form in forms}
    if " " not in target:
        base = target.casefold()
        return {base, *(base + ending for ending in ("e", "en", "em", "er", "es"))}
    return set()


TARGET_SURFACES: dict[str, list[str]] = {}
for _target, _meaning in TARGET_GLOSSES.items():
    for _surface in _surface_forms_for_target(_target, _meaning):
        TARGET_SURFACES.setdefault(_surface, []).append(_target)

SURFACE_OVERRIDES = {
    "bin": "sein", "bist": "sein", "ist": "sein", "sind": "sein", "seid": "sein",
    "war": "sein", "waren": "sein",
    "habe": "haben", "hast": "haben", "hat": "haben", "habt": "haben",
    "möchte": "möchten", "möchtest": "möchten", "möchten": "möchten", "mag": "mögen",
    "kann": "können", "kannst": "können", "könnt": "können", "könnten": "können",
    "darf": "dürfen", "darfst": "dürfen", "dürft": "dürfen",
    "muss": "müssen", "musst": "müssen", "müsst": "müssen",
    "will": "wollen", "willst": "wollen", "wollt": "wollen",
    "soll": "sollen", "sollst": "sollen", "sollt": "sollen",
    "spricht": "sprechen", "isst": "essen", "fährt": "fahren", "trägt": "tragen",
    "tut": "wehtun", "schläft": "schlafen", "liest": "lesen", "hilft": "helfen",
    "nimmt": "nehmen", "fängt": "anfangen", "trifft": "sich treffen", "gebt": "geben",
    "empfiehlt": "empfehlen", "wirft": "werfen", "bäckt": "backen",
    "denkt": "denken", "bittet": "bitten", "gibt": "geben", "sieht": "sehen",
    "steht": "stehen", "liegt": "liegen", "bleibt": "bleiben", "bringt": "bringen",
    "schreibt": "schreiben", "findet": "finden",
    "abgegeben": "abgeben", "abheben": "abheben", "antwortet": "antworten",
    "anzukommen": "ankommen", "aufgestanden": "aufstehen", "aufzupassen": "aufpassen",
    "ausruht": "sich ausruhen", "bat": "bitten", "bekomme": "bekommen",
    "bekommen": "bekommen", "bekommt": "bekommen", "bestanden": "bestehen",
    "brauche": "brauchen", "braucht": "brauchen", "brauchte": "brauchen",
    "bring": "bringen", "eingezogen": "einziehen", "erledigt": "erledigen",
    "erzählt": "erzählen", "fragt": "fragen", "freut": "freuen",
    "funktionierte": "funktionieren", "fällt": "fallen", "führt": "führen",
    "gebeten": "bitten", "gefunden": "finden", "gegangen": "gehen", "gegeben": "geben",
    "geholfen": "helfen", "gehören": "gehören", "gehört": "gehören", "gelebt": "leben",
    "gemeldet": "melden", "gesagt": "sagen", "geschrieben": "schreiben",
    "geschützt": "schützen", "gewartet": "warten", "gib": "geben", "halten": "halten",
    "hatte": "haben", "kennenlernen": "kennenlernen", "kleben": "kleben",
    "klingelt": "klingeln", "konnte": "können", "konnten": "können",
    "lassen": "lassen", "lässt": "lassen", "leben": "leben", "lebt": "leben",
    "lädt": "einladen", "lösen": "lösen", "markiert": "markieren",
    "mitnehmen": "mitnehmen", "musste": "müssen", "nennt": "nennen",
    "organisiert": "organisieren", "probiert": "probieren", "putzt": "putzen",
    "ruf": "anrufen", "sagt": "sagen", "schick": "schicken", "schlägt": "vorschlagen",
    "singen": "singen", "sollte": "sollen", "startet": "starten",
    "stattgefunden": "stattfinden", "stellt": "stellen", "sucht": "suchen",
    "teilgenommen": "teilnehmen", "verloren": "verlieren", "verschoben": "verschieben",
    "verschwinden": "verschwinden", "vorbereitet": "vorbereiten", "vorgestellt": "sich vorstellen",
    "gekümmert": "sich kümmern", "beeilt": "sich beeilen", "geärgert": "sich ärgern", "wehgetan": "wehtun",
    "weht": "wehen", "weiß": "wissen", "weiss": "wissen", "weiterzulernen": "lernen", "wird": "werden",
    "wissen": "wissen", "wollte": "wollen", "wäre": "sein", "wäscht": "waschen",
    "würde": "werden", "zurückbekommen": "zurückbekommen", "zurückgegangen": "zurückgehen",
    "übt": "üben",
}

EXTRA_VERBS = {
    "sein": "to be", "haben": "to have", "werden": "to become", "mögen": "to like",
    "geben": "to give", "sehen": "to see", "stehen": "to stand",
    "liegen": "to lie / be located", "bleiben": "to stay", "bringen": "to bring",
    "schreiben": "to write", "fragen": "to ask", "antworten": "to answer",
    "freuen": "to please / make glad",
    "hören": "to hear / listen", "füllen": "to fill", "verlassen": "to leave", "sagen": "to say",
    "abgeben": "to hand in", "abheben": "to withdraw", "ankommen": "to arrive",
    "aufpassen": "to pay attention", "bekommen": "to receive / get", "erledigen": "to complete",
    "erleichtern": "to make easier", "erzählen": "to tell", "fallen": "to fall",
    "führen": "to lead", "gehören": "to belong", "leben": "to live",
    "schützen": "to protect", "kennenlernen": "to get to know", "kleben": "to stick",
    "klingeln": "to ring", "lassen": "to let / leave", "lösen": "to solve",
    "markieren": "to mark", "mitnehmen": "to take along", "nennen": "to name / call",
    "organisieren": "to organize", "probieren": "to try", "putzen": "to clean",
    "schlagen": "to hit", "vorschlagen": "to suggest", "singen": "to sing", "starten": "to start",
    "suchen": "to look for", "verschwinden": "to disappear", "vorbereiten": "to prepare",
    "lernen": "to learn", "wehen": "to blow", "wissen": "to know", "zurückbekommen": "to get back",
    "zurückgehen": "to go back", "üben": "to practice",
}

# Common nouns that occur as supporting vocabulary rather than deliberate
# lesson targets.  Keeping them controlled prevents capitalization from being
# mistaken for a proper name and preserves the dictionary article.
NOUN_GLOSSES: dict[str, tuple[str, str, str, bool]] = {
    "abendessen": ("das Abendessen", "dinner / evening meal", "neuter", False),
    "abteilungsleiter": ("der Abteilungsleiter", "department manager", "masc.", False),
    "adresse": ("die Adresse", "address", "fem.", False),
    "alltag": ("der Alltag", "everyday life", "masc.", False),
    "angaben": ("die Angabe", "details / information", "fem.", True),
    "apothekerin": ("die Apothekerin", "pharmacist", "fem.", False),
    "arbeitstag": ("der Arbeitstag", "working day", "masc.", False),
    "arzttermin": ("der Arzttermin", "doctor's appointment", "masc.", False),
    "autorin": ("die Autorin", "female author", "fem.", False),
    "bankkarte": ("die Bankkarte", "bank card", "fem.", False),
    "besprechung": ("die Besprechung", "meeting", "fem.", False),
    "bewohner": ("der Bewohner", "resident", "masc.", False),
    "bild": ("das Bild", "picture", "neuter", False),
    "busse": ("der Bus", "buses", "masc.", True),
    "bäckerei": ("die Bäckerei", "bakery", "fem.", False),
    "bühne": ("die Bühne", "stage", "fem.", False),
    "café": ("das Café", "café", "neuter", False),
    "container": ("der Container", "container", "masc.", False),
    "damen": ("die Dame", "ladies", "fem.", True),
    "deutschkurs": ("der Deutschkurs", "German course", "masc.", False),
    "deutschprüfung": ("die Deutschprüfung", "German exam", "fem.", False),
    "dienst": ("der Dienst", "service", "masc.", False),
    "dienste": ("der Dienst", "services", "masc.", True),
    "dienstagnachmittag": ("der Dienstagnachmittag", "Tuesday afternoon", "masc.", False),
    "dienstagvormittag": ("der Dienstagvormittag", "Tuesday morning", "masc.", False),
    "donnerstag": ("der Donnerstag", "Thursday", "masc.", False),
    "empfang": ("der Empfang", "receipt / reception", "masc.", False),
    "ergebnisse": ("das Ergebnis", "results", "neuter", True),
    "fahrgäste": ("der Fahrgast", "passengers", "masc.", True),
    "fahrrad": ("das Fahrrad", "bicycle", "neuter", False),
    "freitag": ("der Freitag", "Friday", "masc.", False),
    "freunde": ("der Freund", "friends", "masc.", True),
    "freunden": ("der Freund", "friends", "masc.", True),
    "fussball": ("der Fußball", "football / soccer", "masc.", False),
    "getränke": ("das Getränk", "drinks", "neuter", True),
    "getränken": ("das Getränk", "drinks", "neuter", True),
    "glascontainer": ("der Glascontainer", "glass-recycling container", "masc.", False),
    "gläser": ("das Glas", "glasses / jars", "neuter", True),
    "glück": ("das Glück", "luck", "neuter", False),
    "grammatik": ("die Grammatik", "grammar", "fem.", False),
    "grüsse": ("der Gruß", "greetings", "masc.", True),
    "gäste": ("der Gast", "guests", "masc.", True),
    "hauptstrasse": ("die Hauptstraße", "main street", "fem.", False),
    "heizung": ("die Heizung", "heating", "fem.", False),
    "herd": ("der Herd", "stove", "masc.", False),
    "herren": ("der Herr", "gentlemen", "masc.", True),
    "hilfe": ("die Hilfe", "help", "fem.", False),
    "hunger": ("der Hunger", "hunger", "masc.", False),
    "informationsschalter": ("der Informationsschalter", "information desk", "masc.", False),
    "inhalt": ("der Inhalt", "content", "masc.", False),
    "internet": ("das Internet", "internet", "neuter", False),
    "internetseite": ("die Internetseite", "website", "fem.", False),
    "kino": ("das Kino", "cinema", "neuter", False),
    "kisten": ("die Kiste", "boxes", "fem.", True),
    "kleidung": ("die Kleidung", "clothing", "fem.", False),
    "komödie": ("die Komödie", "comedy", "fem.", False),
    "krimi": ("der Krimi", "crime novel / thriller", "masc.", False),
    "kundin": ("die Kundin", "female customer", "fem.", False),
    "lampe": ("die Lampe", "lamp", "fem.", False),
    "land": ("das Land", "country / countryside", "neuter", False),
    "lernenden": ("der Lernende", "learners", "masc.", True),
    "lesung": ("die Lesung", "reading", "fem.", False),
    "lieferung": ("die Lieferung", "delivery", "fem.", False),
    "liste": ("die Liste", "list", "fem.", False),
    "mann": ("der Mann", "man", "masc.", False),
    "menschen": ("der Mensch", "people", "masc.", True),
    "menü": ("das Menü", "menu", "neuter", False),
    "minuten": ("die Minute", "minutes", "fem.", True),
    "mitarbeiter": ("der Mitarbeiter", "employee", "masc.", False),
    "mitarbeiterin": ("die Mitarbeiterin", "female employee", "fem.", False),
    "montag": ("der Montag", "Monday", "masc.", False),
    "musik": ("die Musik", "music", "fem.", False),
    "musikfestival": ("das Musikfestival", "music festival", "neuter", False),
    "nachmittag": ("der Nachmittag", "afternoon", "masc.", False),
    "namen": ("der Name", "names", "masc.", True),
    "nummer": ("die Nummer", "number", "fem.", False),
    "nähe": ("die Nähe", "vicinity / nearby area", "fem.", False),
    "oktober": ("der Oktober", "October", "masc.", False),
    "papiercontainer": ("der Papiercontainer", "paper-recycling container", "masc.", False),
    "park": ("der Park", "park", "masc.", False),
    "parkplatz": ("der Parkplatz", "parking space", "masc.", False),
    "plätze": ("der Platz", "places / spaces", "masc.", True),
    "rad": ("das Rad", "bicycle", "neuter", False),
    "restaurant": ("das Restaurant", "restaurant", "neuter", False),
    "räume": ("der Raum", "rooms", "masc.", True),
    "rückseite": ("die Rückseite", "back / reverse side", "fem.", False),
    "rückweg": ("der Rückweg", "way back", "masc.", False),
    "schlaf": ("der Schlaf", "sleep", "masc.", False),
    "schluss": ("der Schluss", "end", "masc.", False),
    "schlüssel": ("der Schlüssel", "key", "masc.", False),
    "sonntag": ("der Sonntag", "Sunday", "masc.", False),
    "sonntagabend": ("der Sonntagabend", "Sunday evening", "masc.", False),
    "stadtpark": ("der Stadtpark", "city park", "masc.", False),
    "stand": ("der Stand", "stall / stand", "masc.", False),
    "stunde": ("die Stunde", "hour", "fem.", False),
    "stunden": ("die Stunde", "hours", "fem.", True),
    "stücke": ("das Stück", "pieces", "neuter", True),
    "supermarkt": ("der Supermarkt", "supermarket", "masc.", False),
    "suppe": ("die Suppe", "soup", "fem.", False),
    "sängerin": ("die Sängerin", "female singer", "fem.", False),
    "tablette": ("die Tablette", "tablet / pill", "fem.", False),
    "tag": ("der Tag", "day", "masc.", False),
    "tage": ("der Tag", "days", "masc.", True),
    "tagen": ("der Tag", "days", "masc.", True),
    "techniker": ("der Techniker", "technician", "masc.", False),
    "tonne": ("die Tonne", "bin", "fem.", False),
    "umschlag": ("der Umschlag", "envelope", "masc.", False),
    "umzug": ("der Umzug", "move / relocation", "masc.", False),
    "unterricht": ("der Unterricht", "class / instruction", "masc.", False),
    "verkäufer": ("der Verkäufer", "salesman", "masc.", False),
    "verkäuferin": ("die Verkäuferin", "saleswoman", "fem.", False),
    "verlust": ("der Verlust", "loss", "masc.", False),
    "versicherung": ("die Versicherung", "insurance company / insurance", "fem.", False),
    "viertel": ("das Viertel", "neighborhood", "neuter", False),
    "vormittag": ("der Vormittag", "morning", "masc.", False),
    "woche": ("die Woche", "week", "fem.", False),
    "wohnzimmer": ("das Wohnzimmer", "living room", "neuter", False),
    "wörtern": ("das Wort", "words", "neuter", True),
    "zahl": ("die Zahl", "number", "fem.", False),
    "zeit": ("die Zeit", "time", "fem.", False),
    "äpfel": ("der Apfel", "apples", "masc.", True),
}

# Carefully authored meaning chunks for lessons whose useful constructions do
# not fall on comma boundaries.  These are deliberately larger than a bare
# article+noun pair, so they explain structure rather than repeat a word card.
CURATED_PHRASES: dict[str, str] = {
    "sehen Sie den Bahnhof": "you will see the station",
    "Heute Morgen": "this morning",
    "hilft sofort": "helps right away",
    "eine Stunde später treffen": "meet one hour later",
    "ruft Leo später an": "calls Leo later",
    "öffnen automatisch": "open automatically",
    "spät aufgestanden": "got up late",
    "auf den nächsten Bus gewartet": "waited for the next bus",
    "eine interessante Stelle": "an interesting position",
    "zu ihrer Erfahrung passen": "fit her experience",
    "an ihrem ersten Arbeitstag": "on her first day at work",
    "an ihrer ersten Besprechung teilgenommen": "took part in her first meeting",
    "die Wohnung noch frei ist": "the apartment is still available",
    "einen Termin um siebzehn Uhr": "an appointment at five o'clock",
    "vereinbaren einen Termin": "arrange an appointment",
    "sich nicht weiter beschweren": "no longer complain",
    "hat wieder Ruhe": "has peace and quiet again",
    "gesünder leben": "live a healthier life",
    "sehr erleichtert": "very relieved",
    "alles zurückbekommen": "got everything back",
    "möchte die Lampe deshalb zurückgeben": "would therefore like to return the lamp",
    "deshalb zurückgeben": "return it for that reason",
    "bestätigen Sie mir schriftlich": "confirm to me in writing",
    "wohin ich das Paket schicken soll": "where I should send the parcel",
    "bestätigt den Termin": "confirms the appointment",
    "kann den Drucker am Telefon nicht reparieren": "cannot repair the printer over the phone",
    "kommt deshalb morgen": "is therefore coming tomorrow",
    "einen Termin beim Vermieter vereinbaren": "arrange an appointment with the landlord",
    "schlägt Dienstagvormittag vor": "suggests Tuesday morning",
    "Öffnen Sie dann die Datei": "then open the file",
    "die Sie drucken möchten": "that you want to print",
    "melden Sie sich deshalb vorher auf unserer Internetseite an": "therefore register in advance on our website",
    "lange draußen bleibt": "stays outside for a long time",
    "das Konzert einer berühmten Sängerin": "a famous singer's concert",
    "dort das Konzert einer berühmten Sängerin gehört": "listened to a famous singer's concert there",
    "eine Ausstellung im Museum": "an exhibition at the museum",
    "schicken Sie mir": "send me",
    "möchte ich einen Teil meines Geldes zurück": "I would like part of my money back",
    "schicke Ihnen die Rechnung mit": "am including the bill",
    "es geschafft": "managed it",
    "pünktlich anzukommen": "to arrive on time",
    "in kleine Stücke": "into small pieces",
    "in einen großen Topf": "into a large pot",
    "am Morgen beeilt": "hurried in the morning",
    "auf einem anderen Bahnsteig umsteigen": "change trains on another platform",
    "einen kurzen Artikel": "a short article",
    "seine Antwort kurz begründen": "briefly justify their answer",
    "einen Ausflug zu einem See": "a trip to a lake",
    "durch einen Wald": "through a forest",
    "in den Glascontainer": "in the glass container",
    "den Platz um die Container": "the area around the containers",
    "mit Freunden zu chatten": "to chat with friends",
    "beim Lesen weniger zu benutzen": "to use less while reading",
    "ein Formular ausfüllen": "fill in a form",
    "die Kosten für die Reparatur": "the repair costs",
    "sich zuerst in eine Liste eintragen": "first enter your name on a list",
    "das Formular unterschreiben": "sign the form",
    "in ihre neue Wohnung eingezogen": "moved into her new apartment",
    "in den Schrank gelegt": "put in the wardrobe",
    "in einem Reisebüro beraten": "get advice at a travel agency",
    "eine günstige Unterkunft": "inexpensive accommodation",
    "eine gute Note bekommen": "received a good grade",
    "besser als beim Schreiben": "better than in writing",
    "besonders schön": "especially nice",
    "Erst danach": "only then",
    "die Aufgabe beenden": "finish the task",
    "was ein neues Wort bedeutet": "what a new word means",
    "über eine alte Brücke": "over an old bridge",
    "Mina und Leo diskutieren": "Mina and Leo discuss",
    "welchen Film sie gemeinsam sehen möchten": "which film they want to watch together",
    "Antwort der Versicherung": "the insurance company's response",
    "spricht Mina einen Buchstaben noch nicht richtig aus": "Mina still does not pronounce one letter correctly",
    "die Sprache besser zu benutzen": "to use the language better",
    "möchte weiter regelmäßig hören": "wants to continue listening regularly",
    "sprechen, lesen und schreiben": "speaking, reading, and writing",
}
IMPERATIVE_SURFACES = {
    "beachten", "bratet", "bring", "drücken", "füllen", "gebt", "gehen",
    "gib", "halten", "informieren", "kaufen", "kleben", "kocht", "melden",
    "nehmen", "öffnen", "prüfen", "ruf", "schick", "schicken", "schneidet", "schreiben",
    "tragen", "vergessen", "werfen", "wählen", "zeigen",
}
CAPITALIZED_NOUNS = {
    "essen": ("das Essen", "food / meal", "neuter"),
    "kosten": ("die Kosten", "costs", "plural"),
    "leben": ("das Leben", "life", "neuter"),
    "lesen": ("das Lesen", "reading", "neuter"),
    "reise": ("die Reise", "trip / journey", "fem."),
    "reisen": ("das Reisen", "travel", "neuter"),
    "ruhe": ("die Ruhe", "rest / quiet", "fem."),
    "schreiben": ("das Schreiben", "writing", "neuter"),
    "sprechen": ("das Sprechen", "speaking", "neuter"),
    "antworten": ("die Antworten", "answers", "plural"),
    "treffen": ("das Treffen", "meeting", "neuter"),
    "üben": ("das Üben", "practice", "neuter"),
    "wiedersehen": ("das Wiedersehen", "seeing one another again", "neuter"),
    "zahlen": ("die Zahlen", "numbers", "plural"),
}
CONTRACTION_MEANINGS = {
    "am": "at/on the", "ans": "to the", "aufs": "onto the",
    "beim": "at/while", "durchs": "through the", "fürs": "for the",
    "im": "in the", "ins": "into the", "ums": "around the",
    "vom": "from the", "zum": "to the", "zur": "to the",
}
CONTRACTION_BASES = {
    "am": ("an", "at / on", "dative"),
    "ans": ("an", "at / on", "accusative"),
    "aufs": ("auf", "on / onto", "accusative"),
    "beim": ("bei", "at / with", "dative"),
    "durchs": ("durch", "through", "accusative"),
    "fürs": ("für", "for", "accusative"),
    "im": ("in", "in / into", "dative"),
    "ins": ("in", "in / into", "accusative"),
    "ums": ("um", "around", "accusative"),
    "vom": ("von", "from / of", "dative"),
    "zum": ("zu", "to", "dative"),
    "zur": ("zu", "to", "dative"),
}
CONTRACTION_PHRASE_MEANINGS = {
    "am abend": "in the evening", "am arbeitsplatz": "at the workplace",
    "am computer": "at the computer", "am dienstag": "on Tuesday",
    "am dienstagnachmittag": "on Tuesday afternoon", "am donnerstag": "on Thursday",
    "am ende": "at the end", "am fenster": "by the window",
    "am freitag": "on Friday", "am informationsschalter": "at the information desk",
    "am montag": "on Monday", "am morgen": "in the morning",
    "am nächsten morgen": "the next morning", "am nächsten tag": "the next day",
    "am nachmittag": "in the afternoon", "am samstag": "on Saturday",
    "am schalter": "at the counter", "am sonntag": "on Sunday",
    "am sonntagabend": "on Sunday evening", "am tag": "during the day",
    "am telefon": "on the phone", "am vormittag": "in the morning",
    "am wochenende": "at the weekend", "beim arzt": "at the doctor's",
    "beim lesen": "while reading", "beim schlafen": "while sleeping",
    "beim schreiben": "in writing", "beim sprechen": "in speaking",
    "beim vermieter": "with the landlord", "beim üben": "while practicing",
    "im alltag": "in everyday life", "im bus": "on the bus",
    "im büro": "in the office", "im deutschkurs": "in German class",
    "im dritten stock": "on the third floor", "im fach": "in the subject",
    "im geschäft": "in the store", "im hotel": "in the hotel",
    "im internet": "online", "im kalender": "in the calendar",
    "im krankenhaus": "in the hospital", "im kurs": "in class",
    "im menü": "in the menu", "im museum": "in the museum",
    "im park": "in the park", "im restaurant": "in the restaurant",
    "im schrank": "in the wardrobe", "im stadtpark": "in the city park",
    "im supermarkt": "in the supermarket", "im viertel": "in the neighborhood",
    "im wörterbuch": "in the dictionary", "ins bett": "to bed",
    "ins kino": "to the cinema", "ins wohnzimmer": "into the living room",
    "vom bahnhof": "from the station", "vom fahrrad": "of the bicycle",
    "zum deutschkurs": "to German class", "zum glück": "fortunately",
    "zum nächsten geschäft": "to the next store", "zum schluss": "finally",
    "zur arbeit": "to work", "zur haltestelle": "to the bus stop",
}
NOUN_LABELS = {"noun", "compound noun", "proper noun", "masc.", "fem.", "neuter"}

PREPOSITIONS = {
    "an", "auf", "aus", "bei", "durch", "für", "gegen", "hinter", "in",
    "mit", "nach", "neben", "ohne", "per", "seit", "über", "um", "unter",
    "von", "vor", "wegen", "zwischen", "zu",
}
DETERMINERS = {
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen",
    "einem", "einer", "eines", "kein", "keine", "keinen", "keinem",
    "keiner", "mein", "meine", "meinen", "meinem", "meiner", "meines",
    "dein", "deine", "deinen", "deinem", "deiner", "deines", "sein",
    "seine", "seinen", "seinem", "seiner", "seines", "ihr", "ihre",
    "ihren", "ihrem", "ihrer", "ihres", "unser", "unsere", "unseren",
    "unserem", "unserer", "unseres", "dies", "diese", "dieser", "diesem",
    "diesen", "dieses", "jede", "jeder", "jedem", "jeden", "jedes",
    "alle", "allen", "anderer", "andere", "anderen", "einige", "einigen",
    "mehrere", "viel", "viele", "wenig", "wenige",
}
BARE_ARTICLES = {
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen",
    "einem", "einer", "eines",
}
NOUN_MODIFIERS = {
    "aktuelle", "aktuellen", "angegebene", "angegebenen", "begrenzte",
    "begrenzten", "bekannte", "bekannten", "blaue", "blauen", "deutsche",
    "deutschen", "dritten", "einfache", "einfachen", "einzelne", "einzelnen",
    "erste", "ersten", "fehlende", "fehlenden", "frische", "frischen",
    "ganze", "ganzen", "gemütliche", "gemütlichen", "große", "großen",
    "gesunde", "gesunden", "gesundes", "gute", "guten", "günstige",
    "günstigen", "helle", "hellen",
    "interessante", "interessanten", "klare", "klaren", "kleine", "kleinen",
    "kleines", "kurze", "kurzen", "laute", "lauten", "leere", "leeren",
    "letzte", "letzten", "lustige", "lustigen", "mehrere", "neue", "neuen",
    "neuer", "neues", "nächste", "nächsten", "ruhige", "ruhigen",
    "schwarze", "schwarzen", "schwarzes", "schwere", "schweren",
    "schwierige", "schwierigen", "schmutziges", "schriftliche",
    "schriftlichen", "starke", "starken", "starker", "technische",
    "technischen", "tägliche", "täglichen", "vegetarische",
    "vegetarischen", "vegetarisches", "warme", "warmen", "wichtige",
    "wichtigen", "wichtigste", "wichtigsten",
}
PLACE_GLOSSES = {
    "bonn": "Bonn", "deutschland": "Germany", "hamburg": "Hamburg",
    "köln": "Cologne", "madrid": "Madrid", "spanien": "Spain",
}
CONNECTOR_PAIRS = (
    ("und", "and"), ("aber", "but"), ("weil", "because"),
    ("denn", "because"), ("deshalb", "so"), ("dass", "that"),
    ("obwohl", "although"), ("ob", "whether"), ("sondern", "but"),
    ("oder", "or"), ("als", "when"), ("wenn", "if"),
)
ALIGNMENT_CONNECTOR_PAIRS = (
    *CONNECTOR_PAIRS,
    ("doch", "but"),
    ("statt", "instead of"),
)
INVERSION_OPENERS = {
    "abends", "außerdem", "besonders", "da", "damals", "danach", "dann",
    "darum", "darin", "deshalb", "dort", "draussen", "eigentlich", "erst",
    "gemeinsam", "gestern", "heute", "hier", "jeden", "jetzt", "leider",
    "morgen", "nun", "plötzlich", "später", "trotzdem", "vielleicht",
    "wahrscheinlich", "zuerst", "zurzeit",
}
COORDINATING_CONNECTORS = {"aber", "denn", "doch", "oder", "sondern", "und"}
FRONTED_SUBORDINATORS = {"als", "obwohl", "wenn"}
QUESTION_OPENERS = {"wann", "warum", "was", "wie", "wo", "woher", "wohin"}
FRONTED_FIELD_STARTS = {
    ("als", "kundin"),
    ("die", "bedeutung"),
    ("ein", "geschenk"),
    ("weitere", "informationen"),
}
NON_INVERSION_STARTS = {
    # This is a formal direction, not a declarative clause with a fronted field.
    ("dann", "gehen", "sie"),
}
NOUN_PHRASE_MEANINGS = {
    "den technischen dienst": "technical support",
    "der neue krimi": "the new crime film",
    "die ganze rechnung": "the entire invoice",
    "ein kleines brot": "a small piece of bread",
    "eine günstige unterkunft": "inexpensive accommodation",
    "einzelne stücke": "individual slices",
    "an der haltestelle": "at the bus stop",
    "an der hauptstraße": "on the main road",
    "an der nächsten haltestelle": "at the next bus stop",
    "an ihrem ersten arbeitstag": "on her first day at work",
    "an ihrer ersten besprechung": "in her first meeting",
    "an ihre heimat": "of her home country",
    "auf dem markt": "at the market",
    "auf dem paket": "on the parcel",
    "auf dem handy": "on their phone",
    "auf den nächsten bus": "for the next bus",
    "auf die antwort": "for the response",
    "auf samstag": "to Saturday",
    "bei der arbeit": "at work",
    "bei der post": "at the post office",
    "bei der polizei": "at the police station",
    "bei der lieferung": "when it was delivered",
    "bei einem brief": "for a letter",
    "bei ihrem neuen nachbarn": "at her new neighbor's door",
    "für das abendessen": "for dinner",
    "für die anmeldung": "to register",
    "für die feier": "for the party",
    "in das formular": "on the form",
    "in der bäckerei": "at the bakery",
    "in der mittagspause": "during the lunch break",
    "in der schule": "at school",
    "in die schule": "to school",
    "in der nähe": "nearby",
    "in die apotheke": "to the pharmacy",
    "in die praxis": "to the doctor's office",
    "in die stadt": "into town",
    "in eine liste": "on a list",
    "in einem kleinen haus": "in a small building",
    "in einem reisebüro": "at a travel agency",
    "in einer wichtigen rechnung": "in an important invoice",
    "mit dem bus": "by bus",
    "mit dem fahrrad": "by bicycle",
    "mit dem zug": "by train",
    "mit einem kollegen": "with a colleague",
    "mit einer bekannten autorin": "with a well-known author",
    "mit einer kurzen komödie": "to a short comedy",
    "nach der arbeit": "after work",
    "nach ihrem pass": "for her passport",
    "neben dem parkplatz": "next to the car park",
    "um auskunft": "for information",
    "um die getränke": "of the drinks",
    "über ihre erfahrung": "about her experience",
    "über reisen": "about travel",
    "von der krankenkasse": "from the health insurance provider",
    "von gleis": "from platform",
    "von ihrem konto": "from her account",
    "vor ihrer wohnung": "outside her apartment",
    "wegen einer veranstaltung": "because of an event",
    "seine täglichen wege": "his daily routes",
    "auf einem anderen bahnsteig": "on another platform",
    "auf dem land": "in the countryside",
    "zu hause": "at home",
    "zu ende": "over",
    "zu einem gespräch": "to a meeting",
    "zu ihrer erfahrung": "to her experience",
    "alle angaben": "all the details",
    "guten tag": "hello",
    "auf wiedersehen": "goodbye",
    "keinen ersatz": "no replacement ticket",
    "meine kleidung": "my clothes",
    "um hilfe": "for help",
    "viele grüße": "best wishes",
    "viele sehenswürdigkeiten": "many sights",
    "viel arbeit": "a lot of work",
    "viel regen": "a lot of rain",
    "viel wasser": "plenty of water",
    "wenig hunger": "little appetite",
}

POSSESSIVE_GLOSSES = {
    "mein": "my", "meine": "my", "meinen": "my", "meinem": "my",
    "meiner": "my", "meines": "my", "dein": "your", "deine": "your",
    "deinen": "your", "deinem": "your", "deiner": "your", "deines": "your",
    "sein": "his", "seine": "his", "seinen": "his", "seinem": "his",
    "seiner": "his", "seines": "his", "unser": "our", "unsere": "our",
    "unseren": "our", "unserem": "our", "unserer": "our", "unseres": "our",
}

PLURAL_ONLY_TARGETS = {"die Eltern"}
HOUR_VALUES = {
    "eins": 1, "zwei": 2, "drei": 3, "vier": 4, "fünf": 5, "sechs": 6,
    "sieben": 7, "acht": 8, "neun": 9, "zehn": 10, "elf": 11,
    "zwölf": 12, "dreizehn": 13, "vierzehn": 14, "fünfzehn": 15,
    "sechzehn": 16, "siebzehn": 17, "achtzehn": 18, "neunzehn": 19,
    "zwanzig": 20,
}
ENGLISH_HOURS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
    7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
    12: "twelve",
}


def _plain_gloss(item: BreakdownItem, surface: str, sentence_meaning: str) -> str:
    """Choose one contextual English option for a composed meaning chunk."""
    key = surface.casefold()
    if key in PLACE_GLOSSES:
        return PLACE_GLOSSES[key]
    if key in POSSESSIVE_GLOSSES:
        return POSSESSIVE_GLOSSES[key]
    if key in {"ihr", "ihre", "ihren", "ihrem", "ihrer", "ihres"}:
        return "your" if re.search(r"\byour\b", sentence_meaning, re.IGNORECASE) else "her"
    labels = {grammar_tag.label for grammar_tag in item.tags}
    if "proper noun" in labels and key.endswith("s"):
        # German names take a bare -s in the genitive; English uses an apostrophe.
        return f"{surface[:-1]}'s"
    options = [
        option.strip()
        for option in re.split(r"\s*/\s*|\s*;\s*", item.english)
        if option.strip()
    ]
    lowered_meaning = sentence_meaning.casefold()
    contextual_options: list[str] = []
    for option in options:
        contextual_options.append(option)
        if option.startswith(("male ", "female ")):
            contextual_options.append(option.split(" ", 1)[1])
        last_word = option.rsplit(" ", 1)[-1]
        if last_word.endswith("y"):
            plural = f"{last_word[:-1]}ies"
        elif last_word.endswith(("s", "x", "ch", "sh")):
            plural = f"{last_word}es"
        else:
            plural = f"{last_word}s"
        contextual_options.append(
            f"{option.rsplit(' ', 1)[0]} {plural}" if " " in option else plural
        )
        if option.startswith(("male ", "female ")):
            contextual_options.append(plural)
    for option in contextual_options:
        if re.search(rf"\b{re.escape(option.casefold())}\b", lowered_meaning):
            return option
    return options[0] if options else item.english


def _noun_phrase_meaning(
    surfaces: list[str],
    words: list[BreakdownItem],
    start: int,
    end: int,
    sentence_meaning: str,
) -> str:
    german_key = " ".join(surfaces[start : end + 1]).casefold()
    if german_key in NOUN_PHRASE_MEANINGS:
        return NOUN_PHRASE_MEANINGS[german_key]
    if surfaces[end].casefold() == "uhr":
        hour_values = [
            HOUR_VALUES.get(surface.casefold(), int(surface) if surface.isdigit() else None)
            for surface in surfaces[start:end]
        ]
        hour_values = [value for value in hour_values if value is not None]
        if hour_values:
            hour = hour_values[-1]
            spoken_hour = ENGLISH_HOURS[((hour - 1) % 12) + 1]
            lead = {
                "bis": "until", "gegen": "around", "um": "at", "vor": "before",
            }.get(surfaces[start].casefold(), "at")
            return f"{lead} {spoken_hour} o'clock"
    translated = [
        _plain_gloss(words[index], surfaces[index], sentence_meaning)
        for index in range(start, end + 1)
    ]
    for index, value in enumerate(translated[:-1]):
        if value in {"a", "a / an"}:
            translated[index] = (
                "an" if translated[index + 1][:1].lower() in "aeiou" else "a"
            )
    return " ".join(translated)


def _noun_phrases(
    surfaces: list[str],
    words: list[BreakdownItem],
    sentence_meaning: str,
    sentence_text: str,
) -> list[BreakdownItem]:
    """Build useful modified or prepositional noun chunks, never article+noun repeats."""
    phrases: list[BreakdownItem] = []
    source_matches = list(WORD_RE.finditer(sentence_text))
    for noun_index, item in enumerate(words):
        labels = {grammar_tag.label for grammar_tag in item.tags}
        if not labels & NOUN_LABELS:
            continue

        start = noun_index
        has_modifier = False
        seen_determiner = False
        while start > 0 and noun_index - start < 3:
            candidate = start - 1
            between = sentence_text[
                source_matches[candidate].end() : source_matches[start].start()
            ]
            if re.search(r"[,;:.!?„“\"]", between):
                break
            key = surfaces[candidate].casefold()
            candidate_labels = {tag_.label for tag_ in words[candidate].tags}
            if key in DETERMINERS or candidate_labels & {"numeral", "possessive"}:
                if (
                    key == "alle"
                    and candidate > 0
                    and any(
                        tag_.label == "verb" for tag_ in words[candidate - 1].tags
                    )
                ):
                    break
                if seen_determiner:
                    break
                seen_determiner = True
                start = candidate
                continue
            if key in NOUN_MODIFIERS or (
                surfaces[candidate][:1].isupper()
                and key.endswith("s")
                and "proper noun" in candidate_labels
            ):
                start = candidate
                has_modifier = True
                continue
            break

        # A modifier or a preposition makes the chunk useful. A bare
        # article+noun pair is still intentionally omitted.
        modifier_tokens = [surface.casefold() for surface in surfaces[start:noun_index]]
        if any(token not in BARE_ARTICLES for token in modifier_tokens):
            has_modifier = True
        if start > 0 and surfaces[start - 1].casefold() in PREPOSITIONS:
            start -= 1
            has_modifier = True
        if not has_modifier:
            continue

        german = " ".join(surfaces[start : noun_index + 1])
        english = _noun_phrase_meaning(
            surfaces, words, start, noun_index, sentence_meaning
        )
        phrases.append(BreakdownItem(german=german, english=english, kind="phrase"))
    return phrases


def _connector_phrases(
    text: str,
    meaning: str,
    surfaces: list[str],
    words: list[BreakdownItem],
) -> list[BreakdownItem]:
    """Align clauses joined by common German and English connectors."""
    phrases: list[BreakdownItem] = []
    for german_connector, english_connector in CONNECTOR_PAIRS:
        connector_indexes = [
            index
            for index, surface in enumerate(surfaces)
            if surface.casefold() == german_connector
        ]
        if len(connector_indexes) != 1:
            continue
        connector_index = connector_indexes[0]
        finite_verb_indexes = {
            index
            for index, word in enumerate(words)
            if any(tag_.label == "verb" for tag_ in word.tags)
            and not any(
                tag_.label in {"infinitive", "past participle"}
                for tag_ in word.tags
            )
        }
        if not (
            any(index < connector_index for index in finite_verb_indexes)
            and any(index > connector_index for index in finite_verb_indexes)
        ):
            continue
        de_parts = re.split(
            rf"\s*,?\s*\b{re.escape(german_connector)}\b\s+",
            text,
            flags=re.IGNORECASE,
        )
        en_parts = re.split(
            rf"\s*,?\s*\b{re.escape(english_connector)}\b\s+",
            meaning,
            flags=re.IGNORECASE,
        )
        if len(de_parts) != 2 or len(en_parts) != 2:
            continue
        pairs = (
            (de_parts[0], en_parts[0], "main clause"),
            (
                f"{german_connector} {de_parts[1]}",
                f"{english_connector} {en_parts[1]}",
                "subordinate clause"
                if german_connector in {"weil", "dass", "obwohl", "ob"}
                else "main clause",
            ),
        )
        for german, english, label in pairs:
            german = german.strip(" .!?„“\"")
            english = english.strip(" .!?“\"")
            if len(WORD_RE.findall(german)) >= 2:
                phrases.append(
                    BreakdownItem(
                        german=german,
                        english=english,
                        tags=[tag(label)],
                        kind="phrase",
                    )
                )
    return phrases


def _deduplicate_phrases(phrases: list[BreakdownItem]) -> list[BreakdownItem]:
    unique: list[BreakdownItem] = []
    seen: dict[str, BreakdownItem] = {}
    for phrase in phrases:
        original_tokens = WORD_RE.findall(phrase.german)
        if (
            len(original_tokens) == 2
            and original_tokens[0].casefold() in BARE_ARTICLES
            and original_tokens[1][:1].isupper()
        ):
            continue
        key = " ".join(token.casefold() for token in original_tokens)
        if key in seen:
            existing = seen[key]
            existing_labels = {tag_.label for tag_ in existing.tags}
            existing.tags.extend(
                tag_ for tag_ in phrase.tags if tag_.label not in existing_labels
            )
            continue
        seen[key] = phrase
        unique.append(phrase)
    return unique


def _is_finite_verb(item: BreakdownItem) -> bool:
    labels = {grammar_tag.label for grammar_tag in item.tags}
    return (
        "verb" in labels
        and "infinitive" not in labels
        and "past participle" not in labels
        and "imperative" not in labels
    )


def _inversion_sites(
    text: str,
    surfaces: list[str],
    words: list[BreakdownItem],
) -> dict[int, int]:
    """Map each inverted finite verb to its clause's fronted-field start."""
    matches = list(WORD_RE.finditer(text))
    keys = [surface.casefold() for surface in surfaces]
    finite_indexes = {
        index
        for index, item in enumerate(words)
        if _is_finite_verb(item)
        and surfaces[index].casefold() not in PARTICIPLE_SURFACES
    }
    if tuple(keys[:3]) in NON_INVERSION_STARTS:
        finite_indexes.discard(1)

    marked: dict[int, int] = {}
    possible_starts: list[tuple[int, bool, bool]] = []
    for index, key in enumerate(keys):
        is_opener = (
            key in INVERSION_OPENERS
            or key in PREPOSITIONS
            or key in CONTRACTION_MEANINGS
        )
        is_fronted_field = tuple(keys[index : index + 2]) in FRONTED_FIELD_STARTS
        is_question = key in QUESTION_OPENERS
        if not (is_opener or is_fronted_field or is_question):
            continue
        if index == 0:
            possible_starts.append((index, False, is_question))
            continue
        gap = text[matches[index - 1].end() : matches[index].start()]
        if re.search(r"[,;:]", gap) or keys[index - 1] in COORDINATING_CONNECTORS:
            possible_starts.append((index, True, is_question))

    for start, is_internal, is_question in possible_starts:
        for index in range(start + 1, len(words)):
            between = text[matches[start].end() : matches[index].start()]
            if re.search(r"[;:.!?]", between):
                break
            if index in finite_indexes:
                if (
                    is_internal or is_question
                ) and _subject_span_after_verb(surfaces, words, index) is None:
                    break
                marked.setdefault(index, start)
                break

    # A complete subordinate clause can occupy the first field. The following
    # main clause then begins with its finite verb before the subject.
    if keys and keys[0] in FRONTED_SUBORDINATORS:
        comma_index = text.find(",")
        if comma_index >= 0:
            for index in sorted(finite_indexes):
                if matches[index].start() > comma_index:
                    subject_span = _subject_span_after_verb(surfaces, words, index)
                    if subject_span is None:
                        break
                    subject_surface = surfaces[subject_span[0]]
                    if (
                        surfaces[index].casefold() in IMPERATIVE_SURFACES
                        and subject_surface == "Sie"
                    ):
                        break
                    marked.setdefault(index, 0)
                    break

    return marked


def _inversion_verb_indexes(
    text: str,
    surfaces: list[str],
    words: list[BreakdownItem],
) -> set[int]:
    """Find finite verbs placed before the subject after a fronted field."""
    return set(_inversion_sites(text, surfaces, words))


def _subject_span_after_verb(
    surfaces: list[str],
    words: list[BreakdownItem],
    verb_index: int,
) -> tuple[int, int] | None:
    start = verb_index + 1
    if start >= len(words):
        return None
    key = surfaces[start].casefold()
    labels = {grammar_tag.label for grammar_tag in words[start].tags}

    if key in {"alle", "beide", "jeder", "jemand", "man", "niemand"}:
        return start, start

    if key in DETERMINERS:
        for end in range(start + 1, min(start + 5, len(words))):
            end_labels = {tag_.label for tag_ in words[end].tags}
            if end_labels & NOUN_LABELS:
                return start, end
            if end_labels & {"verb", "conjunction"}:
                break
        return None

    if "proper noun" in labels:
        if (
            start + 2 < len(words)
            and surfaces[start + 1].casefold() == "und"
            and any(tag_.label == "proper noun" for tag_ in words[start + 2].tags)
        ):
            return start, start + 2
        if (
            start + 1 < len(words)
            and any(tag_.label in NOUN_LABELS for tag_ in words[start + 1].tags)
        ):
            return start, start + 1
        return start, start

    if key in {"ich", "du", "er", "sie", "es", "wir", "ihr"} or surfaces[start] == "Sie":
        return start, start

    if labels & NOUN_LABELS:
        return start, start
    return None


def _later_subject_span(
    surfaces: list[str],
    words: list[BreakdownItem],
    verb_index: int,
) -> tuple[int, int] | None:
    """Find a subject delayed by an adverb, object, or prepositional phrase."""
    cursor = verb_index + 1
    while cursor < len(words):
        key = surfaces[cursor].casefold()
        labels = {tag_.label for tag_ in words[cursor].tags}
        if labels & {"verb", "conjunction"}:
            return None
        if key in PREPOSITIONS or key in CONTRACTION_MEANINGS:
            cursor += 1
            while cursor < len(words):
                phrase_labels = {tag_.label for tag_ in words[cursor].tags}
                cursor += 1
                if phrase_labels & NOUN_LABELS:
                    break
                if phrase_labels & {"verb", "conjunction"}:
                    return None
            continue
        candidate = _subject_span_after_verb(surfaces, words, cursor - 1)
        if candidate is not None:
            return candidate
        cursor += 1
    return None


def _trimmed_segment_spans(value: str) -> list[tuple[int, int]]:
    """Return non-empty punctuation-delimited text spans."""
    spans: list[tuple[int, int]] = []
    start = 0
    for separator in re.finditer(r"[.!?,;:]", value):
        left, right = start, separator.start()
        while left < right and value[left].isspace():
            left += 1
        while right > left and value[right - 1].isspace():
            right -= 1
        if left < right:
            spans.append((left, right))
        start = separator.end()
    left, right = start, len(value)
    while left < right and value[left].isspace():
        left += 1
    while right > left and value[right - 1].isspace():
        right -= 1
    if left < right:
        spans.append((left, right))
    return spans


def _connector_part_meaning(
    german_region: str,
    english_region: str,
    local_start: int,
    local_end: int,
) -> str | None:
    """Align one coordinated subpart when both authored texts expose it."""
    candidates: list[str] = []
    for german_connector, english_connector in ALIGNMENT_CONNECTOR_PAIRS:
        german_matches = list(
            re.finditer(
                rf"\b{re.escape(german_connector)}\b",
                german_region,
                flags=re.IGNORECASE,
            )
        )
        english_matches = list(
            re.finditer(
                rf"\b{re.escape(english_connector)}\b",
                english_region,
                flags=re.IGNORECASE,
            )
        )
        if not german_matches or len(german_matches) != len(english_matches):
            continue
        german_parts = list(
            zip(
                [0, *(match.end() for match in german_matches)],
                [*(match.start() for match in german_matches), len(german_region)],
                strict=True,
            )
        )
        english_parts = list(
            zip(
                [0, *(match.end() for match in english_matches)],
                [*(match.start() for match in english_matches), len(english_region)],
                strict=True,
            )
        )
        for part_index, (part_start, part_end) in enumerate(german_parts):
            if local_start >= part_start and local_end <= part_end:
                english_start, english_end = english_parts[part_index]
                result = english_region[english_start:english_end].strip(
                    " ,.;:!?„“”\""
                )
                if result:
                    candidates.append(result)
    return min(candidates, key=len) if candidates else None


def _inversion_meaning(
    text: str,
    meaning: str,
    start_char: int,
    end_char: int,
) -> str:
    """Reuse the matching authored translation segment for an inversion chunk."""
    german_spans = _trimmed_segment_spans(text)
    english_spans = _trimmed_segment_spans(meaning)
    if len(german_spans) != len(english_spans):
        german_open = text.rfind("„", 0, start_char)
        german_close = text.find("“", end_char)
        if german_open >= 0 and german_close >= end_char:
            quoted = re.findall(r"[“\"]([^”\"]+)[”\"]", meaning)
            if quoted:
                return quoted[-1].strip(" .!?„“”\"")
        aligned_part = _connector_part_meaning(
            text, meaning, start_char, end_char
        )
        if aligned_part:
            return aligned_part
        start_key_match = WORD_RE.search(text[start_char:end_char])
        start_key = start_key_match.group().casefold() if start_key_match else ""
        for german_connector, english_connector in CONNECTOR_PAIRS:
            if start_key != german_connector:
                continue
            connector_match = re.search(
                rf"\b{re.escape(english_connector)}\b",
                meaning,
                flags=re.IGNORECASE,
            )
            if connector_match:
                return meaning[connector_match.start() :].strip(" .!?„“”\"")
        return meaning.strip(" .!?„“”\"")

    covered = [
        index
        for index, (start, end) in enumerate(german_spans)
        if start < end_char and end > start_char
    ]
    if not covered:
        return meaning.strip(" .!?„“”\"")
    first, last = covered[0], covered[-1]
    english_start = english_spans[first][0]
    english_end = english_spans[last][1]
    english_region = meaning[english_start:english_end].strip(" .!?„“”\"")

    if first == last:
        german_start, german_end = german_spans[first]
        aligned_part = _connector_part_meaning(
            text[german_start:german_end],
            english_region,
            max(0, start_char - german_start),
            min(german_end, end_char) - german_start,
        )
        if aligned_part:
            return aligned_part
    return english_region


def _inversion_phrase_end(
    text: str,
    surfaces: list[str],
    words: list[BreakdownItem],
    matches: list[re.Match[str]],
    verb_index: int,
    next_start: int | None,
) -> int:
    """Find the end of the clause governed by an inverted finite verb."""
    if next_start is not None:
        end = next_start - 1
        if (
            end >= 0
            and surfaces[end].casefold() in COORDINATING_CONNECTORS
        ):
            end -= 1
        return max(verb_index, end)

    clause_starters = {
        *COORDINATING_CONNECTORS,
        "als", "dass", "ob", "obwohl", "statt", "um", "weil", "wenn",
    }
    for index in range(verb_index, len(surfaces) - 1):
        gap = text[matches[index].end() : matches[index + 1].start()]
        if re.search(r"[;:.!?]", gap):
            return index
        if surfaces[index].casefold() in COORDINATING_CONNECTORS:
            if _is_finite_verb(words[index + 1]):
                return max(verb_index, index - 1)
        if "," in gap:
            if surfaces[index + 1].casefold() in clause_starters:
                return index
            for candidate in range(index + 1, min(index + 6, len(words))):
                if _is_finite_verb(words[candidate]):
                    return index
                candidate_gap = text[
                    matches[candidate].end() : matches[candidate + 1].start()
                ] if candidate + 1 < len(matches) else ""
                if re.search(r"[,;:.!?]", candidate_gap):
                    break
    return len(surfaces) - 1


def _right_bracket_indexes(
    surfaces: list[str],
    words: list[BreakdownItem],
    verb_index: int,
    subject_end: int,
    phrase_end: int,
) -> list[int]:
    """Find participles, infinitives, or a separable prefix closing the clause."""
    participles = [
        index
        for index in range(subject_end + 1, phrase_end + 1)
        if "past participle" in {tag_.label for tag_ in words[index].tags}
    ]
    infinitives = [
        index
        for index in range(subject_end + 1, phrase_end + 1)
        if "infinitive" in {tag_.label for tag_ in words[index].tags}
    ]
    indexes = participles or infinitives
    help_card = words[verb_index].verb_help
    if help_card:
        infinitive = help_card.infinitive.casefold()
        prefix = _separable_prefix(infinitive)
        if prefix:
            indexes.extend(
                index
                for index in range(subject_end + 1, phrase_end + 1)
                if surfaces[index].casefold() == prefix
            )
    return sorted(set(indexes))


def _render_inversion_german(
    text: str,
    surfaces: list[str],
    words: list[BreakdownItem],
    matches: list[re.Match[str]],
    start: int,
    verb_index: int,
    subject_end: int,
    phrase_end: int,
) -> str:
    right_bracket = _right_bracket_indexes(
        surfaces, words, verb_index, subject_end, phrase_end
    )
    if not right_bracket:
        return text[matches[start].start() : matches[phrase_end].end()].strip(
            " .!?„“”\""
        )

    left = text[matches[start].start() : matches[subject_end].end()].strip(
        " .!?„“”\""
    )
    rendered_right = surfaces[right_bracket[0]]
    for previous, current in zip(right_bracket, right_bracket[1:]):
        connector = next(
            (
                surfaces[index]
                for index in range(previous + 1, current)
                if surfaces[index].casefold() in COORDINATING_CONNECTORS
            ),
            None,
        )
        rendered_right += (
            f" {connector} … {surfaces[current]}"
            if connector
            else f" … {surfaces[current]}"
        )
    return f"{left} … {rendered_right}"


def _inversion_phrases(
    text: str,
    meaning: str,
    surfaces: list[str],
    words: list[BreakdownItem],
) -> list[BreakdownItem]:
    """Build joined, bilingual chunks that show the complete inversion pattern."""
    sites = _inversion_sites(text, surfaces, words)
    matches = list(WORD_RE.finditer(text))
    ordered = sorted(sites.items(), key=lambda site: site[1])
    phrases: list[BreakdownItem] = []
    for position, (verb_index, start) in enumerate(ordered):
        subject_span = _subject_span_after_verb(
            surfaces, words, verb_index
        ) or _later_subject_span(surfaces, words, verb_index)
        if subject_span is None:
            continue
        next_start = (
            ordered[position + 1][1]
            if position + 1 < len(ordered)
            else None
        )
        phrase_end = _inversion_phrase_end(
            text, surfaces, words, matches, verb_index, next_start
        )
        start_char = matches[start].start()
        end_char = matches[phrase_end].end()
        phrases.append(
            BreakdownItem(
                german=_render_inversion_german(
                    text,
                    surfaces,
                    words,
                    matches,
                    start,
                    verb_index,
                    subject_span[1],
                    phrase_end,
                ),
                english=_inversion_meaning(
                    text, meaning, start_char, end_char
                ),
                tags=[tag("inversion")],
                kind="phrase",
            )
        )
    return phrases


def _contraction_phrases(
    surfaces: list[str], words: list[BreakdownItem]
) -> list[BreakdownItem]:
    phrases: list[BreakdownItem] = []
    for index, surface in enumerate(surfaces):
        key = surface.casefold()
        if key not in CONTRACTION_MEANINGS:
            continue
        end = min(index + 1, len(words) - 1)
        for candidate in range(index + 1, min(index + 4, len(words))):
            labels = {grammar_tag.label for grammar_tag in words[candidate].tags}
            end = candidate
            if labels & NOUN_LABELS or surfaces[candidate][:1].isupper():
                break
        german = " ".join(surfaces[index : end + 1])
        tail = " ".join(word.english for word in words[index + 1 : end + 1])
        phrase_meaning = CONTRACTION_PHRASE_MEANINGS.get(
            german.casefold(),
            f"{CONTRACTION_MEANINGS[key]} {tail}".strip(),
        )
        phrases.append(
            BreakdownItem(
                german=german,
                english=phrase_meaning,
                tags=[tag("contraction")],
                kind="phrase",
            )
        )
    return phrases


ARTICLES = {"der", "die", "das", "ein", "eine", "einen", "einem", "einer", "eines"}


def _compose_articles(
    surfaces: list[str], words: list[BreakdownItem]
) -> list[BreakdownItem]:
    """Represent a source article through its noun card, not a duplicate row."""
    removed: set[int] = set()
    for index, surface in enumerate(surfaces):
        if surface.casefold() not in ARTICLES:
            continue
        for candidate in range(index + 1, min(index + 4, len(words))):
            labels = {grammar_tag.label for grammar_tag in words[candidate].tags}
            if labels & {"verb", "preposition", "conjunction"}:
                break
            if labels & NOUN_LABELS:
                words[candidate].source_forms = [surface, *words[candidate].source_forms]
                removed.add(index)
                break
    return [word for index, word in enumerate(words) if index not in removed]


def _target_for_surface(surface: str, lesson_targets: list[str]) -> str | None:
    override = SURFACE_OVERRIDES.get(surface.casefold())
    if override:
        return override
    candidates = TARGET_SURFACES.get(surface.casefold(), [])
    exact = next(
        (target for target in candidates if target.casefold() == surface.casefold()),
        None,
    )
    return exact or next(
        (target for target in reversed(lesson_targets) if target in candidates),
        None,
    ) or (
        candidates[0] if len(candidates) == 1 else None
    )


def _word_item(
    surface: str,
    lesson_targets: list[str],
    sentence: str = "",
    word_index: int = -1,
) -> BreakdownItem:
    key = surface.casefold()
    if key in CONTRACTION_BASES:
        base, meaning, case = CONTRACTION_BASES[key]
        return BreakdownItem(
            german=base,
            english=meaning,
            tags=[tag("preposition"), tag(case)],
            source_forms=[surface],
        )
    if key == "morgens":
        return BreakdownItem(
            german="morgens",
            english="in the mornings",
            tags=[tag("adverb"), tag("frequency"), tag("time")],
            source_forms=[surface],
        )
    if key == "gibt" and re.search(r"\bEs\s+gibt\b", sentence):
        help_card, _, tense_tags = _contextual_verb_help(
            "geben", "to give", surface, sentence, word_index
        )
        help_card.english = "to give; es gibt = there is / there are"
        return BreakdownItem(
            german=surface,
            english="there is / there are",
            tags=tense_tags,
            verb_help=help_card,
            source_forms=[surface],
        )
    if surface[:1].isupper() and word_index > 0 and key in CAPITALIZED_NOUNS:
        german, english, gender = CAPITALIZED_NOUNS[key]
        return BreakdownItem(
            german=german,
            english=english,
            tags=[tag("noun"), tag(gender)],
            source_forms=[surface],
        )
    if key in EXTRA_VERBS:
        meaning = EXTRA_VERBS[key]
        help_card, item_meaning, tense_tags = _contextual_verb_help(
            key, meaning, surface, sentence, word_index
        )
        return BreakdownItem(
            german=surface,
            english=item_meaning,
            tags=tense_tags,
            verb_help=help_card,
            source_forms=[surface],
        )
    target = _target_for_surface(surface, lesson_targets)
    if target is not None:
        meaning = TARGET_GLOSSES.get(target, EXTRA_VERBS.get(target, target))
        noun = _noun_parts(target)
        if noun:
            gender = {"der": "masc.", "die": "fem.", "das": "neuter"}[noun[0]]
            noun_tags = [tag("noun")]
            noun_tags.append(
                tag("plural") if target in PLURAL_ONLY_TARGETS else tag(gender)
            )
            return BreakdownItem(
                german=target,
                english=meaning,
                tags=noun_tags,
                source_forms=[surface],
            )
        if _is_verb_target(target, meaning) or target in EXTRA_VERBS:
            help_card, item_meaning, tense_tags = _contextual_verb_help(
                target, meaning, surface, sentence, word_index
            )
            return BreakdownItem(
                german=surface,
                english=item_meaning,
                tags=tense_tags,
                verb_help=help_card,
                source_forms=[surface],
            )
        labels = []
        if target in {"weil", "denn"}:
            labels = [tag("conjunction"), tag("subordinating" if target == "weil" else "coordinating")]
        return BreakdownItem(
            german=target,
            english=meaning,
            tags=labels,
            source_forms=[surface],
        )
    if key in EXTRA_VERBS or key in SURFACE_OVERRIDES:
        infinitive = SURFACE_OVERRIDES.get(key, key)
        meaning = EXTRA_VERBS.get(infinitive, f"to {infinitive}")
        help_card, item_meaning, tense_tags = _contextual_verb_help(
            infinitive, meaning, surface, sentence, word_index
        )
        return BreakdownItem(
            german=surface,
            english=item_meaning,
            tags=tense_tags,
            verb_help=help_card,
            source_forms=[surface],
        )
    if key in NOUN_GLOSSES:
        german, english, gender, plural = NOUN_GLOSSES[key]
        labels = [tag("noun"), tag(gender)]
        if plural:
            labels.append(tag("plural"))
        return BreakdownItem(
            german=german,
            english=english,
            tags=labels,
            source_forms=[surface],
        )
    if key in NUMBER_GLOSSES or key.isdigit():
        return BreakdownItem(
            german=surface,
            english=NUMBER_GLOSSES.get(key, surface),
            tags=[tag("numeral")],
            source_forms=[surface],
        )
    if key in COMMON_GLOSSES:
        labels = (
            [tag("personal pronoun")]
            if key
            in {
                "ich", "du", "er", "sie", "wir", "ihr", "mich", "mir",
                "dich", "ihm", "ihn", "uns",
            }
            else [tag("possessive"), tag("determiner")]
            if key in POSSESSIVE_GLOSSES
            else [tag("conjunction"), tag("coordinating")]
            if key in COORDINATING_CONNECTORS
            else []
        )
        return BreakdownItem(
            german=surface,
            english=COMMON_GLOSSES[key],
            tags=labels,
            source_forms=[surface],
        )
    if surface[:1].isupper():
        return BreakdownItem(
            german=surface,
            english=surface,
            tags=[tag("proper noun")],
            source_forms=[surface],
        )
    raise ValueError(f"Missing controlled gloss for source form {surface!r}")


def _extend_tags(item: BreakdownItem, labels: tuple[str, ...]) -> None:
    existing = {grammar_tag.label for grammar_tag in item.tags}
    item.tags.extend(tag(label) for label in labels if label not in existing)


def _apply_sentence_annotations(
    surfaces: list[str],
    words: list[BreakdownItem],
    phrases: list[BreakdownItem],
    annotations: SentenceAnnotations,
) -> None:
    base_forms = {key.casefold(): value for key, value in annotations.base_forms.items()}
    word_meanings = {
        key.casefold(): value for key, value in annotations.word_meanings.items()
    }
    word_tags = {key.casefold(): value for key, value in annotations.word_tags.items()}
    for surface, item in zip(surfaces, words, strict=True):
        item.german = base_forms.get(surface.casefold(), item.german)
        item.english = word_meanings.get(surface.casefold(), item.english)
        if labels := word_tags.get(surface.casefold()):
            _extend_tags(item, tuple(labels))

    by_normalized_phrase: dict[str, BreakdownItem] = {}
    for phrase in phrases:
        normalized = " ".join(
            token.casefold() for token in WORD_RE.findall(phrase.german)
        )
        by_normalized_phrase.setdefault(normalized, phrase)
    for authored in annotations.phrases:
        normalized = " ".join(
            token.casefold() for token in WORD_RE.findall(authored.german)
        )
        phrase = by_normalized_phrase.get(normalized)
        if phrase is None:
            if authored.english is None:
                raise ValueError(
                    f"Authored phrase {authored.german!r} needs an English meaning "
                    "because the generic compiler did not create it"
                )
            phrase = BreakdownItem(
                german=authored.german,
                english=authored.english,
                kind="phrase",
            )
            phrases.append(phrase)
            by_normalized_phrase[normalized] = phrase
        elif authored.english is not None:
            phrase.english = authored.english
        _extend_tags(phrase, tuple(authored.tags))

    excluded = {
        " ".join(token.casefold() for token in WORD_RE.findall(german))
        for german in annotations.excluded_phrases
    }
    phrases[:] = [
        phrase
        for phrase in phrases
        if " ".join(
            token.casefold() for token in WORD_RE.findall(phrase.german)
        ) not in excluded
    ]
    excluded_tags = {
        " ".join(token.casefold() for token in WORD_RE.findall(german)): set(labels)
        for german, labels in annotations.excluded_phrase_tags.items()
    }
    for phrase in phrases:
        normalized = " ".join(
            token.casefold() for token in WORD_RE.findall(phrase.german)
        )
        if labels := excluded_tags.get(normalized):
            phrase.tags = [tag_ for tag_ in phrase.tags if tag_.label not in labels]


def _sentence_groups(
    text: str,
    meaning: str,
    lesson_targets: list[str],
    annotations: SentenceAnnotations,
) -> list[BreakdownGroup]:
    surfaces = WORD_RE.findall(text)
    source_words = [
        _word_item(surface, lesson_targets, text, index)
        for index, surface in enumerate(surfaces)
    ]
    phrases: list[BreakdownItem] = [
        *_inversion_phrases(text, meaning, surfaces, source_words),
        *_contraction_phrases(surfaces, source_words),
        *_noun_phrases(surfaces, source_words, meaning, text),
        *_connector_phrases(text, meaning, surfaces, source_words),
    ]
    words = _compose_articles(surfaces, source_words)
    de_clauses = [part.strip(" .!?„“\"") for part in re.split(r"[,;:]", text)]
    en_clauses = [part.strip(" .!?“\"") for part in re.split(r"[,;:]", meaning)]
    if len(de_clauses) == len(en_clauses) and len(de_clauses) > 1:
        for german, english in zip(de_clauses, en_clauses, strict=True):
            if len(WORD_RE.findall(german)) >= 2:
                phrase_label = (
                    "subordinate clause"
                    if german.casefold().startswith(("weil ", "wenn ", "dass ", "ob ", "obwohl ", "als "))
                    else "main clause"
                )
                phrases.append(
                    BreakdownItem(
                        german=german,
                        english=english,
                        tags=[tag(phrase_label)],
                        kind="phrase",
                    )
                )
    folded_text = text.casefold()
    for german, english in CURATED_PHRASES.items():
        if german.casefold() in folded_text:
            phrases.append(
                BreakdownItem(
                    german=german,
                    english=english,
                    tags=[tag("fixed phrase")],
                    kind="phrase",
                )
            )
    _apply_sentence_annotations(surfaces, source_words, phrases, annotations)
    group = BreakdownGroup(items=[*words, *_deduplicate_phrases(phrases)])
    return [attach_inflection_help(group)]


def _load_records() -> list[dict]:
    records: list[dict] = []
    for path in sorted((CURRICULUM_ROOT / "lessons").glob("*.json")):
        records.extend(json.loads(path.read_text(encoding="utf-8")))
    return records


def _compile_lesson(record: dict, introduced_targets: list[str]) -> Lesson:
    lesson_targets = [*introduced_targets, *record["new_targets"]]
    record_audio_path = record.get("audio_path")
    sentence_audio_paths = [
        sentence.get("audio_path") for sentence in record["sentences"]
    ]
    has_complete_audio = bool(record_audio_path) and all(sentence_audio_paths)
    sentences = [
        Sentence(
            text=sentence["de"],
            natural_meaning=sentence["en"],
            breakdown_groups=_sentence_groups(
                sentence["de"],
                sentence["en"],
                lesson_targets,
                SentenceAnnotations.model_validate(sentence.get("annotations", {})),
            ),
            audio_path=sentence_audio_paths[index] if has_complete_audio else None,
        )
        for index, sentence in enumerate(record["sentences"])
    ]
    return Lesson(
        id=record["id"],
        sequence=record["sequence"],
        title=record["title_de"],
        english_title=record["title_en"],
        level=record["band"],
        lesson_format=record["format"],
        topic=record["topic"],
        new_targets=record["new_targets"],
        recycled_targets=record["recycled_targets"],
        speech_alternatives=record.get("speech_alternatives", []),
        sentences=sentences,
        audio_path=record_audio_path if has_complete_audio else None,
        audio_status="ready" if has_complete_audio else "pending",
        initial_question=record["comprehension"]["question_en"],
        initial_answer=record["comprehension"]["answer_en"],
    )


def load_a1_a2_lessons() -> list[Lesson]:
    records = _load_records()
    audit_targets: list[str] = []
    missing: dict[str, str] = {}
    for record in records:
        lesson_targets = [*audit_targets, *record["new_targets"]]
        for sentence in record["sentences"]:
            for surface in WORD_RE.findall(sentence["de"]):
                try:
                    _word_item(surface, lesson_targets)
                except ValueError as error:
                    missing[surface] = str(error)
        audit_targets.extend(record["new_targets"])
    if missing:
        raise ValueError(
            "Missing controlled glosses for source forms: "
            + "; ".join(
                f"{surface} ({missing[surface]})"
                for surface in sorted(missing, key=str.casefold)
            )
        )

    lessons: list[Lesson] = []
    introduced_targets: list[str] = []
    for record in records:
        try:
            lesson = _compile_lesson(record, introduced_targets)
        except ValueError as error:
            raise ValueError(f"Could not compile curriculum lesson {record['id']}: {error}") from error
        lessons.append(lesson)
        introduced_targets.extend(record["new_targets"])
    return lessons


A1_A2_LESSONS = load_a1_a2_lessons()
