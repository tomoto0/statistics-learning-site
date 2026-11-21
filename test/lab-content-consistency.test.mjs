import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const labSource = fs.readFileSync(path.join(root, "src/scripts/learning-lab.ts"), "utf8");

test("descriptive lab heading matches its fixed observations and added shock day", () => {
  const heading = labSource.match(/function drawDescriptive[\s\S]*?frame\(svg,"([^"]+)"/);
  const baseData = labSource.match(/function drawDescriptive[\s\S]*?const data=\[([^\]]+)\];\s*data\.push\(/);
  assert.ok(heading, "descriptive lab heading is present");
  assert.ok(baseData, "descriptive lab's fixed data and movable shock are present");

  const observations = baseData[1].split(",").filter((value) => value.trim().length > 0);
  assert.equal(observations.length, 21, "the fixed synthetic series has 21 daily changes");
  assert.equal(heading[1], "Twenty-one daily changes + one movable shock day");
  assert.equal(observations.length + 1, 22, "the movable shock makes 22 displayed observations");
});
