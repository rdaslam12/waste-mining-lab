import fs from "node:fs";
import path from "node:path";

const output = path.resolve("_site");
if (fs.existsSync(output)) fs.rmSync(output, { recursive: true, force: true });
