/* Port of darija_toolkit.transliterate + rules. Keep in sync via shared fixtures. */
(function (global) {
  "use strict";

  function loadRules(rules) {
    const SHORT_VOWELS = rules.short_vowels;
    const SEMIVOWELS = rules.semivowels;
    const DIGRAPHS = rules.digraphs;
    const LONG_VOWELS = rules.long_vowels;
    const CONSONANTS = rules.consonants;
    const C_SOFT = rules.c_soft;
    const C_HARD = rules.c_hard;
    const C_SOFT_BEFORE = rules.c_soft_before;
    const DIGITS = rules.digits;
    const DIGIT_HAMZA_INITIAL = rules.digit_hamza_initial;
    const VOWELS = rules.vowels;
    const LEXICON = rules.lexicon;

    const TOKEN = /[A-Za-z0-9]+/g;
    const REPEAT = /(.)\1+/g;
    const ELONGATION = /(.)\1{2,}/g;

    function collapseElongation(token) {
      return token.replace(ELONGATION, (m, ch) => {
        if (SHORT_VOWELS.includes(ch)) return ch + ch;
        if (ch === "h") return "hhh";
        return ch;
      });
    }

    function undouble(token) {
      return token.replace(/([a-z])\1/g, (m, ch) => {
        if (SHORT_VOWELS.includes(ch) || ch === "h") return m;
        return ch;
      });
    }

    function segment(token) {
      const units = [];
      let i = 0;
      while (i < token.length) {
        const pair = token.slice(i, i + 2);
        const ch = token[i];
        if (Object.prototype.hasOwnProperty.call(LONG_VOWELS, pair)) {
          units.push({ text: pair, kind: "L", options: [[LONG_VOWELS[pair], 1.0]] });
          i += 2;
        } else if (Object.prototype.hasOwnProperty.call(DIGRAPHS, pair)) {
          units.push({ text: pair, kind: "C", options: DIGRAPHS[pair] });
          i += 2;
        } else if (SHORT_VOWELS.includes(ch)) {
          units.push({ text: ch, kind: "V", options: [] });
          i += 1;
        } else if (ch === "c") {
          const soft = token[i + 1] && C_SOFT_BEFORE.includes(token[i + 1]);
          units.push({ text: ch, kind: "C", options: soft ? C_SOFT : C_HARD });
          i += 1;
        } else if (Object.prototype.hasOwnProperty.call(CONSONANTS, ch)) {
          units.push({ text: ch, kind: "C", options: CONSONANTS[ch] });
          i += 1;
        } else if (Object.prototype.hasOwnProperty.call(DIGITS, ch)) {
          let options = DIGITS[ch];
          if (ch === "2" && units.length === 0) options = DIGIT_HAMZA_INITIAL;
          units.push({ text: ch, kind: "C", options });
          i += 1;
        } else {
          units.push({ text: ch, kind: "X", options: [[ch, 1.0]] });
          i += 1;
        }
      }
      return units;
    }

    function isVowelish(unit) {
      return unit.kind === "V" || unit.kind === "L";
    }

    function aIsLong(units, k) {
      if (k + 1 >= units.length) return true;
      const nxt = units[k + 1];
      if (isVowelish(nxt) || SEMIVOWELS.includes(nxt.text)) return true;
      if (k + 2 === units.length) return true;
      return isVowelish(units[k + 2]);
    }

    function vowelOptions(units, k) {
      const letter = units[k].text;
      const last = k === units.length - 1;
      if (k === 0) return VOWELS.initial[letter];
      if (k === 1 && units[0].text === "2") return VOWELS.after_hamza[letter];
      if (last) return VOWELS.final[letter];
      if (letter === "a") {
        const key = aIsLong(units, k) ? "mid_a_long" : "mid_a_short";
        return VOWELS[key].a;
      }
      return VOWELS.mid[letter];
    }

    function slots(token) {
      const units = segment(token);
      return units.map((unit, k) => (unit.kind === "V" ? vowelOptions(units, k) : unit.options));
    }

    function build(slotList, maxAlternatives) {
      const bestText = slotList.map((o) => o[0][0]).join("");
      let bestScore = 1;
      for (const options of slotList) bestScore *= options[0][1];
      const found = {};
      slotList.forEach((options, i) => {
        options.slice(1).forEach(([text, weight]) => {
          const variant =
            slotList.slice(0, i).map((o) => o[0][0]).join("") +
            text +
            slotList.slice(i + 1).map((o) => o[0][0]).join("");
          const score = (bestScore / options[0][1]) * weight;
          if (variant !== bestText && score > (found[variant] || 0)) found[variant] = score;
        });
      });
      const ranked = Object.entries(found)
        .sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1))
        .slice(0, maxAlternatives)
        .map(([t, s]) => ({ text: t, score: Math.round(s * 1000) / 1000 }));
      return {
        best: { text: bestText, score: Math.round(bestScore * 1000) / 1000 },
        alternatives: ranked,
      };
    }

    function convertToken(token, maxAlternatives) {
      if (/^\d+$/.test(token)) return null;
      const lowered = token.toLowerCase();
      const collapsedKey = lowered.replace(REPEAT, "$1");
      if (Object.prototype.hasOwnProperty.call(LEXICON, collapsedKey)) {
        return {
          source: token,
          best: { text: LEXICON[collapsedKey], score: 1.0 },
          alternatives: [],
        };
      }
      let normalized = collapseElongation(lowered);
      normalized = undouble(normalized);
      const { best, alternatives } = build(slots(normalized), maxAlternatives);
      return { source: token, best, alternatives };
    }

    function transliterate(text, maxAlternatives) {
      if (maxAlternatives === undefined) maxAlternatives = 3;
      const tokens = [];
      const out = text.replace(TOKEN, (m) => {
        const result = convertToken(m, maxAlternatives);
        if (!result) return m;
        tokens.push(result);
        return result.best.text;
      });
      return { text: out, tokens };
    }

    return { transliterate };
  }

  global.DarijaToolkit = { loadRules };
})(typeof window !== "undefined" ? window : globalThis);
