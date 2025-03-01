import json
import sqlite3

conn = sqlite3.connect("films.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT title, release_year, directors, box_office, countries 
    FROM films
""")

films = []
for row in cursor.fetchall():
    films.append(
        {
            "Film Title": row[0],
            "Release Year": row[1],
            "Director(s)": json.loads(row[2]) if row[2] else [],
            "Box Office Revenue": row[3],
            "Country of Origin": json.loads(row[4]) if row[4] else [],
        }
    )

with open("films.json", "w") as f:
    json.dump(films, f, indent=2)

conn.close()
