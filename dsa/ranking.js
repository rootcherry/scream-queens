import loadScreamQueens from "./utils/dataLoader.js";

const screamQueens = loadScreamQueens();

// Build ranking by number of horror films
const getFilmRanking = (data) => {
  return data
    .map(({ name, stats }) => ({
      name,
      films: stats.horror_count,
      survived: stats.survived_count,
    }))
    .sort((a, b) => b.films - a.films);
};

// Print top N actresses
function printFilmRanking(ranking, limit = 10) {
  console.log(`🎬 Top ${limit} Scream Queens by Number of Horror Films`);
  console.log("-----------------------------------------------");
  ranking.slice(0, limit).forEach((queen, index) => {
    console.log(
      `${index + 1}. ${queen.name} | Films: ${queen.films} | Survived: ${
        queen.survived
      }`
    );
  });
}

// Main flow
const filmRanking = getFilmRanking(screamQueens);
printFilmRanking(filmRanking);
