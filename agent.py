"""
An AI player for Othello. 

Note: OpenAI's ChatGPT aided in the drafting of this code
"""

import random
import sys
import time

# You can use the functions in othello_shared to write your AI
from othello_shared import find_lines, get_possible_moves, get_score, play_move

cached_states = {}

def eprint(*args, **kwargs): #you can use this for debugging, as it will print to sterr and not stdout
    print(*args, file=sys.stderr, **kwargs)
    
# Method to compute utility value of terminal state
def compute_utility(board, color):
    #IMPLEMENT
    P1, P2 = get_score(board)
    if color == 1:
        return  P1 - P2 
    else:
        return P2 - P1


# Better heuristic value of board
def compute_heuristic(board, color): #not implemented, optional
    #IMPLEMENT

    return 0 # change this
    

############ MINIMAX ###############################
def minimax_min_node(board, color, limit, caching):
    #IMPLEMENT (and replace the line below)
    global state_cache

    cache_key = str((board, color))

    if caching == 1 and cache_key in cached_states:
        return cached_states[cache_key]

    pos_movs = get_possible_moves(board, color)
    best_move = None
    min_val = float("inf")

    if (limit == 0) or (pos_movs == []): 
       terminal_return = (None, (-1) * compute_utility(board, color))
       #return None, compute_utility(board, color)
       if caching == 1 and limit == 0:
            #cache utililty value for terminal state 
            cached_states[str((board, color, limit))] = terminal_return
       return terminal_return
       
    for move in pos_movs:
        nxt_board = play_move(board, color, move[0], move[1])
        curr_val = minimax_max_node(nxt_board, (3 - color), limit - 1, caching)[1]
        if curr_val < min_val:
            min_val = curr_val
            best_move = move
    
    if caching == 1:
        #cacheing for non-terminal states
        cached_states[cache_key] = (best_move, min_val)

    return (best_move, min_val)

def minimax_max_node(board, color, limit, caching): #returns highest possible utility
    #IMPLEMENT (and replace the line below)
    global cached_states
    
    cache_key = str((board, color))

    if caching == 1 and  cache_key in cached_states:
        return cached_states[cache_key]
    

    pos_movs = get_possible_moves(board, color)
    best_move = None
    max_val = float("-inf")

    if (limit == 0) or (pos_movs == []):   
        terminal_return = (None, compute_utility(board, color))
        #return None, compute_utility(board, color)
        if caching == 1 and limit == 0:
            #cache utililty value for terminal state 
            cached_states[str((board, color, limit))] = terminal_return
        return terminal_return
    
    for move in pos_movs:
        nxt_board = play_move(board, color, move[0], move[1])
        curr_val = minimax_min_node(nxt_board, (3 - color), limit - 1, caching)[1]
        if curr_val > max_val:
            max_val = curr_val
            best_move = move
    
    if caching == 1:
        #cacheing for non-terminal states
        cached_states[cache_key] = (best_move, max_val)

    return (best_move, max_val)
        

def select_move_minimax(board, color, limit, caching):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    """
    return minimax_max_node(board, color, limit, caching)[0]

############ ALPHA-BETA PRUNING #####################
def order_moves(board, moves, color, maximizing_player):
    # Evaluate each move
    move_evals = []
    for move in moves:
        nxt_board = play_move(board, color, move[0], move[1])
        move_evals.append((move, compute_utility(nxt_board, color)))
    # Sort moves based on evaluations
    # For max node, sort in descending order; for min node, sort in ascending order
    move_evals.sort(key=lambda x: x[1], reverse=maximizing_player)
    # Extract sorted moves
    sorted_moves = [move_eval[0] for move_eval in move_evals]
    return sorted_moves

def alphabeta_min_node(board, color, alpha, beta, limit, caching, ordering = 0):
    #IMPLEMENT (and replace the line below)
    global cached_states

    if caching == 1 and (board, color) in cached_states:
        return cached_states[(board, color)]

    pos_movs = get_possible_moves(board, color)

    if limit == 0 or not pos_movs:
        (None, (-1) * compute_utility(board, color))
    
    if ordering == 1:
        pos_movs = order_moves(board, pos_movs, color, maximizing_player = False)

    best_move = None

    for move in pos_movs:
        nxt_board = play_move(board, color, move[0], move[1])
        curr_val = alphabeta_max_node(nxt_board, 3-color, alpha, beta, limit-1, caching, ordering)[1]
        if curr_val < beta:
            beta = curr_val
            best_move = move
        if beta <= alpha:
            break

    if caching == 1:
        cached_states[(board, color)] = (best_move, beta)

    return best_move, beta

def alphabeta_max_node(board, color, alpha, beta, limit, caching, ordering = 0):
    #IMPLEMENT (and replace the line below)
    global cached_states
    
    if caching == 1 and (board, color) in cached_states:
        return cached_states[(board, color)]

    pos_movs = get_possible_moves(board, color)
    if limit == 0 or not pos_movs:
        return (None, compute_utility(board, color))
    
    if ordering == 1:
        pos_movs = order_moves(board, pos_movs, color, maximizing_player = True)

    best_move = None

    for move in pos_movs:
        nxt_board = play_move(board, color, move[0], move[1])
        curr_val = alphabeta_min_node(nxt_board, 3-color, alpha, beta, limit-1, caching, ordering)[1]
        if curr_val > alpha:
            alpha = curr_val
            best_move = move
        if beta <= alpha:
            break

    if caching == 1:
        cached_states[(board, color)] = (best_move, alpha)

    return best_move, alpha

def select_move_alphabeta(board, color, limit, caching = 0, ordering = 0):
    """
    Given a board and a player color, decide on a move. 
    The return value is a tuple of integers (i,j), where
    i is the column and j is the row on the board.  

    Note that other parameters are accepted by this function:
    If limit is a positive integer, your code should enfoce a depth limit that is equal to the value of the parameter.
    Search only to nodes at a depth-limit equal to the limit.  If nodes at this level are non-terminal return a heuristic 
    value (see compute_utility)
    If caching is ON (i.e. 1), use state caching to reduce the number of state evaluations.
    If caching is OFF (i.e. 0), do NOT use state caching to reduce the number of state evaluations.    
    If ordering is ON (i.e. 1), use node ordering to expedite pruning and reduce the number of state evaluations. 
    If ordering is OFF (i.e. 0), do NOT use node ordering to expedite pruning and reduce the number of state evaluations. 
    """
    #IMPLEMENT (and replace the line below)
    return alphabeta_max_node(board, color, float("-inf"), float("inf"), limit, caching, ordering)[0]

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Othello AI") # First line is the name of this AI
    arguments = input().split(",")
    
    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light. 
    limit = int(arguments[1]) #Depth limit
    minimax = int(arguments[2]) #Minimax or alpha beta
    caching = int(arguments[3]) #Caching 
    ordering = int(arguments[4]) #Node-ordering (for alpha-beta only)

    if (minimax == 1): eprint("Running MINIMAX")
    else: eprint("Running ALPHA-BETA")

    if (caching == 1): eprint("State Caching is ON")
    else: eprint("State Caching is OFF")

    if (ordering == 1): eprint("Node Ordering is ON")
    else: eprint("Node Ordering is OFF")

    if (limit == -1): eprint("Depth Limit is OFF")
    else: eprint("Depth Limit is ", limit)

    if (minimax == 1 and ordering == 1): eprint("Node Ordering should have no impact on Minimax")

    while True: # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()
        dark_score = int(dark_score_s)
        light_score = int(light_score_s)

        if status == "FINAL": # Game is over.
            print
        else:
            board = eval(input()) # Read in the input and turn it into a Python
                                  # object. The format is a list of rows. The
                                  # squares in each row are represented by
                                  # 0 : empty square
                                  # 1 : dark disk (player 1)
                                  # 2 : light disk (player 2)

            # Select the move and send it to the manager
            if (minimax == 1): #run this if the minimax flag is given
                movei, movej = select_move_minimax(board, color, limit, caching)
            else: #else run alphabeta
                movei, movej = select_move_alphabeta(board, color, limit, caching, ordering)
            
            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    run_ai()
