/**
 * Append curriculum supplements without replacing CMS-authored lesson text.
 *
 * @param {unknown} lessons
 * @param {Array<string | number | null | undefined>} moduleKeys
 * @param {Record<string, Record<string, string[]>>} paragraphSupplements
 * @param {Record<string, Record<string, string>>} lessonDeepenings
 * @param {Record<string, Record<string, string>>} furtherLessonDeepenings
 */
export function mergeLessonSupplements(lessons, moduleKeys, paragraphSupplements, lessonDeepenings, furtherLessonDeepenings = {}) {
  const keys = [...new Set(moduleKeys.filter((key) => key != null && String(key).trim()).map(String))];
  const lessonList = Array.isArray(lessons) ? lessons : [];

  return lessonList.map((lesson) => {
    const title = String(lesson?.title ?? "");
    const additions = [];
    for (const key of keys) {
      const existing = paragraphSupplements?.[key]?.[title];
      if (Array.isArray(existing)) additions.push(...existing);
      const deepening = lessonDeepenings?.[key]?.[title];
      if (typeof deepening === "string") additions.push(deepening);
      const furtherDeepening = furtherLessonDeepenings?.[key]?.[title];
      if (typeof furtherDeepening === "string") additions.push(furtherDeepening);
    }

    let body = String(lesson?.body ?? "");
    for (const paragraph of additions) {
      if (typeof paragraph !== "string" || !paragraph.trim() || body.includes(paragraph)) continue;
      body = body.trim() ? `${body.replace(/\s+$/, "")}\n\n${paragraph}` : paragraph;
    }
    return { ...lesson, body };
  });
}
