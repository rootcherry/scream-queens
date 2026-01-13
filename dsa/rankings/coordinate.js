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

const coordinate = (index, filters, ranking) => {
  // start with full index (Map)
  // for each filter config:
  //   apply corresponding filter to current index
  // select ranking function based on ranking config
  // return ranked result
};
