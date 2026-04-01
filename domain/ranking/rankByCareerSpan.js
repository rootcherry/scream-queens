const rankByCareerSpan = (index, order = "desc") => {
  return [...index]
    .map(([name, profile]) => ({
      name,
      career_span: profile.stats.career_span,
    }))
    .sort((a, b) =>
      order === "desc"
        ? b.career_span - a.career_span
        : a.career_span - b.career_span
    );
};

export default rankByCareerSpan;
