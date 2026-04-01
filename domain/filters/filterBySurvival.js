const filterBySurvival = (index) => {
  return new Map(
    [...index].filter(
      ([_, profile]) =>
        profile.stats.survived_count !== null &&
        profile.stats.survived_count > 0
    )
  );
};

export default filterBySurvival;
