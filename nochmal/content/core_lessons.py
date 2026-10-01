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


def gt(label: str) -> GrammarTag:
    return GrammarTag(label=label, category=TAG_KEYWORDS[label])


def verb_help(
    infinitive: str,
    tense: str,
    forms: tuple[str, str, str, str, str, str],
    usage: str,
) -> VerbHelp:
    pronouns = ("ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie")
    return VerbHelp(
        infinitive=infinitive,
        tense=tense,
        forms=[
            ConjugationForm(pronoun=pronoun, verb=form)
            for pronoun, form in zip(pronouns, forms, strict=True)
        ],
        usage=usage,
    )


KAUFEN_INFINITIVE = verb_help(
    "kaufen", "Präsens (present)",
    ("kaufe", "kaufst", "kauft", "kaufen", "kauft", "kaufen"),
    "The sentence uses kaufen as the infinitive after the modal verb wollte.",
)
VERKAUFEN_PLUPERFECT = verb_help(
    "verkaufen", "Plusquamperfekt (pluperfect)",
    ("hatte verkauft", "hattest verkauft", "hatte verkauft", "hatten verkauft", "hattet verkauft", "hatten verkauft"),
    "Verkauft combines with hatte to describe a sale completed before the arrival.",
)
FAHREN_INFINITIVE = verb_help(
    "fahren", "Präsens (present)",
    ("fahre", "fährst", "fährt", "fahren", "fahrt", "fahren"),
    "The sentence uses fahren as the infinitive after the modal verb wollte.",
)
AUSFALLEN_PERFECT = verb_help(
    "ausfallen", "Perfekt (perfect)",
    ("bin ausgefallen", "bist ausgefallen", "ist ausgefallen", "sind ausgefallen", "seid ausgefallen", "sind ausgefallen"),
    "Ausgefallen is the past participle of separable ausfallen and combines with sein.",
)
NEHMEN_INFINITIVE = verb_help(
    "nehmen", "Präsens (present)",
    ("nehme", "nimmst", "nimmt", "nehmen", "nehmt", "nehmen"),
    "The sentence uses nehmen as the infinitive after the modal verb musste.",
)
TREFFEN_PERFECT = verb_help(
    "sich treffen", "Perfekt (perfect)",
    ("habe mich getroffen", "hast dich getroffen", "hat sich getroffen", "haben uns getroffen", "habt euch getroffen", "haben sich getroffen"),
    "Sich treffen is reflexive here; getroffen combines with haben in the perfect tense.",
)
TRINKEN_INFINITIVE = verb_help(
    "trinken", "Präsens (present)",
    ("trinke", "trinkst", "trinkt", "trinken", "trinkt", "trinken"),
    "The sentence uses trinken as the infinitive after wollten.",
)
BEKOMMEN_PERFECT = verb_help(
    "bekommen", "Perfekt (perfect)",
    ("habe bekommen", "hast bekommen", "hat bekommen", "haben bekommen", "habt bekommen", "haben bekommen"),
    "Bekommen is both the infinitive and past participle; it combines with haben here.",
)
EMPFEHLEN_PERFECT = verb_help(
    "empfehlen", "Perfekt (perfect)",
    ("habe empfohlen", "hast empfohlen", "hat empfohlen", "haben empfohlen", "habt empfohlen", "haben empfohlen"),
    "Empfohlen is the past participle of empfehlen and combines with haben.",
)
BESTELLEN_PERFECT = verb_help(
    "bestellen", "Perfekt (perfect)",
    ("habe bestellt", "hast bestellt", "hat bestellt", "haben bestellt", "habt bestellt", "haben bestellt"),
    "Bestellt is the past participle of bestellen and combines with haben.",
)
TEILEN_PERFECT = verb_help(
    "sich teilen", "Perfekt (perfect)",
    ("habe mir ... geteilt", "hast dir ... geteilt", "hat sich ... geteilt", "haben uns ... geteilt", "habt euch ... geteilt", "haben sich ... geteilt"),
    "Sich etwas teilen uses a dative reflexive pronoun; geteilt combines with haben.",
)
LAUFEN_PERFECT = verb_help(
    "laufen", "Perfekt (perfect)",
    ("bin gelaufen", "bist gelaufen", "ist gelaufen", "sind gelaufen", "seid gelaufen", "sind gelaufen"),
    "Gelaufen is the past participle of laufen and uses sein for movement here.",
)
SPRECHEN_PERFECT = verb_help(
    "sprechen", "Perfekt (perfect)",
    ("habe gesprochen", "hast gesprochen", "hat gesprochen", "haben gesprochen", "habt gesprochen", "haben gesprochen"),
    "Gesprochen is the past participle of sprechen and combines with haben.",
)
FAHREN_PERFECT = verb_help(
    "fahren", "Perfekt (perfect)",
    ("bin gefahren", "bist gefahren", "ist gefahren", "sind gefahren", "seid gefahren", "sind gefahren"),
    "Gefahren is the past participle of fahren and uses sein for movement to a destination.",
)


WOLLEN_PAST = VerbHelp(
    infinitive="wollen",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="wollte"),
        ConjugationForm(pronoun="du", verb="wolltest"),
        ConjugationForm(pronoun="er/sie/es", verb="wollte"),
        ConjugationForm(pronoun="wir", verb="wollten"),
        ConjugationForm(pronoun="ihr", verb="wolltet"),
        ConjugationForm(pronoun="sie/Sie", verb="wollten"),
    ],
    usage=(
        "A modal verb expressing intention or desire. Put the conjugated form "
        "in the finite-verb position and the other verb as an infinitive at the "
        "end: Ich wollte mit der U-Bahn fahren."
    ),
)

SEIN_PRESENT = VerbHelp(
    infinitive="sein",
    tense="Präsens (present)",
    forms=[
        ConjugationForm(pronoun="ich", verb="bin"),
        ConjugationForm(pronoun="du", verb="bist"),
        ConjugationForm(pronoun="er/sie/es", verb="ist"),
        ConjugationForm(pronoun="wir", verb="sind"),
        ConjugationForm(pronoun="ihr", verb="seid"),
        ConjugationForm(pronoun="sie/Sie", verb="sind"),
    ],
    usage=(
        "Sein is the Perfekt auxiliary for many movement and change-of-state "
        "verbs: Ich bin gefahren. It can also be the main verb meaning ‘to be’."
    ),
)


HABEN_PRESENT = VerbHelp(
    infinitive="haben",
    tense="Präsens (present), used as a Perfekt auxiliary",
    forms=[
        ConjugationForm(pronoun="ich", verb="habe"),
        ConjugationForm(pronoun="du", verb="hast"),
        ConjugationForm(pronoun="er/sie/es", verb="hat"),
        ConjugationForm(pronoun="wir", verb="haben"),
        ConjugationForm(pronoun="ihr", verb="habt"),
        ConjugationForm(pronoun="sie/Sie", verb="haben"),
    ],
    usage=(
        "Haben is the Perfekt auxiliary for most German verbs. Conjugate haben "
        "and place the past participle toward the end: Wir haben Hunger bekommen."
    ),
)

MUESSEN_PAST = VerbHelp(
    infinitive="müssen",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="musste"),
        ConjugationForm(pronoun="du", verb="musstest"),
        ConjugationForm(pronoun="er/sie/es", verb="musste"),
        ConjugationForm(pronoun="wir", verb="mussten"),
        ConjugationForm(pronoun="ihr", verb="musstet"),
        ConjugationForm(pronoun="sie/Sie", verb="mussten"),
    ],
    usage=(
        "A modal verb expressing necessity. The conjugated form is finite and "
        "the other verb goes to the end as an infinitive: Ich musste ein Taxi "
        "nehmen."
    ),
)

SEIN_PAST = VerbHelp(
    infinitive="sein",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="war"),
        ConjugationForm(pronoun="du", verb="warst"),
        ConjugationForm(pronoun="er/sie/es", verb="war"),
        ConjugationForm(pronoun="wir", verb="waren"),
        ConjugationForm(pronoun="ihr", verb="wart"),
        ConjugationForm(pronoun="sie/Sie", verb="waren"),
    ],
    usage=(
        "The simple past of sein, used to describe a past state: Ich war "
        "pünktlich. This form is common in conversation and writing."
    ),
)


ANKOMMEN_PAST = VerbHelp(
    infinitive="ankommen",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="kam an"),
        ConjugationForm(pronoun="du", verb="kamst an"),
        ConjugationForm(pronoun="er/sie/es", verb="kam an"),
        ConjugationForm(pronoun="wir", verb="kamen an"),
        ConjugationForm(pronoun="ihr", verb="kamt an"),
        ConjugationForm(pronoun="sie/Sie", verb="kamen an"),
    ],
    usage=(
        "Ankommen is separable in a main clause: Ich kam dort an. After als, "
        "the conjugated verb goes to the end and the prefix stays attached: "
        "als ich dort ankam."
    ),
)

HABEN_PAST = VerbHelp(
    infinitive="haben",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="hatte"),
        ConjugationForm(pronoun="du", verb="hattest"),
        ConjugationForm(pronoun="er/sie/es", verb="hatte"),
        ConjugationForm(pronoun="wir", verb="hatten"),
        ConjugationForm(pronoun="ihr", verb="hattet"),
        ConjugationForm(pronoun="sie/Sie", verb="hatten"),
    ],
    usage=(
        "Here hatte is the auxiliary used with verkauft to form the "
        "Plusquamperfekt: Der Händler hatte die Tomaten verkauft. This tense "
        "shows that the selling happened before the arrival."
    ),
)

NEHMEN_PAST = VerbHelp(
    infinitive="nehmen",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="nahm"),
        ConjugationForm(pronoun="du", verb="nahmst"),
        ConjugationForm(pronoun="er/sie/es", verb="nahm"),
        ConjugationForm(pronoun="wir", verb="nahmen"),
        ConjugationForm(pronoun="ihr", verb="nahmt"),
        ConjugationForm(pronoun="sie/Sie", verb="nahmen"),
    ],
    usage=(
        "The simple past of nehmen. With something being selected or bought, "
        "nehmen can mean ‘choose’ or ‘take’: Ich nahm stattdessen Paprika."
    ),
)

KOCHEN_PAST = VerbHelp(
    infinitive="kochen",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="kochte"),
        ConjugationForm(pronoun="du", verb="kochtest"),
        ConjugationForm(pronoun="er/sie/es", verb="kochte"),
        ConjugationForm(pronoun="wir", verb="kochten"),
        ConjugationForm(pronoun="ihr", verb="kochtet"),
        ConjugationForm(pronoun="sie/Sie", verb="kochten"),
    ],
    usage=(
        "A regular weak verb. The simple past adds -te to the stem: Ich "
        "kochte am Abend eine Suppe."
    ),
)


BESUCHEN_PAST = VerbHelp(
    infinitive="besuchen",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="besuchte"),
        ConjugationForm(pronoun="du", verb="besuchtest"),
        ConjugationForm(pronoun="er/sie/es", verb="besuchte"),
        ConjugationForm(pronoun="wir", verb="besuchten"),
        ConjugationForm(pronoun="ihr", verb="besuchtet"),
        ConjugationForm(pronoun="sie/Sie", verb="besuchten"),
    ],
    usage=(
        "A regular verb meaning ‘to visit’. The simple-past form describes a "
        "completed visit: Ich besuchte eine Bäckerei."
    ),
)

EMPFEHLEN_PAST = VerbHelp(
    infinitive="empfehlen",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="empfahl"),
        ConjugationForm(pronoun="du", verb="empfahlst"),
        ConjugationForm(pronoun="er/sie/es", verb="empfahl"),
        ConjugationForm(pronoun="wir", verb="empfahlen"),
        ConjugationForm(pronoun="ihr", verb="empfahlt"),
        ConjugationForm(pronoun="sie/Sie", verb="empfahlen"),
    ],
    usage=(
        "An irregular verb meaning ‘to recommend’. The person receiving the "
        "recommendation is in the dative: Sie empfahl mir ein Brot."
    ),
)

KAUFEN_PAST = VerbHelp(
    infinitive="kaufen",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="kaufte"),
        ConjugationForm(pronoun="du", verb="kauftest"),
        ConjugationForm(pronoun="er/sie/es", verb="kaufte"),
        ConjugationForm(pronoun="wir", verb="kauften"),
        ConjugationForm(pronoun="ihr", verb="kauftet"),
        ConjugationForm(pronoun="sie/Sie", verb="kauften"),
    ],
    usage=(
        "A regular verb meaning ‘to buy’. Here it describes what the speaker "
        "bought at the bakery."
    ),
)

MACHEN_PAST = VerbHelp(
    infinitive="machen",
    tense="Präteritum (simple past)",
    forms=[
        ConjugationForm(pronoun="ich", verb="machte"),
        ConjugationForm(pronoun="du", verb="machtest"),
        ConjugationForm(pronoun="er/sie/es", verb="machte"),
        ConjugationForm(pronoun="wir", verb="machten"),
        ConjugationForm(pronoun="ihr", verb="machtet"),
        ConjugationForm(pronoun="sie/Sie", verb="machten"),
    ],
    usage=(
        "A regular verb meaning ‘to make’ or ‘to do’. Here machen means to "
        "prepare tea: Ich machte Tee."
    ),
)


BAKERY_LESSON = Lesson(
    id="bakery-visit",
    title="In der Bäckerei",
    english_title="At the bakery",
    level="A2",
    audio_path="assets/audio/bakery-visit.wav",
    initial_question="Was kaufte die Person in der Bäckerei?",
    sentences=[
        Sentence(
            text=(
                "Nach der Arbeit besuchte ich eine neue Bäckerei in meiner "
                "Straße."
            ),
            natural_meaning=(
                "After work, I visited a new bakery on my street."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="nach",
                            english="after",
                            tags=[gt("preposition"), gt("dative")],
                        ),
                        BreakdownItem(
                            german="die Arbeit",
                            english="work",
                            tags=[gt("fem.")],
                            source_forms=["der"],
                        ),
                        BreakdownItem(
                            german="Nach der Arbeit",
                            english="after work",
                            tags=[gt("dative")],
                            kind="phrase",
                        ),
                        BreakdownItem(
                            german="besuchte",
                            english="visited",
                            tags=[
                                gt("verb"),
                                gt("regular"),
                                gt("simple past"),
                            ],
                            verb_help=BESUCHEN_PAST,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[gt("subject"), gt("personal pronoun")],
                        ),
                        BreakdownItem(
                            german="Nach der Arbeit besuchte ich",
                            english="After work, I visited",
                            tags=[gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="neu",
                            english="new",
                            tags=[gt("adjective")],
                            source_forms=["neue"],
                        ),
                        BreakdownItem(
                            german="die Bäckerei",
                            english="bakery",
                            tags=[gt("fem.")],
                            source_forms=["eine"],
                        ),
                        BreakdownItem(
                            german="eine neue Bäckerei",
                            english="a new bakery",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="in",
                            english="in/on",
                            tags=[gt("preposition"), gt("dative")],
                        ),
                        BreakdownItem(
                            german="mein",
                            english="my",
                            tags=[gt("possessive")],
                            source_forms=["meiner"],
                        ),
                        BreakdownItem(
                            german="die Straße",
                            english="street",
                            tags=[gt("fem.")],
                        ),
                        BreakdownItem(
                            german="in meiner Straße",
                            english="on my street",
                            tags=[gt("dative")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/bakery-visit-1.wav",
        ),
        Sentence(
            text=(
                "Die Verkäuferin empfahl mir ein frisches Vollkornbrot, und "
                "ich kaufte auch zwei Brötchen."
            ),
            natural_meaning=(
                "The saleswoman recommended a fresh whole-grain loaf to me, "
                "and I also bought two bread rolls."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="die Verkäuferin",
                            english="saleswoman",
                            tags=[gt("fem.")],
                        ),
                        BreakdownItem(
                            german="empfahl",
                            english="recommended",
                            tags=[
                                gt("verb"),
                                gt("irregular"),
                                gt("simple past"),
                            ],
                            verb_help=EMPFEHLEN_PAST,
                        ),
                        BreakdownItem(
                            german="mir",
                            english="to me",
                            tags=[
                                gt("personal pronoun"),
                                gt("dative"),
                            ],
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="frisch",
                            english="fresh",
                            tags=[gt("adjective")],
                            source_forms=["frisches"],
                        ),
                        BreakdownItem(
                            german="das Vollkornbrot",
                            english="whole-grain bread",
                            tags=[gt("neuter"), gt("compound noun")],
                            source_forms=["ein"],
                        ),
                        BreakdownItem(
                            german="ein frisches Vollkornbrot",
                            english="a fresh whole-grain loaf",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="und",
                            english="and",
                            tags=[gt("conjunction"), gt("coordinating")],
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[gt("subject"), gt("personal pronoun")],
                        ),
                        BreakdownItem(
                            german="kaufte",
                            english="bought",
                            tags=[
                                gt("verb"),
                                gt("regular"),
                                gt("simple past"),
                            ],
                            verb_help=KAUFEN_PAST,
                        ),
                        BreakdownItem(
                            german="auch",
                            english="also",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(
                            german="zwei",
                            english="two",
                            tags=[gt("numeral")],
                        ),
                        BreakdownItem(
                            german="das Brötchen",
                            english="bread roll",
                            tags=[gt("neuter"), gt("plural")],
                        ),
                        BreakdownItem(
                            german="zwei Brötchen",
                            english="two bread rolls",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/bakery-visit-2.wav",
        ),
        Sentence(
            text="Zu Hause machte ich Tee, weil das Brot noch warm war.",
            natural_meaning=(
                "At home, I made tea because the bread was still warm."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="zu",
                            english="at/to",
                            tags=[gt("preposition"), gt("dative")],
                        ),
                        BreakdownItem(
                            german="das Haus",
                            english="home/house",
                            tags=[gt("neuter")],
                            source_forms=["Hause"],
                        ),
                        BreakdownItem(
                            german="Zu Hause",
                            english="at home",
                            tags=[gt("fixed phrase")],
                            kind="phrase",
                        ),
                        BreakdownItem(
                            german="machte",
                            english="made",
                            tags=[
                                gt("verb"),
                                gt("regular"),
                                gt("simple past"),
                            ],
                            verb_help=MACHEN_PAST,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[gt("subject"), gt("personal pronoun")],
                        ),
                        BreakdownItem(
                            german="Zu Hause machte ich",
                            english="At home, I made",
                            tags=[gt("inversion")],
                            kind="phrase",
                        ),
                        BreakdownItem(
                            german="der Tee",
                            english="tea",
                            tags=[gt("masc."), gt("accusative")],
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="weil",
                            english="because",
                            tags=[gt("conjunction"), gt("subordinating")],
                        ),
                        BreakdownItem(
                            german="das Brot",
                            english="bread",
                            tags=[gt("neuter")],
                        ),
                        BreakdownItem(
                            german="noch",
                            english="still",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(
                            german="warm",
                            english="warm",
                            tags=[gt("adjective"), gt("predicate")],
                        ),
                        BreakdownItem(
                            german="war",
                            english="was",
                            tags=[
                                gt("verb"),
                                gt("irregular"),
                                gt("simple past"),
                            ],
                            verb_help=SEIN_PAST,
                        ),
                        BreakdownItem(
                            german="weil das Brot noch warm war",
                            english="because the bread was still warm",
                            tags=[gt("subordinate clause"), gt("verb-final")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/bakery-visit-3.wav",
        ),
    ],
)


MARKET_LESSON = Lesson(
    id="weekly-market",
    title="Auf dem Wochenmarkt",
    english_title="At the weekly market",
    level="A2",
    audio_path="assets/audio/weekly-market.wav",
    initial_question=(
        "Was wollte die Person kaufen, und was nahm sie stattdessen?"
    ),
    sentences=[
        Sentence(
            text=(
                "Am Samstag wollte ich auf dem Wochenmarkt frisches Gemüse "
                "kaufen."
            ),
            natural_meaning=(
                "On Saturday, I wanted to buy fresh vegetables at the weekly "
                "market."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="an",
                            english="on/at",
                            tags=[
                                gt("preposition"),
                                gt("dative"),
                            ],
                            source_forms=["Am"],
                        ),
                        BreakdownItem(
                            german="der Samstag",
                            english="Saturday",
                            tags=[gt("masc.")],
                        ),
                        BreakdownItem(
                            german="Am Samstag",
                            english="on Saturday",
                            kind="phrase",
                        ),
                        BreakdownItem(
                            german="wollte",
                            english="wanted",
                            tags=[
                                gt("modal verb"),
                                gt("simple past"),
                            ],
                            verb_help=WOLLEN_PAST,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[
                                gt("subject"),
                                gt("personal pronoun"),
                            ],
                        ),
                        BreakdownItem(
                            german="Am Samstag wollte ich",
                            english="On Saturday I wanted",
                            tags=[gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="auf",
                            english="at/on",
                            tags=[
                                gt("preposition"),
                                gt("dative"),
                            ],
                        ),
                        BreakdownItem(
                            german="der Wochenmarkt",
                            english="weekly market",
                            tags=[gt("masc."), gt("compound noun")],
                            source_forms=["dem"],
                        ),
                        BreakdownItem(
                            german="auf dem Wochenmarkt",
                            english="at the weekly market",
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="frisch",
                            english="fresh",
                            tags=[gt("adjective")],
                            source_forms=["frisches"],
                        ),
                        BreakdownItem(
                            german="das Gemüse",
                            english="vegetables/produce",
                            tags=[gt("neuter")],
                        ),
                        BreakdownItem(
                            german="frisches Gemüse",
                            english="fresh vegetables",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                        BreakdownItem(
                            german="kaufen",
                            english="to buy",
                            tags=[gt("verb"), gt("infinitive")],
                            verb_help=KAUFEN_INFINITIVE,
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/weekly-market-1.wav",
        ),
        Sentence(
            text=(
                "Als ich dort ankam, hatte der Händler die Tomaten schon "
                "verkauft."
            ),
            natural_meaning=(
                "When I arrived there, the vendor had already sold the "
                "tomatoes."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="als",
                            english="when",
                            tags=[
                                gt("conjunction"),
                                gt("subordinating"),
                                gt("time"),
                            ],
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[
                                gt("subject"),
                                gt("personal pronoun"),
                            ],
                        ),
                        BreakdownItem(
                            german="dort",
                            english="there",
                            tags=[gt("place"), gt("adverb")],
                        ),
                        BreakdownItem(
                            german="ankam",
                            english="arrived",
                            tags=[
                                gt("verb"),
                                gt("separable"),
                                gt("simple past"),
                            ],
                            verb_help=ANKOMMEN_PAST,
                        ),
                        BreakdownItem(
                            german="Als ich dort ankam",
                            english="When I arrived there",
                            tags=[
                                gt("subordinate clause"),
                                gt("verb-final"),
                            ],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="hatte",
                            english="had",
                            tags=[
                                gt("verb"),
                                gt("auxiliary"),
                                gt("simple past"),
                            ],
                            verb_help=HABEN_PAST,
                        ),
                        BreakdownItem(
                            german="der Händler",
                            english="vendor",
                            tags=[gt("masc.")],
                        ),
                        BreakdownItem(
                            german="die Tomate",
                            english="tomato",
                            tags=[
                                gt("fem."),
                                gt("plural"),
                            ],
                            source_forms=["Tomaten"],
                        ),
                        BreakdownItem(
                            german="schon",
                            english="already",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(
                            german="verkauft",
                            english="sold",
                            tags=[gt("verb"), gt("past participle")],
                            verb_help=VERKAUFEN_PLUPERFECT,
                        ),
                        BreakdownItem(
                            german="hatte ... verkauft",
                            english="had sold",
                            tags=[gt("pluperfect")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/weekly-market-2.wav",
        ),
        Sentence(
            text=(
                "Deshalb nahm ich stattdessen Paprika und kochte am Abend "
                "eine Suppe."
            ),
            natural_meaning=(
                "So I chose bell peppers instead and cooked a soup that "
                "evening."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="deshalb",
                            english="therefore/so",
                            tags=[gt("adverb"), gt("connector")],
                        ),
                        BreakdownItem(
                            german="nahm",
                            english="took/chose",
                            tags=[
                                gt("verb"),
                                gt("irregular"),
                                gt("simple past"),
                            ],
                            verb_help=NEHMEN_PAST,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[
                                gt("subject"),
                                gt("personal pronoun"),
                            ],
                        ),
                        BreakdownItem(
                            german="Deshalb nahm ich",
                            english="So I chose",
                            tags=[gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="stattdessen",
                            english="instead",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(
                            german="die Paprika",
                            english="bell peppers",
                            tags=[
                                gt("fem."),
                            ],
                        ),
                        BreakdownItem(
                            german="stattdessen Paprika",
                            english="bell peppers instead",
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="und",
                            english="and",
                            tags=[gt("conjunction"), gt("coordinating")],
                        ),
                        BreakdownItem(
                            german="kochte",
                            english="cooked",
                            tags=[
                                gt("verb"),
                                gt("regular"),
                                gt("simple past"),
                            ],
                            verb_help=KOCHEN_PAST,
                        ),
                        BreakdownItem(
                            german="an",
                            english="in/on/at",
                            tags=[
                                gt("preposition"),
                                gt("dative"),
                            ],
                            source_forms=["am"],
                        ),
                        BreakdownItem(
                            german="der Abend",
                            english="evening",
                            tags=[gt("masc.")],
                        ),
                        BreakdownItem(
                            german="am Abend",
                            english="in the evening",
                            kind="phrase",
                        ),
                        BreakdownItem(
                            german="die Suppe",
                            english="soup",
                            tags=[gt("fem.")],
                            source_forms=["eine"],
                        ),
                        BreakdownItem(
                            german="eine Suppe",
                            english="a soup",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/weekly-market-3.wav",
        ),
    ],
)


SEED_LESSON = Lesson(
    id="missed-train",
    title="Auf dem Weg zum Vorstellungsgespräch",
    english_title="On the way to the job interview",
    level="A2-B1",
    audio_path="assets/audio/missed-train.wav",
    initial_question="Was ist passiert? Antworte auf Deutsch oder Englisch.",
    sentences=[
        Sentence(
            text=(
                "Gestern wollte ich mit der U-Bahn zum "
                "Vorstellungsgespräch fahren."
            ),
            natural_meaning=(
                "Yesterday, I wanted to take the subway to the job interview."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="gestern",
                            english="yesterday",
                            tags=[gt("time"), gt("adverb")],
                        ),
                        BreakdownItem(
                            german="wollte",
                            english="wanted",
                            tags=[
                                gt("modal verb"),
                                gt("simple past"),
                            ],
                            verb_help=WOLLEN_PAST,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[
                                gt("subject"),
                                gt("personal pronoun"),
                            ],
                        ),
                        BreakdownItem(
                            german="Gestern wollte ich",
                            english="Yesterday I wanted",
                            tags=[gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="mit",
                            english="with/by",
                            tags=[
                                gt("preposition"),
                                gt("dative"),
                            ],
                        ),
                        BreakdownItem(
                            german="die U-Bahn",
                            english="subway",
                            tags=[gt("fem.")],
                            source_forms=["der"],
                        ),
                        BreakdownItem(
                            german="mit der U-Bahn",
                            english="by/on the subway",
                            tags=[gt("dative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="zu",
                            english="to",
                            tags=[
                                gt("preposition"),
                                gt("dative"),
                            ],
                            source_forms=["zum"],
                        ),
                        BreakdownItem(
                            german="das Vorstellungsgespräch",
                            english="job interview",
                            tags=[gt("neuter"), gt("compound noun")],
                        ),
                        BreakdownItem(
                            german="zum Vorstellungsgespräch",
                            english="to the job interview",
                            tags=[
                                gt("dative"),
                            ],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="fahren",
                            english="to go/travel/ride",
                            tags=[gt("verb"), gt("infinitive")],
                            verb_help=FAHREN_INFINITIVE,
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/missed-train-1.wav",
        ),
        Sentence(
            text=(
                "Aber der Zug ist ausgefallen, deshalb musste ich ein Taxi "
                "nehmen."
            ),
            natural_meaning=(
                "But the train was cancelled, so I had to take a taxi."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="aber",
                            english="but/however",
                            tags=[gt("conjunction"), gt("coordinating")],
                        ),
                        BreakdownItem(
                            german="der Zug",
                            english="train",
                            tags=[gt("masc.")],
                        ),
                        BreakdownItem(
                            german="ist",
                            english="is",
                            tags=[
                                gt("verb"),
                                gt("auxiliary"),
                                gt("present"),
                            ],
                            verb_help=SEIN_PRESENT,
                        ),
                        BreakdownItem(
                            german="ausgefallen",
                            english="cancelled",
                            tags=[gt("verb"), gt("past participle")],
                            verb_help=AUSFALLEN_PERFECT,
                        ),
                        BreakdownItem(
                            german="der Zug ist ausgefallen",
                            english="the train was cancelled",
                            tags=[gt("perfect")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="deshalb",
                            english="therefore/so",
                            tags=[gt("adverb"), gt("connector")],
                        ),
                        BreakdownItem(
                            german="musste",
                            english="had to",
                            tags=[
                                gt("modal verb"),
                                gt("simple past"),
                            ],
                            verb_help=MUESSEN_PAST,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[
                                gt("subject"),
                                gt("personal pronoun"),
                            ],
                        ),
                        BreakdownItem(
                            german="deshalb musste ich",
                            english="so I had to",
                            tags=[gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="das Taxi",
                            english="taxi",
                            tags=[gt("neuter")],
                            source_forms=["ein"],
                        ),
                        BreakdownItem(
                            german="ein Taxi",
                            english="a taxi",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                        BreakdownItem(
                            german="nehmen",
                            english="to take",
                            tags=[gt("verb"), gt("infinitive")],
                            verb_help=NEHMEN_INFINITIVE,
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/missed-train-2.wav",
        ),
        Sentence(
            text="Zum Glück war ich trotzdem pünktlich.",
            natural_meaning="Fortunately, I was still on time.",
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="zu",
                            english="to",
                            tags=[
                                gt("preposition"),
                                gt("dative"),
                            ],
                            source_forms=["Zum"],
                        ),
                        BreakdownItem(
                            german="das Glück",
                            english="luck",
                            tags=[gt("neuter")],
                        ),
                        BreakdownItem(
                            german="Zum Glück",
                            english="fortunately/luckily",
                            tags=[
                                gt("fixed phrase"),
                            ],
                            kind="phrase",
                        ),
                        BreakdownItem(
                            german="war",
                            english="was",
                            tags=[
                                gt("verb"),
                                gt("irregular"),
                                gt("simple past"),
                            ],
                            verb_help=SEIN_PAST,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[
                                gt("subject"),
                                gt("personal pronoun"),
                            ],
                        ),
                        BreakdownItem(
                            german="Zum Glück war ich",
                            english="Fortunately, I was",
                            tags=[gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="trotzdem",
                            english="nevertheless/still",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(
                            german="pünktlich",
                            english="on time/punctual",
                            tags=[
                                gt("adjective"),
                                gt("predicate"),
                            ],
                        ),
                        BreakdownItem(
                            german="trotzdem pünktlich",
                            english="still on time",
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/missed-train-3.wav",
        ),
    ],
)


FRIENDS_EVENING_LESSON = Lesson(
    id="evening-with-friends",
    title="Ein spontaner Abend mit Freunden",
    english_title="A spontaneous evening with friends",
    level="B1",
    audio_path="assets/audio/evening-with-friends.wav",
    initial_question="Wo haben die Freunde schließlich gegessen?",
    sentences=[
        Sentence(
            text=(
                "Am Freitagabend habe ich mich spontan mit zwei Freunden im "
                "kleinen Café an der Ecke getroffen."
            ),
            natural_meaning=(
                "On Friday evening, I spontaneously met up with two friends "
                "at the small café on the corner."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="an",
                            english="on/at",
                            tags=[gt("preposition"), gt("dative")],
                            source_forms=["Am"],
                        ),
                        BreakdownItem(
                            german="der Freitagabend",
                            english="Friday evening",
                            tags=[gt("masc."), gt("compound noun")],
                        ),
                        BreakdownItem(
                            german="Am Freitagabend",
                            english="on Friday evening",
                            tags=[gt("time"), gt("dative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="habe",
                            english="have",
                            tags=[gt("auxiliary"), gt("present")],
                            verb_help=HABEN_PRESENT,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[gt("subject"), gt("personal pronoun")],
                        ),
                        BreakdownItem(
                            german="mich",
                            english="myself",
                            tags=[gt("personal pronoun"), gt("accusative")],
                        ),
                        BreakdownItem(
                            german="spontan",
                            english="spontaneously",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(
                            german="getroffen",
                            english="met up",
                            tags=[
                                gt("past participle"),
                                gt("irregular"),
                                gt("reflexive"),
                            ],
                            verb_help=TREFFEN_PERFECT,
                        ),
                        BreakdownItem(
                            german="habe ich mich spontan ... getroffen",
                            english="spontaneously met up",
                            tags=[gt("perfect")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="mit",
                            english="with",
                            tags=[gt("preposition"), gt("dative")],
                        ),
                        BreakdownItem(
                            german="zwei",
                            english="two",
                            tags=[gt("numeral")],
                        ),
                        BreakdownItem(
                            german="der Freund",
                            english="friend",
                            tags=[gt("masc."), gt("plural")],
                            source_forms=["Freunden"],
                        ),
                        BreakdownItem(
                            german="mit zwei Freunden",
                            english="with two friends",
                            tags=[gt("dative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="in",
                            english="in/at",
                            tags=[gt("preposition"), gt("dative")],
                            source_forms=["im"],
                        ),
                        BreakdownItem(
                            german="klein",
                            english="small",
                            tags=[gt("adjective")],
                            source_forms=["kleinen"],
                        ),
                        BreakdownItem(
                            german="das Café",
                            english="café",
                            tags=[gt("neuter")],
                        ),
                        BreakdownItem(
                            german="im kleinen Café",
                            english="at the small café",
                            tags=[gt("dative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="an",
                            english="at/on",
                            tags=[gt("preposition"), gt("dative")],
                        ),
                        BreakdownItem(
                            german="die Ecke",
                            english="corner",
                            tags=[gt("fem.")],
                            source_forms=["der"],
                        ),
                        BreakdownItem(
                            german="an der Ecke",
                            english="on the corner",
                            tags=[gt("dative")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/evening-with-friends-1.wav",
        ),
        Sentence(
            text=(
                "Eigentlich wollten wir nur etwas trinken, aber dann haben "
                "wir Hunger bekommen."
            ),
            natural_meaning=(
                "We originally only wanted to have something to drink, "
                "but then we got hungry."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="eigentlich",
                            english="actually/originally",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(
                            german="wollten",
                            english="wanted/planned",
                            tags=[gt("modal verb"), gt("simple past")],
                            verb_help=WOLLEN_PAST,
                        ),
                        BreakdownItem(
                            german="wir",
                            english="we",
                            tags=[gt("subject"), gt("personal pronoun")],
                        ),
                        BreakdownItem(
                            german="Eigentlich wollten wir",
                            english="Originally, we wanted",
                            tags=[gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="nur",
                            english="only",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(german="etwas", english="something"),
                        BreakdownItem(
                            german="trinken",
                            english="to drink",
                            tags=[gt("verb"), gt("infinitive")],
                            verb_help=TRINKEN_INFINITIVE,
                        ),
                        BreakdownItem(
                            german="nur etwas trinken",
                            english="only have something to drink",
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="aber",
                            english="but",
                            tags=[gt("conjunction"), gt("coordinating")],
                        ),
                        BreakdownItem(
                            german="dann",
                            english="then",
                            tags=[gt("time"), gt("adverb")],
                        ),
                        BreakdownItem(
                            german="haben",
                            english="have",
                            tags=[gt("auxiliary"), gt("present")],
                            verb_help=HABEN_PRESENT,
                        ),
                        BreakdownItem(
                            german="wir",
                            english="we",
                            tags=[gt("subject"), gt("personal pronoun")],
                        ),
                        BreakdownItem(
                            german="der Hunger",
                            english="hunger",
                            tags=[gt("masc.")],
                        ),
                        BreakdownItem(
                            german="bekommen",
                            english="got",
                            tags=[gt("past participle"), gt("irregular")],
                            verb_help=BEKOMMEN_PERFECT,
                        ),
                        BreakdownItem(
                            german="dann haben wir Hunger bekommen",
                            english="then we got hungry",
                            tags=[gt("perfect"), gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/evening-with-friends-2.wav",
        ),
        Sentence(
            text=(
                "Weil das Restaurant nebenan voll war, hat uns die Kellnerin "
                "den ruhigen Imbiss um die Ecke empfohlen."
            ),
            natural_meaning=(
                "Because the restaurant next door was full, the waitress "
                "recommended the quiet snack bar around the corner to us."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="weil",
                            english="because",
                            tags=[gt("conjunction"), gt("subordinating")],
                        ),
                        BreakdownItem(
                            german="das Restaurant",
                            english="restaurant",
                            tags=[gt("neuter")],
                        ),
                        BreakdownItem(
                            german="nebenan",
                            english="next door",
                            tags=[gt("place"), gt("adverb")],
                        ),
                        BreakdownItem(
                            german="voll",
                            english="full",
                            tags=[gt("adjective")],
                        ),
                        BreakdownItem(
                            german="war",
                            english="was",
                            tags=[gt("verb"), gt("simple past")],
                            verb_help=SEIN_PAST,
                        ),
                        BreakdownItem(
                            german="Weil das Restaurant nebenan voll war",
                            english="Because the restaurant next door was full",
                            tags=[gt("subordinate clause"), gt("verb-final")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="hat",
                            english="has",
                            tags=[gt("auxiliary"), gt("present")],
                            verb_help=HABEN_PRESENT,
                        ),
                        BreakdownItem(
                            german="uns",
                            english="to us",
                            tags=[gt("personal pronoun"), gt("dative")],
                        ),
                        BreakdownItem(
                            german="die Kellnerin",
                            english="waitress",
                            tags=[gt("fem.")],
                        ),
                        BreakdownItem(
                            german="empfohlen",
                            english="recommended",
                            tags=[gt("past participle"), gt("irregular")],
                            verb_help=EMPFEHLEN_PERFECT,
                        ),
                        BreakdownItem(
                            german="hat uns die Kellnerin ... empfohlen",
                            english="the waitress recommended ... to us",
                            tags=[gt("perfect")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="ruhig",
                            english="quiet",
                            tags=[gt("adjective")],
                            source_forms=["ruhigen"],
                        ),
                        BreakdownItem(
                            german="der Imbiss",
                            english="snack bar",
                            tags=[gt("masc.")],
                            source_forms=["den"],
                        ),
                        BreakdownItem(
                            german="den ruhigen Imbiss",
                            english="the quiet snack bar",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="um",
                            english="around",
                            tags=[gt("preposition"), gt("accusative")],
                        ),
                        BreakdownItem(
                            german="die Ecke",
                            english="corner",
                            tags=[gt("fem.")],
                        ),
                        BreakdownItem(
                            german="um die Ecke",
                            english="around the corner",
                            tags=[gt("fixed phrase"), gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/evening-with-friends-3.wav",
        ),
        Sentence(
            text=(
                "Dort habe ich die Gemüsesuppe bestellt, und meine Freunde "
                "haben sich die große Pizza geteilt."
            ),
            natural_meaning=(
                "I ordered the vegetable soup there, and my friends shared "
                "the large pizza."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="dort",
                            english="there",
                            tags=[gt("place"), gt("adverb")],
                        ),
                        BreakdownItem(
                            german="habe",
                            english="have",
                            tags=[gt("auxiliary"), gt("present")],
                            verb_help=HABEN_PRESENT,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[gt("subject"), gt("personal pronoun")],
                        ),
                        BreakdownItem(
                            german="bestellt",
                            english="ordered",
                            tags=[gt("past participle"), gt("regular")],
                            verb_help=BESTELLEN_PERFECT,
                        ),
                        BreakdownItem(
                            german="Dort habe ich ... bestellt",
                            english="I ordered ... there",
                            tags=[gt("perfect"), gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="die Gemüsesuppe",
                            english="vegetable soup",
                            tags=[gt("fem."), gt("compound noun")],
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="und",
                            english="and",
                            tags=[gt("conjunction"), gt("coordinating")],
                        ),
                        BreakdownItem(
                            german="mein",
                            english="my",
                            tags=[gt("possessive")],
                            source_forms=["meine"],
                        ),
                        BreakdownItem(
                            german="der Freund",
                            english="friend",
                            tags=[gt("masc."), gt("plural")],
                            source_forms=["Freunde"],
                        ),
                        BreakdownItem(
                            german="meine Freunde",
                            english="my friends",
                            tags=[gt("nominative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="haben",
                            english="have",
                            tags=[gt("auxiliary"), gt("present")],
                            verb_help=HABEN_PRESENT,
                        ),
                        BreakdownItem(
                            german="sich",
                            english="for themselves",
                            tags=[gt("personal pronoun"), gt("dative")],
                        ),
                        BreakdownItem(
                            german="geteilt",
                            english="shared",
                            tags=[gt("past participle"), gt("regular")],
                            verb_help=TEILEN_PERFECT,
                        ),
                        BreakdownItem(
                            german="haben sich ... geteilt",
                            english="shared ...",
                            tags=[gt("perfect"), gt("reflexive")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="groß",
                            english="large",
                            tags=[gt("adjective")],
                            source_forms=["große"],
                        ),
                        BreakdownItem(
                            german="die Pizza",
                            english="pizza",
                            tags=[gt("fem.")],
                        ),
                        BreakdownItem(
                            german="die große Pizza",
                            english="the large pizza",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/evening-with-friends-4.wav",
        ),
        Sentence(
            text=(
                "Danach sind wir noch durch den Park gelaufen und haben lange "
                "über unsere Pläne für das Wochenende gesprochen."
            ),
            natural_meaning=(
                "Afterwards, we walked through the park and talked for a long "
                "time about our plans for the weekend."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="danach",
                            english="afterwards",
                            tags=[gt("time"), gt("adverb")],
                        ),
                        BreakdownItem(
                            german="sind",
                            english="are",
                            tags=[gt("auxiliary"), gt("present")],
                            verb_help=SEIN_PRESENT,
                        ),
                        BreakdownItem(
                            german="wir",
                            english="we",
                            tags=[gt("subject"), gt("personal pronoun")],
                        ),
                        BreakdownItem(
                            german="noch",
                            english="still/then",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(
                            german="gelaufen",
                            english="walked",
                            tags=[gt("past participle"), gt("irregular")],
                            verb_help=LAUFEN_PERFECT,
                        ),
                        BreakdownItem(
                            german="Danach sind wir noch ... gelaufen",
                            english="Afterwards, we walked ...",
                            tags=[gt("perfect"), gt("inversion")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="durch",
                            english="through",
                            tags=[gt("preposition"), gt("accusative")],
                        ),
                        BreakdownItem(
                            german="der Park",
                            english="park",
                            tags=[gt("masc.")],
                            source_forms=["den"],
                        ),
                        BreakdownItem(
                            german="durch den Park",
                            english="through the park",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="und",
                            english="and",
                            tags=[gt("conjunction"), gt("coordinating")],
                        ),
                        BreakdownItem(
                            german="haben",
                            english="have",
                            tags=[gt("auxiliary"), gt("present")],
                            verb_help=HABEN_PRESENT,
                        ),
                        BreakdownItem(
                            german="lange",
                            english="for a long time",
                            tags=[gt("time"), gt("adverb")],
                        ),
                        BreakdownItem(
                            german="gesprochen",
                            english="talked",
                            tags=[gt("past participle"), gt("irregular")],
                            verb_help=SPRECHEN_PERFECT,
                        ),
                        BreakdownItem(
                            german="haben lange ... gesprochen",
                            english="talked for a long time ...",
                            tags=[gt("perfect")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="über",
                            english="about",
                            tags=[gt("preposition"), gt("accusative")],
                        ),
                        BreakdownItem(
                            german="unser",
                            english="our",
                            tags=[gt("possessive")],
                            source_forms=["unsere"],
                        ),
                        BreakdownItem(
                            german="der Plan",
                            english="plan",
                            tags=[gt("masc."), gt("plural")],
                            source_forms=["Pläne"],
                        ),
                        BreakdownItem(
                            german="über unsere Pläne",
                            english="about our plans",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="für",
                            english="for",
                            tags=[gt("preposition"), gt("accusative")],
                        ),
                        BreakdownItem(
                            german="das Wochenende",
                            english="weekend",
                            tags=[gt("neuter"), gt("compound noun")],
                        ),
                        BreakdownItem(
                            german="für das Wochenende",
                            english="for the weekend",
                            tags=[gt("accusative")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/evening-with-friends-5.wav",
        ),
        Sentence(
            text=(
                "Gegen Mitternacht bin ich müde, aber sehr zufrieden nach "
                "Hause gefahren."
            ),
            natural_meaning=(
                "Around midnight, I went home tired but very satisfied."
            ),
            breakdown_groups=[
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="gegen",
                            english="around",
                            tags=[gt("preposition"), gt("accusative")],
                        ),
                        BreakdownItem(
                            german="die Mitternacht",
                            english="midnight",
                            tags=[gt("fem.")],
                        ),
                        BreakdownItem(
                            german="Gegen Mitternacht",
                            english="around midnight",
                            tags=[gt("time")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="bin",
                            english="am",
                            tags=[gt("auxiliary"), gt("present")],
                            verb_help=SEIN_PRESENT,
                        ),
                        BreakdownItem(
                            german="ich",
                            english="I",
                            tags=[gt("subject"), gt("personal pronoun")],
                        ),
                        BreakdownItem(
                            german="gefahren",
                            english="went/travelled",
                            tags=[gt("past participle"), gt("irregular")],
                            verb_help=FAHREN_PERFECT,
                        ),
                        BreakdownItem(
                            german="bin ich ... gefahren",
                            english="I went/travelled ...",
                            tags=[gt("perfect")],
                            kind="phrase",
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="müde",
                            english="tired",
                            tags=[gt("adjective")],
                        ),
                        BreakdownItem(
                            german="aber",
                            english="but",
                            tags=[gt("conjunction"), gt("coordinating")],
                        ),
                        BreakdownItem(
                            german="sehr",
                            english="very",
                            tags=[gt("adverb")],
                        ),
                        BreakdownItem(
                            german="zufrieden",
                            english="satisfied",
                            tags=[gt("adjective")],
                        ),
                    ]
                ),
                BreakdownGroup(
                    items=[
                        BreakdownItem(
                            german="nach",
                            english="to",
                            tags=[gt("preposition"), gt("dative")],
                        ),
                        BreakdownItem(
                            german="das Haus",
                            english="home/house",
                            tags=[gt("neuter")],
                            source_forms=["Hause"],
                        ),
                        BreakdownItem(
                            german="nach Hause",
                            english="home",
                            tags=[gt("direction"), gt("fixed phrase")],
                            kind="phrase",
                        ),
                    ]
                ),
            ],
            audio_path="assets/audio/sentences/evening-with-friends-6.wav",
        ),
    ],
)


from .additional_lessons import ADDITIONAL_LESSONS


LESSONS = [
    BAKERY_LESSON,
    MARKET_LESSON,
    SEED_LESSON,
    FRIENDS_EVENING_LESSON,
    *ADDITIONAL_LESSONS,
]
