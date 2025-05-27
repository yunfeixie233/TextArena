import numpy as np

def create_board_str(board_state: np.ndarray) -> str:
    grid_lookup = {0:"#", 1:"_", 2:"O", 3:"√", 4:"X", 5:"P", 6:"S"}

    board_str = ""
    for row in board_state:
        board_str += ' '.join([grid_lookup[cell] for cell in row])
        board_str += "\n"
    return board_str