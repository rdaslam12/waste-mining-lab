import fs from "node:fs";
import path from "node:path";

const TYPE_LABELS = {
  journal: "Journal Article",
  conference: "Conference Paper",
  book_chapter: "Book Chapter",
  preprint: "Preprint / Working Paper",
  report: "Technical Report",
};

const NEWS_LABELS = {
  announcement: "Announcements",
  research: "Research updates",
  lab: "Lab news",
};

const PROJECT_STATUS_LABELS = {
  active: "Active research",
  completed: "Completed",
  planned: "Planned inquiry",
};

const ACTIVITY_LABELS = {
  field: "Field visits",
  laboratory: "Laboratory activities",
  workshop: "Workshops",
  seminar: "Seminars",
  presentation: "Research presentations",
  outreach: "Outreach & collaborations",
};

function parseDate(value) {
  if (!value) return null;
  const date = new Date(`${value}T00:00:00Z`);
  return Number.isNaN(date.valueOf()) ? null : date;
}

function bibtex(publication) {
  const cleanedAuthors = (publication.authors || "").replace(/et al\.?/gi, "").trim();
  const firstPerson = cleanedAuthors.split(",")[0].trim();
  const firstAuthor = (firstPerson.split(/\s+/).filter(Boolean).at(-1) || "author")
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "") || "author";
  const firstWord = (publication.title || "work")
    .split(/\s+/)
    .find((word) => /^[a-z0-9]+$/i.test(word))?.toLowerCase() || "work";
  const entryType = {
    journal: "article",
    conference: "inproceedings",
    book_chapter: "incollection",
    preprint: "misc",
    report: "techreport",
  }[publication.publication_type] || "article";
  const lines = [
    `@${entryType}{${firstAuthor}${publication.year}${firstWord},`,
    `  title = {${publication.title}},`,
    `  author = {${publication.authors}},`,
    `  year = {${publication.year}},`,
  ];
  if (publication.venue) lines.push(`  ${entryType === "article" ? "journal" : "booktitle"} = {${publication.venue}},`);
  if (publication.doi) lines.push(`  doi = {${publication.doi}},`);
  if (publication.publication_url) lines.push(`  url = {${publication.publication_url}},`);
  lines.push("}");
  return lines.join("\n");
}

export default function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  eleventyConfig.addPassthroughCopy({ "src/media": "media" });
  eleventyConfig.addPassthroughCopy("src/_redirects");
  eleventyConfig.addPassthroughCopy("src/_headers");

  eleventyConfig.addWatchTarget("src/assets");
  eleventyConfig.addWatchTarget("src/content");

  eleventyConfig.addFilter("dateLong", (value) => {
    const date = parseDate(value);
    return date ? new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "long", year: "numeric", timeZone: "UTC" }).format(date) : "";
  });
  eleventyConfig.addFilter("dateShort", (value) => {
    const date = parseDate(value);
    return date ? new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" }).format(date) : "";
  });
  eleventyConfig.addFilter("monthYear", (value) => {
    const date = parseDate(value);
    return date ? new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric", timeZone: "UTC" }).format(date) : "";
  });
  eleventyConfig.addFilter("day", (value) => {
    const date = parseDate(value);
    return date ? new Intl.DateTimeFormat("en-GB", { day: "2-digit", timeZone: "UTC" }).format(date) : "";
  });
  eleventyConfig.addFilter("monthYearShort", (value) => {
    const date = parseDate(value);
    return date ? new Intl.DateTimeFormat("en-GB", { month: "short", year: "numeric", timeZone: "UTC" }).format(date) : "";
  });
  eleventyConfig.addFilter("truncateWords", (value = "", count = 22) => {
    const words = String(value).trim().split(/\s+/).filter(Boolean);
    return words.length > count ? `${words.slice(0, count).join(" ")}…` : words.join(" ");
  });
  eleventyConfig.addFilter("publicationType", (value) => TYPE_LABELS[value] || value || "");
  eleventyConfig.addFilter("newsCategory", (value) => NEWS_LABELS[value] || value || "");
  eleventyConfig.addFilter("projectStatus", (value) => PROJECT_STATUS_LABELS[value] || value || "");
  eleventyConfig.addFilter("activityCategory", (value) => ACTIVITY_LABELS[value] || value || "");
  eleventyConfig.addFilter("periodDisplay", (grant) => {
    if (grant?.start_date && grant?.end_date) return `${new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric", timeZone: "UTC" }).format(parseDate(grant.start_date))} – ${new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric", timeZone: "UTC" }).format(parseDate(grant.end_date))}`;
    if (grant?.start_date) return `From ${new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric", timeZone: "UTC" }).format(parseDate(grant.start_date))}`;
    if (grant?.end_date) return `Until ${new Intl.DateTimeFormat("en-US", { month: "long", year: "numeric", timeZone: "UTC" }).format(parseDate(grant.end_date))}`;
    return "";
  });
  eleventyConfig.addFilter("initials", (value = "") => {
    const parts = String(value).replace(/\b(Dr|Prof)\./g, "").trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return "WML";
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return `${parts[0][0]}${parts.at(-1)[0]}`.toUpperCase();
  });
  eleventyConfig.addFilter("bibtex", bibtex);
  eleventyConfig.addFilter("json", (value) => JSON.stringify(value));
  eleventyConfig.addFilter("findBySlug", (items = [], slug = "") => items.find((item) => item.slug === slug));
  eleventyConfig.addFilter("filterPublished", (items = []) => items.filter((item) => item.published));
  eleventyConfig.addFilter("filterCategory", (items = [], category = "") => items.filter((item) => item.category === category));

  eleventyConfig.addShortcode("asset", (assetPath) => `/assets/${String(assetPath).replace(/^\//, "")}`);

  eleventyConfig.on("eleventy.after", ({ dir }) => {
    const output = path.resolve(dir.output);
    if (!fs.existsSync(path.join(output, "index.html"))) {
      throw new Error(`Expected build output was not generated at ${output}`);
    }
  });

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "_site",
    },
    templateFormats: ["njk", "html", "11ty.js"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
}
