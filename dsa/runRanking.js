import rankingsRegistry from "./rankings/rankingsRegistry.js";
import loadScreamQueens from "./utils/dataLoader.js";

// 1) Load data (array)
const data = loadScreamQueens();

// 2) Build index (Map: name -> profile)
const index = new Map(data.map(({ name, ...profile }) => [name, profile]));

// 3) Read CLI args: node dsa/runRanking.js filmCount [desc|asc] [limit]
const rankingKey = process.argv[2];
const order = process.argv[3] || "desc";
const limit = Number(process.argv[4] || 10);

if (!rankingKey) {
  console.error(
    "Usage: node dsa/runRanking.js <rankingKey> [desc|asc] [limit]"
  );
  console.error(
    "Available rankings:",
    Object.keys(rankingsRegistry).join(", ")
  );
  process.exit(1);
}

const rankFn = rankingsRegistry[rankingKey];

if (!rankFn) {
  console.error(`Unknown ranking: ${rankingKey}`);
  console.error(
    "Available rankings:",
    Object.keys(rankingsRegistry).join(", ")
  );
  process.exit(1);
}

const ranking = rankFn(index, order);

console.log(`🏆 Ranking: ${rankingKey} (order=${order}, limit=${limit})`);
console.log("--------------------------------------------------");

ranking.slice(0, limit).forEach((row, i) => {
  // row shape depends on ranking implementation
  const raw =
    row.films ??
    row.horror_count ??
    row.survived ??
    row.box_office ??
    row.career_span ??
    row.value ??
    null;

  let value = raw;

  if (Array.isArray(raw) && raw.length === 2) {
    const [start, end] = raw;
    value =
      start == null || end == null
        ? "N/A"
        : start === end
        ? String(start)
        : `${start}–${end}`;
  } else if (raw == null || raw === "") {
    value = "N/A";
  }

  console.log(`${i + 1}. ${row.name} | ${value}`);
});
