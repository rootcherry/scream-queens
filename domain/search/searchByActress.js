import loadScreamQueens from "./utils/dataLoader.js";

const actresses = loadScreamQueens();

const buildActressIndex = (actresses) => {
  return new Map(actresses.map(({ name, ...profile }) => [name, profile]));
};

const actressIndex = buildActressIndex(actresses);

const actressName = process.argv[2]; // CLI input

if (!actressName) {
  console.log("Please provide an actress name.");
  process.exit(1);
}

const actress = actressIndex.get(actressName);

if (!actress) {
  console.log(`The actress "${actressName}" was not found.`);
} else {
  console.log(actressName, actress);
}
