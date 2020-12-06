import csv
import sys
import time

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to dictionary: name, birth, movies (set of movie_ids)
people = {}

# Maps movie_ids to dictionary: title, year, stars (set of person_ids)
movies = {}

def loadData(directory):
    """
    Load data from CSV files into memory.
    """
    begin = time.time() # start find time
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass
    end = time.time() # end find time
    print(f"\nTime: {end - begin}")


def main():
    # Load data from files into memory
    print("Loading data...")
    loadData("D:\\Documents\\p-projects\\ai\\degrees\\large")
    print("Data loaded.")

    source = personIdForName(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = personIdForName(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortestPath(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


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
        neighbors = nieghborsForPerson(node.state)
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
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def nieghborsForPerson(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
