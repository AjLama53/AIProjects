"""
Tic Tac Toe Player
"""

import math
import copy

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


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    x_count = 0
    o_count = 0

    row = len(board)
    col = len(board[0])

    for i in range(row):
        for j in range(col):
            if board[i][j] == X:
                x_count += 1
            elif board[i][j] == O:
                o_count += 1

    
    return X if x_count == o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    moves = set()

    row = len(board)
    col = len(board[0])

    for i in range(row):
        for j in range(col):
            if board[i][j] == EMPTY:
                moves.add((i, j))

    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    if action not in actions(board):
        raise Exception("Invalid move")

    i, j = action

    result_board = copy.deepcopy(board)

    result_board[i][j] = player(board)

    return result_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """


    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:
            return board[i][0]
        
        elif board[0][i] == board[1][i] == board[2][i] != EMPTY:
            return board[0][i]
        

    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]

    if board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[0][2]
    
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board) != None:
        return True
    
    row = len(board)
    col = len(board[0])

    for i in range(row):
        for j in range(col):
            if board[i][j] == EMPTY:
                return False

    return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None
    
    best_action = None
    turn = player(board)

    if turn == X:
        best = -math.inf
        for action in actions(board):
            new_board = result(board, action)
            util = evaluate(new_board)

            if util > best:
                best = util
                best_action = action



    else:
        best = math.inf
        for action in actions(board):
            util = evaluate(result(board, action))
            if util < best:
                best = util
                best_action = action

    return best_action



def evaluate(board):

    if terminal(board):
        return utility(board)
    
    turn = player(board)

    if turn == X:
        best = -math.inf
        for action in actions(board):
            val = evaluate(result(board, action))
            best = max(val, best)
            # we are trying to save the best utility value, if we save val it will always change
        


    else:
        best = math.inf
        for action in actions(board):
            val = evaluate(result(board, action))
            best = min(val, best)

    

    return best

    

    




