import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

const output = path.resolve("_site");
const read = (relative) => fs.readFileSync(path.join(output, relative), "utf8");

test("all required public routes are generated", () => {
  for (const route of ["index.html", "publications/index.html", "research/index.html", "grants/index.html", "team/index.html", "activity/index.html", "news/index.html", "waste-monitoring/index.html", "contact/index.html", "sitemap.xml", "robots.txt", "404.html"]) {
    assert.ok(fs.existsSync(path.join(output, route)), route);
  }
});

test("all migrated project and news detail routes are generated", () => {
  assert.equal(fs.readdirSync(path.join(output, "research"), { withFileTypes: true }).filter((entry) => entry.isDirectory()).length, 5);
  assert.equal(fs.readdirSync(path.join(output, "news"), { withFileTypes: true }).filter((entry) => entry.isDirectory()).length, 3);
});

test("all publications and BibTeX downloads are rendered", () => {
  const publications = read("publications/index.html");
  assert.equal((publications.match(/data-publication(?:\s|>)/g) || []).length, 9);
  assert.equal(fs.readdirSync(path.join(output, "downloads", "bibtex")).filter((name) => name.endsWith(".bib")).length, 9);
});

test("monitoring dashboard keeps the verified no-dataset state", () => {
  const page = read("waste-monitoring/index.html");
  assert.match(page, /Data source not connected/);
  assert.match(page, /No verified dataset is currently connected/);
});

test("public output excludes backend and sensitive runtime artifacts", () => {
  const names = [];
  const stack = [output];
  while (stack.length) {
    const directory = stack.pop();
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const full = path.join(directory, entry.name);
      if (entry.isDirectory()) stack.push(full); else names.push(path.relative(output, full));
    }
  }
  assert.equal(names.some((name) => /(?:db\.sqlite3|\.py$|\.env|manage\.py|requirements\.txt)/i.test(name)), false);
  const combinedHtml = names.filter((name) => name.endsWith(".html")).map(read).join("\n");
  assert.doesNotMatch(combinedHtml, /django_session|DJANGO_SECRET_KEY|wagtailcore_apitoken|password_hash/i);
});
