import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));
const expansions = JSON.parse(fs.readFileSync(path.join(root, "src/data/lesson-expansions.json"), "utf8"));
const byId = new Map(modules.map((module) => [module.id, module]));

test("every curriculum module has substantive, linked lesson expansions included exactly once", () => {
  assert.equal(modules.length, 42);
  assert.equal(modules.reduce((total, module) => total + module.lessons.length, 0), 238);
  assert.equal(Object.keys(expansions).length, modules.length);
  assert.equal(
    Object.values(expansions).reduce((total, lessons) => total + Object.keys(lessons).length, 0),
    238,
  );
  assert.deepEqual(Object.keys(expansions).sort(), [...byId.keys()].sort());

  for (const [moduleId, lessons] of Object.entries(expansions)) {
    const module = byId.get(moduleId);
    assert.ok(module, `missing module ${moduleId}`);
      assert.deepEqual(
        Object.keys(lessons).sort(),
        module.lessons.map(({ title }) => title).sort(),
        `${moduleId}: expected every existing lesson to be expanded`,
      );
      const sourceLabels = module.sources.map(({ label }) => label);

      for (const [title, paragraphs] of Object.entries(lessons)) {
      const matches = module.lessons.filter((lesson) => lesson.title === title);
      assert.equal(matches.length, 1, `${moduleId}: expected one lesson named ${title}`);
      assert.ok(Array.isArray(paragraphs) && paragraphs.length >= 1, `${moduleId}/${title}: expected substantive paragraphs`);
      for (const paragraph of paragraphs) {
        assert.ok(typeof paragraph === "string" && paragraph.length >= 200, `${moduleId}/${title}: expansion should add substantive explanation`);
        assert.equal(matches[0].body.split(paragraph).length - 1, 1, `${moduleId}/${title}: expansion must be present exactly once`);
      }
        assert.ok(
          paragraphs.some((paragraph) => /linked/i.test(paragraph) || sourceLabels.some((label) => paragraph.includes(label))),
          `${moduleId}/${title}: point learners to a relevant linked source or name a listed source`,
        );
    }
  }
});
