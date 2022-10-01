import csv
import sys
import queue

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
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


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print(f"Loading data from {directory}...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    print_new_step("Solution:")
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


################################
class Node:
    def __init__(self, person_id, movie_id, parent):
        self.person_id = person_id
        self.movie_id = movie_id
        self.parent = parent

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    print_new_step(f"Starting search for shortest path between source={source} and target={target}")

    return bfs(source, target, set())

def bfs(source, target, seen):
    print_new_step("Finding all valid paths using BFS.")

    valid_end_nodes = list()
    q = queue.Queue()
    q.put(Node(source, None, None))
    while not q.empty():
        cur = q.get()
        person_id = cur.person_id

        print_debug(f"Explored node with person_Id: {person_id}")
        print_debug(people[person_id])

        if person_id == target:
            print_debug("Found target")
            return backtrack(cur, source, target)

        seen.add(person_id)

        neighbors = neighbors_for_person(person_id)
        for neighbor in neighbors:
            movie_id = neighbor[0]
            neighbor_id = neighbor[1]
            if neighbor_id not in seen:
                print_debug(f"{person_id} and {neighbor_id} were in {movie_id} together")
                q.put(Node(neighbor_id, movie_id, cur))

    return None

def backtrack(cur, source, target):
    path = list()

    if cur.person_id != target:
        print_debug(f"Backtracing from non-target node = {cur.person_id}. Returning empty list")
        return list()

    while cur != None and cur.person_id != source:
        print_debug(f"Visiting node={cur.person_id} while backtracking")
        path.append([cur.movie_id, cur.person_id])
        cur = cur.parent

    if cur.person_id != source:
        print_debug("Backtrack doesn't connect to source. Returning empty list")
        return list()

    path.reverse()
    print_debug(f"Backtracking produced: {path}")
    return path

def min_path(valid_paths):
    print_new_step("Finding the minimum cost path out of all valid paths found.")
    if valid_paths == None:
        return None

    minimum_cost = len(valid_paths[0])
    minimum_cost_path = None
    for path in valid_paths:
        print_debug(f"Evaluating path with length={len(path)}\tpath={path}")
        if len(path) <= minimum_cost:
            print_debug("New min cost path found.")
            minimum_cost = len(path)
            minimum_cost_path = path

    print_debug(f"Min cost path={minimum_cost_path}")
    return minimum_cost_path

def expand_valid_end_nodes(valid_end_nodes, source, target):
    print_new_step("Expanding end nodes into full paths.")
    valid_paths = list()

    for end_node in valid_end_nodes:
        path = backtrack(end_node, source, target)
        if path != None:
            valid_paths.append(path)

    return valid_paths

def print_new_step(msg):
    print_debug("")
    print_debug("=======================")
    print_debug(msg)
    print_debug("=======================")
    print_debug("")

def print_debug(msg):
    print(msg)
    #pass

################################

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
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


def neighbors_for_person(person_id):
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
