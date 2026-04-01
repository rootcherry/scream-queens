const rankByBoxOffice = (index, order = "desc") => {
  return [...index]
    .map(([name, profile]) => ({
      name,
      boxOffice: profile.stats.box_office_total,
    }))
    .sort((a, b) =>
      order === "desc" ? b.boxOffice - a.boxOffice : a.boxOffice - b.boxOffice
    );
};

export default rankByBoxOffice;
