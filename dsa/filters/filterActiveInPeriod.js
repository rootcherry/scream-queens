const filterActiveInPeriod = (index, startYear, endYear) => {
  return new Map(
    [...index].filter(([_, profile]) => {
      const career_span = profile.stats.career_span;

      if (career_span == null) return false;

      const [firstYear, lastYear] = career_span;

      if (lastYear < startYear) return false;
      if (firstYear > endYear) return false;

      return true;
    })
  );
};
