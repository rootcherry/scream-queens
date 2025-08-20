from config import WIKI_BASE_URL


def find_filmography_table(bs):
    # headers first (h2, h3) with "film" keyword
    headers = bs.find_all('h2', 'h3')
    for header in headers:
        if header.text and 'film' in header.text.lower():
            next_tag = header.find_next_sibling()
            while next_tag:
                if next_tag.name == 'table':
                    return next_tag
                next_tag = next_tag.find_next_sibling()

    # check all tables for columns year/title
    for table in bs.find_all('table'):
        headers = table.find_all('th')
        column_names = [h.get_text(strip=True).lower() for h in headers]
        if any('year' in c for c in column_names) and any('title' in c for c in column_names):
            return table

    return None


def extract_films_from_table(table):
    films = []
    # track of the last year
    current_year = None

    # loop each row in table
    for row in table.find_all('tr'):
        # th/tds
        year = row.find('th')
        columns = row.find_all('td')

        # update curr_year if there's a new <th>
        if year:
            current_year = year.text.strip()

        if not columns or len(columns) < 2 or not current_year:
            continue

        title_cell = columns[0]
        title = title_cell.text.strip()
        role = columns[1].text.strip()

        link = title_cell.find('a', href=True)
        url = None
        if link:
            url = WIKI_BASE_URL + link['href']

        films.append({
            'title': title,
            'year': current_year,
            'character': role,
            'url': url
        })

    return films
