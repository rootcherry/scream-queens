import filterByCareerSpan from "../filters/filterByCareerSpan.js";

const rankByCarrerSpan = (index, minYears) => {
  return [...filterByCareerSpan(index, minYears)]
    .map(([name, profile]) => ({
      name,
      career_span: profile.status.career_span,
    }))
    .sort((a, b) => b.career_span - a.career_span);
};

export default rankByCarrerSpan;
