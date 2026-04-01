import filterByActiveInPeriod from "./filterActiveInPeriod.js";
import filterByBoxOffice from "./filterByBoxOffice.js";
import filterByFilmCount from "./filterByFilmCount.js";
import filterByCareerSpan from "./filterByCareerSpan.js";
import filterBySurvival from "./filterBySurvival.js";

const filtersRegistry = {
  activeInPeriod: filterByActiveInPeriod,
  boxOffice: filterByBoxOffice,
  filmCount: filterByFilmCount,
  careerSpan: filterByCareerSpan,
  survival: filterBySurvival,
};

export default filtersRegistry;
