const filterByBoxOffice = (index, minValue) => {
  return new Map(
    [...index].filter(([_, profile]) => {
      const box_office = profile.stats.box_office_total;
      if (box_office == null) return false;

      return box_office >= minValue;
    })
  );
};
