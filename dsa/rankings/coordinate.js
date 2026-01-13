import filtersRegistry from "../filters/filtersRegistry.js";

const coordinate = (index, filters) => {
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
  // return ranked result
  return currentIndex;
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

const filters = [{ type: "filmCount", params: 3 }];

console.log(coordinate(testIndex, filters));
