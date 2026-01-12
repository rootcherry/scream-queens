import filterBySurvival from "../filters/filterBySurvival.js";

const rankBySurvival = (index) => {
  // const survivors = filterBySurvival(index);
  // const entries = [...survivors];

  // const projected = [...filterBySurvival(index)].map(([name, profile]) => ({
  return [...filterBySurvival(index)]
    .map(([name, profile]) => ({
      name,
      survived: profile.stats.survived_count,
    }))
    .sort((a, b) => b.survived - a.survived);

  // projected.sort((a, b) => b.survived - a.survived);
  // return projected;
};

export default rankBySurvival;
