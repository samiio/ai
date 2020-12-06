import csv
import sys
import time

from cs50 import SQL
from util import Node, StackFrontier, QueueFrontier

# Delcare database
db = SQL("sqlite:///movies.db")

# TODO: Dictionary of mapping person_id-set(movies)
people = {}


def loadData():
    """
    Returns (movie_id, person_id) pairs for all actors.
    """
    # Load people
    peopleIds = db.execute("SELECT id FROM people;")
    peopleQuery = db.execute("SELECT * FROM stars;")
    # TODO: add dict key (id), search movie_id for id and add to set


def main():
    source = personIdForName(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = personIdForName(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortestPath(source, target)
    startPath = time.time() # start find time

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"\n{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = getPersonNameFromId([path[i][1]])
            person2 = getPersonNameFromId([path[i + 1][1]])
            movie = getMovieTitleFromId([path[i + 1][0]])
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")
    endPath = time.time() # end find time
    print(f"\nTime: {endPath - startPath}") 


def shortestPath(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs that 
    connect the source to the target.

    If no possible path, returns None.
    """
    # Keep track of explored nodes 
    num_explored = 0
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
        num_explored += 1
        explored.add(node.state)

        # Find neighbors (actors to which he can connect) of the actor
        neighbors = neighborsForPerson(node.state)
        for movie, actor in neighbors:
            if actor not in explored and not frontier.contains_state(actor):
                child = Node(state=actor, parent=node, action=movie)

                # If node contains goal state, return list of tuples
                if child.state == target:
                    path = []
                    node = child
                    while node.parent is not None:
                        path.append((node.action, node.state))
                        node = node.parent

                    path.reverse()
                    return path

                frontier.add(child)


def personIdForName(name):
    """
    Returns the IMDB id for a person's name, resolving ambiguities.
    
    NOTE: Do I have to change output to string?
    """
    births = db.execute(
        "SELECT id, name, birth FROM people WHERE name LIKE ?", 
        name.lower())
    
    # Map ids to (name + birth) as key-value pairs
    personDict = {}
    births = list(births)
    for entry in births:
        person = list(entry.values())
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
                return str(personId)
        except ValueError:
            pass
        return None
    else:
        return str(list(personDict)[0])


def neighborsForPerson(personId):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    rows = db.execute(
        "SELECT movie_id, person_id FROM stars WHERE stars.movie_id IN"
        "(SELECT stars.movie_id FROM stars WHERE stars.person_id = ?)"
        "AND stars.person_id != ?;", personId, personId)
    rows = list(rows)
    neighbors = set()
    for row in rows:
        neighbor = list(row.values())
        pair = (str(neighbor[0]), str(neighbor[1]))
        neighbors.add(pair)
    return neighbors


def getPersonNameFromId(personId):
    """
    Return an actors name with id 'personId'.
    """
    name = db.execute("SELECT name FROM people WHERE id = ?;", personId)
    name = list(name)[0]
    return name.get("name", 0)


def getMovieTitleFromId(movieId):
    """
    Return a movies title with id 'movieId'.
    """
    title = db.execute("SELECT title FROM movies WHERE id = ?;", movieId)
    title = list(title)[0]
    return title.get("title", 0)


if __name__ == "__main__":
    main()
