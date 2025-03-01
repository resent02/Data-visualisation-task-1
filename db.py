import sqlite3


# Function to create the database and table
def create_table():
    conn = sqlite3.connect("films.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            release_year INTEGER,
            director TEXT,
            box_office REAL,
            country TEXT
        )
    """)

    conn.commit()
    conn.close()


# Function to add a film record to the table
def add_film(title, release_year, director, box_office, country):
    conn = sqlite3.connect("films.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO films (title, release_year, director, box_office, country)
        VALUES (?, ?, ?, ?, ?)
    """,
        (title, release_year, director, box_office, country),
    )

    conn.commit()
    conn.close()


# Function to get a film by ID
def get_film_by_id(film_id):
    conn = sqlite3.connect("films.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM films WHERE id = ?", (film_id,))
    film = cursor.fetchone()

    conn.close()
    return film


# Example usage
if __name__ == "__main__":
    create_table()  # Creates the table if it doesn't exist
