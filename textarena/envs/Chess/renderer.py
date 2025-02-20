# """
# Chess Board Renderer

# Provides functions for rendering chess boards as string or colored representations.
# """

# import curses
# import chess
# from typing import List, Tuple, Dict, Optional
# from dataclasses import dataclass


# @dataclass
# class CellInfo:
#     """Information about a chess board cell for rendering"""
#     symbol: str
#     fg_color: int  # Foreground color (text color)
#     bg_color: int  # Background color
#     attrs: int = 0  # Additional attributes (bold, etc.)


# # Color indices for use with curses
# LIGHT_SQUARE = 3
# DARK_SQUARE = 4
# WHITE_PIECE = 0  # Will use default white
# BLACK_PIECE = 1  # Will use default white with bold

# # Unicode chess pieces
# PIECE_SYMBOLS = {
#     'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
#     'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
#     '.': ' '
# }


# def create_board_str(board: chess.Board) -> str:
#     """
#     Generate a string representation of the chess board with pieces.
#     Each board position is represented by a piece Unicode symbol.
    
#     Args:
#         board: A chess.Board object representing the current game state
        
#     Returns:
#         str: A multiline string representing the current board state
#     """
#     # Get board as FEN string and parse
#     board_fen = board.board_fen()
#     rows = board_fen.split('/')
    
#     # Build piece grid
#     piece_grid = []
#     for row in rows:
#         current_row = []
#         for char in row:
#             if char.isdigit():
#                 # Empty squares
#                 current_row.extend([' '] * int(char))
#             else:
#                 # Piece
#                 current_row.append(PIECE_SYMBOLS.get(char, '?'))
#         piece_grid.append(current_row)
    
#     # Build the board string with coordinates and borders
#     board_str = "   a b c d e f g h \n"
#     board_str += "  ┌───────────────┐\n"
    
#     for row_idx, row in enumerate(piece_grid):
#         # Add row number
#         rank_num = 8 - row_idx
#         board_str += f"{rank_num} │"
        
#         # Add pieces for this row
#         for piece in row:
#             board_str += f"{piece} "
            
#         # Close the row
#         board_str += f"│ {rank_num}\n"
        
#     board_str += "  └───────────────┘\n"
#     board_str += "   a b c d e f g h "
    
#     return board_str


# def create_colored_board(board: chess.Board, 
#                          highlighted_squares: Optional[List[str]] = None) -> List[List[CellInfo]]:
#     """
#     Create a colored board representation with pieces.
#     This version returns cell info objects that can be used with curses.
    
#     Args:
#         board: A chess.Board object representing the current game state
#         highlighted_squares: Optional list of squares to highlight (e.g., ['e4', 'd5'])
        
#     Returns:
#         List[List[CellInfo]]: Grid of cell information for curses rendering
#     """
#     grid = []
    
#     # Use highlighted squares or initialize empty set
#     highlight_set = set(highlighted_squares) if highlighted_squares else set()
    
#     # Add last move squares to highlights if not provided
#     if not highlighted_squares and board.move_stack:
#         last_move = board.move_stack[-1]
#         if last_move:
#             # Highlight the from and to squares of the last move
#             highlight_set.add(chess.square_name(last_move.from_square))
#             highlight_set.add(chess.square_name(last_move.to_square))
    
#     # Get FEN representation and parse it
#     board_fen = board.board_fen()
#     rows = board_fen.split('/')
    
#     for row_idx, row in enumerate(rows):
#         grid_row = []
#         col_idx = 0
        
#         # Process each character in the FEN row
#         for char in row:
#             if char.isdigit():
#                 # Empty squares
#                 empty_count = int(char)
#                 for _ in range(empty_count):
#                     is_light_square = (row_idx + col_idx) % 2 == 0
#                     bg_color = LIGHT_SQUARE if is_light_square else DARK_SQUARE
                    
#                     # Get square name
#                     square_name = chess.square_name(chess.square(col_idx, 7-row_idx))
                    
#                     # Highlight squares if needed
#                     if square_name in highlight_set:
#                         # Use a different background color for highlighted squares
#                         # Here using player color for highlighting
#                         bg_color = 6 if is_light_square else 7
                    
#                     grid_row.append(CellInfo(' ', WHITE_PIECE, bg_color))
#                     col_idx += 1
#             else:
#                 # Piece
#                 is_light_square = (row_idx + col_idx) % 2 == 0
#                 bg_color = LIGHT_SQUARE if is_light_square else DARK_SQUARE
                
#                 # Get square name
#                 square_name = chess.square_name(chess.square(col_idx, 7-row_idx))
                
#                 # Highlight squares if needed
#                 if square_name in highlight_set:
#                     # Use a different background color for highlighted squares
#                     bg_color = 6 if is_light_square else 7
                
#                 # Determine if this is a white or black piece
#                 is_white_piece = char.isupper()
#                 fg_color = WHITE_PIECE
                
#                 # Use bold for black pieces, normal for white pieces
#                 attrs = 0 if is_white_piece else curses.A_BOLD
                
#                 symbol = PIECE_SYMBOLS.get(char, '?')
#                 grid_row.append(CellInfo(symbol, fg_color, bg_color, attrs))
#                 col_idx += 1
        
#         grid.append(grid_row)
    
#     return grid

"""
TextArena Chess Renderer

Provides functions for rendering chess boards as strings or colored representations.
"""

import curses
import chess
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class CellInfo:
    """Information about a chess board cell for rendering"""
    symbol: str
    fg_color: int  # Foreground color (text color)
    bg_color: int  # Background color
    attrs: int = 0  # Additional attributes (bold, etc.)


# Color indices for use with curses
LIGHT_SQUARE = 3
DARK_SQUARE = 4
WHITE_PIECE = 0  # Will use default white
BLACK_PIECE = 1  # Will use default white with bold

# Unicode chess pieces
PIECE_SYMBOLS = {
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    '.': ' '
}


def create_board_str(board: chess.Board, 
                    show_coordinates: bool = True, 
                    unicode_pieces: bool = True) -> str:
    """
    Generate a string representation of the chess board with pieces.
    
    Args:
        board: A chess.Board object representing the current game state
        show_coordinates: Whether to show rank/file coordinates
        unicode_pieces: Whether to use Unicode chess symbols
        
    Returns:
        str: A multiline string representing the current board state
    """
    # Get board as FEN string and parse
    board_fen = board.board_fen()
    rows = board_fen.split('/')
    
    # Build piece grid
    piece_grid = []
    for row in rows:
        current_row = []
        for char in row:
            if char.isdigit():
                # Empty squares
                current_row.extend([' '] * int(char))
            else:
                if unicode_pieces:
                    # Unicode piece
                    current_row.append(PIECE_SYMBOLS.get(char, '?'))
                else:
                    # ASCII piece
                    current_row.append(char)
        piece_grid.append(current_row)
    
    # Build the board string
    if show_coordinates:
        board_str = " a b c d e f g h \n"
        board_str += " ┌────────────────┐\n"
        
        for row_idx, row in enumerate(piece_grid):
            # Add row number
            rank_num = 8 - row_idx
            board_str += f"{rank_num} │"
            
            # Add pieces for this row
            for piece in row:
                board_str += f"{piece} "
                
            # Close the row
            board_str += f"│ {rank_num}\n"
            
        board_str += " └────────────────┘\n"
        board_str += " a b c d e f g h "
    else:
        # Simple board without coordinates
        board_str = "┌───────────────┐\n"
        
        for row in piece_grid:
            board_str += "│"
            # Add pieces for this row
            for piece in row:
                board_str += f"{piece} "
                
            # Close the row
            board_str += "│\n"
            
        board_str += "└───────────────┘"
    
    return board_str


def create_colored_board(board: chess.Board, 
                         highlighted_squares: Optional[List[str]] = None) -> List[List[CellInfo]]:
    """
    Create a colored board representation with pieces.
    This version returns cell info objects that can be used with curses.
    
    Args:
        board: A chess.Board object representing the current game state
        highlighted_squares: Optional list of squares to highlight (e.g., ['e4', 'd5'])
        
    Returns:
        List[List[CellInfo]]: Grid of cell information for curses rendering
    """
    grid = []
    
    # Use highlighted squares or initialize empty set
    highlight_set = set(highlighted_squares) if highlighted_squares else set()
    
    # Add last move squares to highlights if not provided
    if not highlighted_squares and board.move_stack:
        last_move = board.move_stack[-1]
        if last_move:
            # Highlight the from and to squares of the last move
            highlight_set.add(chess.square_name(last_move.from_square))
            highlight_set.add(chess.square_name(last_move.to_square))
    
    # Get FEN representation and parse it
    board_fen = board.board_fen()
    rows = board_fen.split('/')
    
    for row_idx, row in enumerate(rows):
        grid_row = []
        col_idx = 0
        
        # Process each character in the FEN row
        for char in row:
            if char.isdigit():
                # Empty squares
                empty_count = int(char)
                for _ in range(empty_count):
                    is_light_square = (row_idx + col_idx) % 2 == 0
                    bg_color = LIGHT_SQUARE if is_light_square else DARK_SQUARE
                    
                    # Get square name
                    square_name = chess.square_name(chess.square(col_idx, 7-row_idx))
                    
                    # Highlight squares if needed
                    if square_name in highlight_set:
                        # Use a different background color for highlighted squares
                        # Here using player color for highlighting
                        bg_color = 6 if is_light_square else 7
                    
                    grid_row.append(CellInfo(' ', WHITE_PIECE, bg_color))
                    col_idx += 1
            else:
                # Piece
                is_light_square = (row_idx + col_idx) % 2 == 0
                bg_color = LIGHT_SQUARE if is_light_square else DARK_SQUARE
                
                # Get square name
                square_name = chess.square_name(chess.square(col_idx, 7-row_idx))
                
                # Highlight squares if needed
                if square_name in highlight_set:
                    # Use a different background color for highlighted squares
                    bg_color = 6 if is_light_square else 7
                
                # Determine if this is a white or black piece
                is_white_piece = char.isupper()
                fg_color = WHITE_PIECE
                
                # Use bold for black pieces, normal for white pieces
                attrs = 0 if is_white_piece else curses.A_BOLD
                
                symbol = PIECE_SYMBOLS.get(char, '?')
                grid_row.append(CellInfo(symbol, fg_color, bg_color, attrs))
                col_idx += 1
        
        grid.append(grid_row)
    
    return grid

# def draw_chess_board(self, win, board_str):
#     """Draw a chess board with proper checkered background and alignment"""
#     # Clear window and draw border
#     win.clear()
#     win.box()
    
#     # Get window dimensions
#     height, width = win.getmaxyx()
    
#     # Fill window with background color
#     for y in range(1, height-1):
#         win.addstr(y, 1, " " * (width-2), curses.color_pair(1))
    
#     # Add title
#     title = " Game Board "
#     win.addstr(0, (width - len(title)) // 2, title, curses.color_pair(2) | curses.A_BOLD)
    
#     # Parse board string to determine layout
#     lines = board_str.split('\n')
    
#     # Extract board content - look for a better way to detect board boundaries
#     board_content = []
#     coordinate_row = []
#     top_border_idx = -1
#     bottom_border_idx = -1
    
#     # Find coordinates row (usually contains 'a b c d e f g h')
#     for i, line in enumerate(lines):
#         if 'a b c d e f g h' in line:
#             coordinate_row = line
#             # Assume the border is on the next line
#             if i+1 < len(lines) and '┌' in lines[i+1]:
#                 top_border_idx = i+1
    
#     # If we found the top border, look for bottom border
#     if top_border_idx >= 0:
#         for i in range(top_border_idx+1, len(lines)):
#             if '└' in lines[i]:
#                 bottom_border_idx = i
#                 break
    
#     # Extract the actual board content
#     if 0 <= top_border_idx < bottom_border_idx:
#         for i in range(top_border_idx+1, bottom_border_idx):
#             if '│' in lines[i]:
#                 parts = lines[i].split('│')
#                 if len(parts) > 2:
#                     # Extract row number and board content
#                     row_num = parts[0].strip()
#                     board_content.append((row_num, parts[1].strip()))
    
#     # If parsing failed, just center the text
#     if not board_content:
#         self._center_text(win, board_str, y_offset=2)
#         win.refresh()
#         return
    
#     # Get board dimensions
#     board_height = len(board_content)
#     board_width = len(board_content[0][1])
    
#     # Calculate starting position to center the board
#     start_y = max(2, (height - board_height - 4) // 2)
#     start_x = max(4, (width - board_width - 4) // 2)
    
#     # Draw column coordinates (a-h) at top
#     if coordinate_row:
#         col_y = start_y - 1
#         coords = coordinate_row.strip()
#         for i, char in enumerate(coords):
#             x_pos = start_x + i
#             if 0 <= col_y < height-1 and 0 <= x_pos < width-1 and char != ' ':
#                 try:
#                     win.addstr(col_y, x_pos, char, curses.color_pair(2))
#                 except curses.error:
#                     pass
    
#     # Draw column coordinates (a-h) at bottom
#     if coordinate_row:
#         col_y = start_y + board_height
#         coords = coordinate_row.strip()
#         for i, char in enumerate(coords):
#             x_pos = start_x + i
#             if 0 <= col_y < height-1 and 0 <= x_pos < width-1 and char != ' ':
#                 try:
#                     win.addstr(col_y, x_pos, char, curses.color_pair(2))
#                 except curses.error:
#                     pass
    
#     # Draw the board with checkered background
#     for row_idx, (row_num, row_content) in enumerate(board_content):
#         # Draw row number on left
#         if 0 <= start_y + row_idx < height-1 and 0 <= start_x - 2 < width:
#             try:
#                 win.addstr(start_y + row_idx, start_x - 2, row_num, curses.color_pair(2))
#             except curses.error:
#                 pass
        
#         # Draw row number on right
#         if 0 <= start_y + row_idx < height-1 and 0 <= start_x + board_width + 1 < width:
#             try:
#                 win.addstr(start_y + row_idx, start_x + board_width + 1, row_num, curses.color_pair(2))
#             except curses.error:
#                 pass
        
#         # Draw each square and piece
#         for col_idx, char in enumerate(row_content):
#             if col_idx >= board_width or start_y + row_idx >= height-1 or start_x + col_idx >= width-1:
#                 continue
            
#             # Determine square color (checkerboard pattern)
#             # Use the actual position on the board for correct alternating colors
#             rank = 8 - row_idx
#             file = col_idx // 2  # Adjust for the space between pieces
#             is_light_square = (rank + file) % 2 == 0
#             square_color = curses.color_pair(3) if is_light_square else curses.color_pair(4)
            
#             # Determine piece color and attributes
#             attrs = 0
#             if char in '♙♖♘♗♕♔':  # White pieces
#                 # White pieces on either square color
#                 color = square_color
#             elif char in '♟♜♞♝♛♚':  # Black pieces
#                 # Black pieces need bold attribute
#                 color = square_color | curses.A_BOLD
#                 attrs = curses.A_BOLD
#             else:
#                 # Empty square or coordinate
#                 color = square_color
            
#             # Draw the square with piece
#             try:
#                 win.addstr(start_y + row_idx, start_x + col_idx, char, color | attrs)
#             except curses.error:
#                 pass
    
#     # Draw board frame
#     frame_y_top = start_y - 1
#     frame_y_bottom = start_y + board_height
#     frame_x_left = start_x - 1
#     frame_x_right = start_x + board_width
    
#     # Draw horizontal borders
#     for x in range(frame_x_left, frame_x_right + 1):
#         if 0 <= frame_y_top < height and 0 <= x < width:
#             try:
#                 win.addstr(frame_y_top, x, "─", curses.color_pair(2))
#             except curses.error:
#                 pass
#         if 0 <= frame_y_bottom < height and 0 <= x < width:
#             try:
#                 win.addstr(frame_y_bottom, x, "─", curses.color_pair(2))
#             except curses.error:
#                 pass
    
#     # Draw vertical borders
#     for y in range(frame_y_top, frame_y_bottom + 1):
#         if 0 <= y < height and 0 <= frame_x_left < width:
#             try:
#                 win.addstr(y, frame_x_left, "│", curses.color_pair(2))
#             except curses.error:
#                 pass
#         if 0 <= y < height and 0 <= frame_x_right < width:
#             try:
#                 win.addstr(y, frame_x_right, "│", curses.color_pair(2))
#             except curses.error:
#                 pass
    
#     # Draw corners
#     if 0 <= frame_y_top < height and 0 <= frame_x_left < width:
#         try:
#             win.addstr(frame_y_top, frame_x_left, "┌", curses.color_pair(2))
#         except curses.error:
#             pass
#     if 0 <= frame_y_top < height and 0 <= frame_x_right < width:
#         try:
#             win.addstr(frame_y_top, frame_x_right, "┐", curses.color_pair(2))
#         except curses.error:
#             pass
#     if 0 <= frame_y_bottom < height and 0 <= frame_x_left < width:
#         try:
#             win.addstr(frame_y_bottom, frame_x_left, "└", curses.color_pair(2))
#         except curses.error:
#             pass
#     if 0 <= frame_y_bottom < height and 0 <= frame_x_right < width:
#         try:
#             win.addstr(frame_y_bottom, frame_x_right, "┘", curses.color_pair(2))
#         except curses.error:
#             pass
    
#     win.refresh()