"""Consistent dictionary and conjugation data for verb help cards."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ConjugationForm, VerbHelp


GERMAN_PRONOUNS = ("ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie")
ENGLISH_SUBJECTS = ("I", "you", "he/she/it", "we", "you", "they/you")


@dataclass(frozen=True)
class VerbReference:
    english: str
    present: tuple[str, str, str, str, str, str]
    base: str
    third_person: str
    past: str
    participle: str


def ref(
    english: str,
    present: tuple[str, str, str, str, str, str],
    base: str,
    third_person: str,
    past: str,
    participle: str,
) -> VerbReference:
    return VerbReference(
        english=english,
        present=present,
        base=base,
        third_person=third_person,
        past=past,
        participle=participle,
    )


VERB_REFERENCES: dict[str, VerbReference] = {
    "besuchen": ref("to visit", ("besuche", "besuchst", "besucht", "besuchen", "besucht", "besuchen"), "visit", "visits", "visited", "visited"),
    "empfehlen": ref("to recommend", ("empfehle", "empfiehlst", "empfiehlt", "empfehlen", "empfehlt", "empfehlen"), "recommend", "recommends", "recommended", "recommended"),
    "kaufen": ref("to buy", ("kaufe", "kaufst", "kauft", "kaufen", "kauft", "kaufen"), "buy", "buys", "bought", "bought"),
    "machen": ref("to make", ("mache", "machst", "macht", "machen", "macht", "machen"), "make", "makes", "made", "made"),
    "sein": ref("to be", ("bin", "bist", "ist", "sind", "seid", "sind"), "be", "is", "was", "been"),
    "wollen": ref("to want", ("will", "willst", "will", "wollen", "wollt", "wollen"), "want", "wants", "wanted", "wanted"),
    "ankommen": ref("to arrive", ("komme an", "kommst an", "kommt an", "kommen an", "kommt an", "kommen an"), "arrive", "arrives", "arrived", "arrived"),
    "haben": ref("to have", ("habe", "hast", "hat", "haben", "habt", "haben"), "have", "has", "had", "had"),
    "verkaufen": ref("to sell", ("verkaufe", "verkaufst", "verkauft", "verkaufen", "verkauft", "verkaufen"), "sell", "sells", "sold", "sold"),
    "nehmen": ref("to take", ("nehme", "nimmst", "nimmt", "nehmen", "nehmt", "nehmen"), "take", "takes", "took", "taken"),
    "kochen": ref("to cook", ("koche", "kochst", "kocht", "kochen", "kocht", "kochen"), "cook", "cooks", "cooked", "cooked"),
    "fahren": ref("to travel", ("fahre", "fährst", "fährt", "fahren", "fahrt", "fahren"), "travel", "travels", "travelled", "travelled"),
    "ausfallen": ref("to be cancelled", ("falle aus", "fällst aus", "fällt aus", "fallen aus", "fallt aus", "fallen aus"), "be cancelled", "is cancelled", "was cancelled", "been cancelled"),
    "müssen": ref("to have to", ("muss", "musst", "muss", "müssen", "müsst", "müssen"), "have to", "has to", "had to", "had to"),
    "sich treffen": ref("to meet up", ("treffe mich", "triffst dich", "trifft sich", "treffen uns", "trefft euch", "treffen sich"), "meet up", "meets up", "met up", "met up"),
    "trinken": ref("to drink", ("trinke", "trinkst", "trinkt", "trinken", "trinkt", "trinken"), "drink", "drinks", "drank", "drunk"),
    "bekommen": ref("to get", ("bekomme", "bekommst", "bekommt", "bekommen", "bekommt", "bekommen"), "get", "gets", "got", "got"),
    "bestellen": ref("to order", ("bestelle", "bestellst", "bestellt", "bestellen", "bestellt", "bestellen"), "order", "orders", "ordered", "ordered"),
    "sich teilen": ref("to share", ("teile mir …", "teilst dir …", "teilt sich …", "teilen uns …", "teilt euch …", "teilen sich …"), "share", "shares", "shared", "shared"),
    "laufen": ref("to walk", ("laufe", "läufst", "läuft", "laufen", "lauft", "laufen"), "walk", "walks", "walked", "walked"),
    "sprechen": ref("to talk", ("spreche", "sprichst", "spricht", "sprechen", "sprecht", "sprechen"), "talk", "talks", "talked", "talked"),
    "picknicken": ref("to have a picnic", ("picknicke", "picknickst", "picknickt", "picknicken", "picknickt", "picknicken"), "have a picnic", "has a picnic", "had a picnic", "had a picnic"),
    "regnen": ref("to rain", ("regne", "regnest", "regnet", "regnen", "regnet", "regnen"), "rain", "rains", "rained", "rained"),
    "reden": ref("to talk", ("rede", "redest", "redet", "reden", "redet", "reden"), "talk", "talks", "talked", "talked"),
    "bemerken": ref("to notice", ("bemerke", "bemerkst", "bemerkt", "bemerken", "bemerkt", "bemerken"), "notice", "notices", "noticed", "noticed"),
    "fehlen": ref("to be missing", ("fehle", "fehlst", "fehlt", "fehlen", "fehlt", "fehlen"), "be missing", "is missing", "was missing", "been missing"),
    "anrufen": ref("to call", ("rufe an", "rufst an", "ruft an", "rufen an", "ruft an", "rufen an"), "call", "calls", "called", "called"),
    "finden": ref("to find", ("finde", "findest", "findet", "finden", "findet", "finden"), "find", "finds", "found", "found"),
    "aufbewahren": ref("to keep", ("bewahre auf", "bewahrst auf", "bewahrt auf", "bewahren auf", "bewahrt auf", "bewahren auf"), "keep", "keeps", "kept", "kept"),
    "vergessen": ref("to forget", ("vergesse", "vergisst", "vergisst", "vergessen", "vergesst", "vergessen"), "forget", "forgets", "forgot", "forgotten"),
    "anbrennen": ref("to burn", ("brenne an", "brennst an", "brennt an", "brennen an", "brennt an", "brennen an"), "burn", "burns", "burned", "burned"),
    "lachen": ref("to laugh", ("lache", "lachst", "lacht", "lachen", "lacht", "lachen"), "laugh", "laughs", "laughed", "laughed"),
    "suchen": ref("to look for", ("suche", "suchst", "sucht", "suchen", "sucht", "suchen"), "look for", "looks for", "looked for", "looked for"),
    "besichtigen": ref("to view", ("besichtige", "besichtigst", "besichtigt", "besichtigen", "besichtigt", "besichtigen"), "view", "views", "viewed", "viewed"),
    "schicken": ref("to send", ("schicke", "schickst", "schickt", "schicken", "schickt", "schicken"), "send", "sends", "sent", "sent"),
    "warten": ref("to wait", ("warte", "wartest", "wartet", "warten", "wartet", "warten"), "wait", "waits", "waited", "waited"),
    "lernen": ref("to learn", ("lerne", "lernst", "lernt", "lernen", "lernt", "lernen"), "learn", "learns", "learned", "learned"),
    "schreiben": ref("to write", ("schreibe", "schreibst", "schreibt", "schreiben", "schreibt", "schreiben"), "write", "writes", "wrote", "written"),
    "hören": ref("to listen to", ("höre", "hörst", "hört", "hören", "hört", "hören"), "listen to", "listens to", "listened to", "listened to"),
    "verstehen": ref("to understand", ("verstehe", "verstehst", "versteht", "verstehen", "versteht", "verstehen"), "understand", "understands", "understood", "understood"),
    "notieren": ref("to write down", ("notiere", "notierst", "notiert", "notieren", "notiert", "notieren"), "write down", "writes down", "wrote down", "written down"),
    "können": ref("to be able to", ("kann", "kannst", "kann", "können", "könnt", "können"), "can", "can", "could", "been able to"),
    "merken": ref("to remember", ("merke", "merkst", "merkt", "merken", "merkt", "merken"), "remember", "remembers", "remembered", "remembered"),
    "werden": ref("to become / passive auxiliary", ("werde", "wirst", "wird", "werden", "werdet", "werden"), "become", "becomes", "became", "become"),
    "verlegen": ref("to move", ("verlege", "verlegst", "verlegt", "verlegen", "verlegt", "verlegen"), "move", "moves", "moved", "moved"),
    "tragen": ref("to carry", ("trage", "trägst", "trägt", "tragen", "tragt", "tragen"), "carry", "carries", "carried", "carried"),
    "helfen": ref("to help", ("helfe", "hilfst", "hilft", "helfen", "helft", "helfen"), "help", "helps", "helped", "helped"),
    "liegen": ref("to be located", ("liege", "liegst", "liegt", "liegen", "liegt", "liegen"), "be located", "is located", "was located", "been located"),
    "beschließen": ref("to decide", ("beschließe", "beschließt", "beschließt", "beschließen", "beschließt", "beschließen"), "decide", "decides", "decided", "decided"),
    "anlegen": ref("to create", ("lege an", "legst an", "legt an", "legen an", "legt an", "legen an"), "create", "creates", "created", "created"),
    "anbauen": ref("to grow", ("baue an", "baust an", "baut an", "bauen an", "baut an", "bauen an"), "grow", "grows", "grew", "grown"),
    "organisieren": ref("to organize", ("organisiere", "organisierst", "organisiert", "organisieren", "organisiert", "organisieren"), "organize", "organizes", "organized", "organized"),
    "verändern": ref("to change", ("verändere", "veränderst", "verändert", "verändern", "verändert", "verändern"), "change", "changes", "changed", "changed"),
    "zusammenbringen": ref("to bring together", ("bringe zusammen", "bringst zusammen", "bringt zusammen", "bringen zusammen", "bringt zusammen", "bringen zusammen"), "bring together", "brings together", "brought together", "brought together"),
    "vorstellen": ref("to present", ("stelle vor", "stellst vor", "stellt vor", "stellen vor", "stellt vor", "stellen vor"), "present", "presents", "presented", "presented"),
    "warnen": ref("to warn", ("warne", "warnst", "warnt", "warnen", "warnt", "warnen"), "warn", "warns", "warned", "warned"),
    "stehen": ref("to stand", ("stehe", "stehst", "steht", "stehen", "steht", "stehen"), "stand", "stands", "stood", "stood"),
    "erklären": ref("to explain", ("erkläre", "erklärst", "erklärt", "erklären", "erklärt", "erklären"), "explain", "explains", "explained", "explained"),
    "verteilen": ref("to distribute", ("verteile", "verteilst", "verteilt", "verteilen", "verteilt", "verteilen"), "distribute", "distributes", "distributed", "distributed"),
    "entstehen": ref("to emerge", ("entstehe", "entstehst", "entsteht", "entstehen", "entsteht", "entstehen"), "emerge", "emerges", "emerged", "emerged"),
    "schauen": ref("to look", ("schaue", "schaust", "schaut", "schauen", "schaut", "schauen"), "look", "looks", "looked", "looked"),
    "einlegen": ref("to take", ("lege ein", "legst ein", "legt ein", "legen ein", "legt ein", "legen ein"), "take", "takes", "took", "taken"),
    "ausschalten": ref("to switch off", ("schalte aus", "schaltest aus", "schaltet aus", "schalten aus", "schaltet aus", "schalten aus"), "switch off", "switches off", "switched off", "switched off"),
    "lassen": ref("to leave", ("lasse", "lässt", "lässt", "lassen", "lasst", "lassen"), "leave", "leaves", "left", "left"),
    "fallen": ref("to fall", ("falle", "fällst", "fällt", "fallen", "fallt", "fallen"), "fall", "falls", "fell", "fallen"),
    "aushalten": ref("to tolerate", ("halte aus", "hältst aus", "hält aus", "halten aus", "haltet aus", "halten aus"), "tolerate", "tolerates", "tolerated", "tolerated"),
    "feststellen": ref("to realize", ("stelle fest", "stellst fest", "stellt fest", "stellen fest", "stellt fest", "stellen fest"), "realize", "realizes", "realized", "realized"),
    "arbeiten": ref("to work", ("arbeite", "arbeitest", "arbeitet", "arbeiten", "arbeitet", "arbeiten"), "work", "works", "worked", "worked"),
    "umgehen": ref("to handle", ("gehe um", "gehst um", "geht um", "gehen um", "geht um", "gehen um"), "handle", "handles", "handled", "handled"),
    "planen": ref("to plan", ("plane", "planst", "plant", "planen", "plant", "planen"), "plan", "plans", "planned", "planned"),
    "sperren": ref("to close", ("sperre", "sperrst", "sperrt", "sperren", "sperrt", "sperren"), "close", "closes", "closed", "closed"),
    "hoffen": ref("to hope", ("hoffe", "hoffst", "hofft", "hoffen", "hofft", "hoffen"), "hope", "hopes", "hoped", "hoped"),
    "befürchten": ref("to fear", ("befürchte", "befürchtest", "befürchtet", "befürchten", "befürchtet", "befürchten"), "fear", "fears", "feared", "feared"),
    "ausweichen": ref("to divert", ("weiche aus", "weichst aus", "weicht aus", "weichen aus", "weicht aus", "weichen aus"), "divert", "diverts", "diverted", "diverted"),
    "sollen": ref("should / to be supposed to", ("soll", "sollst", "soll", "sollen", "sollt", "sollen"), "should", "should", "should", "been supposed to"),
    "einbringen": ref("to contribute", ("bringe ein", "bringst ein", "bringt ein", "bringen ein", "bringt ein", "bringen ein"), "contribute", "contributes", "contributed", "contributed"),
}


def reference_for(help_card: VerbHelp) -> VerbReference:
    """Return the shared dictionary entry for a lesson verb."""
    try:
        return VERB_REFERENCES[help_card.infinitive]
    except KeyError as error:
        raise ValueError(
            f"Missing verb reference for {help_card.infinitive!r}"
        ) from error


def english_infinitive(help_card: VerbHelp) -> str:
    """Return the authored English dictionary meaning for a verb card."""
    if help_card.english:
        return help_card.english
    return reference_for(help_card).english


def present_forms(help_card: VerbHelp) -> list[ConjugationForm]:
    if help_card.present_forms is not None:
        return help_card.present_forms
    reference = reference_for(help_card)
    return [
        ConjugationForm(pronoun=pronoun, verb=form)
        for pronoun, form in zip(GERMAN_PRONOUNS, reference.present, strict=True)
    ]


def _present_english(reference: VerbReference) -> tuple[str, ...]:
    base = reference.base
    if base == "be" or base.startswith("be "):
        complement = base[2:].strip()
        verbs = ("am", "are", "is", "are", "are", "are")
        return tuple(
            f"{subject} {verb}{f' {complement}' if complement else ''}"
            for subject, verb in zip(ENGLISH_SUBJECTS, verbs, strict=True)
        )
    if base == "have to":
        verbs = ("have to", "have to", "has to", "have to", "have to", "have to")
    elif base in {"can", "should"}:
        verbs = (base,) * 6
    else:
        verbs = (base, base, reference.third_person, base, base, base)
    return tuple(
        f"{subject} {verb}"
        for subject, verb in zip(ENGLISH_SUBJECTS, verbs, strict=True)
    )


def english_present_forms(help_card: VerbHelp) -> tuple[str, ...]:
    if help_card.present_english_forms is not None:
        return tuple(help_card.present_english_forms)
    return _present_english(reference_for(help_card))


def english_current_forms(help_card: VerbHelp) -> tuple[str, ...]:
    """Translate the six existing German forms at their authored tense."""
    if help_card.current_english_forms is not None:
        return tuple(help_card.current_english_forms)
    reference = reference_for(help_card)
    tense = help_card.tense.casefold()

    if "präsens" in tense or "present" in tense:
        return _present_english(reference)
    if "plusquamperfekt" in tense or "pluperfect" in tense:
        verbs = (f"had {reference.participle}",) * 6
    elif "perfekt" in tense or "perfect" in tense:
        verbs = tuple(
            f"{auxiliary} {reference.participle}"
            for auxiliary in ("have", "have", "has", "have", "have", "have")
        )
    elif "passive" in tense:
        verbs = tuple(
            f"{auxiliary} {reference.participle}"
            for auxiliary in ("was", "were", "was", "were", "were", "were")
        )
    elif "konjunktiv" in tense or "subjunctive" in tense:
        modal = "would" if help_card.infinitive == "werden" else f"would {reference.base}"
        verbs = (modal,) * 6
    elif reference.base == "be" or reference.base.startswith("be "):
        complement = reference.base[2:].strip()
        verbs = tuple(
            f"{verb}{f' {complement}' if complement else ''}"
            for verb in ("was", "were", "was", "were", "were", "were")
        )
    else:
        verbs = (reference.past,) * 6

    return tuple(
        f"{subject} {verb}"
        for subject, verb in zip(ENGLISH_SUBJECTS, verbs, strict=True)
    )
