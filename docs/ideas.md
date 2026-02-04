# Scream Queens Project - Notes

## Actresses
- Jamie Lee Curtis
- Neve Campbell
- Florence Pugh
- Vera Farmiga
- Megumi Okina
- Anya Taylor-Joy

## JSON Structure
scream_queen_films = {
    "Jamie Lee Curtis": [
        {"title": "Halloween", "year": 1978, "character": "Laurie", "url": "..."}
    ]
}

screamQueens = {
    "Jamie Lee Curtis": {
        "movies": ["Halloween (1978)"],
        "survivals": 2,
        "totalBoxOffice": 450000000,
        "subgenres": ["Slasher"]
    }
}

## Keywords
keywords = ['horror', 'terror', 'slasher', 'thriller', 'supernatural', 'suspense']

## Fields
- Essentials: name, films (year, title, character), stats (horror_count, survived_count, career_span)
- Useful: films (subgenre, survived)
- Optional: box_office, stats (box_office_total)
