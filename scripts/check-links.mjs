import fs from "node:fs";
import path from "node:path";

const root = path.resolve("_site");
const failures = [];

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const full = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(full) : [full];
  });
}

function resolveTarget(source, reference) {
  const clean = reference.split(/[?#]/)[0];
  if (!clean || /^(?:https?:|mailto:|tel:|data:|javascript:|#)/i.test(reference)) return null;
  const target = clean.startsWith("/") ? path.join(root, clean) : path.resolve(path.dirname(source), clean);
  if (path.extname(target)) return target;
  return clean.endsWith("/") ? path.join(target, "index.html") : `${target}.html`;
}

const files = walk(root);
for (const file of files.filter((item) => item.endsWith(".html"))) {
  const html = fs.readFileSync(file, "utf8");
  const references = [...html.matchAll(/(?:href|src|srcset)="([^"]+)"/g)].flatMap((match) => match[1].split(",").map((part) => part.trim().split(/\s+/)[0]));
  for (const reference of references) {
    const target = resolveTarget(file, reference);
    if (target && !fs.existsSync(target)) failures.push(`${path.relative(root, file)} -> ${reference}`);
  }
}
for (const file of files.filter((item) => item.endsWith(".css"))) {
  const css = fs.readFileSync(file, "utf8");
  for (const match of css.matchAll(/url\((['"]?)([^)'"\s]+)\1\)/g)) {
    const target = resolveTarget(file, match[2]);
    if (target && !fs.existsSync(target)) failures.push(`${path.relative(root, file)} -> ${match[2]}`);
  }
}

if (failures.length) {
  console.error(`Broken internal references:\n${failures.map((item) => `- ${item}`).join("\n")}`);
  process.exit(1);
}
console.log(`Checked ${files.length} build files: no broken internal HTML or CSS references.`);
