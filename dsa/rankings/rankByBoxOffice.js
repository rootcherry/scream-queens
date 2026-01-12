import filterByBoxOffice from "../filters/filterByBoxOffice.js";

const rankByBoxOffice = (index, minValue) => {
  return [...filterByBoxOffice(index, minValue)]
    .map(([name, profile]) => ({
      name,
      boxOffice: profile.stats.box_office_total,
    }))
    .sort((a, b) => b.boxOffice - a.boxOffice);
};

export default rankByBoxOffice;
