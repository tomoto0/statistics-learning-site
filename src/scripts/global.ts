type CurriculumState = { completed: string[] };
const STORE_KEY = "statistics-finance-lab-progress-v1";

function readState(): CurriculumState {
  try {
    const value = JSON.parse(localStorage.getItem(STORE_KEY) || "{}");
    return { completed: Array.isArray(value.completed) ? value.completed : [] };
  } catch {
    return { completed: [] };
  }
}
function saveState(state: CurriculumState) {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(state)); } catch { /* Private browsing may block storage. */ }
}
function renderProgress() {
  const state = readState();
  document.querySelectorAll<HTMLElement>("[data-progress-card]").forEach((card) => {
    const done = state.completed.includes(card.dataset.progressCard || "");
    card.dataset.completed = done ? "true" : "false";
    const badge = card.querySelector<HTMLElement>("[data-progress-badge]");
    if (badge) badge.textContent = done ? "Completed" : card.dataset.defaultBadge || "Start here";
  });
  const total = Number(document.querySelector<HTMLElement>("[data-progress-total]")?.dataset.progressTotal || "12");
  const count = Math.min(state.completed.length, total);
  const number = document.querySelector<HTMLElement>("[data-progress-count]");
  if (number) number.textContent = `${count} of ${total} modules completed`;
  const ring = document.querySelector<HTMLElement>("[data-progress-ring]");
  if (ring) {
    const percent = total ? (count / total) * 100 : 0;
    ring.style.setProperty("--progress", `${percent}%`);
    const percentLabel = ring.querySelector<HTMLElement>("[data-progress-percent]");
    if (percentLabel) percentLabel.textContent = `${Math.round(percent)}%`;
  }
  const completeButton = document.querySelector<HTMLButtonElement>("[data-mark-complete]");
  if (completeButton) {
    const id = completeButton.dataset.markComplete || "";
    const done = state.completed.includes(id);
    completeButton.textContent = done ? "Completed ✓" : "Mark module complete";
    completeButton.setAttribute("aria-pressed", String(done));
  }
}
function setupCatalog() {
  const search = document.querySelector<HTMLInputElement>("[data-module-search]");
  const cards = Array.from(document.querySelectorAll<HTMLElement>("[data-module-card]"));
  const chips = Array.from(document.querySelectorAll<HTMLButtonElement>("[data-filter-category]"));
  const resultCount = document.querySelector<HTMLElement>("[data-result-count]");
  const noResults = document.querySelector<HTMLElement>("[data-no-results]");
  if (!cards.length) return;
  let active = "All modules";
  const apply = () => {
    const term = (search?.value || "").trim().toLowerCase();
    let count = 0;
    for (const card of cards) {
      const text = `${card.dataset.search || ""} ${card.dataset.category || ""}`.toLowerCase();
      const visible = (!term || text.includes(term)) && (active === "All modules" || card.dataset.category === active);
      card.hidden = !visible;
      if (visible) count++;
    }
    if (resultCount) resultCount.textContent = `${count} ${count === 1 ? "module" : "modules"}`;
    if (noResults) noResults.hidden = count !== 0;
  };
  search?.addEventListener("input", apply);
  chips.forEach((chip) => chip.addEventListener("click", () => {
    active = chip.dataset.filterCategory || "All modules";
    chips.forEach((item) => item.setAttribute("aria-pressed", String(item === chip)));
    apply();
  }));
  apply();
}
function setupStepNavigation() {
  const steps = Array.from(document.querySelectorAll<HTMLElement>("[data-lesson-step]"));
  const dots = Array.from(document.querySelectorAll<HTMLButtonElement>("[data-step-index]"));
  const progress = document.querySelector<HTMLElement>("[data-step-progress]");
  const currentLabel = document.querySelector<HTMLElement>("[data-current-step]");
  if (!steps.length) return;
  let active = 0;
  const show = (next: number) => {
    active = Math.max(0, Math.min(next, steps.length - 1));
    steps.forEach((step, index) => { step.hidden = index !== active; });
    dots.forEach((dot, index) => dot.setAttribute("aria-current", index === active ? "step" : "false"));
    if (progress) progress.style.width = `${((active + 1) / steps.length) * 100}%`;
    if (currentLabel) currentLabel.textContent = `Step ${active + 1} of ${steps.length}`;
    const prev = document.querySelector<HTMLButtonElement>("[data-step-nav='prev']");
    const nextButton = document.querySelector<HTMLButtonElement>("[data-step-nav='next']");
    if (prev) prev.disabled = active === 0;
    if (nextButton) nextButton.textContent = active === steps.length - 1 ? "Finish this lesson" : "Next lesson →";
  };
  dots.forEach((dot) => dot.addEventListener("click", () => show(Number(dot.dataset.stepIndex || 0))));
  document.querySelector("[data-step-nav='prev']")?.addEventListener("click", () => show(active - 1));
  document.querySelector("[data-step-nav='next']")?.addEventListener("click", () => show(active === steps.length - 1 ? active : active + 1));
  show(0);
}
function setupCompletion() {
  document.querySelector<HTMLButtonElement>("[data-mark-complete]")?.addEventListener("click", (event) => {
    const button = event.currentTarget as HTMLButtonElement;
    const id = button.dataset.markComplete || "";
    const state = readState();
    state.completed = state.completed.includes(id) ? state.completed.filter((item) => item !== id) : [...state.completed, id];
    saveState(state);
    renderProgress();
  });
}
function setupQuiz() {
  document.querySelectorAll<HTMLElement>("[data-quiz]").forEach((quiz) => {
    const feedback = quiz.querySelector<HTMLElement>("[data-quiz-feedback]");
    quiz.querySelectorAll<HTMLButtonElement>("[data-answer-index]").forEach((option) => option.addEventListener("click", () => {
      const correct = Number(option.dataset.answerIndex) === Number(quiz.dataset.correctIndex);
      quiz.querySelectorAll<HTMLButtonElement>("[data-answer-index]").forEach((button) => {
        button.dataset.state = Number(button.dataset.answerIndex) === Number(quiz.dataset.correctIndex) ? "correct" : "";
        button.disabled = true;
      });
      if (!correct) option.dataset.state = "wrong";
      if (feedback) feedback.textContent = correct ? `That's right. ${quiz.dataset.explanation || ""}` : `Not quite. ${quiz.dataset.explanation || "Try reviewing the lesson above."}`;
    }));
  });
}
function setupAskAI() {
  const form = document.querySelector<HTMLFormElement>("[data-ask-form]");
  const question = form?.querySelector<HTMLTextAreaElement>("textarea");
  const answer = document.querySelector<HTMLElement>("[data-ask-answer]");
  const submit = form?.querySelector<HTMLButtonElement>("button[type='submit']");
  if (!form || !question || !answer || !submit) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const value = question.value.trim();
    if (value.length < 5) { question.focus(); return; }
    const activeStep = document.querySelector<HTMLElement>("[data-lesson-step]:not([hidden])");
    const lessonTitle = activeStep?.querySelector("h2")?.textContent || "Module overview";
    const lessonText = Array.from(activeStep?.querySelectorAll("p") || []).map((node) => node.textContent).join(" ").slice(0, 2200);
    const graph = Array.from(document.querySelectorAll<HTMLElement>("[data-metric]"))
      .map((node) => `${node.dataset.metric}: ${node.dataset.value || node.textContent}`)
      .join("; ").slice(0, 400);
    submit.disabled = true;
    submit.textContent = "Thinking…";
    answer.dataset.visible = "true";
    answer.textContent = "Connecting your question to this lesson and its interactive example…";
    try {
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          moduleId: form.dataset.moduleId,
          question: value,
          lessonTitle,
          lessonText,
          graph
        })
      });
      const data = await response.json() as { answer?: string; error?: string };
      if (!response.ok) throw new Error(data.error || "The learning assistant is temporarily unavailable.");
      answer.textContent = data.answer || "No answer was returned. Please try again.";
    } catch (error) {
      answer.textContent = error instanceof Error ? error.message : "The learning assistant is temporarily unavailable. Please try again.";
    } finally {
      submit.disabled = false;
      submit.textContent = "Ask this question";
    }
  });
}
function setupEmailLinks() {
  document.querySelectorAll<HTMLAnchorElement>("[data-email-link]").forEach((link) => link.addEventListener("click", () => {
    const moduleTitle = link.dataset.moduleTitle || "this statistics lesson";
    const category = link.dataset.moduleCategory || "statistics";
    const concept = link.dataset.exampleConcept || "the current concept";
    const activeStep = document.querySelector<HTMLElement>("[data-lesson-step]:not([hidden])");
    const lessonTitle = activeStep?.dataset.stepTitle || activeStep?.querySelector("h2")?.textContent || "Module overview";
    const graph = Array.from(document.querySelectorAll<HTMLElement>("[data-metric], [data-results]"))
      .map((node) => node.textContent?.trim()).filter(Boolean).join("; ").slice(0, 600) || "No graph values are visible yet.";
    const pageUrl = `${window.location.origin}${window.location.pathname}`;
    const subject = encodeURIComponent(`Question about ${moduleTitle}`);
    const body = encodeURIComponent(`Hi learning agent,\n\nI'm studying "${moduleTitle}" (${category}). Could you explain how "${concept}" connects to the result shown?\n\nSelected lesson: ${lessonTitle}\nVisible graph text: ${graph}\nPage: ${pageUrl}\n\nMy question:\n\nThanks!`);
    link.href = `mailto:statistics_learning@bot.cue.im?subject=${subject}&body=${body}`;
  }));
}
function setupGlobal() {
  const year = document.querySelector<HTMLElement>("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
  setupCatalog();
  setupStepNavigation();
  setupCompletion();
  setupQuiz();
  setupAskAI();
  setupEmailLinks();
  renderProgress();
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setupGlobal, { once: true });
else setupGlobal();
