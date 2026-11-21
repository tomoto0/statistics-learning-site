import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const modules = JSON.parse(fs.readFileSync(path.join(root, "src/data/modules.json"), "utf8"));
const seed = {
  $schema: "https://emdashcms.com/seed.schema.json",
  version: "1",
  meta: {
    name: "Applied Statistics for Economics",
    description: "Step-by-step applied statistics, econometrics and causal inference for economics",
    author: "Applied Statistics for Economics"
  },
  settings: {
    title: "Applied Statistics for Economics",
    tagline: "Visual lessons in applied statistics and econometrics."
  },
  collections: [
    {
      slug: "modules",
      label: "Learning Modules",
      labelSingular: "Learning Module",
      urlPattern: "/modules/{slug}",
      supports: ["drafts", "revisions", "preview", "search", "seo"],
      fields: [
        { slug: "module_key", label: "Stable module key", type: "string", required: true },
        { slug: "title", label: "Title", type: "string", required: true, searchable: true },
        { slug: "category", label: "Category", type: "string", required: true, searchable: true },
        { slug: "level", label: "Level", type: "string" },
        { slug: "minutes", label: "Estimated minutes", type: "string" },
        { slug: "lab", label: "Interactive lab", type: "string" },
        { slug: "excerpt", label: "Short description", type: "text", searchable: true },
        { slug: "objectives", label: "Learning objectives (one per line)", type: "text" },
        { slug: "lessons", label: "Lessons (JSON array)", type: "text" },
        { slug: "case_study", label: "Economics example", type: "text" },
        { slug: "misconceptions", label: "Common misconceptions (one per line)", type: "text" },
        { slug: "quiz", label: "Knowledge check (JSON)", type: "text" },
        { slug: "sources", label: "Sources (JSON array)", type: "text" },
        { slug: "video", label: "Video asset path", type: "string" },
        { slug: "captions", label: "WebVTT caption track path", type: "string" },
        { slug: "visual", label: "Module illustration path", type: "string" },
        { slug: "diagram", label: "Teaching diagram path", type: "string" },
        { slug: "diagram_alt", label: "Teaching diagram alt text", type: "text" },
        { slug: "diagram_caption", label: "Teaching diagram caption", type: "text" }
      ]
    }
  ],
  menus: [
    {
      name: "primary",
      label: "Primary Navigation",
      items: [
        { type: "custom", label: "Learning path", url: "/#path" },
        { type: "custom", label: "All modules", url: "/#modules" },
        { type: "custom", label: "About", url: "/#about" }
      ]
    }
  ],
  content: {
    modules: modules.map((module) => ({
      id: `module-${module.id}`,
      slug: module.slug,
      status: "published",
      data: {
        module_key: module.id,
        title: module.title,
        category: module.category,
        level: module.level,
        minutes: String(module.minutes),
        lab: module.lab,
        excerpt: module.excerpt,
        objectives: module.objectives.join("\n"),
        lessons: JSON.stringify(module.lessons),
        case_study: module.caseStudy,
        misconceptions: module.misconceptions.join("\n"),
        quiz: JSON.stringify(module.quiz),
        sources: JSON.stringify(module.sources),
        video: module.video ?? "",
        captions: module.captions ?? "",
        visual: module.visual ?? "",
        diagram: module.diagram ?? "",
        diagram_alt: module.diagramAlt ?? "",
        diagram_caption: module.diagramCaption ?? ""
      }
    }))
  }
};
fs.writeFileSync(path.join(root, "seed/seed.json"), `${JSON.stringify(seed, null, 2)}\n`);
console.log(`Generated EmDash seed for ${modules.length} modules.`);
