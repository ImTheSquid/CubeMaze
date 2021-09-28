import pyglet
from enum import Enum

"""
Cube Edge Layout:
            1
         24     2
            23
   19       22       3      4
18    20|21    11|10    8|7    5
   17       12       9      6
            13
         16    14
            15
"""

side_length = 8

# Sanity check
if side_length == 0:
    exit(1)

# Allows for creation of the cube maze by excluding parts that are irrelevant (x, y)
maze_exclusion_ranges = [
    (range(0, side_length), range(0, side_length)), 
    (range(side_length * 2, side_length * 4), range(0, side_length)),
    (range(0, side_length), range(side_length * 2, side_length * 3)), 
    (range(side_length * 2, side_length * 4), range(side_length * 2, side_length * 3))
]

# Determines the x/y values that determine edges and their pairs
# If a edge set has more than one item, the other axis / side length should be used to determine the correct index
x_leading_edge = [
    [18], [24, 21, 16], [10], [7]
]
x_trailing_edge = [
    [20], [2, 11, 14], [8], [5]
]
y_leading_edge = [
    [1], [19, 22, 3, 4], [13]
]
y_trailing_edge = [
    [23], [17, 12, 9, 6], [15]
]

# Determines which edges connect to eachother along with orientation information (axis and direction to next plane as well as 's' to determine whether axes switch and 'i' to determine if an inversion is needed)
maze_edge_maps = [
    (1, 4, "y+i"), 
    (2, 3, "x+si"), 
    (5, 18, "x+"), 
    (6, 15, "y-i"), 
    (7, 8, "x-"), 
    (9, 14, "y-s"), 
    (16, 17, "x-si"), 
    (12, 13, "y-"), 
    (19, 24, "x+s"), 
    (20, 21, "x+"), 
    (22, 23, "y+"), 
    (11, 10, "x+")
]

maze = [[]]

# Finds an edge's partner if it exists, returns None otherwise
def find_next_edge(edge):
    for map in maze_edge_maps:
        if map[0] == edge:
            return map[1]
        elif map[1] == edge:
            return map[0]
    return None


# Determines the edge to use from a specific set by using the value of the other axis
def edge_from_edge_set(set, other_val):
    if len(set) == 1:
        return set[0]
    else:
        return set[other_val // side_length]


# Gets a point's edge(s) if they exist, returns None otherwise
def edges_from_point(x, y):
    edges = []
    selected_set = None
    if x % side_length == 0: # Leading edge
        selected_set = x_leading_edge[x // side_length]
    elif (x + 1) % side_length == 0: # Trailing edge
        selected_set = x_trailing_edge[x // side_length]

    if selection := selected_set:
        edges.append(edge_from_edge_set(selection, y))

    selected_set = None
    if y % side_length == 0:
        selected_set = y_leading_edge[y // side_length]
    elif (y + 1) % side_length == 0:
        selected_set = y_trailing_edge[y // side_length]

    if selection := selected_set:
        edges.append(edge_from_edge_set(selection, x))

    return edges


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


# Determines what happens when an edge crossing occurs, returns the effected direction and whether an axis flip is needed
def parse_edge_effect(edge):
    res = [0, False, False, edge]
    for map in maze_edge_maps:
        if edge == map[0]:
            res[1] = "s" in map[2]
            res[2] = "i" in map[2]
            if "x" in map[2]:
                res[0] = Direction.RIGHT if "+" in map[2] else Direction.LEFT
            elif "y" in map[2]:
                res[0] = Direction.UP if "+" in map[2] else Direction.DOWN
            return res
        elif edge == map[1]:
            res[1] = "s" in map[2]
            res[2] = "i" in map[2]
            if "x" in map[2]:
                res[0] = Direction.LEFT if "+" in map[2] else Direction.RIGHT
            elif "y" in map[2]:
                res[0] = Direction.DOWN if "+" in map[2] else Direction.UP
            return res

    return None


# Gets the affected direction(s) from a list of edges
def affected_directions(edges):
    directions = []
    for edge in edges:
        if effect := parse_edge_effect(edge):
            directions.append(effect)

    return directions


# Returns tuple with x offset, y offset, axis lock ("x" or "y")
def offset_from_edge(edge):
    # Check each array for the edge
    for i, edge_set in enumerate(x_leading_edge + x_trailing_edge):
        # Deals with trailing edge being on the other side
        offset = 1 if i >= 4 else 0
        if len(edge_set) == 1 and edge_set[0] == edge:
            return (side_length * (i % 4 + offset) - offset, side_length, "x")
        for j, edge_member in enumerate(edge_set):
            if edge == edge_member:
                return (side_length * (i % 4 + offset) - offset, side_length * j, "x")

    for i, edge_set in enumerate(y_leading_edge + y_trailing_edge):
        # Deals with trailing edge being on the other side
        offset = 1 if i >= 3 else 0
        if len(edge_set) == 1 and edge_set[0] == edge:
            return (side_length, side_length * (i % 3 + offset) - offset, "y")
        for j, edge_member in enumerate(edge_set):
            if edge == edge_member:
                return (side_length * j, side_length * (i % 3 + offset) - offset, "y")

    return None


# Convert the affected direction and points into new coordinates
def process_affected_direction(x, y, switch, invert, current_edge):
    relative_x = x % side_length
    relative_y = y % side_length
    target_edge = find_next_edge(current_edge)
    if switch:
        temp = relative_x
        relative_x = relative_y
        relative_y = temp

    if invert:
        relative_x = side_length - 1 - relative_x
        relative_y = side_length - 1 - relative_y

    res = offset_from_edge(target_edge)
    # Only add offset if not on lock axis
    return (res[0] + relative_x * int(res[2] == "y"), res[1] + relative_y * int(res[2] == "x"))


# Gets next cell in any direction (U: 0, D: 2, L: 3, R: 1)
def next_cell(x, y, direction):
    if edges := edges_from_point(x, y): # If on edge then figure out what direction we need to go and check if the plane(s) will affect that
        affected = affected_directions(edges)
        # If not affected, fallthrough to normal processing
        # Otherwise, start figuring out where to map next point
        for dir in affected:
            if direction == dir[0]:
                return process_affected_direction(x, y, dir[1], dir[2], dir[3])

    # Determines what direction to go (x, y)
    direction_values = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    return (x + direction_values[direction.value][0], y + direction_values[direction.value][1])


# Gets a cell's cardinal neighbors
def neighbors(x, y):
    pass


# Tests whether a point is in the exclusion ranges
def point_is_excluded(x, y):
    for range in maze_exclusion_ranges:
        if x in range[0] and y in range[1]:
            return True
    return False


# Generates the initial maze, W -> wall, P -> passage
def fill_initial_maze():
    global maze
    maze = [["W" if not point_is_excluded(x, y) else None for y in range(0, side_length * 3)] for x in range(0, side_length * 4)]


fill_initial_maze()
print(next_cell(0, 8, Direction.LEFT))