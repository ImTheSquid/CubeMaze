import pyglet
from pyglet.window import key
import cubeMaze

window = pyglet.window.Window(resizable=True)
window.width = 640
window.height = 480

side_length = 0

@window.event
def on_resize(width, height):
    global cell_x, cell_y
    cell_x = width // (4 * side_length)
    cell_y = height // (3 * side_length)

# Maze data
maze_walls = []
# Defines the cell that was generated last
last_generated_cell = None
maze = []
can_generate = True

def update(dt):
    global maze, maze_walls, last_generated_cell, can_generate
    if len(maze) == 0:
        maze = cubeMaze.fill_initial_maze(side_length)
    if can_generate:
        can_generate, last_generated_cell = cubeMaze.step_generator(maze, maze_walls, last_generated_cell)

pyglet.clock.schedule_interval(update, 0.01)


no_maze = pyglet.text.Label("NO MAZE!", x=window.width//2, y=window.height//2, anchor_x='center', anchor_y='center')
rect = pyglet.shapes.Rectangle(x=0, y=0, width=0, height=0, color=(0, 0, 0))

@window.event
def on_key_release(symbol, mods):
    global maze, last_generated_cell, maze_walls, can_generate
    if symbol == key.R:
        maze = []
        last_generated_cell = None
        maze_walls = []
        can_generate = True

@window.event
def on_draw():
    window.clear()
    if len(maze) == 0:
        no_maze.draw()
    else:
        for x in range(0, side_length * 4):
            for y in range(0, side_length * 3):
                cell = maze[x][y]
                if (x, y) == last_generated_cell:
                    if not can_generate:
                        color = (0, 255, 0)
                    else:
                        color = (255, 0, 0)
                elif cell is None:
                    color = (100, 100, 100)
                elif cell == "W":
                    color = (10, 10, 10)
                else:
                    color = (255, 255, 255)
                rect.width = cell_x
                rect.height = cell_y
                rect.x = x * cell_x
                rect.y = window.height - y * cell_y - cell_y
                rect.color = color
                rect.draw()

def run(side):
    global side_length, cell_x, cell_y
    side_length = side
    cell_x = window.width // (4 * side_length)
    cell_y = window.height // (3 * side_length)
    print(f"Rendering maze with side length {side_length} and cell x {cell_x} and cell y {cell_y}")
    pyglet.app.run()

run(8)