import json
import random

pieces = {
    "W": [(1,0), (0, 1), (-1, 0), (0, -1)],
    "B": [(1,0), (0, 1), (-1, 0), (0, -1)]
}
rules = {
    "pieces": pieces,
    "max_repetitions": 5,
    "max_turns": 200,
    "rows": 5,
    "cols": 5,
    "starting_positions": {
        "B": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
        "W": [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
    }
}

def display(board):
    for row in board:
        print(" ".join(row))
    print("")

def get_legal_moves(board, pieces):
    rows = len(board)
    cols = len(board[0])

    moves = {
        "B": [],
        "W": []
    }
    for i in range(rows):
        for j in range(cols):
            if board[i][j] in pieces:
                for dr in pieces[board[i][j]]:
                    move = [i, j, i + dr[0], j + dr[1]]
                    if move[2] >= 0 and move[2] < rows and move[3] >= 0 and move[3] < cols and board[move[2]][move[3]] != board[i][j]:
                        moves[board[i][j]].append(move)
    
    return moves

def set_board(board, starting_positions):
    new_board = [row[:] for row in board]

    for piece, positions in starting_positions.items():
        for row, col in positions:
            new_board[row][col] = piece

    return new_board

def get_move(moves, current_player) -> list[int]:
    move = None

    print(f"Legal Moves: {moves[current_player]}")
    user = input(f"Player {current_player}, input a legal move seperated by commas. \n>")
    try:
        user_move = [int(num) for num in user.split(",")]
    except ValueError:
        user_move = None
        print("Invalid Input")

    if user_move in moves[current_player]:
        move = user_move

    while move is None:
        user = input(f"{user_move} was not a legal move, please try again. \n>")
        try:
            user_move = [int(num) for num in user.split(",")]
        except ValueError:
            user_move = None
            print("Invalid Input")

        if user_move in moves[current_player]:
            move = user_move

    return move

def random_agent(moves, current_player) -> list[int]:
    move = random.choice(moves[current_player])

    return move

def greedy_agent(board, moves, current_player) -> list[int]:
    move = ""
    for m in moves[current_player]:
        if board[m[2]][m[3]] != ".":
            move = m
            break

    if move == "":
        move = random.choice(moves[current_player])

    return move

def look_ahead_agent(pieces, board, moves, current_player) -> list[int]:
    poss_moves = {}
    score = float("-inf")
    opp_player = "W"
    if current_player == "W":
        opp_player = "B"
    
    for m in moves[current_player]:
        m_score = 0
        if board[m[2]][m[3]] != ".":
            m_score += 10

        new_board = move_piece(board, m)
        new_moves = get_legal_moves(new_board, pieces)
        for om in new_moves[opp_player]:
            if om[2] == m[2] and om[3] == m[3]:
                m_score -= 10
                break
        
        if m_score in poss_moves:
            poss_moves[m_score].append(m)
        else:
            poss_moves[m_score] = [m]

        if m_score > score:
            score = m_score
        
    move = random.choice(poss_moves[score])

    return move

def minimax(depth, moves, state, rules):
    board = state["board"]
    current_player = state["current_player"]
    pieces = rules["pieces"]

    if not moves["B"] and not moves["W"]:
        return 0

    if not moves["W"]:
        return -1000
    
    if not moves["B"]:
        return 1000
    
    if state["previous_moves"]["W"][1] >= rules["max_repetitions"]:
        return -1000
    
    if state["previous_moves"]["B"][1] >= rules["max_repetitions"]:
        return 1000
    
    if state["turns"] >= rules["max_turns"]:
        return 0

    if depth == 0:
        return evaluate_board(board)

    scores = []    

    for m in moves[current_player]:
        new_state = apply_action(state, m)
        new_moves = get_legal_moves(new_state["board"], pieces)

        score = minimax(depth-1, new_moves, new_state, rules)
    
        scores.append(score)

    if current_player == "W":
        return max(scores)
    else:
        return min(scores)


def evaluate_board(board):
    score = 0
    for row in board:
        for space in row:
            if space == "W":
                score += 1

            elif space == "B":
                score -= 1
    
    return score

def minimax_agent(depth, moves, state, rules):
    current_player = state["current_player"]
    pieces = rules["pieces"]
    m_score = float("-inf")
    poss_moves = {}
    for m in moves[current_player]:
        new_state = apply_action(state, m)
        new_moves = get_legal_moves(new_state["board"], pieces)

        score = minimax(depth-1, new_moves, new_state, rules)

        if current_player == "B":
            score = score * -1
        
        if score in poss_moves:
            poss_moves[score].append(m)
        else:
            poss_moves[score] = [m]

        if m_score < score:
            m_score = score
        
    move = random.choice(poss_moves[m_score])

    return move

def move_piece(board, move):
    new_board = [row[:] for row in board]

    temp = new_board[move[0]][move[1]]
    new_board[move[0]][move[1]] = "."
    new_board[move[2]][move[3]] = temp

    return new_board

def update_repetitions(previous_moves, current_player, move):
    history = {
        player: [moves.copy(), count]
        for player, (moves, count) in previous_moves.items()
    }

    if len(history[current_player][0]) < 2:
        history[current_player][0].append(move)
    else:
        if history[current_player][0].pop(0) == move:
            history[current_player][1] += 1

        else:
            history[current_player][1] = 0

        history[current_player][0].append(move)
    
    return history

def get_result(moves, previous_moves, max_repetitions, turns, max_turns):
    if len(moves["W"]) == 0 and len(moves["B"]) == 0:
        return {
            "winner": "tie",
            "reason": "no moves"
        }

    elif len(moves["W"]) == 0:
        return {
            "winner": "B",
            "reason": "win"
        }

    elif len(moves["B"]) == 0:
        return {
            "winner": "W",
            "reason": "win"
        }

    elif previous_moves["W"][1] >= max_repetitions:
        return {
            "winner": "B",
            "reason": "repetition"
        }
    
    elif previous_moves["B"][1] >= max_repetitions:
        return {
            "winner": "W",
            "reason": "repetition"
        }
    
    elif turns >= max_turns:
        return {
            "winner": "tie",
            "reason": "max turns exceeded"
        }

    return None

def apply_action(state, move):
    player = state["current_player"]

    return {
        "board": move_piece(state["board"], move),
        "previous_moves": update_repetitions(state["previous_moves"], player, move),
        "current_player": "B" if player == "W" else "W",
        "turns": state["turns"] + 1
    }

def display_win(result):
    if result["winner"] == "tie":
        if result["reason"] == "max turns exceeded":
            print("Max Turns Exceeded, Tie Game!!")
        else:
            print("No Turns Avaliable, Tie Game!!")
    
    elif result["winner"] == "W":
        if result["reason"] == "repetition":
            print("Player W Wins by Repetition!!")
        else:
            print("Player W Wins!!")

    elif result["winner"] == "B":
        if result["reason"] == "repetition":
            print("Player B Wins by Repetition!!")
        else:
            print("Player B Wins!!")

def record_results(result, turns):
    with open("data/minimax3_vs_lookahead_v2/data.json", "r") as f:
        data = json.load(f)

    data[result["winner"]][result["reason"]] += 1
    data["total_games"] += 1
    data["total_turns"] += turns
    
    with open("data/minimax3_vs_lookahead_v2/data.json", "w") as f:
        json.dump(data, f)

# Game Loop
def play_game(rules):
    board = [["."] * rules["cols"] for _ in range(rules["rows"])]

    previous_moves = {
        "W": [[], 0],
        "B": [[], 0]
    }

    state = {
        "board": board,
        "current_player": "W",
        "previous_moves": previous_moves,
        "turns": 0
    }

    state["board"] = set_board(state["board"], rules["starting_positions"])
    # display(state["board"])
    moves = get_legal_moves(state["board"], rules["pieces"])
    result = get_result(moves, state["previous_moves"], rules["max_repetitions"], state["turns"], rules["max_turns"])

    while result is None:
        """
        human input
        move = get_move(moves, state["current_player"])
        ---------------------------------------------------

        random vs random
        move = random_agent(moves, state["current_player"])
        ---------------------------------------------------

        greedy vs greedy
        move = greedy_agent(state["board"], moves, state["current_player"])
        ---------------------------------------------------

        greedy vs random
        if state["current_player"] == "W":
            move = greedy_agent(state["board"], moves, state["current_player"])
        else:
            move = random_agent(moves, state["current_player"])
        ---------------------------------------------------

        random vs greedy
        if state["current_player"] == "B":
            move = greedy_agent(state["board"], moves, state["current_player"])
        else:
            move = random_agent(moves, state["current_player"])
        ---------------------------------------------------

        look ahead vs look ahead
        move = look_ahead_agent(rules["pieces"], state["board"], moves, state["current_player"])
        ---------------------------------------------------

        look ahead vs greedy
        if state["current_player"] == "B":
            move = greedy_agent(state["board"], moves, state["current_player"])
        else:
            move = look_ahead_agent(rules["pieces"], state["board"], moves, state["current_player"])

        ---------------------------------------------------

        greedy vs look ahead
        if state["current_player"] == "W":
            move = greedy_agent(state["board"], moves, state["current_player"])
        else:
            move = look_ahead_agent(rules["pieces"], state["board"], moves, state["current_player"])
        state = apply_action(state, move)
        ---------------------------------------------------

        minimax vs greedy
        if state["current_player"] == "W":
            move = minimax_agent(X, moves, state, rules)
        else:
            move = greedy_agent(state["board"], moves, state["current_player"])
        ---------------------------------------------------

        minimax vs look ahead
        if state["current_player"] == "W":
            move = minimax_agent(X, moves, state, rules)
        else:
            move = look_ahead_agent(rules["pieces"], state["board"], moves, state["current_player"])
        ---------------------------------------------------
        """

        if state["current_player"] == "W":
            move = minimax_agent(3, moves, state, rules)
        else:
            move = look_ahead_agent(rules["pieces"], state["board"], moves, state["current_player"])
        state = apply_action(state, move)

        # display(state["board"])
        moves = get_legal_moves(state["board"], rules["pieces"])
        result = get_result(moves, state["previous_moves"], rules["max_repetitions"], state["turns"], rules["max_turns"])

    display_win(result)

    return result, state["turns"]

for _ in range(1000):
    result, turns = play_game(rules)
    record_results(result, turns)