import loadScreamQueens from "./utils/dataLoader.js";

const actresses = loadScreamQueens();

const buildActressIndex = (actresses) => {
  const entries = actresses.map(({ name, ...profile }) => {
    return [name, { ...profile }];
  });

  return new Map(entries);
};

const printActressIndex = (index) => {
  for (const [name, profile] of index) {
    console.log(name, profile);
    console.log();
  }
};

const actressIndex = buildActressIndex(actresses);
printActressIndex(actressIndex);
