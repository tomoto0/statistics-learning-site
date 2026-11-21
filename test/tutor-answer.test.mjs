import test from "node:test";
import assert from "node:assert/strict";
import { formatTutorAnswer, TUTOR_PROMPT_RULES } from "../src/utils/tutor-answer.mjs";

test("tutor prompt separates significance, effect size, uncertainty, practical importance and causal identification", () => {
  assert.match(TUTOR_PROMPT_RULES, /p-value is a probability of data.*under the null hypothesis/s);
  assert.match(TUTOR_PROMPT_RULES, /Never infer practical or economic importance from statistical significance/);
  assert.match(TUTOR_PROMPT_RULES, /If an uncertainty interval spans a stated materiality threshold.*say practical importance is uncertain/s);
  assert.match(TUTOR_PROMPT_RULES, /Do not compare a standardized effect.*percentage point/);
  assert.match(TUTOR_PROMPT_RULES, /Never say that the data fit a specified model unless actual fit statistics or diagnostic evidence/);
  assert.match(TUTOR_PROMPT_RULES, /Statistical significance does not establish causality/);
});

test("mock response keeps a materiality-crossing interval uncertain and does not compare unlike units", () => {
  const mock = "The interval runs from -0.4 to 1.2 percentage points and crosses the stated 1 percentage-point threshold, so practical importance is uncertain. The 0.20 SD standardized effect is not directly comparable to that threshold without a valid conversion. Model fit was not evaluated. Under H_0 and the stated assumptions, the p-value describes how unusual the data would be.";
  const answer = formatTutorAnswer(mock);
  assert.match(answer, /practical importance is uncertain/);
  assert.match(answer, /not directly comparable/);
  assert.match(answer, /Model fit was not evaluated/);
  assert.match(answer, /Under H₀ and the stated assumptions/);
  assert.doesNotMatch(answer, /\$|\\(?:mathrm|text|mathit|operatorname)/);
});

test("math delimiters and raw emphasis are converted to readable plain text", () => {
  const answer = formatTutorAnswer("Under $H_0$, **the p-value** is conditional on the model. *Practical importance* depends on size and units; use \\(\\beta_1\\) only when defined.");
  assert.match(answer, /H₀/);
  assert.match(answer, /the p-value/);
  assert.match(answer, /Practical importance/);
  assert.match(answer, /β₁/);
  assert.doesNotMatch(answer, /\$|\*|\\\(/);
});

test("formatter does not turn arbitrary markup into executable HTML", () => {
  const answer = formatTutorAnswer("<script>alert(1)</script> **plain emphasis**");
  assert.match(answer, /<script>/);
  assert.match(answer, /plain emphasis/);
  assert.doesNotMatch(answer, /\*\*plain/);
});
