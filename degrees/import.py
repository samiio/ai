"""
Import IMDb CSV data to SQLite database 
"""
import csv
import cs50

def main():
    # Create database by opening and closing an empty file first
    open(f"movies.db", "w").close()
    db = cs50.SQL("sqlite:///movies.db")

    # Create table called 'people'
    db.execute(
        "CREATE TABLE people (id INTEGER, name TEXT NOT NULL, birth NUMERIC, "
        "PRIMARY KEY(id))")

    # Create table called 'movies'
    db.execute(
        "CREATE TABLE movies (id INTEGER, title TEXT NOT NULL, year NUMERIC, "
        "PRIMARY KEY(id))")

    # Create table called 'stars'
    db.execute(
        "CREATE TABLE stars ("
        "movie_id INTEGER NOT NULL, "
        "person_id INTEGER NOT NULL, "
        "FOREIGN KEY(movie_id) REFERENCES movies(id), "
        "FOREIGN KEY(person_id) REFERENCES people(id))")

    importData("D:\\Documents\\p-projects\\ai\\degrees\\large", db)


def importData(directory, database):
    """
    Read CSV files into SQL database
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            database.execute(
                "INSERT INTO people (id, name, birth) VALUES(?, ?, ?)",
                row["id"], row["name"], row["birth"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            database.execute(
                "INSERT INTO movies (id, title, year) VALUES(?, ?, ?)",
                row["id"], row["title"], row["year"])

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                database.execute(
                    "INSERT INTO stars (movie_id, person_id) VALUES(?, ?)",
                    row["movie_id"], row["person_id"])
            except KeyError:
                pass


if __name__ == "__main__":
    main()