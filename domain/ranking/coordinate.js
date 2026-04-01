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

  // no ranking provided: return filtered Map
  if (!ranking) {
    return currentIndex;
  }

  // apply ranking
  const rankingFn = rankingsRegistry[ranking.type];

  if (!rankingFn) {
    throw new Error(`Unknown ranking: ${ranking.type}`);
  }

  return rankingFn(currentIndex, ranking.order);
};

export default coordinate;
