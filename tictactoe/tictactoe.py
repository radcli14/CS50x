"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def count(board):
    return sum([sum([0 if pos is None else 1 for pos in row]) for row in board])


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    return X if count(board) % 2 == 0 else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                actions.add((i, j))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    current_player = player(board)
    board_copy = [row.copy() for row in board]
    board_copy[action[0]][action[1]] = current_player
    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check if any row has the same non-empty value
    for row in board:
        if row[0] is not None and row[0] == row[1] == row[2]:
            return row[0]
        
    # Check if any row has the same non-empty value
    for k in range(3):
        if board[0][k] is not None and board[0][k] == board[1][k] == board[2][k]:
            return board[0][k]
        
    # Check if any diagonal has the same non-empty value
    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    
    # No winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # First check if the board is full
    if count(board) == 9:
        return True
    
    # Then check if there is a winner
    if winner(board) is not None:
        return True

    # No winner and board not full
    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    board_winner = winner(board)
    return 1 if board_winner == X else -1 if board_winner == O else 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    current_player = player(board)

    best_value = -math.inf if current_player == X else math.inf
    best_action = None
    strategy = min_value if current_player == X else max_value
    is_best = (lambda v: v > best_value) if current_player == X else (lambda v: v < best_value)

    for action in actions(board):
        action_result = result(board, action)
        value = strategy(action_result)
        if is_best(value):
            best_value = value
            best_action = action

    return best_action


def max_value(board):
    if terminal(board):
        return utility(board)
    v = -math.inf
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v


def min_value(board):
    if terminal(board):
        return utility(board)
    v = math.inf
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v