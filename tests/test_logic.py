import tetris

def test_line_clear_and_score():
    game = tetris.TetrisGame()
    # Fill bottom row
    for x in range(tetris.COLUMNS):
        game.grid[tetris.ROWS - 1][x] = tetris.COLORS['I']
    cleared = game.clear_lines()
    assert cleared == 1
    assert game.score == 100
    assert all(cell is None for cell in game.grid[0])


def test_move_bounds_and_rotation():
    game = tetris.TetrisGame()
    piece = tetris.Piece('I')
    piece.x = 0
    piece.rotation = 0  # horizontal
    game.current = piece
    game.move(-1, 0)  # should not move left beyond board
    assert piece.x == 0
    game.rotate()
    assert piece.rotation == 1
