(async function () {
  const input = document.getElementById("input");
  const output = document.getElementById("output");
  const alts = document.getElementById("alts");
  const meta = document.getElementById("meta");
  const samples = document.getElementById("samples");
  const failureRows = document.getElementById("failure-rows");

  const sampleTexts = [
    "salam labas 3lik",
    "wach bghiti 9ahwa",
    "kan7ebbek",
    "mzyaaaaan",
    "ghadi nmchi",
  ];

  let engine = null;

  function cell(text, className) {
    const td = document.createElement("td");
    td.textContent = text;
    if (className) td.className = className;
    return td;
  }

  function altRow(text, score, isAlternative) {
    const li = document.createElement("li");
    if (isAlternative) li.className = "alt";
    const word = document.createElement("span");
    word.className = "arabic";
    word.lang = "ar";
    word.dir = "rtl";
    word.textContent = text;
    const number = document.createElement("span");
    number.className = "score";
    number.textContent = score;
    li.append(word, number);
    return li;
  }

  function render() {
    if (!engine) return;
    const result = engine.transliterate(input.value || "");
    output.textContent = result.text || "…";
    alts.replaceChildren();
    const ambiguous = result.tokens.filter((token) => token.alternatives.length);
    meta.textContent = ambiguous.length
      ? `${ambiguous.length} ambiguous word${ambiguous.length === 1 ? "" : "s"}. Scores rank the options; they are not probabilities.`
      : "No ambiguous words in this input.";
    ambiguous.forEach((token) => {
      alts.appendChild(altRow(token.best.text, token.best.score, false));
      token.alternatives.forEach((alt) => alts.appendChild(altRow(alt.text, alt.score, true)));
    });
  }

  sampleTexts.forEach((text) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chip";
    button.textContent = text;
    button.addEventListener("click", () => {
      input.value = text;
      render();
    });
    samples.appendChild(button);
  });

  try {
    const [rules, fixtures] = await Promise.all([
      fetch("rules.json").then((response) => response.json()),
      fetch("fixtures-transliteration.json").then((response) => response.json()),
    ]);
    engine = window.DarijaToolkit.loadRules(rules);

    const cases = fixtures.cases || [];
    const failing = cases.filter((item) => item.known_failure);
    document.getElementById("fact-fixtures").textContent = String(cases.length);
    document.getElementById("fact-failures").textContent = String(failing.length);

    failureRows.replaceChildren();
    failing.forEach((item) => {
      const row = document.createElement("tr");
      const source = document.createElement("td");
      const code = document.createElement("code");
      code.textContent = item.input;
      source.appendChild(code);
      row.append(
        source,
        cell(item.expected, "arabic"),
        cell(engine.transliterate(item.input).text, "arabic miss"),
      );
      failureRows.appendChild(row);
    });
  } catch {
    meta.textContent = "Could not load the rule files. Reload the page to try again.";
    failureRows.replaceChildren();
    const row = document.createElement("tr");
    const td = cell("Could not load the fixture file. Reload the page to try again.");
    td.colSpan = 3;
    row.appendChild(td);
    failureRows.appendChild(row);
    return;
  }

  input.addEventListener("input", render);
  render();
})();
