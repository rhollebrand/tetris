import random
import tkinter as tk

# Constants for the game board
CELL_SIZE = 30
COLUMNS = 10
ROWS = 20

COLORS = {
    'S': '#00ff00',
    'Z': '#ff0000',
    'I': '#00ffff',
    'O': '#ffff00',
    'J': '#0000ff',
    'L': '#ff8c00',
    'T': '#800080',
}

# Definition of shapes and their rotations
SHAPES = {
    'S': [
        [(0, 1), (1, 1), (1, 0), (2, 0)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (2, 1), (1, 1), (1, 2)],
    ],
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
}


class Piece:
    def __init__(self, shape: str):
        self.shape = shape
        self.rotation = 0
        self.x = COLUMNS // 2 - 2
        self.y = 0

    def blocks(self, rotation=None):
        rotation = self.rotation if rotation is None else rotation
        return SHAPES[self.shape][rotation]

    def rotated(self):
        return (self.rotation + 1) % len(SHAPES[self.shape])


class TetrisGame:
    """Core game logic, independent of any UI."""

    def __init__(self, rows: int = ROWS, cols: int = COLUMNS):
        self.rows = rows
        self.cols = cols
        self.grid = [[None] * cols for _ in range(rows)]
        self.score = 0
        self.game_over = False
        self.next_shape = random.choice(list(SHAPES.keys()))
        self.spawn_piece()

    # Game state methods --------------------------------------------------
    def spawn_piece(self):
        self.current = Piece(self.next_shape)
        self.next_shape = random.choice(list(SHAPES.keys()))
        self.current.x = self.cols // 2 - 2
        self.current.y = 0
        if not self.is_valid_position(self.current):
            self.game_over = True

    def is_valid_position(self, piece: Piece, dx: int = 0, dy: int = 0, rotation=None) -> bool:
        for x_off, y_off in piece.blocks(rotation):
            x = piece.x + x_off + dx
            y = piece.y + y_off + dy
            if x < 0 or x >= self.cols or y >= self.rows:
                return False
            if y >= 0 and self.grid[y][x]:
                return False
        return True

    def move(self, dx: int, dy: int) -> bool:
        if self.is_valid_position(self.current, dx, dy):
            self.current.x += dx
            self.current.y += dy
            return True
        elif dy:
            self.lock_piece()
        return False

    def rotate(self):
        new_rot = self.current.rotated()
        if self.is_valid_position(self.current, rotation=new_rot):
            self.current.rotation = new_rot

    def hard_drop(self):
        while self.move(0, 1):
            pass

    def lock_piece(self):
        for x_off, y_off in self.current.blocks():
            x = self.current.x + x_off
            y = self.current.y + y_off
            if 0 <= y < self.rows:
                self.grid[y][x] = COLORS[self.current.shape]
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self) -> int:
        lines = [i for i, row in enumerate(self.grid) if all(row)]
        for i in reversed(lines):
            del self.grid[i]
            self.grid.insert(0, [None] * self.cols)
        if lines:
            self.score += [0, 100, 300, 500, 800][len(lines)]
        return len(lines)

    def step(self):
        if not self.game_over:
            self.move(0, 1)


# Graphical interface -----------------------------------------------------
class TetrisApp(tk.Frame):
    def __init__(self, master, game: TetrisGame):
        super().__init__(master)
        self.master = master
        self.game = game
        self.canvas = tk.Canvas(master, width=COLUMNS * CELL_SIZE, height=ROWS * CELL_SIZE, bg="black")
        self.canvas.pack(side=tk.LEFT)

        self.panel = tk.Canvas(master, width=150, height=ROWS * CELL_SIZE, bg="gray20")
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.score_text = self.panel.create_text(10, 10, anchor="nw", fill="white", font=("Helvetica", 16))
        self.panel.create_text(10, 50, anchor="nw", fill="white", font=("Helvetica", 16), text="Next:")
        self.next_ids = []

        master.bind("<Key>", self.handle_key)
        self.update_ui()
        self.game_loop()

    def handle_key(self, event):
        if self.game.game_over:
            return
        if event.keysym == "Left":
            self.game.move(-1, 0)
        elif event.keysym == "Right":
            self.game.move(1, 0)
        elif event.keysym == "Down":
            self.game.move(0, 1)
        elif event.keysym == "Up":
            self.game.rotate()
        elif event.keysym == "space":
            self.game.hard_drop()
        self.update_ui()

    def update_ui(self):
        self.canvas.delete("block")
        for y in range(self.game.rows):
            for x in range(self.game.cols):
                color = self.game.grid[y][x]
                if color:
                    self._draw_cell(x, y, color)
        piece = self.game.current
        if not self.game.game_over:
            for x_off, y_off in piece.blocks():
                x = piece.x + x_off
                y = piece.y + y_off
                if y >= 0:
                    self._draw_cell(x, y, COLORS[piece.shape])
        self._draw_next()
        self.panel.itemconfig(self.score_text, text=f"Score: {self.game.score}")

    def _draw_cell(self, x, y, color):
        x1 = x * CELL_SIZE
        y1 = y * CELL_SIZE
        self.canvas.create_rectangle(
            x1,
            y1,
            x1 + CELL_SIZE,
            y1 + CELL_SIZE,
            fill=color,
            outline="gray20",
            tags="block",
        )

    def _draw_next(self):
        for _id in self.next_ids:
            self.panel.delete(_id)
        self.next_ids.clear()
        shape = self.game.next_shape
        color = COLORS[shape]
        for x_off, y_off in SHAPES[shape][0]:
            x1 = 10 + x_off * CELL_SIZE
            y1 = 80 + y_off * CELL_SIZE
            self.next_ids.append(
                self.panel.create_rectangle(
                    x1,
                    y1,
                    x1 + CELL_SIZE,
                    y1 + CELL_SIZE,
                    fill=color,
                    outline="gray20",
                )
            )

    def game_loop(self):
        if not self.game.game_over:
            self.game.step()
            self.update_ui()
            self.after(500, self.game_loop)
        else:
            self.canvas.create_text(
                COLUMNS * CELL_SIZE / 2,
                ROWS * CELL_SIZE / 2,
                text="GAME OVER",
                fill="white",
                font=("Helvetica", 24),
                tags="block",
            )


def main():
    root = tk.Tk()
    root.title("Tetris")
    game = TetrisGame()
    TetrisApp(root, game)
    root.mainloop()


if __name__ == "__main__":
    main()
