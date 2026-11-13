import fs from "node:fs";
import path from "node:path";

const root = path.resolve("src/content");

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function readCollection(name) {
  const directory = path.join(root, name);
  if (!fs.existsSync(directory)) return [];
  return fs.readdirSync(directory)
    .filter((file) => file.endsWith(".json"))
    .sort()
    .map((file) => ({ ...readJson(path.join(directory, file)), _filename: file }));
}

function bySortOrder(a, b) {
  return (a.sort_order ?? 0) - (b.sort_order ?? 0) || (a.title || a.name || "").localeCompare(b.title || b.name || "");
}

export default function () {
  const publications = readCollection("publications").sort((a, b) => (b.year ?? 0) - (a.year ?? 0) || (b.legacy_id ?? 0) - (a.legacy_id ?? 0));
  const researchAreas = readCollection("research-areas").sort(bySortOrder);
  const researchProjects = readCollection("research-projects").sort(bySortOrder);
  const grants = readCollection("grants").sort(bySortOrder);
  const team = readCollection("team").sort(bySortOrder);
  const news = readCollection("news").sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")) || (b.legacy_id ?? 0) - (a.legacy_id ?? 0));
  const activities = readCollection("activities").sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")) || (b.legacy_id ?? 0) - (a.legacy_id ?? 0));
  const pages = readCollection("pages");
  const site = readJson(path.join(root, "site.json"));

  const projectBySlug = Object.fromEntries(researchProjects.map((item) => [item.slug, item]));
  const areaBySlug = Object.fromEntries(researchAreas.map((item) => [item.slug, item]));
  const publicationBySlug = Object.fromEntries(publications.map((item) => [item.slug, item]));
  const activityBySlug = Object.fromEntries(activities.map((item) => [item.slug, item]));
  const pageBySlug = Object.fromEntries(pages.map((item) => [item.slug, item]));

  for (const project of researchProjects) {
    project.area = areaBySlug[project.research_area] || null;
    project.related_publications = (project.publications || []).map((slug) => publicationBySlug[slug]).filter(Boolean);
  }
  for (const grant of grants) grant.project = projectBySlug[grant.related_project] || null;
  for (const project of researchProjects) {
    project.related_grants = grants.filter((grant) => grant.published && grant.related_project === project.slug);
    project.related_members = team.filter((member) => member.published && (member.projects || []).includes(project.slug));
    project.related_activities = activities.filter((activity) => activity.published && activity.related_project === project.slug);
  }
  for (const member of team) member.related_projects = (member.projects || []).map((slug) => projectBySlug[slug]).filter(Boolean);
  for (const activity of activities) activity.project = projectBySlug[activity.related_project] || null;
  for (const article of news) {
    article.project = projectBySlug[article.related_project] || null;
    article.publication = publicationBySlug[article.related_publication] || null;
    article.activity = activityBySlug[article.related_activity] || null;
  }

  const activeGrants = grants.filter((grant) => grant.published && grant.project?.status === "active");
  const previousGrants = grants.filter((grant) => grant.published && !activeGrants.includes(grant));
  const publicationYears = [...new Set(publications.filter((item) => item.published).map((item) => item.year))].sort((a, b) => b - a);
  const publishedPublications = publications.filter((item) => item.published);
  const publishedResearchProjects = researchProjects.filter((item) => item.published);
  const publishedNews = news.filter((item) => item.published);

  return {
    site,
    pages,
    pageBySlug,
    publications,
    publishedPublications,
    publicationYears,
    researchAreas,
    researchProjects,
    publishedResearchProjects,
    grants,
    activeGrants,
    previousGrants,
    team,
    news,
    publishedNews,
    activities,
    projectBySlug,
    areaBySlug,
    publicationBySlug,
  };
}
