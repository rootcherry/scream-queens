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
