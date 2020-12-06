"""
Using list instead of set
Removed node = child assigment in shortestPath()
"""
import sys
import time
import sqlite3

from util import Node, StackFrontier, QueueFrontier

# Connect to database
db = sqlite3.connect("movies.db")

# Map person id to set(movies)
people = {}

# Map movie id to set(stars)
movies = {}

def main():
    loadData()
    source = personIdForName(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = personIdForName(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    begin = time.time() # start find time
    path = shortestPath(source, target)

    if path is None:
        print("Not connected.")
    else:
        queryPeople = "SELECT name FROM people WHERE id = ?"
        queryMovies = "SELECT title FROM movies WHERE id = ?"
        degrees = len(path)
        print(f"\n{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = getNameFromId(queryPeople, path[i][1])
            person2 = getNameFromId(queryPeople, path[i + 1][1])
            movie = getNameFromId(queryMovies, path[i + 1][0])
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")
    end = time.time() # end find time
    print(f"\nTime: {end - begin}")


def loadData():
    begin = time.time() # start find time
    # Load people
    pids = getIds("SELECT id FROM people")
    for pid in pids:
        people[pid] = { "movies": set() }

    # Load movies
    mids = getIds("SELECT id FROM movies")
    for mid in mids:
        movies[mid] = { "stars": set() }

    # Load stars
    myStars = getStars()
    for star in myStars:
        # star[0] = movieId, star[1] = personId
        try:
            people[star[1]]["movies"].add(star[0])
            movies[star[0]]["stars"].add(star[1])
        except KeyError:
            pass
    end = time.time() # end find time
    print(f"\nTime: {end - begin}")


def getIds(query):
    """
    Return a list of every id in a table.
    """
    db.row_factory = lambda cursor, row: row[0]
    c = db.cursor()
    ids = c.execute(query).fetchall()
    c.close()
    return ids


def getStars():
    """
    Return set of (movie_id, person_id) pairs from stars table.
    """
    db.row_factory = None
    c = db.cursor()
    stars = c.execute("SELECT movie_id, person_id FROM stars").fetchall()
    c.close()
    return stars


def shortestPath(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs that 
    connect the source to the target.

    If no possible path, returns None.
    src: https://github.com/fernandezpablo85/cs50ai/blob/master/0_search/
    """
    def rPath(node: Node):
        if node.parent is None:
            return []
        return [(node.action, node.state)] + rPath(node.parent)

    def path(node: Node):
        return list(reversed(rPath(node)))

    # Keep track of explored nodes
    explored = set()

    # Initialise node and add it to frontier
    start = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(start)
    
    # Loop to perform breadth-first search
    while True:

        # If frontier is empty, there is no solution
        if frontier.empty():
            return None

        # Remove node from frontier, this node will be considered
        node = frontier.remove()
        explored.add(node.state)
        if node.state == target:
            return path(node)

        nodes = [
            Node(state=n[1], parent=node, action=n[0])
            for n in neighborsForPerson(node.state)
            if n[1] not in explored
        ]

        # Optimization: check for goal nodes before adding to frontier
        goalNodes = (node for node in nodes if node.state == target)
        anyGoal = next(goalNodes, False)
        if anyGoal:
            return path(anyGoal)

        [frontier.add(node) for node in nodes]


def personIdForName(name):
    """
    Returns the IMDB id for a person's name, resolving ambiguities.
    """
    c = db.cursor()
    births = c.execute(
        "SELECT id, name, birth FROM people WHERE name LIKE ?;", 
        (name.lower(),)).fetchall()
    c.close()
    
    # Map id to (name and birth)
    personDict = {}
    births = list(births)
    for person in births:
        personDict[person[0]] = person[1] + ", " + str(person[2])

    # Return output depending on dictionary length
    if len(personDict) == 0:
        return None
    elif len(personDict) > 1:
        print(f"Which '{name}'?")
        for pId, pName in personDict.items():
            print(f"ID: {pId}, Name: {pName}")
        try:
            personId = input("Intended Person ID: ")
            if personId in personDict.keys():
                return personId
        except ValueError:
            pass
        return None
    else:
        return list(personDict)[0]


def neighborsForPerson(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = []
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.append((movie_id, person_id))
    return neighbors


def getNameFromId(query, anId):
    """
    Return the name with id 'personId'.
    """
    db.row_factory = lambda cursor, row: row[0]
    c = db.cursor()
    name = c.execute(query, (anId,)).fetchall()
    c.close()
    return name[0]


if __name__ == "__main__":
    main()
