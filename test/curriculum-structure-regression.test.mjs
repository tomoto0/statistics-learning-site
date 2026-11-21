import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));
const baseline = JSON.parse(fs.readFileSync(path.join(root, "test/curriculum-structure-baseline.json"), "utf8"));

function structureOf(module) {
  const quiz = module.quiz;
  return {
    id: module.id,
    slug: module.slug,
    title: module.title,
    lessons: module.lessons.map((lesson) => {
      const practice = lesson.practice;
      const quiz = lesson.quiz;
      return {
        title: lesson.title,
        practiceCount: practice ? 1 : 0,
        practiceQuestionCount: practice?.question ? 1 : 0,
        lessonQuizCount: quiz ? 1 : 0,
        lessonQuizOptionCount: quiz?.options?.length ?? 0,
      };
    }),
    moduleQuizCount: quiz ? 1 : 0,
    moduleQuizQuestionCount: quiz?.question ? 1 : 0,
    moduleQuizOptionCount: quiz?.options?.length ?? 0,
  };
}

test("lesson enrichment preserves the exact 42-module, 238-lesson structure and assessment counts", () => {
  const actual = {
    moduleCount: modules.length,
    lessonCount: modules.reduce((total, module) => total + module.lessons.length, 0),
    modules: modules.map(structureOf),
  };
  assert.equal(actual.moduleCount, 42, "module count must remain unchanged");
  assert.equal(actual.lessonCount, 238, "lesson count must remain unchanged");
  assert.deepEqual(actual, baseline,
    "module/lesson identities, titles, order, module quizzes, lesson quizzes, and practice exercises must match the before snapshot");
});
