from enum import Enum
import random

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

def get_first_point():
    return (int(side_length * 1.5), int(side_length * 1.5))

# Sanity check
if side_length == 0:
    exit(1)

# Allows for creation of the cube maze by excluding parts that are irrelevant (x, y)
def maze_exclusion_ranges():
    return [
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

# Determines which edges connect to eachother along with orientation information 
# (axis and direction to next plane as well as 's' to determine whether axes switch and 'i' to determine if an inversion is needed (which also flips the sign on a reverse traversal)
maze_edge_maps = [
    (1, 4, "y+i"), 
    (2, 3, "x+si"), 
    (5, 18, "x+"), 
    (6, 15, "y-i"), 
    (7, 8, "x-"), 
    (9, 14, "y-s"), 
    (16, 17, "x-si"), 
    (12, 13, "y-"), 
    (19, 24, "y+s"), 
    (20, 21, "x+"), 
    (22, 23, "y+"), 
    (11, 10, "x+")
]

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

    def opposite(self):
        if self.value < 2:
            return Direction(self.value + 2)
        else:
            return Direction(self.value - 2)


# Determines what happens when an edge crossing occurs, returns the effected direction and whether an axis flip is needed
def parse_edge_effect(edge):
    res = [0, False, False, edge]
    for map in maze_edge_maps:
        if edge == map[0]:
            res[1] = "s" in map[2]
            res[2] = "i" in map[2]
            if "x" in map[2]:
                res[0] = Direction.RIGHT if "+" in map[2] else Direction.LEFT
            else:
                res[0] = Direction.UP if "+" in map[2] else Direction.DOWN
            return res
        elif edge == map[1]: # Reverse everything if edge is second
            res[1] = "s" in map[2]
            res[2] = "i" in map[2]
            sign = "-" if "i" in map[2] else "+"
            # Make sure the target axis is switched if needed since this is the reverse relation
            if ("x" in map[2] and not res[1]) or ("y" in map[2] and res[1]): # Normal X transistion or swapped Y transition
                res[0] = Direction.LEFT if sign in map[2] else Direction.RIGHT
            else: # Swapped X transition or normal Y transition
                res[0] = Direction.DOWN if sign in map[2] else Direction.UP
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


# Gets a cell's cardinal wall neighbors
def wall_neighbors(x, y, maze):
    return list(filter(lambda cell: maze[cell[0]][cell[1]] == "W", [next_cell(x, y, d) for d in Direction]))


# Checks if the cell has front diagonal neighbors by assuming that the cell only has one cardinal passage
def has_front_diagonal_neighbors(x, y, maze):
    for d in Direction:
        next = next_cell(x, y, d)
        if maze[next[0]][next[1]] == "P":
            back_direction = d
            break
    
    direction = back_direction.opposite()
    forward_cell = next_cell(x, y, direction)
    for_x, for_y = forward_cell

    if direction.value % 2 == 0:
        first, second = next_cell(for_x, for_y, Direction.LEFT), next_cell(for_x, for_y, Direction.RIGHT)
    else:
        first, second = next_cell(for_x, for_y, Direction.UP), next_cell(for_x, for_y, Direction.DOWN)
    return maze[first[0]][first[1]] == "P" or maze[second[0]][second[1]] == "P"


# Checks if a wall can become a passage
def wall_can_become_passage(x, y, maze):
    # If 3 of the cell's neighbors are walls, that means the fourth is a passage and therefore the wall can become a passage
    return len(wall_neighbors(x, y, maze)) == 3 and not has_front_diagonal_neighbors(x, y, maze)


# Tests whether a point is in the exclusion ranges
def point_is_excluded(x, y):
    for range in maze_exclusion_ranges():
        if x in range[0] and y in range[1]:
            return True
    return False


# Generates the initial maze, W -> wall, P -> passage
def fill_initial_maze(side):
    global side_length
    side_length = side
    print(f"Maze generated with size {side_length * 3}x{side_length * 4}")
    return [["W" if not point_is_excluded(x, y) else None for y in range(0, side_length * 3)] for x in range(0, side_length * 4)]


# Run Prim's algorithm, returns whether or not generation can continue as well as last generated cell
def step_generator(maze, walls, last_generated_cell):
    if len(maze) == 0:
        print("Maze not generated yet!")
        return (False, None)

    if len(walls) == 0:
        if last_generated_cell is None: # If maze doesn't have any walls but is generated, use the first point
            first_point = get_first_point()
            maze[first_point[0]][first_point[1]] = "P"
            walls += wall_neighbors(first_point[0], first_point[1], maze)
            return (True, first_point)
        else:
            return (False, last_generated_cell)

    selected_wall = random.choice(walls)
    if wall_can_become_passage(selected_wall[0], selected_wall[1], maze):
        last_generated_cell = selected_wall
        maze[selected_wall[0]][selected_wall[1]] = "P"
        walls += wall_neighbors(selected_wall[0], selected_wall[1], maze)

    walls.remove(selected_wall)
    return (len(walls) > 0, last_generated_cell)


# BEGIN SHOW CODE
"""with open('testfile.txt', 'w') as f:
    for x in range(0, side_length * 4):
        for y in range(0, side_length * 3):
            if not point_is_excluded(x, y):
                for d in Direction:
                    x2, y2 = next_cell(x, y, d)
                    res = f'The cell in direction {d.name} from ({x}, {y}) is ({x2}, {y2})'
                    if point_is_excluded(x2, y2) or x2 > 31 or y2 > 23:
                        res += ' ERROR!'
                    f.write(f'{res}\n')"""