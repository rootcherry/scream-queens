import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DB_PATH = path.resolve(__dirname, "../../data/db/horrorverse.sqlite3");

export const openDb = () => {
  return new Database(DB_PATH);
};
