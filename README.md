# Applied Statistics for Economics

Explore it here: https://statistical-finance-lab-preview.bidwise-uk.workers.dev/

![Homepage of the Applied Statistics for Economics learning site](docs/assets/homepage-screenshot.png)

An open, English-language learning site for applied statistics, econometrics, and causal inference across economics. The current curriculum has **42 learning modules and 238 guided lessons**, from foundational methods to intermediate applications in policy evaluation, labour, education, health, macroeconomics, and more. Finance is one application area, not the site's sole focus. Learners can read lessons without an account and use original interactive charts, exercises, quizzes, worked examples, and linked references.

This repository is private. The screenshot above is stored here for project documentation and should not be copied to public repositories or sites without explicit authorization.

## Live site and route model

The live learner site is served at the `workers.dev` URL above. Main routes are:

- `/` — learning path, search, filters, and module catalogue.
- `/modules/<slug>` — guided module, lessons, interactive lab, practice, quiz, and sources.
- `/posts` and related CMS routes — EmDash-managed editorial content, where configured.
- `/_emdash/admin` — EmDash administration. On the deployed site, the `/_emdash*` path is protected by the existing owner-only Cloudflare Access application as well as EmDash authentication.
- `/api/ask` — same-site, lesson-contextual Ask AI endpoint.
- `/images/<filename>` and `/videos/<filename>` — media served from the Cloudflare R2 binding.

Public learner pages are intentionally open without login. Keep that public learner experience separate from the protected `/_emdash*` administration paths. Do not broaden or remove the existing Access policy, expose CMS write APIs, or add administrator email addresses or credentials to this repository.

## Architecture and verified Cloudflare resources

The application is an Astro server-rendered site running on a Cloudflare Worker. EmDash supplies the CMS runtime and admin interface. D1 stores CMS and application data; R2 stores learning media; Workers AI powers Ask AI. The `@astrojs/cloudflare` adapter supplies deployment-time asset/image bindings in addition to the bindings declared in the source Wrangler configuration.

The following non-secret identifiers were verified for this project. They identify resources; they are **not** credentials:

| Resource | Binding / name | Verified identifier or purpose |
| --- | --- | --- |
| Cloudflare account | — | `22c45ad6ebfcc228c2793c92e8945c5d` |
| Worker | `statistical-finance-lab-preview` | Live learner site at `https://statistical-finance-lab-preview.bidwise-uk.workers.dev/` |
| D1 database | `DB` / `statistics-learning-preview` | `59b15c5d-3428-4512-a33c-83a3b109aeac` |
| R2 bucket | `MEDIA` / `statistical-finance-lab-media` | Learning images and videos |
| KV namespace | `SESSION` | `801f2b3f641448d2bfd0b2afc6634995` |
| Workers AI | `AI` | Cloudflare Workers AI binding; no third-party API key is used by the current tutor endpoint |
| Adapter-managed bindings | `ASSETS`, `IMAGES` | Added by the Astro/Cloudflare build/deployment integration; preserve them when reviewing generated deployment configuration |

`wrangler.jsonc` is the source of truth for the Worker name, account ID, compatibility date/flag, `workers.dev` settings, and the declared D1, R2, KV, AI, and hourly Cron configuration. The current source configuration keeps `workers_dev: true` and `preview_urls: false`. The project uses the standard Workers usage model; do not purchase a domain or change the account plan as part of routine maintenance.

### Cloudflare Worker behavior

`src/worker.ts` composes the EmDash Cloudflare handler with two site-specific services:

- The media handler reads safe `/images/` and `/videos/` object keys from R2, supports `GET`, `HEAD`, and byte ranges, and applies response headers.
- Ask AI validates same-site requests and bounds learner input lengths. It loads module context from D1 when available and falls back to the bundled curriculum. A D1-backed shared limit caps the endpoint at 40 answers per UTC day. The model is Cloudflare Workers AI `@cf/zai-org/glm-4.7-flash`; the endpoint does not use a paid fallback. If Workers AI or its free allocation is unavailable, the learning site remains usable and the endpoint returns an error rather than silently switching providers.

`migrations/0001_ai_usage.sql` defines the application usage table. Do not replace production D1 data with a local seed or a database export. `seed/seed.json` is the EmDash schema/initial content seed; it is not a backup of the live D1 database.

### EmDash CMS

This is an EmDash site integrated into a standard Astro application, using `emdash` and `@emdash-cms/cloudflare` (currently declared as `^1.3.0` in `package.json`). The CMS is not a separate hosted frontend:

- `astro.config.mjs` enables server rendering, the Cloudflare adapter, the EmDash D1 adapter on `DB`, and media storage on `MEDIA`.
- `src/live.config.ts` registers EmDash's live content collection.
- The admin UI is at `/_emdash/admin`: locally, `http://localhost:4321/_emdash/admin`; live, the same path on the site host behind Access.
- `seed/seed.json` is generated from the project's curriculum inputs and provides the schema and initial content model. EmDash schema/content is stored in D1; media objects are in R2.
- Public learning pages use CMS content first where available and retain bundled curriculum fallbacks so the learner-facing site can remain useful during CMS maintenance.

Read the included `.agents/skills/building-emdash-site/` guidance before changing EmDash schemas, queries, content rendering, or cache behavior. For plugin work, consult `.agents/skills/creating-plugins/`. The current project does not require an EmDash API token for normal local site development.

## Development

Use the package-manager version pinned in `package.json` (`pnpm@11.9.0`). With Node.js and Corepack available:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

The local site is served at `http://localhost:4321`; local EmDash administration is at `http://localhost:4321/_emdash/admin`. `pnpm dev` runs the curriculum seed/build scripts before starting Astro. The seed pipeline is designed to be idempotent, but review generated source-data changes before committing.

Useful checks:

```bash
pnpm typecheck
pnpm test
pnpm build
pnpm preview
```

`pnpm build` runs `pnpm seed` before building. `pnpm test` is an offline Node test suite and does not call the live AI endpoint. `pnpm preview` previews the local Astro build; it does not publish to Cloudflare. The `pnpm deploy` script **does** run `wrangler deploy` after seeding/building and can change the live Worker—do not use it as a local verification command.

## Curriculum and extension guidance

Keep the learning experience open without login. Maintain the site's applied-economics scope beyond finance, its foundational-to-intermediate progression, original explanations, and consistent diagram/card-art style. By default, expand or improve existing lessons rather than increasing the established count of 42 modules and 238 lessons; change that structure only when explicitly approved.

When revising curriculum content:

1. Preserve existing module IDs, slugs, ordering, and routes unless a migration plan requires otherwise.
2. Write original explanations and examples; label synthetic examples as synthetic and never present illustrations as measured results.
3. Cite a trustworthy source for methods and keep module-specific references attached to the relevant lessons.
4. Preserve clear assumptions, interpretation, limitations, and common pitfalls. Avoid copying textbook prose, questions, data, or figures.
5. Update or add focused tests for structural, content, math, and media changes; run the full checks above.

Key curriculum inputs include `src/data/module-descriptions.json`, `src/data/lesson-expansions.json`, `src/data/lesson-deepenings.json`, `src/data/lesson-further-deepenings.json`, `src/data/gap-filling-modules.json`, and the topic-specific files under `src/data/enriched/`. `src/data/modules.json` is the bundled curriculum used by the public site and tutor context. Curriculum scripts under `scripts/` apply authored changes idempotently; `scripts/generate-seed.mjs` generates `seed/seed.json`. Run `pnpm seed` to rebuild the content pipeline, then inspect all resulting diffs before committing.

For a new or substantially revised teaching diagram, keep the established visual language and register its asset and descriptive alt text through `scripts/generate-diagrams.py`. Module card illustrations are produced through `scripts/generate-card-illustrations.py` and should remain visually consistent as a set. Keep captions with their matching videos in `public/videos/` and preserve topic-to-video mappings. The `RESEARCH.md` file records research sources and copyright/attribution guardrails.

## Repository structure

```text
.
├── .agents/skills/             # EmDash development and CLI guidance
├── docs/assets/                # README screenshot (private-repository asset)
├── migrations/                 # App-owned D1 SQL migrations
├── public/
│   ├── diagrams/               # Original SVG teaching diagrams
│   ├── images/                 # Site art and consistent module-card illustrations
│   └── videos/                 # Topic clips and WebVTT captions
├── scripts/                    # Idempotent curriculum transforms, asset and seed generation
├── seed/seed.json              # Generated EmDash schema/initial content seed
├── src/
│   ├── data/                   # Bundled curriculum and authored supplements
│   ├── layouts/                # Shared Astro layouts
│   ├── pages/                  # Server-rendered learning, CMS, and taxonomy routes
│   ├── scripts/                # Browser-side labs and global interactions
│   ├── styles/                 # Site styling
│   ├── utils/                  # Tutor, curriculum merge, math, and site helpers
│   ├── live.config.ts          # EmDash live collection registration
│   └── worker.ts               # Worker entry, R2 media, Ask AI, response headers
├── test/                       # Offline curriculum, lab, runtime, and media tests
├── AGENTS.md                   # Repository-level development instructions
├── astro.config.mjs            # Astro, Cloudflare adapter, and EmDash configuration
├── package.json                # Dependencies and development/build scripts
├── pnpm-lock.yaml              # Reproducible dependency lockfile
├── RESEARCH.md                 # Sources and content/copyright notes
└── wrangler.jsonc              # Cloudflare Worker resource configuration
```

### Important files

| File | Role |
| --- | --- |
| `src/pages/index.astro` | Public learning path and searchable/filterable module catalogue |
| `src/pages/modules/[slug].astro` | Lesson, quiz, sources, teaching diagrams, and interactive lab rendering |
| `src/data/modules.json` | Bundled curriculum and tutor context fallback |
| `src/utils/merge-lesson-supplements.mjs` | Adds missing bundled lesson supplements without replacing CMS-edited content |
| `src/scripts/learning-lab.ts` | Core deterministic browser learning labs |
| `src/scripts/applied-econometrics-labs.ts` | Applied econometrics visualizations and interactive labs |
| `src/utils/tutor-answer.mjs` | Ask AI interpretation and answer-formatting rules |
| `test/` | Regression and content-consistency checks |
| `public/` | Site assets, originals, diagrams, videos, and captions |
| `wrangler.jsonc` | Cloudflare bindings and Worker settings; contains identifiers, not credentials |

## Environment, bindings, and secrets

The site currently defines **no application-specific API-key environment variable**. At runtime it uses platform bindings rather than a third-party credential:

| Runtime name | Type | Required use |
| --- | --- | --- |
| `DB` | Cloudflare D1 | EmDash content and shared Ask AI daily usage limit |
| `MEDIA` | Cloudflare R2 | Learning images and videos |
| `SESSION` | Cloudflare KV | EmDash/session support |
| `AI` | Cloudflare Workers AI | Contextual tutor endpoint |
| `ASSETS`, `IMAGES` | Astro/Cloudflare adapter-managed | Generated deployment asset and image services |

The EmDash CLI also supports an optional `EMDASH_TOKEN` for authenticated remote CLI operations. It is not required by the site runtime or ordinary local development. If remote CLI access is needed, provide it through an approved local secret store or CI secret and never commit it.

For any future Worker secret, set it with Wrangler's secret mechanism (which prompts for the value):

```bash
pnpm exec wrangler secret put SECRET_NAME --name statistical-finance-lab-preview
```

For Wrangler-based local Worker runs, keep local-only values in the supported `.dev.vars` file. `.dev.vars`, `.env*`, Wrangler state, and generated/local databases are ignored by Git. Put only non-secret configuration in `wrangler.jsonc` or Cloudflare's non-secret `vars`. Never put values in `README.md`, source code, seed JSON, issue text, shell command arguments, or commits. Do not copy secrets from Cloudflare's dashboard into repository documentation. Use least-privilege, project-scoped access and rotate a credential if it is ever accidentally committed.

The Cloudflare account ID and resource IDs in this README are operational identifiers, not authorization material. Keep the repository private and do not add passwords, API tokens, session cookies, Access service tokens, private keys, environment files, or a live database export.

## Safe publishing workflow

This repository handoff does not deploy the Worker or change Cloudflare, CMS, D1, R2, Access, or live-site state. Any future production publishing is a separate operational action and must be intentional.

Before a release:

1. Review the current live Worker deployment and bindings in Cloudflare; verify which version is serving 100% and retain a known-good rollback version.
2. Run `pnpm test`, `pnpm typecheck`, and `pnpm build`; inspect the source and generated diffs. Confirm no `.map` source maps, local data, secret files, or transfer bundles are in the upload.
3. For a versioned release, use Wrangler version upload with strict binding checks, `--keep-vars`, and `--no-upload-source-maps`. `--keep-vars` protects dashboard-managed variables from accidental overwrite; strict checks fail closed on binding differences.
4. Stage a candidate at 0% while the known-good version remains at 100%. Test the candidate with Cloudflare's documented version-override mechanism, including all public learner pages/assets and the admin path's Access redirect.
5. Promote only the validated candidate; keep the previous known-good version available for rollback. Verify live traffic percentages, bindings, public routes, and admin protection after promotion.
6. Do not run `wrangler triggers deploy` unless an intentional route/trigger change is in scope. Do not weaken Access policies to work around a deployment issue.

If a Wrangler upload reports a network error, first inspect Cloudflare's versions and deployments: an upload may have succeeded even when the CLI returned an error. Do not blindly repeat uploads or assume an uploaded version is active. `pnpm deploy` is a direct deployment shortcut, not the staged release workflow described above.

Useful official references: [Cloudflare Workers versions and deployments](https://developers.cloudflare.com/workers/versions-and-deployments/), [version overrides](https://developers.cloudflare.com/workers/versions-and-deployments/version-overrides/), [Cloudflare Access for Workers](https://developers.cloudflare.com/workers/configuration/cloudflare-access/), [EmDash documentation](https://docs.emdashcms.com/), and the project's source list in [`RESEARCH.md`](RESEARCH.md).

## Included and intentionally excluded

The repository includes the site's source, authored curriculum inputs, generated curriculum/EmDash seed snapshot, original public images/diagrams/videos/captions, tests, dependency lockfile, project instructions, and the requested screenshot. The Git ignore policy excludes dependency folders, build/cache outputs, local databases, Cloudflare transfer packages and compiled bundles, temporary lesson-deepening work logs, and database-export files. These are not needed to develop the site and could expose operational state or duplicate generated content.

The `pnpm deploy` command is preserved in `package.json` for authorized future releases, but no deployment was performed as part of this repository handoff.
