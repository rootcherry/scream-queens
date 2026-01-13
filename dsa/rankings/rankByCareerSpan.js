import filterByCareerSpan from "../filters/filterByCareerSpan.js";

const rankByCareerSpan = (index, minYears) => {
  return [...filterByCareerSpan(index, minYears)]
    .map(([name, profile]) => ({
      name,
      career_span: profile.stats.career_span,
    }))
    .sort((a, b) => b.career_span - a.career_span);
};

export default rankByCareerSpan;
