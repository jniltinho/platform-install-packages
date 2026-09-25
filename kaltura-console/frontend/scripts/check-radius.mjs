import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
function check(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) check(p);
    else if (readFileSync(p, "utf8").includes("rounded-"))
      throw new Error(`Forbidden radius utility: ${p}`);
  }
}
check("src");
