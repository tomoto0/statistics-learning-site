import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));
const descriptions = JSON.parse(fs.readFileSync(path.join(root, "src/data/module-descriptions.json"), "utf8"));

test("all catalogue modules have clear, expanded descriptions", () => {
  assert.equal(modules.length, 42);
  assert.deepEqual(new Set(modules.map((module) => module.id)), new Set(Object.keys(descriptions)));
  for (const module of modules) {
    assert.ok(module.excerpt.length >= 150, `${module.id}: description should explain more than a short tagline`);
    assert.equal(module.excerpt, descriptions[module.id], `${module.id}: generated catalogue copy should match its source`);
  }
});
