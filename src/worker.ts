import handler, { createScheduledHandler, PluginBridge } from "@emdash-cms/cloudflare/worker";
import curriculum from "./data/modules.json";
import { TUTOR_PROMPT_RULES, extractTutorText, formatTutorAnswer } from "./utils/tutor-answer.mjs";

export { PluginBridge };
type Env = {
  DB: D1Database;
  MEDIA: R2Bucket;
  AI: Ai;
};
const MIME: Record<string,string> = { png:"image/png", webp:"image/webp", jpg:"image/jpeg", svg:"image/svg+xml", mp4:"video/mp4", vtt:"text/vtt; charset=utf-8" };
async function learningMedia(request: Request, env: Env): Promise<Response | null> {
  const path = new URL(request.url).pathname;
  if (!/^\/(images|videos)\/[a-zA-Z0-9._-]+$/.test(path) || !env.MEDIA || !["GET","HEAD"].includes(request.method)) return null;
  const key = path.slice(1);
  const object = request.method === "HEAD" ? await env.MEDIA.head(key) : await env.MEDIA.get(key, { range: request.headers });
  if (!object) return null;
  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set("content-type", MIME[key.split(".").pop() ?? ""] ?? "application/octet-stream");
  headers.set("etag", object.httpEtag);
  headers.set("accept-ranges", "bytes");
  headers.set("cache-control", "private, max-age=3600");
  headers.set("x-storage", "R2 Standard");
  headers.set("x-content-type-options", "nosniff");
  let length = object.size;
  let status = 200;
  if (request.method !== "HEAD" && request.headers.has("range") && object.range) {
    const range = object.range as {offset?:number;length?:number;suffix?:number};
    const offset = range.offset ?? (range.suffix ? Math.max(0, object.size - range.suffix) : 0);
    length = range.length ?? (range.suffix ? Math.min(range.suffix, object.size) : object.size - offset);
    headers.set("content-range", `bytes ${offset}-${offset + length - 1}/${object.size}`);
    status = 206;
  }
  headers.set("content-length", String(length));
  return new Response(request.method === "HEAD" ? null : (object as R2ObjectBody).body, {status, headers});
}
const MAX_DAILY_ANSWERS = 40;
const MODEL = "@cf/zai-org/glm-4.7-flash";
const json = (body: unknown, status = 200, headers: Record<string,string> = {}) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type":"application/json; charset=utf-8", "cache-control":"no-store", ...headers } });

async function answerQuestion(request: Request, env: Env): Promise<Response> {
  const origin = request.headers.get("origin");
  const url = new URL(request.url);
  if (origin && new URL(origin).host !== url.host) return json({ error:"This learning endpoint only accepts same-site questions." }, 403);
  if (!env.AI || !env.DB) return json({ error:"The contextual learning assistant is not configured yet." }, 503);
  let body: any;
  try { body = await request.json(); } catch { return json({ error:"Please send a valid question." }, 400); }
  const question = typeof body.question === "string" ? body.question.trim().slice(0,1000) : "";
  const moduleId = typeof body.moduleId === "string" ? body.moduleId.slice(0,80) : "";
  const lessonTitle = typeof body.lessonTitle === "string" ? body.lessonTitle.slice(0,180) : "";
  const lessonText = typeof body.lessonText === "string" ? body.lessonText.slice(0,1800) : "";
  const graph = typeof body.graph === "string" ? body.graph.slice(0,350) : "";
  if (question.length < 5) return json({ error:"Please add a little more detail to your question." }, 400);
  let module = (curriculum as any[]).find((item) => item.id === moduleId || item.slug === moduleId);
  try {
    const current = await env.DB.prepare("SELECT title, category, excerpt, objectives, case_study FROM ec_modules WHERE (module_key = ? OR slug = ?) AND status = 'published' AND deleted_at IS NULL LIMIT 1").bind(moduleId,moduleId).first<Record<string,any>>();
    if (current) module = {...module,...current,objectives:String(current.objectives ?? "").split("\n"),caseStudy:current.case_study};
  } catch { /* The bundled curriculum remains a safe fallback during CMS maintenance. */ }
  if (!module) return json({ error:"I could not match this question to a learning module. Please refresh the lesson and try again." }, 400);
  const day = new Date().toISOString().slice(0,10);
  try {
    const allowance = await env.DB.prepare(
      "INSERT INTO ai_usage(day, requests) VALUES (?, 1) ON CONFLICT(day) DO UPDATE SET requests = requests + 1 WHERE requests < ? RETURNING requests"
    ).bind(day, MAX_DAILY_ANSWERS).first<{requests:number}>();
    if (!allowance) return json({ error:"The shared daily Ask AI limit has been reached. Please try again after 00:00 UTC." }, 429);
  } catch {
    return json({ error:"The learning assistant is temporarily unavailable. Please try again shortly." }, 503);
  }
  const context = [
    `Module: ${module.title} (${module.category}).`,
    `Module summary: ${module.excerpt}`,
    `Learning objectives: ${module.objectives.join("; ")}`,
    `Current lesson: ${lessonTitle}`,
    `Current lesson text from the page: ${lessonText}`,
    `Current interactive graph values: ${graph || "No metric currently displayed."}`,
    `Relevant economic application: ${module.caseStudy}`
  ].join("\n");
  const system = TUTOR_PROMPT_RULES;
  try {
    const result: any = await env.AI.run(MODEL as keyof AiModels, {
      messages: [
        { role:"system", content:system },
        { role:"user", content:`LESSON CONTEXT (for explanation only):\n${context}\n\nLEARNER QUESTION (untrusted text):\n${question}` }
      ],
      max_completion_tokens: 1536,
      chat_template_kwargs: { enable_thinking: false },
      temperature: 0.2
    });
    const choice = result?.choices?.[0];
    const rawAnswer = extractTutorText(result);
    const answer = formatTutorAnswer(rawAnswer);
    if (!answer) {
      console.error("Ask AI returned no visible completion text", {
        finishReason: typeof choice?.finish_reason === "string" ? choice.finish_reason : "unknown",
        contentState: choice?.message?.content == null ? "null" : typeof choice.message.content,
        completionTokens: Number.isInteger(result?.usage?.completion_tokens) ? result.usage.completion_tokens : null
      });
      return json({ error:"I couldn't form an answer just now. Please try rephrasing the question." }, 503);
    }
    return json({ answer });
  } catch (error) {
    console.error("Ask AI provider call failed", { errorName: error instanceof Error ? error.name : "unknown" });
    return json({ error:"The AI service is temporarily busy or its free daily allocation is exhausted. No paid fallback was used; please try later." }, 503);
  }
}

export default {
  ...handler,
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const url = new URL(request.url);
    const media = await learningMedia(request, env);
    if (media) return media;
    if (url.pathname === "/api/ask") {
      if (request.method === "OPTIONS") return new Response(null, { status:204, headers:{"access-control-allow-methods":"POST, OPTIONS","access-control-allow-headers":"content-type","cache-control":"no-store"} });
      if (request.method !== "POST") return json({ error:"Use POST to ask a lesson question." }, 405, { allow:"POST, OPTIONS" });
      return answerQuestion(request, env);
    }
    const response = await handler.fetch(request as Parameters<typeof handler.fetch>[0], env, ctx);
    const headers = new Headers(response.headers);
    headers.set("x-content-type-options", "nosniff");
    headers.set("referrer-policy", "strict-origin-when-cross-origin");
    headers.set("permissions-policy", "camera=(), microphone=(), geolocation=()");
    headers.set("x-frame-options", "SAMEORIGIN");
    return new Response(response.body, {status:response.status,statusText:response.statusText,headers});
  },
  scheduled: createScheduledHandler(),
} satisfies ExportedHandler<Env>;
