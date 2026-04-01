const rankBySurvival = (index, order = "desc") => {
  return [...index]
    .map(([name, profile]) => ({
      name,
      survived: profile.stats.survived_count,
    }))
    .sort((a, b) =>
      order === "desc" ? b.survived - a.survived : a.survived - b.survived
    );
};

export default rankBySurvival;
