(async function () {
  const input = document.getElementById("input");
  const output = document.getElementById("output");
  const alts = document.getElementById("alts");
  const meta = document.getElementById("meta");
  const samples = document.getElementById("samples");
  const failures = document.getElementById("failures");

  const sampleTexts = [
    "salam labas 3lik",
    "wach bghiti 9ahwa",
    "kan7ebbek",
    "mzyaaaaan",
    "ghadi nmchi",
  ];

  sampleTexts.forEach((text) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "chip";
    btn.textContent = text;
    btn.addEventListener("click", () => {
      input.value = text;
      render();
      input.focus();
    });
    samples.appendChild(btn);
  });

  const [rules, fixtures] = await Promise.all([
    fetch("rules.json").then((r) => r.json()),
    fetch("fixtures-transliteration.json").then((r) => r.json()),
  ]);

  const engine = window.DarijaToolkit.loadRules(rules);

  function render() {
    const result = engine.transliterate(input.value || "");
    output.textContent = result.text || "—";
    alts.innerHTML = "";
    const ambiguous = result.tokens.filter((t) => t.alternatives.length);
    meta.textContent = ambiguous.length
      ? `${ambiguous.length} ambiguous token(s). Scores are hand weights, not probabilities.`
      : "No ambiguous tokens in this input.";
    ambiguous.forEach((token) => {
      const block = document.createElement("li");
      block.innerHTML = `<span><code>${escapeHtml(token.source)}</code> → <span class="arab">${escapeHtml(token.best.text)}</span> <span class="meta">(${token.best.score})</span></span>`;
      alts.appendChild(block);
      token.alternatives.forEach((alt) => {
        const row = document.createElement("li");
        row.innerHTML = `<span class="arab">${escapeHtml(alt.text)}</span><span class="meta">${alt.score}</span>`;
        alts.appendChild(row);
      });
    });
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  (fixtures.cases || [])
    .filter((c) => c.known_failure)
    .forEach((c) => {
      const engineOut = engine.transliterate(c.input).text;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><code>${escapeHtml(c.input)}</code></td>
        <td class="arab-cell">${escapeHtml(c.expected)}</td>
        <td class="arab-cell fail">${escapeHtml(engineOut)}</td>`;
      failures.appendChild(tr);
    });

  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.getAttribute("data-copy");
      const node = document.getElementById(id);
      const text = node ? node.innerText : "";
      try {
        await navigator.clipboard.writeText(text);
        btn.textContent = "Copied";
        setTimeout(() => {
          btn.textContent = "Copy commands";
        }, 1200);
      } catch {
        btn.textContent = "Copy failed";
      }
    });
  });

  input.addEventListener("input", render);
  render();
})();
