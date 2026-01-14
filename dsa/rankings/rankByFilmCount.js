const rankByFilmCount = (index, order = "desc") => {
  return [...index]
    .map(([name, profile]) => ({
      name,
      films: profile.stats.horror_count,
    }))
    .sort((a, b) => (order === "desc" ? b.films - a.films : a.films - b.films));
};

export default rankByFilmCount;
