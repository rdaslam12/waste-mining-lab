import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const fixturePath = path.resolve("src/content/news/pages-cms-workflow-fixture.json");
const outputPath = path.resolve("_site/news/pages-cms-workflow-fixture/index.html");

function run(command, args) {
  const result = spawnSync(command, args, { cwd: process.cwd(), encoding: "utf8", stdio: "pipe" });
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed\n${result.stdout}\n${result.stderr}`);
}
function build() { run(process.execPath, ["scripts/clean-output.mjs"]); run("npm", ["run", "build"]); }
function write(payload) { fs.writeFileSync(fixturePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8"); }

const fixture = {
  slug: "pages-cms-workflow-fixture",
  title: "Pages CMS workflow fixture",
  seo_title: "",
  search_description: "Temporary automated content workflow fixture.",
  date: "2026-11-13",
  category: "announcement",
  excerpt: "Temporary automated content workflow fixture.",
  cover_image: "",
  cover_image_alt: "",
  body_html: "<p>This entry exists only during automated testing.</p>",
  featured: false,
  related_project: "",
  related_publication: "",
  related_activity: "",
  published: false
};

try {
  write(fixture);
  build();
  if (fs.existsSync(outputPath)) throw new Error("Draft fixture was exposed in the public build");
  fixture.published = true;
  write(fixture);
  build();
  if (!fs.existsSync(outputPath)) throw new Error("Published fixture did not generate a route");
  fixture.title = "Pages CMS workflow fixture updated";
  write(fixture);
  build();
  if (!fs.readFileSync(outputPath, "utf8").includes(fixture.title)) throw new Error("Edited fixture did not update its route");
  fs.unlinkSync(fixturePath);
  build();
  if (fs.existsSync(outputPath)) throw new Error("Deleted fixture route remained after a clean rebuild");
  console.log("Create, draft-hide, publish, edit, and delete fixture workflow passed.");
} finally {
  if (fs.existsSync(fixturePath)) fs.unlinkSync(fixturePath);
  build();
}
