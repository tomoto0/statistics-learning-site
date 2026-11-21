import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));
const further = JSON.parse(fs.readFileSync(path.join(root, "src/data/lesson-further-deepenings.json"), "utf8"));

function normalized(text) {
  return text.normalize("NFKC").toLocaleLowerCase("en").replace(/[^a-z0-9]+/g, " ").trim().replace(/\s+/g, " ");
}

function fiveWordShingles(text) {
  const words = normalized(text).split(" ").filter(Boolean);
  const shingles = new Set();
  for (let i = 0; i + 5 <= words.length; i += 1) shingles.add(words.slice(i, i + 5).join(" "));
  return shingles;
}

function containmentSimilarity(left, right) {
  const a = fiveWordShingles(left);
  const b = fiveWordShingles(right);
  if (!a.size || !b.size) return 0;
  let shared = 0;
  for (const shingle of a) if (b.has(shingle)) shared += 1;
  return shared / Math.min(a.size, b.size);
}

test("the third teaching pass covers all 238 existing lessons with substantial lesson-specific additions", () => {
  assert.equal(modules.length, 42, "the module count must remain unchanged");
  assert.equal(modules.reduce((total, module) => total + module.lessons.length, 0), 238, "the lesson count must remain unchanged");
  assert.deepEqual(Object.keys(further).sort(), modules.map(({ id }) => id).sort(), "every existing module must have a deepening map");
  assert.equal(Object.values(further).reduce((total, lessons) => total + Object.keys(lessons).length, 0), 238);

  const allNew = [];
  const unique = new Set();
  for (const module of modules) {
    const lessonMap = further[module.id];
    assert.deepEqual(Object.keys(lessonMap).sort(), module.lessons.map(({ title }) => title).sort(), `${module.id}: lesson titles and ordering identities must match`);
    for (const lesson of module.lessons) {
      const paragraph = lessonMap[lesson.title];
      assert.equal(typeof paragraph, "string", `${module.id}/${lesson.title}: missing prose`);
      assert.ok(paragraph.length >= 600, `${module.id}/${lesson.title}: prose is too short to teach substantively`);
      const words = paragraph.trim().split(/\s+/).length;
      assert.ok(words >= 100 && words <= 135, `${module.id}/${lesson.title}: unexpected word count (${words})`);
      assert.equal(paragraph.includes("\n"), false, `${module.id}/${lesson.title}: expected one paragraph`);
      const key = normalized(paragraph);
      assert.ok(!unique.has(key), `${module.id}/${lesson.title}: duplicate third-pass paragraph`);
      unique.add(key);
      assert.equal(lesson.body.split(paragraph).length - 1, 1, `${module.id}/${lesson.title}: paragraph must appear exactly once in bundled content`);

      const priorBody = lesson.body.replace(`\n\n${paragraph}`, "");
      const priorParagraphs = priorBody.split(/\n\s*\n/).map((part) => part.trim()).filter(Boolean);
      for (const previous of priorParagraphs) {
        assert.notEqual(normalized(paragraph), normalized(previous), `${module.id}/${lesson.title}: third pass repeats existing text`);
        assert.ok(containmentSimilarity(paragraph, previous) < 0.48,
          `${module.id}/${lesson.title}: third pass is too close to an earlier paragraph (five-word-shingle containment)`);
      }
      allNew.push({ id: module.id, title: lesson.title, paragraph });
    }
  }
  assert.equal(unique.size, 238);

  for (let i = 0; i < allNew.length; i += 1) {
    for (let j = i + 1; j < allNew.length; j += 1) {
      assert.ok(containmentSimilarity(allNew[i].paragraph, allNew[j].paragraph) < 0.58,
        `${allNew[i].id}/${allNew[i].title} is too similar to ${allNew[j].id}/${allNew[j].title}`);
    }
  }
});

test("the production seed pipeline applies the third-pass source", () => {
  const packageJson = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
  assert.match(packageJson.scripts.seed, /apply-lesson-further-deepenings\.py/);
});
