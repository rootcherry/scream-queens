import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

// Resolve __dirname in ES module environment
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const filePath = path.join(
  __dirname,
  "../../data/processed/processed_scream_queens_clean.json"
);

const loadScreamQueensData = () => {
  try {
    const jsonString = fs.readFileSync(filePath, "utf8");
    return JSON.parse(jsonString);
  } catch (error) {
    console.error("Error reading or parsing Scream Queens data:", error);
  }
};

export default loadScreamQueensData;
