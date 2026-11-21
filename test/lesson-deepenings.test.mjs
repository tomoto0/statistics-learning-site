import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { mergeLessonSupplements } from "../src/utils/merge-lesson-supplements.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));
const deepenings = JSON.parse(fs.readFileSync(path.join(root, "src/data/lesson-deepenings.json"), "utf8"));
const priorExpansions = JSON.parse(fs.readFileSync(path.join(root, "src/data/lesson-expansions.json"), "utf8"));

test("the second teaching pass covers exactly one distinct deepening for every existing lesson", () => {
  assert.equal(modules.length, 42);
  assert.equal(modules.reduce((total, module) => total + module.lessons.length, 0), 238);
  assert.deepEqual(Object.keys(deepenings).sort(), modules.map(({ id }) => id).sort());
  assert.equal(Object.values(deepenings).reduce((total, lessons) => total + Object.keys(lessons).length, 0), 238);

  const unique = new Set();
  for (const module of modules) {
    const lessonMap = deepenings[module.id];
    assert.deepEqual(Object.keys(lessonMap).sort(), module.lessons.map(({ title }) => title).sort(), `${module.id}: every original lesson must have exactly one deepening`);
    for (const lesson of module.lessons) {
      const paragraph = lessonMap[lesson.title];
      assert.equal(typeof paragraph, "string", `${module.id}/${lesson.title}: deepening must be text`);
      assert.ok(paragraph.length >= 850, `${module.id}/${lesson.title}: deepening must be substantive`);
      const words = paragraph.trim().split(/\s+/).length;
      assert.ok(words >= 140 && words <= 210, `${module.id}/${lesson.title}: unexpected length (${words} words)`);
      assert.equal(paragraph.includes("\n"), false, `${module.id}/${lesson.title}: expected one paragraph`);
      const normalized = paragraph.normalize("NFKC").toLocaleLowerCase("en").trim().replace(/\s+/g, " ");
      assert.equal(unique.has(normalized), false, `${module.id}/${lesson.title}: paragraph must be distinct`);
      unique.add(normalized);
      assert.equal(lesson.body.split(paragraph).length - 1, 1, `${module.id}/${lesson.title}: deepening must appear exactly once in bundled content`);
      const previous = priorExpansions[module.id]?.[lesson.title] ?? [];
      if (previous.length) {
        const lastPrevious = previous.at(-1);
        assert.ok(lesson.body.indexOf(paragraph) > lesson.body.indexOf(lastPrevious), `${module.id}/${lesson.title}: second pass must follow retained prior supplements`);
      }
    }
  }
  assert.equal(unique.size, 238);
});

test("CMS-first rendering appends all three supplement sources without replacing or duplicating authored text", () => {
  const page = fs.readFileSync(path.join(root, "src/pages/modules/[slug].astro"), "utf8");
  assert.match(page, /lessonDeepenings/);
  assert.match(page, /lessonFurtherDeepenings/);
  assert.match(page, /mergeLessonSupplements/);

  const cmsLessons = [
    { title: "Worked step", body: "Owner-edited explanation.\n\nPrior supplement." },
    { title: "New step", body: "A CMS-authored sentence." },
  ];
  const existing = {
    routeSlug: { "Worked step": ["Prior supplement.", "Slug-only source."] },
    moduleKey: { "Worked step": ["Module-key source."] },
  };
  const newContent = {
    moduleKey: { "Worked step": "New worked calculation.", "New step": "New-step calculation." },
  };
  const furtherContent = {
    moduleKey: { "Worked step": "Latest worked example.", "New step": "New-step interpretation." },
  };
  const merged = mergeLessonSupplements(cmsLessons, ["routeSlug", "moduleKey"], existing, newContent, furtherContent);

  assert.equal(merged[0].body, "Owner-edited explanation.\n\nPrior supplement.\n\nSlug-only source.\n\nModule-key source.\n\nNew worked calculation.\n\nLatest worked example.");
  assert.equal(merged[1].body, "A CMS-authored sentence.\n\nNew-step calculation.\n\nNew-step interpretation.");
  assert.equal(cmsLessons[0].body, "Owner-edited explanation.\n\nPrior supplement.", "the CMS source object must not be mutated");
  const rerun = mergeLessonSupplements(merged, ["routeSlug", "moduleKey"], existing, newContent, furtherContent);
  assert.deepEqual(rerun, merged, "repeated rendering must not duplicate content");
});
