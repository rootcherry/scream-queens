import rankByBoxOffice from "./rankByBoxOffice.js";
import rankByCareerSpan from "./rankByCareerSpan.js";
import rankByFilmCount from "./rankByFilmCount.js";
import rankBySurvival from "./rankBySurvival.js";

const rankingsRegistry = {
  boxOffice: rankByBoxOffice,
  careerSpan: rankByCareerSpan,
  filmCount: rankByFilmCount,
  survival: rankBySurvival,
};

export default rankingsRegistry;
