"""Progressive A2–B2 listening lessons for the prepared content library."""

from __future__ import annotations

from .models import (
    BreakdownGroup,
    BreakdownItem,
    ConjugationForm,
    GrammarTag,
    Lesson,
    Sentence,
    TAG_KEYWORDS,
    VerbHelp,
)


_PRONOUNS = ("ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie")
_VERB_HELP: dict[tuple[str, str], VerbHelp] = {}


def register_verb_help(
    infinitive: str,
    tense: str,
    forms: tuple[str, str, str, str, str, str],
    usage: str,
    *lookups: tuple[str, str],
) -> None:
    help_card = VerbHelp(
        infinitive=infinitive,
        tense=tense,
        forms=[
            ConjugationForm(pronoun=pronoun, verb=form)
            for pronoun, form in zip(_PRONOUNS, forms, strict=True)
        ],
        usage=usage,
    )
    for german, english in lookups:
        _VERB_HELP[(german.casefold(), english.casefold())] = help_card


register_verb_help(
    "wollen", "Präteritum (simple past)",
    ("wollte", "wolltest", "wollte", "wollten", "wolltet", "wollten"),
    "Wollen expresses an intention or plan. The other verb appears as an infinitive at the end.",
    ("wollte", "wanted"), ("wollten", "wanted"),
)
register_verb_help(
    "regnen", "Präteritum (simple past)",
    ("regnete", "regnetest", "regnete", "regneten", "regnetet", "regneten"),
    "A regular past-tense verb describing the rain that changed the plan.",
    ("regnete", "rained"),
)
register_verb_help(
    "sein", "Präsens (present)",
    ("bin", "bist", "ist", "sind", "seid", "sind"),
    "Sein is the auxiliary used to form the perfect tense of fahren here.",
    ("sind", "are"),
)
register_verb_help(
    "sein", "Präteritum (simple past)",
    ("war", "warst", "war", "waren", "wart", "waren"),
    "The simple past of sein describes a state in the past.",
    ("war", "was"),
)
register_verb_help(
    "haben", "Präsens (present)",
    ("habe", "hast", "hat", "haben", "habt", "haben"),
    "Haben is the auxiliary used to form the perfect tense here.",
    ("haben", "have"), ("hat", "has"),
)
register_verb_help(
    "haben", "Präteritum (simple past)",
    ("hatte", "hattest", "hatte", "hatten", "hattet", "hatten"),
    "Hatte or hatten combines with a past participle to form the pluperfect here.",
    ("hatte", "had"), ("hatten", "had"),
)
register_verb_help(
    "bemerken", "Präteritum (simple past)",
    ("bemerkte", "bemerktest", "bemerkte", "bemerkten", "bemerktet", "bemerkten"),
    "A regular verb meaning to notice.",
    ("bemerkte", "noticed"), ("bemerkten", "noticed"),
)
register_verb_help(
    "fehlen", "Präteritum (simple past)",
    ("fehlte", "fehltest", "fehlte", "fehlten", "fehltet", "fehlten"),
    "Fehlen describes something that was missing.",
    ("fehlte", "was missing"),
)
register_verb_help(
    "anrufen", "Präteritum (simple past)",
    ("rief an", "riefst an", "rief an", "riefen an", "rieft an", "riefen an"),
    "Anrufen is separable: the prefix an appears later in a main clause.",
    ("rief", "called"),
)
register_verb_help(
    "vergessen", "Präteritum (simple past)",
    ("vergaß", "vergaßest", "vergaß", "vergaßen", "vergaßt", "vergaßen"),
    "An irregular verb meaning to forget.",
    ("vergaß", "forgot"),
)
register_verb_help(
    "anbrennen", "Präteritum (simple past)",
    ("brannte an", "branntest an", "brannte an", "brannten an", "branntet an", "brannten an"),
    "Anbrennen is separable and means to burn or scorch while cooking.",
    ("brannte", "burned"),
)
register_verb_help(
    "bestellen", "Präteritum (simple past)",
    ("bestellte", "bestelltest", "bestellte", "bestellten", "bestelltet", "bestellten"),
    "A regular verb meaning to order.",
    ("bestellten", "ordered"),
)
register_verb_help(
    "lachen", "Präteritum (simple past)",
    ("lachte", "lachtest", "lachte", "lachten", "lachtet", "lachten"),
    "A regular verb meaning to laugh.",
    ("lachten", "laughed"),
)
register_verb_help(
    "suchen", "Präsens (present)",
    ("suche", "suchst", "sucht", "suchen", "sucht", "suchen"),
    "Suchen means to look for; with seit it describes an activity continuing into the present.",
    ("sucht", "is looking for"), ("sucht", "looks for"),
)
register_verb_help(
    "besichtigen", "Präteritum (simple past)",
    ("besichtigte", "besichtigtest", "besichtigte", "besichtigten", "besichtigtet", "besichtigten"),
    "A regular verb meaning to view or inspect a place.",
    ("besichtigte", "viewed"),
)
register_verb_help(
    "schicken", "Präteritum (simple past)",
    ("schickte", "schicktest", "schickte", "schickten", "schicktet", "schickten"),
    "A regular verb meaning to send.",
    ("schickte", "sent"),
)
register_verb_help(
    "warten", "Präsens (present)",
    ("warte", "wartest", "wartet", "warten", "wartet", "warten"),
    "Warten auf takes the accusative and means to wait for.",
    ("wartet", "is waiting"),
)
register_verb_help(
    "lernen", "Präteritum (simple past)",
    ("lernte", "lerntest", "lernte", "lernten", "lerntet", "lernten"),
    "A regular verb meaning to learn.",
    ("lernte", "learned"),
)
register_verb_help(
    "schreiben", "Präsens (present)",
    ("schreibe", "schreibst", "schreibt", "schreiben", "schreibt", "schreiben"),
    "An irregular present-tense verb meaning to write.",
    ("schreibt", "writes"),
)
register_verb_help(
    "hören", "Präsens (present)",
    ("höre", "hörst", "hört", "hören", "hört", "hören"),
    "A regular verb meaning to hear or listen to.",
    ("hört", "listens to"),
)
register_verb_help(
    "verstehen", "Präsens (present)",
    ("verstehe", "verstehst", "versteht", "verstehen", "versteht", "verstehen"),
    "An irregular verb meaning to understand.",
    ("versteht", "understands"),
)
register_verb_help(
    "notieren", "Präsens (present)",
    ("notiere", "notierst", "notiert", "notieren", "notiert", "notieren"),
    "A regular verb meaning to note or write something down.",
    ("notiert", "writes down"),
)
register_verb_help(
    "können", "Präsens (present)",
    ("kann", "kannst", "kann", "können", "könnt", "können"),
    "Können is a modal verb; the other verb appears as an infinitive at the end.",
    ("kann", "can"),
)
register_verb_help(
    "werden", "Präteritum (simple past)",
    ("wurde", "wurdest", "wurde", "wurden", "wurdet", "wurden"),
    "Werden combines with a past participle to form the passive voice here.",
    ("wurde", "was"), ("wurden", "were"),
)
register_verb_help(
    "tragen", "Präteritum (simple past)",
    ("trug", "trugst", "trug", "trugen", "trugt", "trugen"),
    "An irregular verb meaning to carry.",
    ("trug", "carried"),
)
register_verb_help(
    "helfen", "Präteritum (simple past)",
    ("half", "halfst", "half", "halfen", "halft", "halfen"),
    "An irregular verb that takes a person in the dative.",
    ("half", "helped"),
)
register_verb_help(
    "finden", "Präteritum (simple past)",
    ("fand", "fandst", "fand", "fanden", "fandet", "fanden"),
    "An irregular verb meaning to find.",
    ("fanden", "found"),
)
register_verb_help(
    "liegen", "Präteritum (simple past)",
    ("lag", "lagst", "lag", "lagen", "lagt", "lagen"),
    "An irregular verb describing where something lay or was located.",
    ("lag", "lay/was located"),
)
register_verb_help(
    "beschließen", "Präteritum (simple past)",
    ("beschloss", "beschlossest", "beschloss", "beschlossen", "beschlosst", "beschlossen"),
    "Beschließen means to decide and is often followed by an infinitive with zu.",
    ("beschlossen", "decided"), ("beschloss", "decided"),
)
register_verb_help(
    "anbauen", "Präsens (present)",
    ("baue an", "baust an", "baut an", "bauen an", "baut an", "bauen an"),
    "Anbauen is separable and means to grow or cultivate crops.",
    ("bauen", "grow"),
)
register_verb_help(
    "organisieren", "Präsens (present)",
    ("organisiere", "organisierst", "organisiert", "organisieren", "organisiert", "organisieren"),
    "A regular verb meaning to organize.",
    ("organisieren", "organize"),
)
register_verb_help(
    "vorstellen", "Präteritum (simple past)",
    ("stellte vor", "stelltest vor", "stellte vor", "stellten vor", "stelltet vor", "stellten vor"),
    "Vorstellen is separable; here it means to present something.",
    ("stellte", "presented"),
)
register_verb_help(
    "warnen", "Präteritum (simple past)",
    ("warnte", "warntest", "warnte", "warnten", "warntet", "warnten"),
    "A regular verb meaning to warn.",
    ("warnten", "warned"),
)
register_verb_help(
    "entstehen", "Präteritum (simple past)",
    ("entstand", "entstandest", "entstand", "entstanden", "entstandet", "entstanden"),
    "Entstehen is intransitive and means to emerge, arise, or result.",
    ("entstand", "emerged/resulted"),
)
register_verb_help(
    "schauen", "Präteritum (simple past)",
    ("schaute", "schautest", "schaute", "schauten", "schautet", "schauten"),
    "A regular verb meaning to look.",
    ("schaute", "looked"),
)
register_verb_help(
    "ausschalten", "Präteritum (simple past)",
    ("schaltete aus", "schaltetest aus", "schaltete aus", "schalteten aus", "schaltetet aus", "schalteten aus"),
    "Ausschalten is separable and means to switch off.",
    ("schaltete", "switched"),
)
register_verb_help(
    "lassen", "Präteritum (simple past)",
    ("ließ", "ließest", "ließ", "ließen", "ließt", "ließen"),
    "An irregular verb meaning to leave something in a place here.",
    ("ließ", "left"),
)
register_verb_help(
    "fallen", "Präteritum (simple past)",
    ("fiel", "fielst", "fiel", "fielen", "fielt", "fielen"),
    "In the fixed expression jemandem schwerfallen, it means to be difficult for someone.",
    ("fiel", "was/felt"),
)
register_verb_help(
    "feststellen", "Präteritum (simple past)",
    ("stellte fest", "stelltest fest", "stellte fest", "stellten fest", "stelltet fest", "stellten fest"),
    "Feststellen is separable and means to realize or determine.",
    ("stellte", "realized"),
)
register_verb_help(
    "arbeiten", "Präteritum (simple past)",
    ("arbeitete", "arbeitetest", "arbeitete", "arbeiteten", "arbeitetet", "arbeiteten"),
    "A regular verb meaning to work.",
    ("arbeitete", "worked"),
)
register_verb_help(
    "umgehen", "Präteritum (simple past)",
    ("ging um", "gingst um", "ging um", "gingen um", "gingt um", "gingen um"),
    "Mit etwas umgehen means to handle or deal with something; its past form is ging ... um.",
    ("umging", "handled/dealt with"),
)
register_verb_help(
    "planen", "Präsens (present)",
    ("plane", "planst", "plant", "planen", "plant", "planen"),
    "A regular verb meaning to plan.",
    ("plant", "plans"),
)
register_verb_help(
    "hoffen", "Präsens (present)",
    ("hoffe", "hoffst", "hofft", "hoffen", "hofft", "hoffen"),
    "A regular verb meaning to hope.",
    ("hoffen", "hope"),
)
register_verb_help(
    "werden", "Präsens (present)",
    ("werde", "wirst", "wird", "werden", "werdet", "werden"),
    "Werden means to become; the plural compound subject requires werden here.",
    ("werden", "become"),
)
register_verb_help(
    "befürchten", "Präsens (present)",
    ("befürchte", "befürchtest", "befürchtet", "befürchten", "befürchtet", "befürchten"),
    "A regular verb meaning to fear or be concerned that something may happen.",
    ("befürchten", "fear"),
)
register_verb_help(
    "ausweichen", "Präsens (present)",
    ("weiche aus", "weichst aus", "weicht aus", "weichen aus", "weicht aus", "weichen aus"),
    "Ausweichen is separable and means to divert, shift, or move elsewhere.",
    ("ausweicht", "diverts/shifts"),
)
register_verb_help(
    "fallen", "Präsens (present)",
    ("falle", "fällst", "fällt", "fallen", "fallt", "fallen"),
    "In the expression eine Entscheidung fällt, it means a decision is made.",
    ("fällt", "is made/falls"),
)
register_verb_help(
    "sollen", "Präsens (present)",
    ("soll", "sollst", "soll", "sollen", "sollt", "sollen"),
    "Sollen is a modal verb; the other verb appears as an infinitive at the end.",
    ("sollen", "should"),
)
register_verb_help(
    "werden", "Konjunktiv II (subjunctive)",
    ("würde", "würdest", "würde", "würden", "würdet", "würden"),
    "Würde plus an infinitive expresses a hypothetical consequence.",
    ("würde", "would"),
)
register_verb_help(
    "picknicken", "Präsens (present)",
    ("picknicke", "picknickst", "picknickt", "picknicken", "picknickt", "picknicken"),
    "The sentence uses the infinitive picknicken after the modal verb wollten.",
    ("picknicken", "to have a picnic"),
)
register_verb_help(
    "fahren", "Perfekt (perfect)",
    ("bin gefahren", "bist gefahren", "ist gefahren", "sind gefahren", "seid gefahren", "sind gefahren"),
    "Fahren forms the perfect with sein when it describes movement to a destination.",
    ("gefahren", "went/travelled"),
)
register_verb_help(
    "kochen", "Perfekt (perfect)",
    ("habe gekocht", "hast gekocht", "hat gekocht", "haben gekocht", "habt gekocht", "haben gekocht"),
    "Gekocht is the past participle of kochen and combines with haben here.",
    ("gekocht", "cooked"),
)
register_verb_help(
    "reden", "Perfekt (perfect)",
    ("habe geredet", "hast geredet", "hat geredet", "haben geredet", "habt geredet", "haben geredet"),
    "Geredet is the past participle of reden and combines with haben here.",
    ("geredet", "talked"),
)
register_verb_help(
    "besuchen", "Plusquamperfekt (pluperfect)",
    ("hatte besucht", "hattest besucht", "hatte besucht", "hatten besucht", "hattet besucht", "hatten besucht"),
    "Besucht combines with hatte to describe a visit completed before the phone call.",
    ("besucht", "visited"),
)
register_verb_help(
    "finden", "Plusquamperfekt (pluperfect)",
    ("hatte gefunden", "hattest gefunden", "hatte gefunden", "hatten gefunden", "hattet gefunden", "hatten gefunden"),
    "Gefunden combines with hatte to describe finding the wallet before the later events.",
    ("gefunden", "found"),
)
register_verb_help(
    "aufbewahren", "Plusquamperfekt (pluperfect)",
    ("hatte aufbewahrt", "hattest aufbewahrt", "hatte aufbewahrt", "hatten aufbewahrt", "hattet aufbewahrt", "hatten aufbewahrt"),
    "Aufbewahrt is the past participle of separable aufbewahren and shares the auxiliary hatte.",
    ("aufbewahrt", "kept/stored"),
)
register_verb_help(
    "kochen", "Präsens (present)",
    ("koche", "kochst", "kocht", "kochen", "kocht", "kochen"),
    "The sentence uses the infinitive kochen after the modal verb wollte.",
    ("kochen", "to cook"),
)
register_verb_help(
    "merken", "Präsens (present)",
    ("merke", "merkst", "merkt", "merken", "merkt", "merken"),
    "The sentence uses the infinitive merken after the modal verb kann.",
    ("merken", "to remember"),
)
register_verb_help(
    "verlegen", "Präteritum passive (simple-past passive)",
    ("wurde verlegt", "wurdest verlegt", "wurde verlegt", "wurden verlegt", "wurdet verlegt", "wurden verlegt"),
    "Verlegt is the past participle of verlegen; wurde ... verlegt forms the simple-past passive.",
    ("verlegt", "moved"),
)
register_verb_help(
    "anlegen", "Präsens (present)",
    ("lege an", "legst an", "legt an", "legen an", "legt an", "legen an"),
    "Anzulegen is the zu-infinitive of separable anlegen after beschlossen.",
    ("anzulegen", "to create/set up"),
)
register_verb_help(
    "verändern", "Perfekt (perfect)",
    ("habe verändert", "hast verändert", "hat verändert", "haben verändert", "habt verändert", "haben verändert"),
    "Verändert is the past participle of verändern and combines with haben here.",
    ("verändert", "changed"),
)
register_verb_help(
    "zusammenbringen", "Perfekt (perfect)",
    ("habe zusammengebracht", "hast zusammengebracht", "hat zusammengebracht", "haben zusammengebracht", "habt zusammengebracht", "haben zusammengebracht"),
    "Zusammengebracht is the past participle of separable zusammenbringen and shares the auxiliary hat.",
    ("zusammengebracht", "brought together"),
)
register_verb_help(
    "stehen", "Präsens (present)",
    ("stehe", "stehst", "steht", "stehen", "steht", "stehen"),
    "The sentence uses stehen as the infinitive with würde in a hypothetical construction.",
    ("stehen", "to be/stand"),
)
register_verb_help(
    "erklären", "Plusquamperfekt (pluperfect)",
    ("hatte erklärt", "hattest erklärt", "hatte erklärt", "hatten erklärt", "hattet erklärt", "hatten erklärt"),
    "Erklärt combines with hatten to mark the earlier completed action.",
    ("erklärt", "explained"),
)
register_verb_help(
    "verteilen", "Präteritum passive (simple-past passive)",
    ("wurde verteilt", "wurdest verteilt", "wurde verteilt", "wurden verteilt", "wurdet verteilt", "wurden verteilt"),
    "Verteilt is the past participle of verteilen; wurden ... verteilt forms the plural passive here.",
    ("verteilt", "distributed"),
)
register_verb_help(
    "bemerken", "Plusquamperfekt (pluperfect)",
    ("hatte bemerkt", "hattest bemerkt", "hatte bemerkt", "hatten bemerkt", "hattet bemerkt", "hatten bemerkt"),
    "Bemerkt combines with hatte to describe an observation made before the later decision.",
    ("bemerkt", "noticed"),
)
register_verb_help(
    "einlegen", "Präsens (present)",
    ("lege ein", "legst ein", "legt ein", "legen ein", "legt ein", "legen ein"),
    "Einzulegen is the zu-infinitive of separable einlegen after beschloss.",
    ("einzulegen", "to take"),
)
register_verb_help(
    "aushalten", "Präsens (present)",
    ("halte aus", "hältst aus", "hält aus", "halten aus", "haltet aus", "halten aus"),
    "Auszuhalten is the zu-infinitive of separable aushalten.",
    ("auszuhalten", "to tolerate/endure"),
)
register_verb_help(
    "sperren", "Präsens (present)",
    ("sperre", "sperrst", "sperrt", "sperren", "sperrt", "sperren"),
    "The sentence uses sperren as an infinitive with zu after plant.",
    ("sperren", "to close/block"),
)
register_verb_help(
    "einbringen", "Präsens (present)",
    ("bringe ein", "bringst ein", "bringt ein", "bringen ein", "bringt ein", "bringen ein"),
    "The sentence uses einbringen as the infinitive after the modal verb sollen.",
    ("einbringen", "to contribute"),
)


def word(
    german: str,
    english: str,
    *tags: str,
    forms: tuple[str, ...] = (),
) -> BreakdownItem:
    labels = set(tags)
    verb_help = None
    if labels & {
        "verb",
        "modal verb",
        "auxiliary",
        "reflexive",
        "separable",
        "inseparable",
        "regular",
        "irregular",
        "infinitive",
        "past participle",
    }:
        verb_help = _VERB_HELP.get((german.casefold(), english.casefold()))
    return BreakdownItem(
        german=german,
        english=english,
        tags=[GrammarTag(label=tag, category=TAG_KEYWORDS[tag]) for tag in tags],
        verb_help=verb_help,
        source_forms=list(forms),
    )


def phrase(german: str, english: str, *tags: str) -> BreakdownItem:
    """Create an authored phrase result for a meaningful construction."""
    return BreakdownItem(
        german=german,
        english=english,
        tags=[GrammarTag(label=tag, category=TAG_KEYWORDS[tag]) for tag in tags],
        kind="phrase",
    )


_NOUN_PHRASE_MEANINGS = {
    "eine bezahlbare Wohnung": "an affordable apartment",
    "eine helle Wohnung": "a bright apartment",
    "einen kleinen Balkon": "a small balcony",
    "einen deutschen Podcast": "a German podcast",
    "einen Ausdruck": "an expression",
    "ein Beispiel": "an example",
    "die Wörter": "the words",
    "ein anderes Gleis": "another platform",
    "eine ältere Frau": "an older woman",
    "einen schweren Koffer": "a heavy suitcase",
    "ein ungenutztes Grundstück": "an unused plot of land",
    "einen kleinen Garten": "a small garden",
    "ein gemeinsames Frühstück": "a shared breakfast",
    "die Menschen": "the people",
    "einen neuen Zeitplan": "a new schedule",
    "die Aufgaben": "the tasks",
    "ein realistischer Plan": "a realistic plan",
    "eine digitale Pause": "a digital break",
    "die ungewohnte Stille": "the unfamiliar silence",
    "eine viel befahrene Straße": "a busy road",
    "die umliegenden Straßen": "the surrounding streets",
    "eine endgültige Entscheidung": "a final decision",
    "die Anwohner": "the residents",
}


def _surface_form(item: BreakdownItem, *, noun: bool = False) -> str:
    if item.source_forms:
        return item.source_forms[-1] if noun else item.source_forms[0]
    if noun:
        return item.german.split(maxsplit=1)[-1]
    return item.german


def _compose_noun_phrases(
    words: list[BreakdownItem],
) -> tuple[list[BreakdownItem], list[BreakdownItem]]:
    """Move sentence articles into composed noun phrases.

    Dictionary nouns remain reusable source cards; their sentence article and
    inflected modifiers are shown only in the phrase result on the right.
    """
    generated: list[BreakdownItem] = []
    omitted_article_ids: set[int] = set()
    noun_labels = {"masc.", "fem.", "neuter", "noun", "compound noun"}

    for index, article in enumerate(words):
        labels = {tag.label for tag in article.tags}
        if "article" not in labels or article.english.casefold() not in {
            "a",
            "an",
            "the",
        }:
            continue

        noun_index = next(
            (
                candidate
                for candidate in range(index + 1, min(index + 5, len(words)))
                if {tag.label for tag in words[candidate].tags} & noun_labels
            ),
            None,
        )
        if noun_index is None:
            continue

        chunk = words[index : noun_index + 1]
        if any(
            {tag.label for tag in item.tags}
            & {"verb", "modal verb", "auxiliary", "preposition", "conjunction"}
            for item in chunk[1:-1]
        ):
            continue

        noun = words[noun_index]
        article_surface = _surface_form(article)
        noun_surface = _surface_form(noun, noun=True)
        if article_surface not in noun.source_forms:
            noun.source_forms.append(article_surface)
        omitted_article_ids.add(id(article))

        noun_labels_for_item = {tag.label for tag in noun.tags}
        has_modifier = len(chunk) > 2
        changes_number = "plural" in noun_labels_for_item
        if not has_modifier and not changes_number:
            # The dictionary noun already carries its article. A bare
            # indefinite/definite article adds no reusable meaning of its own.
            continue

        german = " ".join(
            [
                article_surface,
                *(_surface_form(item) for item in chunk[1:-1]),
                noun_surface,
            ]
        )
        english = _NOUN_PHRASE_MEANINGS.get(german)
        if english is None:
            raise ValueError(f"Missing noun-phrase meaning for {german!r}")
        generated.append(
            BreakdownItem(german=german, english=english, kind="phrase")
        )

    return (
        [item for item in words if id(item) not in omitted_article_ids],
        generated,
    )


def sentence(
    slug: str,
    number: int,
    text: str,
    meaning: str,
    words: list[BreakdownItem],
    focus: (
        tuple[str, str, tuple[str, ...]]
        | list[tuple[str, str, tuple[str, ...]]]
        | None
    ) = None,
) -> Sentence:
    normalized_words, noun_phrases = _compose_noun_phrases(list(words))
    items = [*normalized_words, *noun_phrases]
    focuses = focus if isinstance(focus, list) else ([focus] if focus else [])
    for german, english, tags in focuses:
        items.append(
            BreakdownItem(
                german=german,
                english=english,
                tags=[
                    GrammarTag(label=tag, category=TAG_KEYWORDS[tag])
                    for tag in tags
                ],
                kind="phrase",
            )
        )
    return Sentence(
        text=text,
        natural_meaning=meaning,
        breakdown_groups=[BreakdownGroup(items=items)],
        audio_path=f"assets/audio/sentences/{slug}-{number}.wav",
    )


def group(*items: BreakdownItem) -> BreakdownGroup:
    """Keep one reusable set of words beside its phrase-building steps."""
    words = [item for item in items if item.kind == "word"]
    authored_phrases = [item for item in items if item.kind == "phrase"]
    normalized_words, noun_phrases = _compose_noun_phrases(words)
    return BreakdownGroup(
        items=[*normalized_words, *noun_phrases, *authored_phrases]
    )


def grouped_sentence(
    slug: str,
    number: int,
    text: str,
    meaning: str,
    groups: list[BreakdownGroup],
) -> Sentence:
    """Create a sentence whose pedagogical phrase groups are authored explicitly."""
    return Sentence(
        text=text,
        natural_meaning=meaning,
        breakdown_groups=groups,
        audio_path=f"assets/audio/sentences/{slug}-{number}.wav",
    )


RAINY_PICNIC = Lesson(
    id="rainy-picnic",
    title="Das verregnete Picknick",
    english_title="The rainy picnic",
    level="A2",
    audio_path="assets/audio/rainy-picnic.wav",
    initial_question="Warum änderten die Freunde ihre Pläne?",
    sentences=[
        sentence(
            "rainy-picnic", 1,
            "Eigentlich wollten wir am Samstag im Park picknicken.",
            "We originally wanted to have a picnic in the park on Saturday.",
            [
                word("eigentlich", "actually/originally", "adverb"),
                word("wollten", "wanted", "modal verb", "simple past"),
                word("wir", "we", "personal pronoun", "subject"),
                word("an", "on", "preposition", "dative", forms=("am",)),
                word("der Samstag", "Saturday", "masc.", forms=("Samstag",)),
                word("in", "in", "preposition", "dative", forms=("im",)),
                word("der Park", "park", "masc.", forms=("Park",)),
                word("picknicken", "to have a picnic", "verb", "infinitive"),
            ],
            [
                (
                    "Eigentlich wollten wir ... picknicken",
                    "we originally wanted to have a picnic",
                    ("inversion",),
                ),
                ("am Samstag", "on Saturday", ("dative",)),
                ("im Park", "in the park", ("dative",)),
            ],
        ),
        sentence(
            "rainy-picnic", 2,
            "Als es plötzlich stark regnete, sind wir zu meiner Schwester gefahren.",
            "When it suddenly rained heavily, we went to my sister's place.",
            [
                word("als", "when", "conjunction", "subordinating"),
                word("es", "it", "personal pronoun", "subject"),
                word("plötzlich", "suddenly", "adverb"),
                word("stark", "heavily", "adverb"),
                word("regnete", "rained", "verb", "simple past"),
                word("sind", "are", "auxiliary", "present"),
                word("wir", "we", "personal pronoun", "subject"),
                word("zu", "to", "preposition", "dative"),
                word("mein", "my", "possessive", forms=("meiner",)),
                word("die Schwester", "sister", "fem.", forms=("Schwester",)),
                word("gefahren", "went/travelled", "past participle", "irregular"),
            ],
            [
                ("Als es plötzlich stark regnete", "when it suddenly rained heavily", ("subordinate clause", "verb-final")),
                ("zu meiner Schwester", "to my sister's place", ("dative",)),
                ("sind wir ... gefahren", "we went/travelled", ("perfect", "inversion")),
            ],
        ),
        sentence(
            "rainy-picnic", 3,
            "Dort haben wir zusammen gekocht und bis spät am Abend geredet.",
            "There we cooked together and talked until late in the evening.",
            [
                word("dort", "there", "adverb", "place"),
                word("haben", "have", "auxiliary", "present"),
                word("wir", "we", "personal pronoun", "subject"),
                word("zusammen", "together", "adverb"),
                word("gekocht", "cooked", "past participle", "regular"),
                word("und", "and", "conjunction", "coordinating"),
                word("bis", "until", "preposition"),
                word("spät", "late", "adverb", "time"),
                word("an", "in", "preposition", "dative", forms=("am",)),
                word("der Abend", "evening", "masc.", forms=("Abend",)),
                word("geredet", "talked", "past participle", "regular"),
            ],
            [
                (
                    "Dort haben wir ... gekocht und ... geredet",
                    "there we cooked and talked",
                    ("perfect", "inversion"),
                ),
                ("am Abend", "in the evening", ("dative",)),
                ("bis spät am Abend", "until late in the evening", ("time",)),
            ],
        ),
    ],
)


LOST_WALLET = Lesson(
    id="lost-wallet",
    title="Der verlorene Geldbeutel",
    english_title="The lost wallet",
    level="A2",
    audio_path="assets/audio/lost-wallet.wav",
    initial_question="Wo wurde Laras Geldbeutel gefunden?",
    sentences=[
        sentence(
            "lost-wallet", 1,
            "Auf dem Weg zur Arbeit bemerkte Lara, dass ihr Geldbeutel fehlte.",
            "On the way to work, Lara noticed that her wallet was missing.",
            [
                word("auf", "on", "preposition", "dative"),
                word("der Weg", "way", "masc.", forms=("Weg", "dem")),
                word("zu", "to", "preposition", "dative", forms=("zur",)),
                word("die Arbeit", "work", "fem.", forms=("Arbeit",)),
                word("bemerkte", "noticed", "verb", "simple past"),
                word("Lara", "Lara", "proper noun"),
                word("dass", "that", "conjunction", "subordinating"),
                word("ihr", "her", "possessive"),
                word("der Geldbeutel", "wallet", "masc.", "compound noun", forms=("Geldbeutel",)),
                word("fehlte", "was missing", "verb", "simple past"),
            ],
            [
                ("Auf dem Weg", "on the way", ("dative",)),
                ("zur Arbeit", "to work", ("dative",)),
                ("dass ihr Geldbeutel fehlte", "that her wallet was missing", ("subordinate clause", "verb-final")),
            ],
        ),
        sentence(
            "lost-wallet", 2,
            "Sie rief im Café an, das sie am Morgen besucht hatte.",
            "She called the café that she had visited that morning.",
            [
                word("sie", "she", "personal pronoun", "subject"),
                word("rief", "called", "verb", "separable", "simple past"),
                word("in", "in/at", "preposition", "dative", forms=("im",)),
                word("das Café", "café", "neuter", forms=("Café",)),
                word("an", "up", "particle"),
                word("das", "that", "relative pronoun"),
                word("sie", "she", "personal pronoun", "subject"),
                word("an", "in/on", "preposition", "dative", forms=("am",)),
                word("der Morgen", "morning", "masc.", forms=("Morgen",)),
                word("besucht", "visited", "past participle", "regular"),
                word("hatte", "had", "auxiliary", "simple past"),
            ],
            [
                ("rief ... an", "called", ("separable",)),
                ("im Café", "at the café", ("dative",)),
                ("am Morgen", "in the morning", ("dative",)),
                ("das sie ... besucht hatte", "that she had visited", ("subordinate clause", "pluperfect")),
            ],
        ),
        sentence(
            "lost-wallet", 3,
            "Zum Glück hatte eine Mitarbeiterin ihn gefunden und sicher aufbewahrt.",
            "Luckily, an employee had found it and kept it safe.",
            [
                word("zu", "to", "preposition", "dative", forms=("zum",)),
                word("das Glück", "luck", "neuter", forms=("Glück",)),
                word("hatte", "had", "auxiliary", "simple past"),
                word("eine", "a", "article"),
                word("die Mitarbeiterin", "female employee", "fem.", forms=("Mitarbeiterin",)),
                word("ihn", "it", "personal pronoun", "direct object"),
                word("gefunden", "found", "past participle", "irregular"),
                word("und", "and", "conjunction", "coordinating"),
                word("sicher", "safely", "adverb"),
                word("aufbewahrt", "kept/stored", "past participle", "separable"),
            ],
            [
                ("Zum Glück", "luckily", ("fixed phrase",)),
                (
                    "hatte ... gefunden und ... aufbewahrt",
                    "had found it and kept it safe",
                    ("pluperfect",),
                ),
            ],
        ),
    ],
)


BURNT_SOUP = Lesson(
    id="burnt-soup",
    title="Die angebrannte Suppe",
    english_title="The burnt soup",
    level="A2",
    audio_path="assets/audio/burnt-soup.wav",
    initial_question="Was aßen die Freunde am Ende?",
    sentences=[
        sentence(
            "burnt-soup", 1,
            "Mina wollte für ihre Freunde eine Gemüsesuppe kochen.",
            "Mina wanted to cook vegetable soup for her friends.",
            [
                word("Mina", "Mina", "proper noun"),
                word("wollte", "wanted", "modal verb", "simple past"),
                word("für", "for", "preposition", "accusative"),
                word("ihr", "her", "possessive", forms=("ihre",)),
                word("der Freund", "friend", "masc.", "plural", forms=("Freunde",)),
                word("eine", "a", "article"),
                word("die Gemüsesuppe", "vegetable soup", "fem.", "compound noun", forms=("Gemüsesuppe",)),
                word("kochen", "to cook", "verb", "infinitive"),
            ],
            [
                ("Mina wollte ... kochen", "Mina wanted to cook", ("verb-second",)),
                ("für ihre Freunde", "for her friends", ("accusative",)),
            ],
        ),
        sentence(
            "burnt-soup", 2,
            "Leider vergaß sie den Topf auf dem Herd, und die Suppe brannte an.",
            "Unfortunately, she forgot the pot on the stove, and the soup burned.",
            [
                word("leider", "unfortunately", "adverb"),
                word("vergaß", "forgot", "verb", "irregular", "simple past"),
                word("sie", "she", "personal pronoun", "subject"),
                word("der Topf", "pot", "masc.", forms=("den", "Topf")),
                word("auf", "on", "preposition", "dative"),
                word("der Herd", "stove", "masc.", forms=("dem", "Herd")),
                word("und", "and", "conjunction", "coordinating"),
                word("die Suppe", "soup", "fem.", forms=("Suppe",)),
                word("brannte", "burned", "verb", "separable", "simple past"),
                word("an", "up", "particle"),
            ],
            [
                ("auf dem Herd", "on the stove", ("dative",)),
                ("die Suppe brannte an", "the soup burned", ("main clause",)),
            ],
        ),
        sentence(
            "burnt-soup", 3,
            "Am Ende bestellten alle Pizza und lachten über den kleinen Unfall.",
            "In the end, everyone ordered pizza and laughed about the small mishap.",
            [
                word("an", "at", "preposition", "dative", forms=("am",)),
                word("das Ende", "end", "neuter", forms=("Ende",)),
                word("bestellten", "ordered", "verb", "regular", "simple past"),
                word("alle", "everyone", "personal pronoun"),
                word("die Pizza", "pizza", "fem.", forms=("Pizza",)),
                word("und", "and", "conjunction", "coordinating"),
                word("lachten", "laughed", "verb", "regular", "simple past"),
                word("über", "about", "preposition", "accusative"),
                word("klein", "small", "adjective", forms=("kleinen",)),
                word("der Unfall", "mishap/accident", "masc.", forms=("den", "Unfall")),
            ],
            [
                ("Am Ende", "in the end", ("fixed phrase", "time")),
                ("über den kleinen Unfall", "about the small mishap", ("accusative",)),
            ],
        ),
    ],
)


APARTMENT_SEARCH = Lesson(
    id="apartment-search",
    title="Die Wohnungssuche",
    english_title="The apartment search",
    level="B1",
    audio_path="assets/audio/apartment-search.wav",
    initial_question="Warum schickte David trotzdem seine Unterlagen?",
    sentences=[
        sentence(
            "apartment-search", 1,
            "Seit mehreren Wochen sucht David eine bezahlbare Wohnung in der Innenstadt.",
            "David has been looking for an affordable apartment downtown for several weeks.",
            [
                word("seit", "for/since", "preposition", "dative"),
                word("mehrere", "several", "determiner", forms=("mehreren",)),
                word("die Woche", "week", "fem.", "plural", forms=("Wochen",)),
                word("sucht", "is looking for", "verb", "present"),
                word("David", "David", "proper noun"),
                word("eine", "an", "article"),
                word("bezahlbar", "affordable", "adjective", forms=("bezahlbare",)),
                word("die Wohnung", "apartment", "fem.", forms=("Wohnung",)),
                word("in", "in", "preposition", "dative"),
                word("die Innenstadt", "city centre", "fem.", "compound noun", forms=("der", "Innenstadt")),
            ],
            [
                ("Seit mehreren Wochen", "for several weeks", ("dative",)),
                (
                    "sucht David eine bezahlbare Wohnung",
                    "David is looking for an affordable apartment",
                    ("inversion",),
                ),
                ("in der Innenstadt", "in the city centre", ("dative",)),
            ],
        ),
        sentence(
            "apartment-search", 2,
            "Gestern besichtigte er eine helle Wohnung, die einen kleinen Balkon hatte.",
            "Yesterday he viewed a bright apartment that had a small balcony.",
            [
                word("gestern", "yesterday", "adverb", "time"),
                word("besichtigte", "viewed", "verb", "regular", "simple past"),
                word("er", "he", "personal pronoun", "subject"),
                word("eine", "a", "article"),
                word("hell", "bright", "adjective", forms=("helle",)),
                word("die Wohnung", "apartment", "fem.", forms=("Wohnung",)),
                word("die", "that/which", "relative pronoun"),
                word("einen", "a", "article"),
                word("klein", "small", "adjective", forms=("kleinen",)),
                word("der Balkon", "balcony", "masc.", forms=("Balkon",)),
                word("hatte", "had", "verb", "simple past"),
            ],
            [
                (
                    "Gestern besichtigte er eine helle Wohnung",
                    "yesterday he viewed a bright apartment",
                    ("inversion", "simple past"),
                ),
                (
                    "die einen kleinen Balkon hatte",
                    "that had a small balcony",
                    ("subordinate clause", "verb-final"),
                ),
            ],
        ),
        sentence(
            "apartment-search", 3,
            "Obwohl die Miete hoch war, schickte er der Vermieterin sofort seine Unterlagen.",
            "Although the rent was high, he immediately sent the landlady his documents.",
            [
                word("obwohl", "although", "conjunction", "subordinating"),
                word("die Miete", "rent", "fem.", forms=("Miete",)),
                word("hoch", "high", "adjective"),
                word("war", "was", "verb", "simple past"),
                word("schickte", "sent", "verb", "regular", "simple past"),
                word("er", "he", "personal pronoun", "subject"),
                word("die Vermieterin", "landlady", "fem.", forms=("der", "Vermieterin")),
                word("sofort", "immediately", "adverb"),
                word("sein", "his", "possessive", forms=("seine",)),
                word("die Unterlage", "document", "fem.", "plural", forms=("Unterlagen",)),
            ],
            [
                ("Obwohl die Miete hoch war", "although the rent was high", ("subordinate clause", "verb-final")),
                ("der Vermieterin", "to the landlady", ("dative",)),
                ("seine Unterlagen", "his documents", ("plural",)),
                (
                    "schickte er der Vermieterin sofort seine Unterlagen",
                    "he immediately sent the landlady his documents",
                    ("inversion", "simple past"),
                ),
            ],
        ),
        sentence(
            "apartment-search", 4,
            "Nun wartet er gespannt auf ihre Antwort.",
            "Now he is eagerly waiting for her reply.",
            [
                word("nun", "now", "adverb", "time"),
                word("wartet", "is waiting", "verb", "present"),
                word("er", "he", "personal pronoun", "subject"),
                word("gespannt", "eagerly/with anticipation", "adverb"),
                word("auf", "for", "preposition", "accusative"),
                word("ihr", "her", "possessive", forms=("ihre",)),
                word("die Antwort", "reply", "fem.", forms=("Antwort",)),
            ],
            [
                ("Nun wartet er gespannt", "now he waits eagerly", ("inversion",)),
                ("auf ihre Antwort", "for her reply", ("accusative",)),
                (
                    "wartet er gespannt auf ihre Antwort",
                    "he eagerly waits for her reply",
                    ("accusative",),
                ),
            ],
        ),
    ],
)


LEARNING_ROUTINE = Lesson(
    id="learning-routine",
    title="Eine neue Lernroutine",
    english_title="A new learning routine",
    level="B1",
    audio_path="assets/audio/learning-routine.wav",
    initial_question="Was macht Sofia heute anders als früher?",
    sentences=[
        sentence(
            "learning-routine", 1,
            "Früher lernte Sofia neue Wörter nur aus langen Listen.",
            "Sofia used to learn new words only from long lists.",
            [
                word("früher", "in the past", "adverb", "time"),
                word("lernte", "learned", "verb", "regular", "simple past"),
                word("Sofia", "Sofia", "proper noun"),
                word("neu", "new", "adjective", forms=("neue",)),
                word("das Wort", "word", "neuter", "plural", forms=("Wörter",)),
                word("nur", "only", "adverb"),
                word("aus", "from", "preposition", "dative"),
                word("lang", "long", "adjective", forms=("langen",)),
                word("die Liste", "list", "fem.", "plural", forms=("Listen",)),
            ],
            [
                ("neue Wörter", "new words", ("plural",)),
                (
                    "Früher lernte Sofia neue Wörter",
                    "Sofia used to learn new words",
                    ("inversion", "simple past"),
                ),
                ("nur aus langen Listen", "only from long lists", ("dative",)),
            ],
        ),
        sentence(
            "learning-routine", 2,
            "Inzwischen schreibt sie kurze Sätze und hört jeden Morgen einen deutschen Podcast.",
            "By now, she writes short sentences and listens to a German podcast every morning.",
            [
                word("inzwischen", "by now", "adverb", "time"),
                word("schreibt", "writes", "verb", "irregular", "present"),
                word("sie", "she", "personal pronoun", "subject"),
                word("kurz", "short", "adjective", forms=("kurze",)),
                word("der Satz", "sentence", "masc.", "plural", forms=("Sätze",)),
                word("und", "and", "conjunction", "coordinating"),
                word("hört", "listens to", "verb", "regular", "present"),
                word("jeden", "every", "determiner"),
                word("der Morgen", "morning", "masc.", forms=("Morgen",)),
                word("einen", "a", "article"),
                word("deutsch", "German", "adjective", forms=("deutschen",)),
                word("der Podcast", "podcast", "masc.", forms=("Podcast",)),
            ],
            [
                ("kurze Sätze", "short sentences", ("plural",)),
                ("schreibt sie kurze Sätze", "she writes short sentences", ("inversion",)),
                ("jeden Morgen", "every morning", ("time",)),
                (
                    "hört jeden Morgen einen deutschen Podcast",
                    "listens to a German podcast every morning",
                    ("time",),
                ),
            ],
        ),
        sentence(
            "learning-routine", 3,
            "Wenn sie einen Ausdruck nicht versteht, notiert sie ihn und sucht später ein Beispiel.",
            "When she does not understand an expression, she writes it down and later looks for an example.",
            [
                word("wenn", "when/if", "conjunction", "subordinating"),
                word("sie", "she", "personal pronoun", "subject"),
                word("einen", "an", "article"),
                word("der Ausdruck", "expression", "masc.", forms=("Ausdruck",)),
                word("nicht", "not", "particle", "negation"),
                word("versteht", "understands", "verb", "irregular", "present"),
                word("notiert", "writes down", "verb", "regular", "present"),
                word("ihn", "it", "personal pronoun", "direct object"),
                word("und", "and", "conjunction", "coordinating"),
                word("sucht", "looks for", "verb", "present"),
                word("später", "later", "adverb", "time"),
                word("ein", "an", "article"),
                word("das Beispiel", "example", "neuter", forms=("Beispiel",)),
            ],
            [
                (
                    "Wenn sie einen Ausdruck nicht versteht",
                    "when she does not understand an expression",
                    ("subordinate clause", "verb-final", "negation"),
                ),
                ("notiert sie ihn", "she writes it down", ("inversion",)),
                (
                    "sucht später ein Beispiel",
                    "later looks for an example",
                    ("verb-second",),
                ),
            ],
        ),
        sentence(
            "learning-routine", 4,
            "Dadurch kann sie sich die Wörter besser merken.",
            "That helps her remember the words better.",
            [
                word("dadurch", "as a result/through that", "adverb", "connector"),
                word("kann", "can", "modal verb", "present"),
                word("sie", "she", "personal pronoun", "subject"),
                word("sich", "herself", "reflexive pronoun"),
                word("die", "the", "article"),
                word("das Wort", "word", "neuter", "plural", forms=("Wörter",)),
                word("besser", "better", "adverb", "comparative"),
                word("merken", "to remember", "verb", "infinitive"),
            ],
            [
                (
                    "sich die Wörter besser merken",
                    "remember the words better",
                    ("reflexive", "infinitive"),
                ),
                (
                    "Dadurch kann sie sich ... merken",
                    "as a result, she can remember",
                    ("inversion",),
                ),
            ],
        ),
    ],
)


CHANGED_PLATFORM = Lesson(
    id="changed-platform",
    title="Der Gleiswechsel",
    english_title="The platform change",
    level="B1",
    audio_path="assets/audio/changed-platform.wav",
    initial_question="Wie half die erzählende Person einer Reisenden?",
    sentences=[
        sentence(
            "changed-platform", 1,
            "Wegen einer Baustelle wurde unser Zug kurzfristig auf ein anderes Gleis verlegt.",
            "Because of construction work, our train was moved to another platform at short notice.",
            [
                word("wegen", "because of", "preposition", "genitive"),
                word("eine", "a", "article", forms=("einer",)),
                word("die Baustelle", "construction site", "fem.", "compound noun", forms=("Baustelle",)),
                word("wurde", "was", "auxiliary", "simple past"),
                word("unser", "our", "possessive"),
                word("der Zug", "train", "masc.", forms=("Zug",)),
                word("kurzfristig", "at short notice", "adverb"),
                word("auf", "to/onto", "preposition", "accusative"),
                word("ein", "an", "article", forms=("ein",)),
                word("anders", "other", "adjective", forms=("anderes",)),
                word("das Gleis", "platform/track", "neuter", forms=("Gleis",)),
                word("verlegt", "moved", "past participle", "regular"),
            ],
            [
                (
                    "Wegen einer Baustelle wurde unser Zug ... verlegt",
                    "because of construction work, our train was moved",
                    ("simple past", "inversion"),
                ),
                ("Wegen einer Baustelle", "because of construction work", ("genitive",)),
                ("auf ein anderes Gleis", "onto another platform", ("accusative",)),
            ],
        ),
        sentence(
            "changed-platform", 2,
            "Viele Reisende bemerkten die Änderung erst kurz vor der Abfahrt.",
            "Many travellers noticed the change only shortly before departure.",
            [
                word("viel", "many", "adjective", forms=("Viele",)),
                word("der Reisende", "traveller", "masc.", "plural", forms=("Reisende",)),
                word("bemerkten", "noticed", "verb", "regular", "simple past"),
                word("die", "the", "article"),
                word("die Änderung", "change", "fem.", forms=("Änderung",)),
                word("erst", "only/not until", "adverb"),
                word("kurz", "shortly", "adverb"),
                word("vor", "before", "preposition", "dative"),
                word("die Abfahrt", "departure", "fem.", forms=("der", "Abfahrt")),
            ],
            [
                ("Viele Reisende", "many travellers", ("plural",)),
                (
                    "Viele Reisende bemerkten die Änderung",
                    "many travellers noticed the change",
                    ("simple past",),
                ),
                (
                    "erst kurz vor der Abfahrt",
                    "only shortly before departure",
                    ("time", "dative"),
                ),
            ],
        ),
        sentence(
            "changed-platform", 3,
            "Eine ältere Frau trug einen schweren Koffer, deshalb half ich ihr beim Einsteigen.",
            "An older woman was carrying a heavy suitcase, so I helped her board.",
            [
                word("eine", "an", "article"),
                word("alt", "old", "adjective", forms=("ältere",)),
                word("die Frau", "woman", "fem.", forms=("Frau",)),
                word("trug", "carried", "verb", "irregular", "simple past"),
                word("einen", "a", "article"),
                word("schwer", "heavy", "adjective", forms=("schweren",)),
                word("der Koffer", "suitcase", "masc.", forms=("Koffer",)),
                word("deshalb", "therefore/so", "adverb", "connector"),
                word("half", "helped", "verb", "irregular", "simple past"),
                word("ich", "I", "personal pronoun", "subject"),
                word("ihr", "her", "personal pronoun", "indirect object"),
                word("bei", "with/while", "preposition", "dative", forms=("beim",)),
                word("das Einsteigen", "boarding", "neuter", forms=("Einsteigen",)),
            ],
            [
                (
                    "trug einen schweren Koffer",
                    "was carrying a heavy suitcase",
                    ("simple past",),
                ),
                ("deshalb half ich ihr", "so I helped her", ("connector", "inversion")),
                ("beim Einsteigen", "while boarding", ("dative",)),
            ],
        ),
        sentence(
            "changed-platform", 4,
            "Trotz der Hektik fanden wir unsere reservierten Plätze rechtzeitig.",
            "Despite the rush, we found our reserved seats in time.",
            [
                word("trotz", "despite", "preposition", "genitive"),
                word("die Hektik", "rush/commotion", "fem.", forms=("der", "Hektik")),
                word("fanden", "found", "verb", "irregular", "simple past"),
                word("wir", "we", "personal pronoun", "subject"),
                word("unser", "our", "possessive", forms=("unsere",)),
                word("reserviert", "reserved", "adjective", forms=("reservierten",)),
                word("der Platz", "seat/place", "masc.", "plural", forms=("Plätze",)),
                word("rechtzeitig", "in time", "adverb", "time"),
            ],
            [
                ("Trotz der Hektik", "despite the rush", ("genitive",)),
                ("unsere reservierten Plätze", "our reserved seats", ("plural",)),
                (
                    "fanden wir unsere reservierten Plätze rechtzeitig",
                    "we found our reserved seats in time",
                    ("inversion", "simple past"),
                ),
            ],
        ),
    ],
)


COMMUNITY_GARDEN = Lesson(
    id="community-garden",
    title="Der Gemeinschaftsgarten",
    english_title="The community garden",
    level="B1",
    audio_path="assets/audio/community-garden.wav",
    initial_question="Wie hat der Garten das Viertel verändert?",
    sentences=[
        sentence(
            "community-garden", 1,
            "In unserem Viertel lag jahrelang ein ungenutztes Grundstück voller Müll.",
            "For years, an unused plot full of rubbish lay in our neighbourhood.",
            [
                word("in", "in", "preposition", "dative"),
                word("unser", "our", "possessive", forms=("unserem",)),
                word("das Viertel", "neighbourhood", "neuter", forms=("Viertel",)),
                word("lag", "lay/was located", "verb", "irregular", "simple past"),
                word("jahrelang", "for years", "adverb", "time"),
                word("ein", "an", "article"),
                word("ungenutzt", "unused", "adjective", forms=("ungenutztes",)),
                word("das Grundstück", "plot of land", "neuter", "compound noun", forms=("Grundstück",)),
                word("voll", "full of", "adjective", forms=("voller",)),
                word("der Müll", "rubbish", "masc.", forms=("Müll",)),
            ],
            [
                ("In unserem Viertel", "in our neighbourhood", ("dative",)),
                ("voller Müll", "full of rubbish", ("genitive",)),
                (
                    "ein ungenutztes Grundstück voller Müll",
                    "an unused plot of land full of rubbish",
                    ("genitive",),
                ),
                (
                    "lag jahrelang ein ungenutztes Grundstück",
                    "an unused plot of land lay there for years",
                    ("simple past",),
                ),
            ],
        ),
        sentence(
            "community-garden", 2,
            "Einige Nachbarn beschlossen, dort gemeinsam einen kleinen Garten anzulegen.",
            "Several neighbours decided to create a small garden there together.",
            [
                word("einige", "several", "determiner"),
                word("der Nachbar", "neighbour", "masc.", "plural", forms=("Nachbarn",)),
                word("beschlossen", "decided", "verb", "irregular", "simple past"),
                word("dort", "there", "adverb", "place"),
                word("gemeinsam", "together", "adverb"),
                word("einen", "a", "article"),
                word("klein", "small", "adjective", forms=("kleinen",)),
                word("der Garten", "garden", "masc.", forms=("Garten",)),
                word("anzulegen", "to create/set up", "verb", "separable", "infinitive"),
            ],
            [
                (
                    "einen kleinen Garten anzulegen",
                    "to create a small garden",
                    ("infinitive",),
                ),
                (
                    "dort gemeinsam einen kleinen Garten anzulegen",
                    "to create a small garden there together",
                    ("infinitive",),
                ),
                (
                    "Einige Nachbarn beschlossen ... anzulegen",
                    "several neighbours decided to create",
                    ("verb-second",),
                ),
            ],
        ),
        sentence(
            "community-garden", 3,
            "Seitdem bauen wir Gemüse an und organisieren einmal im Monat ein gemeinsames Frühstück.",
            "Since then, we have been growing vegetables and organizing a shared breakfast once a month.",
            [
                word("seitdem", "since then", "adverb", "connector"),
                word("bauen", "grow", "verb", "separable", "present"),
                word("wir", "we", "personal pronoun", "subject"),
                word("das Gemüse", "vegetables/produce", "neuter", forms=("Gemüse",)),
                word("an", "up", "particle"),
                word("und", "and", "conjunction", "coordinating"),
                word("organisieren", "organize", "verb", "regular", "present"),
                word("einmal", "once", "adverb", "frequency"),
                word("in", "in/per", "preposition", "dative", forms=("im",)),
                word("der Monat", "month", "masc.", forms=("Monat",)),
                word("ein", "a", "article"),
                word("gemeinsam", "shared", "adjective", forms=("gemeinsames",)),
                word("das Frühstück", "breakfast", "neuter", forms=("Frühstück",)),
            ],
            [
                ("bauen ... an", "grow", ("separable",)),
                (
                    "Seitdem bauen wir Gemüse an",
                    "since then, we have been growing vegetables",
                    ("inversion", "separable"),
                ),
                ("einmal im Monat", "once a month", ("frequency", "dative")),
                (
                    "organisieren ... ein gemeinsames Frühstück",
                    "organize a shared breakfast",
                    ("present",),
                ),
            ],
        ),
        sentence(
            "community-garden", 4,
            "Das Projekt hat nicht nur den Ort verändert, sondern auch die Menschen näher zusammengebracht.",
            "The project has changed not only the place, but also brought the people closer together.",
            [
                word("das Projekt", "project", "neuter", forms=("Das", "Projekt")),
                word("hat", "has", "auxiliary", "present"),
                word("nicht", "not", "particle", "negation"),
                word("nur", "only", "adverb"),
                word("der Ort", "place", "masc.", forms=("den", "Ort")),
                word("verändert", "changed", "past participle", "regular"),
                word("sondern", "but rather", "conjunction", "coordinating"),
                word("auch", "also", "adverb"),
                word("die", "the", "article"),
                word("der Mensch", "person", "masc.", "plural", forms=("Menschen",)),
                word("nah", "closer", "adverb", "comparative", forms=("näher",)),
                word("zusammengebracht", "brought together", "past participle", "separable"),
            ],
            [
                ("hat ... verändert", "has changed", ("perfect",)),
                ("nicht nur ... sondern auch", "not only ... but also", ("fixed phrase", "connector")),
                ("hat ... zusammengebracht", "has brought together", ("perfect",)),
            ],
        ),
    ],
)


TEAM_MEETING = Lesson(
    id="team-meeting",
    title="Die schwierige Teambesprechung",
    english_title="The difficult team meeting",
    level="B1-B2",
    audio_path="assets/audio/team-meeting.wav",
    initial_question="Wie kam das Team zu einem realistischen Plan?",
    sentences=[
        grouped_sentence(
            "team-meeting", 1,
            "Während der wöchentlichen Besprechung stellte die Projektleiterin einen neuen Zeitplan vor.",
            "During the weekly meeting, the project manager presented a new schedule.",
            [
                group(
                    word("während", "during", "preposition", "genitive"),
                    word("wöchentlich", "weekly", "adjective", forms=("wöchentlichen",)),
                    word("die Besprechung", "meeting", "fem.", forms=("der", "Besprechung")),
                    phrase(
                        "Während der wöchentlichen Besprechung",
                        "during the weekly meeting",
                        "genitive",
                    ),
                ),
                group(
                    word("stellte", "presented", "verb", "separable", "simple past"),
                    word("die Projektleiterin", "project manager", "fem.", "compound noun", forms=("Projektleiterin",)),
                    word("vor", "forward", "particle"),
                    phrase("stellte ... vor", "presented", "separable"),
                    phrase(
                        "stellte die Projektleiterin ... vor",
                        "the project manager presented",
                        "inversion",
                    ),
                ),
                group(
                    word("einen", "a", "article"),
                    word("neu", "new", "adjective", forms=("neuen",)),
                    word("der Zeitplan", "schedule", "masc.", "compound noun", forms=("Zeitplan",)),
                ),
            ],
        ),
        grouped_sentence(
            "team-meeting", 2,
            "Mehrere Kollegen warnten jedoch davor, dass das Team dadurch ständig unter Druck stehen würde.",
            "However, several colleagues warned that this would leave the team under constant pressure.",
            [
                group(
                    word("mehrere", "several", "determiner"),
                    word("der Kollege", "colleague", "masc.", "plural", forms=("Kollegen",)),
                    word("warnten", "warned", "verb", "regular", "simple past"),
                    word("jedoch", "however", "adverb", "connector"),
                    word("davor", "against/about it", "adverb"),
                    phrase("Mehrere Kollegen", "several colleagues", "plural"),
                    phrase(
                        "Mehrere Kollegen warnten jedoch davor",
                        "several colleagues warned about it, however",
                        "main clause",
                    ),
                ),
                group(
                    word("dass", "that", "conjunction", "subordinating"),
                    word("das Team", "team", "neuter", forms=("Team",)),
                    word("dadurch", "as a result", "adverb", "connector"),
                    word("ständig", "constantly", "adverb", "frequency"),
                    word("unter", "under", "preposition", "dative"),
                    word("der Druck", "pressure", "masc.", forms=("Druck",)),
                    word("stehen", "to be/stand", "verb", "infinitive"),
                    word("würde", "would", "auxiliary", "subjunctive"),
                    phrase("unter Druck", "under pressure", "dative", "fixed phrase"),
                    phrase(
                        "unter Druck stehen würde",
                        "would be under pressure",
                        "subjunctive",
                        "verb-final",
                    ),
                    phrase(
                        "dass das Team dadurch ständig unter Druck stehen würde",
                        "that the team would therefore be under constant pressure",
                        "subordinate clause",
                        "verb-final",
                    ),
                ),
            ],
        ),
        grouped_sentence(
            "team-meeting", 3,
            "Nachdem alle ihre Bedenken erklärt hatten, wurden die Aufgaben neu verteilt.",
            "After everyone had explained their concerns, the tasks were redistributed.",
            [
                group(
                    word("nachdem", "after", "conjunction", "subordinating"),
                    word("alle", "everyone", "personal pronoun", "subject"),
                    word("ihr", "their", "possessive", forms=("ihre",)),
                    word("das Bedenken", "concern", "neuter", "plural", forms=("Bedenken",)),
                    word("erklärt", "explained", "past participle", "regular"),
                    word("hatten", "had", "auxiliary", "simple past"),
                    phrase("ihre Bedenken", "their concerns", "plural"),
                    phrase(
                        "ihre Bedenken erklärt hatten",
                        "had explained their concerns",
                        "pluperfect",
                        "verb-final",
                    ),
                    phrase(
                        "Nachdem alle ihre Bedenken erklärt hatten",
                        "after everyone had explained their concerns",
                        "subordinate clause",
                        "pluperfect",
                    ),
                ),
                group(
                    word("wurden", "were", "auxiliary", "simple past"),
                    word("die", "the", "article"),
                    word("die Aufgabe", "task", "fem.", "plural", forms=("Aufgaben",)),
                    word("neu", "anew", "adverb"),
                    word("verteilt", "distributed", "past participle", "regular"),
                    phrase(
                        "wurden die Aufgaben neu verteilt",
                        "the tasks were redistributed",
                        "main clause",
                        "inversion",
                    ),
                ),
            ],
        ),
        grouped_sentence(
            "team-meeting", 4,
            "So entstand ein realistischer Plan, mit dem schließlich jeder einverstanden war.",
            "This resulted in a realistic plan that everyone ultimately agreed with.",
            [
                group(
                    word("so", "in this way", "adverb", "connector"),
                    word("entstand", "emerged/resulted", "verb", "irregular", "simple past"),
                    word("ein", "a", "article"),
                    word("realistisch", "realistic", "adjective", forms=("realistischer",)),
                    word("der Plan", "plan", "masc.", forms=("Plan",)),
                    phrase(
                        "So entstand ein realistischer Plan",
                        "this produced a realistic plan",
                        "inversion",
                    ),
                ),
                group(
                    word("mit", "with", "preposition", "dative"),
                    word("der", "which", "relative pronoun", forms=("dem",)),
                    word("schließlich", "ultimately", "adverb", "time"),
                    word("jeder", "everyone", "personal pronoun", "subject"),
                    word("einverstanden", "in agreement", "adjective"),
                    word("war", "was", "verb", "simple past"),
                    phrase(
                        "mit dem ... einverstanden",
                        "in agreement with it",
                        "fixed phrase",
                        "dative",
                    ),
                    phrase(
                        "mit dem schließlich jeder einverstanden war",
                        "which everyone ultimately agreed with",
                        "subordinate clause",
                        "verb-final",
                    ),
                ),
            ],
        ),
    ],
)


DIGITAL_BREAK = Lesson(
    id="digital-break",
    title="Eine digitale Pause",
    english_title="A digital break",
    level="B2",
    audio_path="assets/audio/digital-break.wav",
    initial_question="Welche Wirkung hatte Maras digitale Pause?",
    sentences=[
        grouped_sentence(
            "digital-break", 1,
            "Nachdem Mara bemerkt hatte, wie oft sie gedankenlos auf ihr Handy schaute, beschloss sie, eine digitale Pause einzulegen.",
            "After Mara had noticed how often she mindlessly looked at her phone, she decided to take a digital break.",
            [
                group(
                    word("nachdem", "after", "conjunction", "subordinating"),
                    word("Mara", "Mara", "proper noun"),
                    word("bemerkt", "noticed", "past participle", "regular"),
                    word("hatte", "had", "auxiliary", "simple past"),
                    phrase("bemerkt hatte", "had noticed", "pluperfect"),
                    phrase("Mara bemerkt hatte", "Mara had noticed", "verb-final"),
                    phrase(
                        "Nachdem Mara bemerkt hatte",
                        "after Mara had noticed",
                        "subordinate clause",
                        "pluperfect",
                    ),
                ),
                group(
                    word("wie", "how", "conjunction", "subordinating"),
                    word("oft", "often", "adverb", "frequency"),
                    word("sie", "she", "personal pronoun", "subject"),
                    word("gedankenlos", "mindlessly", "adverb"),
                    word("auf", "at", "preposition", "accusative"),
                    word("ihr", "her", "possessive"),
                    word("das Handy", "mobile phone", "neuter", forms=("Handy",)),
                    word("schaute", "looked", "verb", "regular", "simple past"),
                    phrase("auf ihr Handy", "at her phone", "accusative"),
                    phrase(
                        "sie ... auf ihr Handy schaute",
                        "she looked at her phone",
                        "verb-final",
                    ),
                    phrase(
                        "wie oft sie gedankenlos auf ihr Handy schaute",
                        "how often she mindlessly looked at her phone",
                        "subordinate clause",
                        "verb-final",
                    ),
                ),
                group(
                    word("beschloss", "decided", "verb", "irregular", "simple past"),
                    word("sie", "she", "personal pronoun", "subject"),
                    word("eine", "a", "article"),
                    word("digital", "digital", "adjective", forms=("digitale",)),
                    word("die Pause", "break", "fem.", forms=("Pause",)),
                    word("einzulegen", "to take", "verb", "separable", "infinitive"),
                    phrase(
                        "eine digitale Pause einzulegen",
                        "to take a digital break",
                        "infinitive",
                    ),
                    phrase(
                        "beschloss sie, eine digitale Pause einzulegen",
                        "she decided to take a digital break",
                        "inversion",
                    ),
                ),
            ],
        ),
        grouped_sentence(
            "digital-break", 2,
            "Eine Woche lang schaltete sie abends alle Benachrichtigungen aus und ließ das Telefon im Flur.",
            "For one week, she turned off all notifications in the evening and left the phone in the hallway.",
            [
                group(
                    word("eine", "one", "article"),
                    word("die Woche", "week", "fem.", forms=("Woche",)),
                    word("lang", "for", "adverb", "time"),
                    phrase("Eine Woche lang", "for one week", "time"),
                ),
                group(
                    word("schaltete", "switched", "verb", "separable", "simple past"),
                    word("sie", "she", "personal pronoun", "subject"),
                    word("abends", "in the evenings", "adverb", "time"),
                    word("alle", "all", "determiner"),
                    word("die Benachrichtigung", "notification", "fem.", "plural", forms=("Benachrichtigungen",)),
                    word("aus", "off", "particle"),
                    phrase("alle Benachrichtigungen", "all notifications", "plural"),
                    phrase(
                        "schaltete ... alle Benachrichtigungen aus",
                        "switched off all notifications",
                        "separable",
                    ),
                    phrase(
                        "schaltete sie abends alle Benachrichtigungen aus",
                        "she switched off all notifications in the evenings",
                        "main clause",
                    ),
                ),
                group(
                    word("und", "and", "conjunction", "coordinating"),
                    word("ließ", "left", "verb", "irregular", "simple past"),
                    word("das Telefon", "telephone", "neuter", forms=("Telefon",)),
                    word("in", "in", "preposition", "dative", forms=("im",)),
                    word("der Flur", "hallway", "masc.", forms=("Flur",)),
                    phrase("im Flur", "in the hallway", "dative"),
                    phrase(
                        "ließ das Telefon im Flur",
                        "left the phone in the hallway",
                        "main clause",
                    ),
                    phrase(
                        "und ließ das Telefon im Flur",
                        "and left the phone in the hallway",
                        "coordinating",
                    ),
                ),
            ],
        ),
        grouped_sentence(
            "digital-break", 3,
            "Anfangs fiel es ihr schwer, die ungewohnte Stille auszuhalten.",
            "At first, she found it difficult to tolerate the unfamiliar silence.",
            [
                group(
                    word("anfangs", "at first", "adverb", "time"),
                    word("fiel", "was/felt", "verb", "irregular", "simple past"),
                    word("es", "it", "personal pronoun", "subject"),
                    word("ihr", "to her", "personal pronoun", "indirect object"),
                    word("schwer", "difficult", "adjective"),
                    phrase("fiel es ihr schwer", "she found it difficult", "fixed phrase"),
                    phrase(
                        "Anfangs fiel es ihr schwer",
                        "at first, she found it difficult",
                        "inversion",
                    ),
                ),
                group(
                    word("die", "the", "article"),
                    word("ungewohnt", "unfamiliar", "adjective", forms=("ungewohnte",)),
                    word("die Stille", "silence", "fem.", forms=("Stille",)),
                    word("auszuhalten", "to tolerate/endure", "verb", "separable", "infinitive"),
                    phrase(
                        "die ungewohnte Stille auszuhalten",
                        "to tolerate the unfamiliar silence",
                        "infinitive",
                    ),
                ),
            ],
        ),
        grouped_sentence(
            "digital-break", 4,
            "Doch bald stellte sie fest, dass sie konzentrierter arbeitete und bewusster mit ihrer Zeit umging.",
            "But she soon realized that she worked with more focus and used her time more consciously.",
            [
                group(
                    word("doch", "but/however", "conjunction", "coordinating"),
                    word("bald", "soon", "adverb", "time"),
                    word("stellte", "realized", "verb", "separable", "simple past"),
                    word("sie", "she", "personal pronoun", "subject"),
                    word("fest", "firmly", "particle"),
                    phrase("stellte ... fest", "realized", "separable"),
                    phrase(
                        "Doch bald stellte sie fest",
                        "but she soon realized",
                        "main clause",
                    ),
                ),
                group(
                    word("dass", "that", "conjunction", "subordinating"),
                    word("sie", "she", "personal pronoun", "subject"),
                    word("konzentriert", "with focus", "adverb", "comparative", forms=("konzentrierter",)),
                    word("arbeitete", "worked", "verb", "regular", "simple past"),
                    word("und", "and", "conjunction", "coordinating"),
                    word("bewusst", "consciously", "adverb", "comparative", forms=("bewusster",)),
                    word("mit", "with", "preposition", "dative"),
                    word("ihr", "her", "possessive", forms=("ihrer",)),
                    word("die Zeit", "time", "fem.", forms=("Zeit",)),
                    word("umging", "handled/dealt with", "verb", "separable", "simple past"),
                    phrase(
                        "konzentrierter arbeitete",
                        "worked with more focus",
                        "comparative",
                    ),
                    phrase(
                        "mit ihrer Zeit umging",
                        "managed her time",
                        "dative",
                    ),
                    phrase(
                        "bewusster mit ihrer Zeit umging",
                        "managed her time more consciously",
                        "comparative",
                    ),
                    phrase(
                        "dass sie konzentrierter arbeitete und bewusster mit ihrer Zeit umging",
                        "that she worked with more focus and managed her time more consciously",
                        "subordinate clause",
                        "verb-final",
                    ),
                ),
            ],
        ),
    ],
)


CAR_FREE_CENTRE = Lesson(
    id="car-free-centre",
    title="Eine autofreie Innenstadt?",
    english_title="A car-free city centre?",
    level="B2",
    audio_path="assets/audio/car-free-centre.wav",
    initial_question="Welche Argumente gibt es für und gegen den Plan?",
    sentences=[
        grouped_sentence(
            "car-free-centre", 1,
            "Der Stadtrat plant, eine viel befahrene Straße im Zentrum teilweise für Autos zu sperren.",
            "The city council plans to partially close a busy road in the centre to cars.",
            [
                group(
                    word("der Stadtrat", "city council", "masc.", "compound noun", forms=("Der", "Stadtrat")),
                    word("plant", "plans", "verb", "regular", "present"),
                    word("teilweise", "partially", "adverb"),
                    word("für", "to/for", "preposition", "accusative"),
                    word("das Auto", "car", "neuter", "plural", forms=("Autos",)),
                    word("zu", "to", "particle"),
                    word("sperren", "to close/block", "verb", "infinitive"),
                    phrase("für Autos", "to cars", "accusative"),
                    phrase(
                        "teilweise für Autos zu sperren",
                        "to close partially to cars",
                        "infinitive",
                    ),
                    phrase(
                        "Der Stadtrat plant ... teilweise für Autos zu sperren",
                        "the city council plans to close it partially to cars",
                        "verb-second",
                    ),
                ),
                group(
                    word("eine", "a", "article"),
                    word("viel", "heavily", "adverb"),
                    word("befahren", "busy/used by traffic", "adjective", forms=("befahrene",)),
                    word("die Straße", "road", "fem.", forms=("Straße",)),
                ),
                group(
                    word("in", "in", "preposition", "dative", forms=("im",)),
                    word("das Zentrum", "centre", "neuter", forms=("Zentrum",)),
                    phrase("im Zentrum", "in the city centre", "dative"),
                ),
            ],
        ),
        grouped_sentence(
            "car-free-centre", 2,
            "Befürworter hoffen, dass dadurch die Luft sauberer und das Viertel ruhiger werden.",
            "Supporters hope this will make the air cleaner and the neighbourhood quieter.",
            [
                group(
                    word("der Befürworter", "supporter", "masc.", "plural", forms=("Befürworter",)),
                    word("hoffen", "hope", "verb", "regular", "present"),
                    phrase("Befürworter hoffen", "supporters hope", "main clause"),
                ),
                group(
                    word("dass", "that", "conjunction", "subordinating"),
                    word("dadurch", "as a result", "adverb", "connector"),
                    word("die Luft", "air", "fem.", forms=("Luft",)),
                    word("sauber", "cleaner", "adjective", "comparative", forms=("sauberer",)),
                    word("und", "and", "conjunction", "coordinating"),
                    word("das Viertel", "neighbourhood", "neuter", forms=("Viertel",)),
                    word("ruhig", "quieter", "adjective", "comparative", forms=("ruhiger",)),
                    word("werden", "become", "verb", "irregular", "present"),
                    phrase("die Luft sauberer", "the air cleaner", "comparative"),
                    phrase("das Viertel ruhiger", "the neighbourhood quieter", "comparative"),
                    phrase(
                        "die Luft sauberer und das Viertel ruhiger werden",
                        "the air becomes cleaner and the neighbourhood quieter",
                        "verb-final",
                    ),
                    phrase(
                        "dass dadurch die Luft sauberer und das Viertel ruhiger werden",
                        "that this will make the air cleaner and the neighbourhood quieter",
                        "subordinate clause",
                        "verb-final",
                    ),
                ),
            ],
        ),
        grouped_sentence(
            "car-free-centre", 3,
            "Kritiker befürchten dagegen, dass der Verkehr lediglich in die umliegenden Straßen ausweicht.",
            "Critics, however, fear that traffic will merely shift to the surrounding streets.",
            [
                group(
                    word("der Kritiker", "critic", "masc.", "plural", forms=("Kritiker",)),
                    word("befürchten", "fear", "verb", "regular", "present"),
                    word("dagegen", "on the other hand", "adverb", "connector"),
                    phrase(
                        "Kritiker befürchten dagegen",
                        "critics, however, fear",
                        "main clause",
                    ),
                ),
                group(
                    word("dass", "that", "conjunction", "subordinating"),
                    word("der Verkehr", "traffic", "masc.", forms=("Verkehr",)),
                    word("lediglich", "merely", "adverb"),
                    word("in", "into", "preposition", "accusative"),
                    word("die", "the", "article"),
                    word("umliegend", "surrounding", "adjective", forms=("umliegenden",)),
                    word("die Straße", "street", "fem.", "plural", forms=("Straßen",)),
                    word("ausweicht", "diverts/shifts", "verb", "separable", "present"),
                    phrase(
                        "in die umliegenden Straßen",
                        "into the surrounding streets",
                        "accusative",
                    ),
                    phrase(
                        "in die umliegenden Straßen ausweicht",
                        "shifts into the surrounding streets",
                        "separable",
                        "verb-final",
                    ),
                    phrase(
                        "dass der Verkehr lediglich in die umliegenden Straßen ausweicht",
                        "that traffic merely shifts into the surrounding streets",
                        "subordinate clause",
                        "verb-final",
                    ),
                ),
            ],
        ),
        grouped_sentence(
            "car-free-centre", 4,
            "Bevor eine endgültige Entscheidung fällt, sollen die Anwohner ihre Erfahrungen und Vorschläge einbringen.",
            "Before a final decision is made, residents should contribute their experiences and suggestions.",
            [
                group(
                    word("bevor", "before", "conjunction", "subordinating"),
                    word("eine", "a", "article"),
                    word("endgültig", "final", "adjective", forms=("endgültige",)),
                    word("die Entscheidung", "decision", "fem.", forms=("Entscheidung",)),
                    word("fällt", "is made/falls", "verb", "irregular", "present"),
                    phrase(
                        "eine endgültige Entscheidung fällt",
                        "a final decision is made",
                        "fixed phrase",
                        "verb-final",
                    ),
                    phrase(
                        "Bevor eine endgültige Entscheidung fällt",
                        "before a final decision is made",
                        "subordinate clause",
                        "verb-final",
                    ),
                ),
                group(
                    word("sollen", "should", "modal verb", "present"),
                    word("die", "the", "article"),
                    word("der Anwohner", "resident", "masc.", "plural", forms=("Anwohner",)),
                    word("ihr", "their", "possessive", forms=("ihre",)),
                    word("die Erfahrung", "experience", "fem.", "plural", forms=("Erfahrungen",)),
                    word("und", "and", "conjunction", "coordinating"),
                    word("der Vorschlag", "suggestion", "masc.", "plural", forms=("Vorschläge",)),
                    word("einbringen", "to contribute", "verb", "separable", "infinitive"),
                    phrase(
                        "ihre Erfahrungen und Vorschläge",
                        "their experiences and suggestions",
                        "plural",
                    ),
                    phrase(
                        "sollen die Anwohner ihre Erfahrungen und Vorschläge einbringen",
                        "the residents should contribute their experiences and suggestions",
                        "inversion",
                    ),
                ),
            ],
        ),
    ],
)


ADDITIONAL_LESSONS = [
    RAINY_PICNIC,
    LOST_WALLET,
    BURNT_SOUP,
    APARTMENT_SEARCH,
    LEARNING_ROUTINE,
    CHANGED_PLATFORM,
    COMMUNITY_GARDEN,
    TEAM_MEETING,
    DIGITAL_BREAK,
    CAR_FREE_CENTRE,
]
