const root = document.documentElement;
const themeButton = document.querySelector(".theme-button");
const appShell = document.querySelector(".app-shell");
const listeningStep = document.querySelector(".listening-step");
const listeningTitle = document.querySelector(".listening-title");
const playbackButton = document.querySelector(".playback-button");
const replayButton = document.querySelector(".replay-button");
const lessonButton = document.querySelector(".lesson-nav");
const lessonPage = document.querySelector(".lesson-page");
const lessonPlaybackButton = document.querySelector(".lesson-playback-button");
const breakdownButton = document.querySelector(".breakdown-nav");
const breakdownPage = document.querySelector(".breakdown-page");
const speakingPage = document.querySelector(".speaking-page");
const speakingPrompts = document.querySelector(".speaking-prompts");
const sentenceSelector = document.querySelector(".sentence-selector");
const sentenceStudy = document.querySelector(".sentence-study");
const breakdownPlaybackButton = document.querySelector(".breakdown-playback-button");
const sentenceGerman = document.querySelector(".sentence-german");
const sentenceEnglish = document.querySelector(".sentence-english");
const sentenceMap = document.querySelector(".sentence-map");
const speedButtons = document.querySelectorAll("[data-speed]");
const lessonSpeedButtons = document.querySelectorAll("[data-lesson-speed]");
const referenceDialog = document.querySelector(".reference-dialog");
const referenceContent = document.querySelector(".reference-content");
const storedTheme = localStorage.getItem("nochmal-theme");
const coursePicker = document.querySelector(".course-picker");
const coursePickerWrap = document.querySelector(".course-picker-wrap");
const courseMenu = document.querySelector(".course-menu");
const courseLevel = document.querySelector(".course-level");
const lessonPicker = document.querySelector(".lesson-picker");
const lessonPickerWrap = document.querySelector(".lesson-picker-wrap");
const lessonMenu = document.querySelector(".lesson-menu");
const lessonNumber = document.querySelector(".lesson-number");
const lessonTitle = document.querySelector(".lesson-title");
const germanPassage = document.querySelector(".german-passage");
let lessons = {};
let catalogEntries = [];
let selectedCourse = null;
let activeLessonId = null;
let lessonAudioDirectory = "";
const listeningAudio = new Audio();
const lessonAudio = new Audio();
const sentenceAudio = new Audio();
let sentenceButtons = [];
let lessonOptions = [];
let courseOptions = [];

let sentenceData = [];
let lastShellScrollTop = appShell.scrollTop;
let lessonLoadToken = 0;
let lessonObserver;
let breakdownObserver;
let speakingObserver;
let typingRun = 0;

[listeningAudio, lessonAudio, sentenceAudio].forEach((audio) => {
  audio.preload = "metadata";
});

let tagDescriptions = {
  "proper noun": "The specific name of a person, place, or organization.",
  verb: "A word expressing an action, process, or state.",
  present: "A tense for current actions, habits, or general facts.",
  determiner: "A word that specifies quantity or reference before a noun.",
  accusative: "The case often used for a direct object.",
  noun: "A word for a person, place, thing, or idea.",
  "masc.": "A noun with masculine grammatical gender.",
  "fem.": "A noun with feminine grammatical gender.",
  preposition: "A word showing a relationship and governing a case.",
  numeral: "A word expressing number, quantity, or order.",
  time: "Shows when something happens.",
  frequency: "Shows how often something happens.",
  "main clause": "A complete clause that can stand on its own.",
  "verb-second": "The finite verb occupies the second sentence position.",
  separable: "A verb whose prefix separates in some sentence patterns.",
  "personal pronoun": "A word such as ich or mir that refers to a participant.",
  nominative: "The case normally used for the subject.",
  dative: "The case often used for a recipient or indirect object.",
  inversion: "The verb comes before the subject after another first element.",
  contraction: "A shortened form made by combining two words.",
  direction: "Shows movement toward or away from a place.",
  possessive: "A form expressing ownership or another close relationship.",
  conjunction: "A word joining words, phrases, or clauses.",
  coordinating: "Joins elements that have equal grammatical status.",
};

const cases = ["nominative", "accusative", "dative", "genitive"];
const genderColumns = ["masculine", "feminine", "neuter", "plural"];
const definiteArticles = {
  nominative: ["der", "die", "das", "die"],
  accusative: ["den", "die", "das", "die"],
  dative: ["dem", "der", "dem", "den"],
  genitive: ["des", "der", "des", "der"],
};
const possessiveEndings = {
  nominative: ["", "e", "", "e"],
  accusative: ["en", "e", "", "e"],
  dative: ["em", "er", "em", "en"],
  genitive: ["es", "er", "es", "er"],
};
const derWordEndings = {
  nominative: ["er", "e", "es", "e"],
  accusative: ["en", "e", "es", "e"],
  dative: ["em", "er", "em", "en"],
  genitive: ["es", "er", "es", "er"],
};

function createElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function prefersDarkTheme() {
  return window.matchMedia("(prefers-color-scheme: dark)").matches;
}

function setTheme(theme, persist = true) {
  root.dataset.theme = theme;
  themeButton.setAttribute("aria-pressed", String(theme === "dark"));
  themeButton.setAttribute("aria-label", `Switch to ${theme === "dark" ? "light" : "dark"} mode`);
  if (persist) localStorage.setItem("nochmal-theme", theme);
}

if (storedTheme === "light" || storedTheme === "dark") {
  setTheme(storedTheme, false);
} else {
  themeButton.setAttribute("aria-pressed", String(prefersDarkTheme()));
  themeButton.setAttribute("aria-label", `Switch to ${prefersDarkTheme() ? "light" : "dark"} mode`);
}

themeButton.addEventListener("click", () => {
  const currentTheme = root.dataset.theme || (prefersDarkTheme() ? "dark" : "light");
  setTheme(currentTheme === "dark" ? "light" : "dark");
});

function setPlaying(isPlaying) {
  appShell.dataset.playing = String(isPlaying);
  if (isPlaying) appShell.dataset.started = "true";
  playbackButton.setAttribute("aria-pressed", String(isPlaying));
  playbackButton.setAttribute("aria-label", isPlaying ? "Pause audio" : "Play audio");
}

function setLessonPlaying(isPlaying) {
  lessonPage.dataset.playing = String(isPlaying);
  lessonPlaybackButton.setAttribute("aria-pressed", String(isPlaying));
  lessonPlaybackButton.setAttribute("aria-label", isPlaying ? "Pause lesson audio" : "Play lesson audio");
}

function setSentencePlaying(isPlaying) {
  sentenceStudy.dataset.playing = String(isPlaying);
  breakdownPlaybackButton.setAttribute("aria-pressed", String(isPlaying));
  breakdownPlaybackButton.setAttribute("aria-label", isPlaying ? "Pause selected sentence" : "Play selected sentence");
}

function resetAudio(audio) {
  audio.pause();
  audio.currentTime = 0;
}

function stopListeningAudio() {
  resetAudio(listeningAudio);
  setPlaying(false);
}

function stopLessonAudio() {
  resetAudio(lessonAudio);
  setLessonPlaying(false);
}

function stopSentenceAudio() {
  resetAudio(sentenceAudio);
  setSentencePlaying(false);
}

function playListeningAudio(restart = false) {
  stopLessonAudio();
  stopSentenceAudio();
  if (restart) listeningAudio.currentTime = 0;
  void listeningAudio.play().then(() => setPlaying(true)).catch(() => setPlaying(false));
}

function playLessonAudio() {
  stopListeningAudio();
  stopSentenceAudio();
  void lessonAudio.play().then(() => setLessonPlaying(true)).catch(() => setLessonPlaying(false));
}

function playSentenceAudio() {
  stopListeningAudio();
  stopLessonAudio();
  void sentenceAudio.play().then(() => setSentencePlaying(true)).catch(() => setSentencePlaying(false));
}

playbackButton.addEventListener("click", () => {
  if (appShell.dataset.playing === "true") {
    listeningAudio.pause();
    setPlaying(false);
    return;
  }
  playListeningAudio();
});

appShell.addEventListener("scroll", () => {
  const nextScrollTop = appShell.scrollTop;
  if (nextScrollTop > lastShellScrollTop) {
    if (appShell.dataset.playing === "true") stopListeningAudio();
    if (lessonPage.dataset.playing === "true") stopLessonAudio();
  }
  lastShellScrollTop = nextScrollTop;
}, { passive: true });

speedButtons.forEach((button) => {
  button.addEventListener("click", () => {
    speedButtons.forEach((option) => option.setAttribute("aria-pressed", String(option === button)));
    appShell.style.setProperty("--orbit-duration", `${2.4 / Number(button.dataset.speed)}s`);
    listeningAudio.playbackRate = Number(button.dataset.speed);
  });
});

replayButton.addEventListener("click", () => {
  playListeningAudio(true);
  replayButton.animate([{ transform: "rotate(0deg)" }, { transform: "rotate(-360deg)" }], { duration: 420, easing: "cubic-bezier(.2, .8, .2, 1)" });
});

lessonButton.addEventListener("click", () => lessonPage.scrollIntoView({ behavior: "smooth", block: "start" }));

lessonPlaybackButton.addEventListener("click", () => {
  if (lessonPage.dataset.playing === "true") {
    lessonAudio.pause();
    setLessonPlaying(false);
    return;
  }
  playLessonAudio();
});

lessonSpeedButtons.forEach((button) => {
  button.addEventListener("click", () => {
    lessonSpeedButtons.forEach((option) => option.setAttribute("aria-pressed", String(option === button)));
    lessonPage.style.setProperty("--lesson-orbit-duration", `${2.4 / Number(button.dataset.lessonSpeed)}s`);
    lessonAudio.playbackRate = Number(button.dataset.lessonSpeed);
  });
});

breakdownButton.addEventListener("click", () => breakdownPage.scrollIntoView({ behavior: "smooth", block: "start" }));

breakdownPlaybackButton.addEventListener("click", () => {
  if (sentenceStudy.dataset.playing === "true") {
    sentenceAudio.pause();
    setSentencePlaying(false);
    return;
  }
  playSentenceAudio();
});

listeningAudio.addEventListener("ended", () => stopListeningAudio());
lessonAudio.addEventListener("ended", () => stopLessonAudio());
sentenceAudio.addEventListener("ended", () => stopSentenceAudio());

function showReference(content, trigger) {
  const triggerRect = trigger?.getBoundingClientRect();
  referenceContent.replaceChildren(content);
  if (referenceDialog.open) referenceDialog.close();
  referenceDialog.showModal();
  if (!triggerRect || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const sheet = referenceDialog.querySelector(".reference-sheet");
  const sheetRect = sheet.getBoundingClientRect();
  const originX = Math.max(24, Math.min(sheetRect.width - 24, triggerRect.left + (triggerRect.width / 2) - sheetRect.left));
  const startOffset = Math.max(28, triggerRect.top + (triggerRect.height / 2) - sheetRect.top);
  sheet.style.transformOrigin = `${originX}px 100%`;
  sheet.animate(
    [
      { opacity: 0, transform: `translateY(${startOffset}px) scale(.94)` },
      { opacity: 1, transform: "translateY(0) scale(1)" },
    ],
    { duration: 420, easing: "cubic-bezier(.16, 1, .3, 1)" },
  );
}

referenceDialog.addEventListener("click", (event) => {
  if (event.target === referenceDialog) referenceDialog.close();
});

function referenceHeading(title, subtitle) {
  const wrapper = createElement("div");
  wrapper.append(createElement("h3", "reference-title", title), createElement("p", "reference-subtitle", subtitle));
  return wrapper;
}

function showTagReference(tag, trigger) {
  const content = createElement("div");
  content.append(referenceHeading(tag.label, tag.category), createElement("p", "reference-definition", tagDescriptions[tag.label] || "Grammar reference."));
  showReference(content, trigger);
}

function tableElement(headers, rows, currentCell) {
  const wrap = createElement("div", "reference-table-wrap");
  const table = createElement("table", "reference-table");
  const head = document.createElement("thead");
  const headRow = document.createElement("tr");
  headers.forEach((header) => headRow.append(createElement("th", "", header)));
  head.append(headRow);
  const body = document.createElement("tbody");
  rows.forEach((row, rowIndex) => {
    const tr = document.createElement("tr");
    row.forEach((value, columnIndex) => tr.append(createElement("td", rowIndex === currentCell?.row && columnIndex === currentCell?.column ? "is-current" : "", value)));
    body.append(tr);
  });
  table.append(head, body);
  wrap.append(table);
  return wrap;
}

function showVerbReference(item, trigger) {
  const help = item.verb_help;
  const content = createElement("div");
  const fields = createElement("div", "reference-fields");
  const dictionaryField = createElement("div", "reference-field");
  dictionaryField.append(createElement("span", "", "Dictionary form"), createElement("strong", "", help.infinitive));
  const meaningField = createElement("div", "reference-field");
  meaningField.append(createElement("span", "", "English"), createElement("strong", "", help.english || item.english));
  fields.append(dictionaryField, meaningField);
  const current = createElement("div", "current-form");
  current.append(createElement("span", "", "Form in this sentence"), createElement("strong", "", item.german), createElement("span", "", item.english));
  const presentForms = help.present_forms || help.forms;
  const englishForms = help.present_english_forms || help.current_english_forms;
  const rows = presentForms.map((form, index) => [form.pronoun, form.verb, englishForms[index]]);
  content.append(referenceHeading(help.infinitive, help.tense), fields, createElement("p", "reference-section-title", "Simple present"), tableElement(["pronoun", "German", "English"], rows), current);
  const hasOtherForms = help.forms?.length && (help.forms.length !== presentForms.length || help.forms.some((form, index) => form.pronoun !== presentForms[index]?.pronoun || form.verb !== presentForms[index]?.verb));
  if (hasOtherForms) {
    const tenseRows = help.forms.map((form, index) => [form.pronoun, form.verb, help.current_english_forms?.[index] || ""]);
    content.append(createElement("p", "reference-section-title", help.tense), tableElement(["pronoun", "German", "English"], tenseRows));
  }
  showReference(content, trigger);
}

function tableForInflection(help) {
  if (help.paradigm === "definite") return definiteArticles;
  if (help.paradigm === "possessive") return Object.fromEntries(cases.map((grammarCase) => [grammarCase, possessiveEndings[grammarCase].map((ending) => `${help.base}${ending}`)]));
  if (help.paradigm === "der-word") {
    const stem = help.base === "jeder" ? "jed" : help.base;
    return Object.fromEntries(cases.map((grammarCase) => [grammarCase, derWordEndings[grammarCase].map((ending) => `${stem}${ending}`)]));
  }
  return definiteArticles;
}

function showInflectionReference(help, trigger) {
  const kindLabels = { "definite-article": "Definite article", "indefinite-article": "Indefinite article", "negative-determiner": "Negative determiner", "possessive-determiner": "Possessive determiner", "der-word-determiner": "Der-word determiner", adjective: "Adjective", "personal-pronoun": "Personal pronoun" };
  const paradigmLabels = { definite: "Definite-article forms", indefinite: "Indefinite-article forms", negative: "Negative-determiner forms", possessive: "Possessive forms", "der-word": "Der-word determiner forms", "weak-adjective": "Weak adjective endings", "mixed-adjective": "Mixed adjective endings", "strong-adjective": "Strong adjective endings", "personal-pronoun": "Personal-pronoun forms" };
  const content = createElement("div");
  const fields = createElement("div", "reference-fields");
  const baseField = createElement("div", "reference-field");
  baseField.append(createElement("span", "", "Base form"), createElement("strong", "", help.base));
  const sentenceField = createElement("div", "reference-field");
  sentenceField.append(createElement("span", "", "Sentence form"), createElement("strong", "", help.resolved_form || help.surface));
  fields.append(baseField, sentenceField);
  if (help.contraction) {
    const contractionField = createElement("div", "reference-field");
    contractionField.append(createElement("span", "", "Contraction"), createElement("strong", "", `${help.surface} = ${help.contraction}`));
    fields.append(contractionField);
  }
  const chips = createElement("div", "reference-chips");
  [help.case, help.gender || help.pronoun_slot, help.number].filter(Boolean).forEach((value) => chips.append(createElement("span", "", value)));
  const table = help.reference_table || tableForInflection(help);
  const columns = help.reference_columns || genderColumns;
  const rows = cases.map((grammarCase) => [grammarCase, ...table[grammarCase]]);
  const column = help.selected_column === undefined ? genderColumns.indexOf(help.gender) : help.selected_column;
  content.append(referenceHeading(help.surface, kindLabels[help.kind] || "Case reference"), fields, chips, createElement("p", "reference-section-title", paradigmLabels[help.paradigm] || "Forms"), tableElement(["case", ...columns], rows, { row: cases.indexOf(help.case), column: column + 1 }));
  showReference(content, trigger);
}

function sourceTokens(text) {
  return [...text.matchAll(/[\p{L}\p{N}]+(?:[-’'][\p{L}\p{N}]+)*/gu)].map((match) => ({
    text: match[0].toLocaleLowerCase("de"),
    start: match.index,
    end: match.index + match[0].length,
  }));
}

function formTokens(text) {
  return sourceTokens(text).map((token) => token.text);
}

function findTokenSequence(tokens, needle, fromToken) {
  for (let index = fromToken; index <= tokens.length - needle.length; index += 1) {
    if (needle.every((token, offset) => tokens[index + offset].text === token)) return index;
  }
  return -1;
}

function itemPosition(item, sentenceText, fromToken = 0) {
  const tokens = sourceTokens(sentenceText);
  const chunks = item.kind === "phrase"
    ? item.german.split(/\.{3}|…/u).map(formTokens).filter((chunk) => chunk.length)
    : (item.source_forms?.length ? item.source_forms : [item.german]).map(formTokens).filter((chunk) => chunk.length);
  let cursor = fromToken;
  let first = -1;
  let last = -1;
  for (const chunk of chunks) {
    const match = findTokenSequence(tokens, chunk, cursor);
    if (match < 0) return { start: Number.MAX_SAFE_INTEGER, end: Number.MAX_SAFE_INTEGER, nextToken: fromToken };
    if (first < 0) first = match;
    last = match + chunk.length - 1;
    cursor = last + 1;
  }
  return first < 0
    ? { start: Number.MAX_SAFE_INTEGER, end: Number.MAX_SAFE_INTEGER, nextToken: fromToken }
    : { start: tokens[first].start, end: tokens[last].end, nextToken: cursor };
}

function orderedItems(sentence) {
  const items = sentence.breakdown_groups.flatMap((group) => group.items);
  const tokens = sourceTokens(sentence.text);
  const claimed = new Set();
  const wordPositions = new Map();
  items.filter((item) => item.kind === "word").forEach((item) => {
    const chunks = (item.source_forms?.length ? item.source_forms : [item.german])
      .map(formTokens)
      .filter((chunk) => chunk.length);
    let firstMatch = -1;
    let firstEnd = -1;
    let failed = false;
    for (const chunk of chunks) {
      let match = -1;
      for (let index = 0; index <= tokens.length - chunk.length; index += 1) {
        const indexes = Array.from({ length: chunk.length }, (_, offset) => index + offset);
        if (
          indexes.every((tokenIndex) => !claimed.has(tokenIndex))
          && chunk.every((token, offset) => tokens[index + offset].text === token)
        ) {
          match = index;
          indexes.forEach((tokenIndex) => claimed.add(tokenIndex));
          break;
        }
      }
      if (match < 0) {
        failed = true;
        break;
      }
      if (firstMatch < 0) {
        firstMatch = match;
        firstEnd = match + chunk.length - 1;
      }
    }
    wordPositions.set(item, failed || firstMatch < 0
      ? { start: Number.MAX_SAFE_INTEGER, end: Number.MAX_SAFE_INTEGER }
      : { start: tokens[firstMatch].start, end: tokens[firstEnd].end });
  });
  return items.map((item, index) => ({
    item,
    index,
    ...(item.kind === "word" ? wordPositions.get(item) : itemPosition(item, sentence.text)),
  })).sort((left, right) => {
    if (left.end !== right.end) return left.end - right.end;
    if (left.item.kind !== right.item.kind) return left.item.kind === "word" ? -1 : 1;
    if (left.item.kind === "phrase" && left.item.german.length !== right.item.german.length) return left.item.german.length - right.item.german.length;
    return left.index - right.index;
  }).map((entry) => entry.item);
}

function grammarTag(tag) {
  const button = createElement("button", "grammar-tag", tag.label);
  button.type = "button";
  button.setAttribute("aria-label", `${tag.label}: open grammar reference`);
  button.addEventListener("click", () => showTagReference(tag, button));
  return button;
}

function inflectionSurfaceStart(text, surface, fromIndex) {
  const normalizedText = text.toLocaleLowerCase("de");
  const normalizedSurface = surface.toLocaleLowerCase("de");
  let start = normalizedText.indexOf(normalizedSurface, fromIndex);
  while (start >= 0) {
    const before = text[start - 1];
    const after = text[start + surface.length];
    const isWordCharacter = (character) => character && /[\p{L}\p{N}]/u.test(character);
    if (!isWordCharacter(before) && !isWordCharacter(after)) return start;
    start = normalizedText.indexOf(normalizedSurface, start + 1);
  }
  return -1;
}

function inflectedPhrase(item) {
  const german = createElement("span", "item-german");
  let cursor = 0;
  const references = item.inflection_help
    .map((help, index) => ({ help, index, start: inflectionSurfaceStart(item.german, help.surface, 0) }))
    .sort((left, right) => left.start - right.start || left.index - right.index);
  references.forEach(({ help }) => {
    const start = inflectionSurfaceStart(item.german, help.surface, cursor);
    if (start < 0) return;
    german.append(document.createTextNode(item.german.slice(cursor, start)));
    const form = createElement("button", "inline-inflection", item.german.slice(start, start + help.surface.length));
    form.type = "button";
    form.setAttribute("aria-label", `${help.surface}: open case forms`);
    form.addEventListener("click", () => showInflectionReference(help, form));
    german.append(form);
    cursor = start + help.surface.length;
  });
  german.append(document.createTextNode(item.german.slice(cursor)));
  return german;
}

function breakdownItem(item) {
  const hasVerbReference = Boolean(item.verb_help);
  const hasInflectionReference = Boolean(item.inflection_help?.length);
  const usesInlineInflections = item.kind === "phrase" && hasInflectionReference;
  const card = createElement("article", `breakdown-item ${item.kind}${hasVerbReference || (hasInflectionReference && !usesInlineInflections) ? " has-reference" : ""}${usesInlineInflections ? " has-inline-inflections" : ""}`);
  const copy = usesInlineInflections ? createElement("div", "item-copy") : createElement("button", "item-copy");
  if (!usesInlineInflections) {
    copy.type = "button";
    if (!hasVerbReference && !hasInflectionReference) copy.disabled = true;
    if (hasVerbReference || hasInflectionReference) {
      copy.setAttribute("aria-label", `${item.german}: open ${hasVerbReference ? "conjugation" : "case forms"}`);
      copy.addEventListener("click", () => hasVerbReference ? showVerbReference(item, copy) : showInflectionReference(item.inflection_help[0], copy));
    }
  }
  copy.append(usesInlineInflections ? inflectedPhrase(item) : createElement("span", "item-german", item.german), createElement("span", "item-english", item.english));
  card.append(copy);
  if (item.inflection_help?.length > 1 && !usesInlineInflections) {
    const references = createElement("div", "grammar-tags");
    item.inflection_help.forEach((help) => {
      const button = createElement("button", "grammar-tag", help.surface);
      button.type = "button";
      button.setAttribute("aria-label", `${help.surface}: open case forms`);
      button.addEventListener("click", () => showInflectionReference(help, button));
      references.append(button);
    });
    card.append(references);
  }
  if (item.tags?.length) {
    const tags = createElement("div", "grammar-tags");
    item.tags.forEach((tag) => tags.append(grammarTag(tag)));
    card.append(tags);
  }
  return card;
}

function renderSentence(index, animate = false) {
  const sentence = sentenceData[index];
  if (!sentence) return;
  stopSentenceAudio();
  const fileName = sentence.audio_path?.split("/").pop();
  if (fileName) sentenceAudio.src = `${lessonAudioDirectory}/${fileName}`;
  sentenceGerman.textContent = sentence.text;
  sentenceEnglish.textContent = sentence.natural_meaning;
  sentenceMap.replaceChildren(...orderedItems(sentence).map(breakdownItem));
  sentenceStudy.dataset.playing = "false";
  breakdownPlaybackButton.setAttribute("aria-pressed", "false");
  breakdownPlaybackButton.setAttribute("aria-label", "Play selected sentence");
  if (animate && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) sentenceStudy.animate([{ opacity: .45, transform: "translateY(6px)" }, { opacity: 1, transform: "translateY(0)" }], { duration: 360, easing: "cubic-bezier(.2, .8, .2, 1)" });
}

function renderSentenceButtons(count) {
  sentenceButtons = Array.from({ length: count }, (_, index) => {
    const button = createElement("button", "", String(index + 1));
    button.type = "button";
    button.dataset.sentence = String(index);
    button.setAttribute("aria-pressed", String(index === 0));
    button.addEventListener("click", () => {
      sentenceButtons.forEach((option) => option.setAttribute("aria-pressed", String(option === button)));
      renderSentence(index, true);
      breakdownPage.scrollIntoView({ behavior: "smooth", block: "start" });
    });
    return button;
  });
  sentenceSelector.replaceChildren(...sentenceButtons);
}

function renderSpeakingPractice(sentences) {
  const prompts = sentences.map((sentence, index) => {
    const prompt = createElement("article", "speaking-prompt");
    const number = createElement("span", "speaking-number", String(index + 1));
    const english = createElement("p", "speaking-english", sentence.natural_meaning);
    const answerId = `speaking-answer-${index + 1}`;
    const answer = createElement("p", "speaking-german", sentence.text);
    answer.id = answerId;
    answer.lang = "de";
    answer.hidden = true;
    const reveal = createElement("button", "speaking-reveal", "Reveal German");
    reveal.type = "button";
    reveal.setAttribute("aria-controls", answerId);
    reveal.setAttribute("aria-expanded", "false");
    reveal.addEventListener("click", () => {
      const revealed = answer.hidden;
      answer.hidden = !revealed;
      reveal.textContent = revealed ? "Hide German" : "Reveal German";
      reveal.setAttribute("aria-expanded", String(revealed));
    });
    prompt.append(number, english, reveal, answer);
    return prompt;
  });
  speakingPrompts.replaceChildren(...prompts);
}

function updateVisibleLesson(payload) {
  lessonTitle.textContent = payload.lesson.title;
  germanPassage.replaceChildren(...payload.lesson.sentences.map((sentence) => createElement("p", "", sentence.text)));
  renderSpeakingPractice(payload.lesson.sentences);
}

async function loadLessonBreakdown() {
  const requestedLessonId = activeLessonId;
  const requestedLesson = lessons[requestedLessonId];
  const loadToken = ++lessonLoadToken;
  sentenceMap.replaceChildren(createElement("p", "map-loading", "Loading the lesson breakdown…"));
  try {
    const response = await fetch(requestedLesson.dataFile);
    if (!response.ok) throw new Error("Lesson data could not be loaded");
    const payload = await response.json();
    if (loadToken !== lessonLoadToken || requestedLessonId !== activeLessonId) return;
    if (payload.lesson?.id !== requestedLessonId) throw new Error("Unexpected lesson data");
    if (payload.tag_descriptions) tagDescriptions = payload.tag_descriptions;
    const paragraphFile = payload.lesson.audio_path?.split("/").pop();
    if (paragraphFile) {
      listeningAudio.src = `${lessonAudioDirectory}/${paragraphFile}`;
      lessonAudio.src = `${lessonAudioDirectory}/${paragraphFile}`;
    }
    updateVisibleLesson(payload);
    sentenceData = payload.lesson.sentences;
    renderSentenceButtons(sentenceData.length);
    renderSentence(0);
  } catch (error) {
    sentenceMap.replaceChildren(createElement("p", "map-error", "The lesson breakdown could not be displayed."));
    console.error(error);
  }
}

const courseLevels = ["A1.1", "A1.2", "A2.1", "A2.2"];

function courseForLesson(entry) {
  return entry.level;
}

function lessonNumberForEntry(entry) {
  return String(Number(entry.id.slice(-3))).padStart(2, "0");
}

function closePicker(picker, menu) {
  menu.hidden = true;
  picker.setAttribute("aria-expanded", "false");
}

function selectCourse(course) {
  selectedCourse = course;
  courseLevel.textContent = course;
  courseOptions.forEach((option) => option.setAttribute("aria-selected", String(option.dataset.courseOption === course)));
  renderLessonOptions(catalogEntries.filter((entry) => courseForLesson(entry) === course));
  closePicker(coursePicker, courseMenu);
  closePicker(lessonPicker, lessonMenu);
}

function chooseLesson(lessonId) {
  const lesson = lessons[lessonId];
  if (!lesson) return;
  const course = courseForLesson(lesson);
  if (course !== selectedCourse) selectCourse(course);
  closePicker(lessonPicker, lessonMenu);
  lessonOptions.forEach((option) => option.setAttribute("aria-selected", String(option.dataset.lessonOption === lessonId)));
  if (lessonId === activeLessonId) return;
  stopListeningAudio();
  stopLessonAudio();
  stopSentenceAudio();
  activeLessonId = lessonId;
  lessonAudioDirectory = lesson.audioDirectory;
  lessonNumber.textContent = lessonNumberForEntry(lesson);
  const paragraphFile = lesson.paragraphFile || "paragraph.wav";
  listeningAudio.src = `${lessonAudioDirectory}/${paragraphFile}`;
  lessonAudio.src = `${lessonAudioDirectory}/${paragraphFile}`;
  sentenceAudio.removeAttribute("src");
  sentenceData = [];
  sentenceSelector.replaceChildren();
  sentenceButtons = [];
  appShell.dataset.switching = "true";
  resetPlaybackRates();
  resetListeningIntroduction();
  lessonPage.dataset.revealed = "false";
  breakdownPage.dataset.revealed = "false";
  speakingPage.dataset.revealed = "false";
  speakingPrompts.replaceChildren();
  appShell.scrollTo({ top: 0, behavior: "auto" });
  window.requestAnimationFrame(() => {
    appShell.dataset.switching = "false";
    window.requestAnimationFrame(() => {
      typeListeningTitle();
      armRevealObservers();
    });
  });
  loadLessonBreakdown();
}

coursePicker.addEventListener("click", () => {
  closePicker(lessonPicker, lessonMenu);
  const opening = courseMenu.hidden;
  courseMenu.hidden = !opening;
  coursePicker.setAttribute("aria-expanded", String(opening));
});

lessonPicker.addEventListener("click", () => {
  closePicker(coursePicker, courseMenu);
  const opening = lessonMenu.hidden;
  lessonMenu.hidden = !opening;
  lessonPicker.setAttribute("aria-expanded", String(opening));
});

function renderLessonOptions(entries) {
  lessonOptions = entries.map((entry) => {
    const option = createElement("button", "", lessonNumberForEntry(entry));
    option.type = "button";
    option.setAttribute("role", "option");
    option.dataset.lessonOption = entry.id;
    option.setAttribute("aria-selected", "false");
    option.addEventListener("click", () => chooseLesson(entry.id));
    return option;
  });
  lessonMenu.replaceChildren(...lessonOptions);
}

function renderCourseOptions(entries) {
  courseOptions = courseLevels.map((course) => {
    const firstLesson = entries.find((entry) => courseForLesson(entry) === course);
    const option = createElement("button", "", firstLesson ? course : `${course} · Soon`);
    option.type = "button";
    option.setAttribute("role", "option");
    option.dataset.courseOption = course;
    option.setAttribute("aria-selected", "false");
    if (firstLesson) {
      option.addEventListener("click", () => chooseLesson(firstLesson.id));
    } else {
      option.disabled = true;
      option.setAttribute("aria-label", `${course} lessons are coming soon`);
    }
    return option;
  });
  courseMenu.replaceChildren(...courseOptions);
}

async function loadLessonCatalog() {
  try {
    const response = await fetch("./lessons.json");
    if (!response.ok) throw new Error("Lesson catalog could not be loaded");
    const catalog = await response.json();
    const entries = catalog.lessons;
    if (!Array.isArray(entries) || !entries.length) throw new Error("Lesson catalog is empty");
    if (entries.some((entry) => !courseLevels.includes(entry.level))) throw new Error("Lesson catalog has an unknown level");
    const previewId = new URLSearchParams(window.location.search).get("preview");
    if (previewId && /^a[12]-course-\d{3}$/.test(previewId)) {
      const previewDataFile = `../prepared/${previewId}/lesson-data.json`;
      const previewResponse = await fetch(previewDataFile);
      if (!previewResponse.ok) throw new Error("Lesson preview could not be loaded");
      const preview = await previewResponse.json();
      if (!courseLevels.includes(preview.lesson?.level)) throw new Error("Lesson preview has an unknown level");
      const existingIndex = entries.findIndex((entry) => entry.id === previewId);
      if (existingIndex >= 0) entries.splice(existingIndex, 1);
      entries.push({
        id: previewId,
        level: preview.lesson.level,
        number: previewId.slice(-2),
        dataFile: previewDataFile,
        audioDirectory: `../prepared/${previewId}/audio`,
      });
    }
    catalogEntries = entries;
    lessons = Object.fromEntries(entries.map((entry) => [entry.id, entry]));
    renderCourseOptions(entries);
    chooseLesson(previewId && lessons[previewId] ? previewId : entries[0].id);
  } catch (error) {
    sentenceMap.replaceChildren(createElement("p", "map-error", "The lesson list could not be displayed."));
    console.error(error);
  }
}

document.addEventListener("pointerdown", (event) => {
  if (!coursePickerWrap.contains(event.target)) closePicker(coursePicker, courseMenu);
  if (!lessonPickerWrap.contains(event.target)) {
    closePicker(lessonPicker, lessonMenu);
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  const courseWasOpen = !courseMenu.hidden;
  const lessonWasOpen = !lessonMenu.hidden;
  closePicker(coursePicker, courseMenu);
  closePicker(lessonPicker, lessonMenu);
  if (courseWasOpen) coursePicker.focus();
  else if (lessonWasOpen) lessonPicker.focus();
});

function armRevealObservers() {
  lessonObserver?.disconnect();
  breakdownObserver?.disconnect();
  speakingObserver?.disconnect();
  lessonObserver = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return;
    lessonPage.dataset.revealed = "true";
    lessonObserver.disconnect();
  }, { root: appShell, threshold: 0.01 });
  breakdownObserver = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return;
    breakdownPage.dataset.revealed = "true";
    breakdownObserver.disconnect();
  }, { root: appShell, threshold: 0.01 });
  speakingObserver = new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting) return;
    speakingPage.dataset.revealed = "true";
    speakingObserver.disconnect();
  }, { root: appShell, threshold: 0.01 });
  lessonObserver.observe(lessonPage);
  breakdownObserver.observe(breakdownPage);
  speakingObserver.observe(speakingPage);
}

loadLessonCatalog();

function revealListeningStep() {
  listeningStep.dataset.revealed = "true";
}

function resetPlaybackRates() {
  listeningAudio.playbackRate = 1;
  lessonAudio.playbackRate = 1;
  appShell.style.setProperty("--orbit-duration", "2.4s");
  lessonPage.style.setProperty("--lesson-orbit-duration", "2.4s");
  speedButtons.forEach((option) => option.setAttribute("aria-pressed", String(option.dataset.speed === "1")));
  lessonSpeedButtons.forEach((option) => option.setAttribute("aria-pressed", String(option.dataset.lessonSpeed === "1")));
}

function resetListeningIntroduction() {
  typingRun += 1;
  listeningStep.dataset.revealed = "false";
  listeningTitle.dataset.typing = "false";
  listeningTitle.textContent = "";
  appShell.dataset.started = "false";
  appShell.dataset.playing = "false";
  playbackButton.setAttribute("aria-pressed", "false");
  playbackButton.setAttribute("aria-label", "Play audio");
}

function restartListeningIntroduction() {
  resetListeningIntroduction();
  window.requestAnimationFrame(typeListeningTitle);
}

function typeListeningTitle() {
  const run = ++typingRun;
  const text = listeningTitle.dataset.text || "Play the audio.";
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    if (run !== typingRun) return;
    listeningTitle.textContent = text;
    revealListeningStep();
    return;
  }
  listeningTitle.textContent = "";
  listeningTitle.dataset.typing = "true";
  let index = 0;
  const typeNextCharacter = () => {
    if (run !== typingRun) return;
    index += 1;
    listeningTitle.textContent = text.slice(0, index);
    if (index < text.length) {
      window.setTimeout(typeNextCharacter, text[index] === " " ? 105 : 72);
      return;
    }
    listeningTitle.dataset.typing = "false";
    window.setTimeout(() => {
      if (run === typingRun) revealListeningStep();
    }, 180);
  };
  window.setTimeout(typeNextCharacter, 260);
}
