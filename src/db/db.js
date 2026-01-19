import Database from "better-sqlite3";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Caminho absoluto para o mesmo banco que você já usa
const DB_PATH = path.resolve(__dirname, "../../data/db/horrorverse.sqlite3");

export const openDb = () => {
  return new Database(DB_PATH, { readonly: true });
};
