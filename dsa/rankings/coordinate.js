import filtersRegistry from "../filters/filtersRegistry.js";
import rankingsRegistry from "./rankingsRegistry.js";

const coordinate = (index, filters, ranking) => {
  // start with full index (Map)
  let currentIndex = index;

  // for each filter config:
  for (const filter of filters) {
    const { type, params } = filter;

    // apply corresponding filter to current index
    const filterFn = filtersRegistry[type];

    if (!filterFn) {
      throw new Error(`Unknown filter: ${type}`);
    }

    // update index after applying filter
    currentIndex = filterFn(currentIndex, params);
  }

  // apply ranking
  const rankingFn = rankingsRegistry[ranking.type];
  const result = rankingFn(currentIndex, ranking.order);

  // return ranked result
  return result;
};

export default coordinate;

const testIndex = new Map([
  [
    "Megumi Okina",
    {
      stats: {
        horror_count: 4,
        survived_count: 2,
        box_office_total: 12000000,
        career_span: 8,
      },
    },
  ],
]);

const filters = [
  { type: "filmCount", params: 3 },
  { type: "boxOffice", params: 100 },
  // !=== number ({ type: "filmCount", params: { min: 3 } })
];

const ranking = {
  type: "boxOffice",
  order: "desc",
};

console.log(coordinate(testIndex, filters, ranking));
