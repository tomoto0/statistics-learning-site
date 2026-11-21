import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));

test("the 14 existing topic videos and available WebVTT captions map to matching modules", () => {
  const withVideo = modules.filter((module) => module.video);
  assert.equal(withVideo.length, 14);
  assert.equal(withVideo.filter((module) => module.captions).length, 14);

  for (const module of withVideo) {
    const videoName = path.basename(module.video, ".mp4");
    const captionName = path.basename(module.captions, ".vtt");
    assert.equal(videoName, module.id, `${module.id} should use its topic-matched clip`);
    assert.equal(captionName, videoName, `${module.id} should use the matching caption track`);
    assert.ok(fs.existsSync(path.join(root, "public", module.video.slice(1))), `missing video: ${module.video}`);
    assert.ok(fs.existsSync(path.join(root, "public", module.captions.slice(1))), `missing captions: ${module.captions}`);
  }
});
