import filterByFilmCount from "../filters/filterByFilmCount.js";

const rankByFilmCount = (index, minFilms) => {
  return [...filterByFilmCount(index, minFilms)]
    .map(([name, profile]) => ({
      name,
      films: profile.stats.horror_count,
    }))
    .sort((a, b) => b.films - a.films);
};

export default rankByFilmCount;
