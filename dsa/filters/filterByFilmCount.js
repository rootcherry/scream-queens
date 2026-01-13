const filterByFilmCount = (index, minFilms) => {
  const entries = [...index];

  const filteredEntries = entries.filter(
    ([_, profile]) => profile.stats.horror_count >= minFilms
  );

  return new Map(filteredEntries);
};

export default filterByFilmCount;
