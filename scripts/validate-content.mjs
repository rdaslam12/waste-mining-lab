import fs from "node:fs";
import path from "node:path";
import yaml from "js-yaml";

const root = process.cwd();
const config = yaml.load(fs.readFileSync(path.join(root, ".pages.yml"), "utf8"));
const failures = [];

function fail(message) { failures.push(message); }
function readCollection(name) {
  const dir = path.join(root, "src", "content", name);
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir).filter((file) => file.endsWith(".json")).map((file) => {
    try { return { file, value: JSON.parse(fs.readFileSync(path.join(dir, file), "utf8")) }; }
    catch (error) { fail(`${name}/${file}: invalid JSON (${error.message})`); return null; }
  }).filter(Boolean);
}

if (!Array.isArray(config.media) || config.media.length < 1) fail(".pages.yml must define at least one media source");
if (!Array.isArray(config.content) || config.content.length < 1) fail(".pages.yml must define content entries");
if (config.settings?.content?.merge !== true) fail("Pages CMS structured-content merge must remain enabled");

const publications = readCollection("publications");
const areas = readCollection("research-areas");
const projects = readCollection("research-projects");
const grants = readCollection("grants");
const team = readCollection("team");
const news = readCollection("news");
const activities = readCollection("activities");
const collections = { publications, areas, projects, grants, team, news, activities };
const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

for (const [name, entries] of Object.entries(collections)) {
  const slugs = new Set();
  for (const { file, value } of entries) {
    if (!value.slug || !slugPattern.test(value.slug)) fail(`${name}/${file}: invalid or missing slug`);
    if (slugs.has(value.slug)) fail(`${name}: duplicate slug ${value.slug}`);
    slugs.add(value.slug);
    if (typeof value.published !== "boolean") fail(`${name}/${file}: published must be boolean`);
  }
}

const publicationSlugs = new Set(publications.map(({ value }) => value.slug));
const areaSlugs = new Set(areas.map(({ value }) => value.slug));
const projectSlugs = new Set(projects.map(({ value }) => value.slug));
const activitySlugs = new Set(activities.map(({ value }) => value.slug));

for (const { file, value } of publications) {
  for (const required of ["title", "authors", "year", "publication_type"]) if (!value[required]) fail(`publications/${file}: missing ${required}`);
}
for (const { file, value } of projects) {
  for (const required of ["title", "summary", "status"]) if (!value[required]) fail(`research-projects/${file}: missing ${required}`);
  if (value.research_area && !areaSlugs.has(value.research_area)) fail(`research-projects/${file}: unknown research area ${value.research_area}`);
  for (const slug of value.publications || []) if (!publicationSlugs.has(slug)) fail(`research-projects/${file}: unknown publication ${slug}`);
}
for (const { file, value } of grants) if (value.related_project && !projectSlugs.has(value.related_project)) fail(`grants/${file}: unknown project ${value.related_project}`);
for (const { file, value } of team) for (const slug of value.projects || []) if (!projectSlugs.has(slug)) fail(`team/${file}: unknown project ${slug}`);
for (const { file, value } of news) {
  if (!value.title || !value.date || !value.excerpt || !value.body_html) fail(`news/${file}: missing required article content`);
  if (value.related_project && !projectSlugs.has(value.related_project)) fail(`news/${file}: unknown project ${value.related_project}`);
  if (value.related_publication && !publicationSlugs.has(value.related_publication)) fail(`news/${file}: unknown publication ${value.related_publication}`);
  if (value.related_activity && !activitySlugs.has(value.related_activity)) fail(`news/${file}: unknown activity ${value.related_activity}`);
}

const publicSource = [path.join(root, "src", "content"), path.join(root, "src", "_data")];
const forbidden = /django_session|password_hash|DJANGO_SECRET_KEY|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY|api[_-]?token/i;
for (const source of publicSource) {
  const stack = [source];
  while (stack.length) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const full = path.join(current, entry.name);
      if (entry.isDirectory()) stack.push(full);
      else if (forbidden.test(fs.readFileSync(full, "utf8"))) fail(`${path.relative(root, full)} contains a forbidden secret/private-data marker`);
    }
  }
}

if (failures.length) {
  console.error(failures.map((message) => `- ${message}`).join("\n"));
  process.exit(1);
}
console.log(`Pages CMS YAML parsed; validated ${Object.values(collections).reduce((sum, items) => sum + items.length, 0)} structured records and all content relationships.`);
