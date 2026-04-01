const filterByCareerSpan = (index, minYears) => {
  return new Map(
    [...index].filter(([_, profile]) => {
      const span = profile.stats.career_span;
      if (!span || span.length !== 2) return false;

      const [startYear, endYear] = span;
      return endYear - startYear >= minYears;
    })
  );
};

export default filterByCareerSpan;
