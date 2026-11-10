from collections import deque
import json
import random
import os

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
        "B": [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
        "W": [(5, 0), (5, 1), (5, 2), (5, 3), (5, 4)]
    }
}

def display(board):
    for row in board:
        print(" ".join(row))
    print("")

def get_legal_moves(state, pieces):
    board = state["board"]
    active_piece = state["active_piece"]
    player = state["current_player"]
    if player == "B":
        own_goal = "X"
    else:
        own_goal = "x"

    rows = len(board)
    cols = len(board[0])

    moves = {
        "B": [],
        "W": []
    }

    if active_piece[player] is None or board[active_piece[player][0]][active_piece[player][1]] != player:
        for i in range(rows):
            for j in range(cols):
                if board[i][j] == player:
                    for dr in pieces[player]:
                        move = [i, j, i + dr[0], j + dr[1]]
                        if move[2] >= 0 and move[2] < rows and move[3] >= 0 and move[3] < cols and board[move[2]][move[3]] != player and board[move[2]][move[3]] != " " and board[move[2]][move[3]] != own_goal and board[move[2]][move[3]] != "#":
                            moves[player].append(move)
    
    else:
        start = active_piece[player]
        seen = set()
        q = deque()
        q.append(start)
        seen.add((start[0], start[1]))

        while q:
            i,j = q.popleft()

            for dr in pieces[board[i][j]]:
                move = [i, j, i + dr[0], j + dr[1]]
                if move[2] >= 0 and move[2] < rows and move[3] >= 0 and move[3] < cols and (move[2], move[3]) not in seen and board[move[2]][move[3]] != " " and board[move[2]][move[3]] != own_goal and board[move[2]][move[3]] != "#":
                    if board[move[2]][move[3]] == board[i][j]:
                        seen.add((move[2], move[3]))
                        q.append([move[2], move[3]])
                    else:
                        moves[board[i][j]].append(move)
        
        for l in range(rows):
            for k in range(cols):
                if board[l][k] == player and (l, k) not in seen:
                    moves[player].append(["s", l, k])
    
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
        mo = user.split(",")
        if len(mo) == 3:
            user_move = [mo[0], int(mo[1]), int(mo[2])]
        elif len(mo) == 4:
            user_move = [int(num) for num in mo]
        else:
            raise ValueError 
    except ValueError:
        user_move = None
        print("Invalid Input")

    if user_move in moves[current_player]:
        move = user_move

    while move is None:
        user = input(f"{user_move} was not a legal move, please try again. \n>")
        try:
            mo = user.split(",")
            if len(mo) == 3:
                user_move = [mo[0], int(mo[1]), int(mo[2])]
            elif len(mo) == 4:
                user_move = [int(num) for num in mo]
            else:
                raise ValueError 
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
    poss_moves = []
    for m in moves[current_player]:
        if len(m) == 4 and board[m[2]][m[3]] != ".":
            poss_moves.append(m)

    if poss_moves:
        move = random.choice(poss_moves)
    else:
        move = random.choice(moves[current_player])

    return move

def look_ahead_agent(pieces, state, moves) -> list[int]:
    poss_moves = {}
    score = float("-inf")
    opp_player = "W"
    current_player = state["current_player"]
    board = state["board"]
    if current_player == "W":
        opp_player = "B"
    
    for m in moves[current_player]:
        m_score = 0
        if len(m) == 4 and board[m[2]][m[3]] != ".":
            m_score += 10

        new_state = apply_action(state, m)
        new_moves = get_legal_moves(new_state, pieces)
        if len(m) == 4:
            for om in new_moves[opp_player]:
                if len(om) == 4 and om[2] == m[2] and om[3] == m[3]:
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

    result = get_result(
        board,
        state["previous_moves"],
        rules["max_repetitions"],
        state["turns"],
        rules["max_turns"],
        state["scoreboard"]
    )

    if result is not None:
        if result["winner"] == "W":
            return 1000
        elif result["winner"] == "B":
            return -1000
        return 0

    if depth == 0:
        return evaluate_board(board)

    scores = []    

    for m in moves[current_player]:
        new_state = apply_action(state, m)
        new_moves = get_legal_moves(new_state, pieces)

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
        new_moves = get_legal_moves(new_state, pieces)

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

    if board[move[2]][move[3]] == "X" or board[move[2]][move[3]] == "x":
        new_board[move[0]][move[1]] = "."
        new_board[move[2]][move[3]] = "#"

    else:
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

def get_result(board, previous_moves, max_repetitions, turns, max_turns, scoreboard):
    total_white = sum(row.count("W") for row in board)
    total_black = sum(row.count("B") for row in board)

    if scoreboard["W"] >= 2:
        return {
            "winner": "W",
            "reason": "win"
        }
    
    elif scoreboard["B"] >= 2:
        return {
            "winner": "B",
            "reason": "win"
        }

    elif total_white == 0:
        return {
            "winner": "B",
            "reason": "win"
        }

    elif total_black == 0:
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

    if player == "B":
        goal = "x"
    else:
        goal = "X"

    active_piece = state["active_piece"].copy()
    scoreboard = state["scoreboard"].copy()

    if len(move) == 3:
        active_piece[player] = [move[1], move[2]]

        return {
            "board": state["board"],
            "previous_moves": update_repetitions(state["previous_moves"], player, move),
            "current_player": "B" if player == "W" else "W",
            "turns": state["turns"] + 1,
            "active_piece": active_piece,
            "scoreboard": scoreboard
        }

    elif state["board"][move[2]][move[3]] == goal:
        active_piece[player] = None
        scoreboard[player] += 1

        return {
            "board": move_piece(state["board"], move),
            "previous_moves": update_repetitions(state["previous_moves"], player, move),
            "current_player": "B" if player == "W" else "W",
            "turns": state["turns"] + 1,
            "active_piece": active_piece,
            "scoreboard": scoreboard
        }

    else:
        active_piece[player] = [move[2], move[3]]

        return {
            "board": move_piece(state["board"], move),
            "previous_moves": update_repetitions(state["previous_moves"], player, move),
            "current_player": "B" if player == "W" else "W",
            "turns": state["turns"] + 1,
            "active_piece": active_piece,
            "scoreboard": state["scoreboard"]
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

def record_results(result, turns, file_path):
    with open(file_path, "r") as f:
        data = json.load(f)

    data[result["winner"]][result["reason"]] += 1
    data["total_games"] += 1
    data["total_turns"] += turns
    
    with open(file_path, "w") as f:
        json.dump(data, f)

def initialize_data(players):
    p_map = {
        1:"random",
        2:"greedy",
        3:"lookahead",
        4:"minimax",
        5:"human"
    }

    name = f"{p_map[players[0][0]]}{players[0][1]}_vs_{p_map[players[1][0]]}{players[1][1]}"

    init_data = {
        "W": {
            "win": 0,
            "repetition": 0
        },
        "B": {
            "win": 0,
            "repetition": 0
        },
        "tie": {
            "no moves": 0,
            "max turns exceeded": 0
        },
        "total_games": 0,
        "total_turns": 0
    }

    folder_path = f"data/{name}"

    count = 2
    while os.path.exists(folder_path):
        folder_path = f"data/{name}_v{count}"
        count += 1

    file_path = f"{folder_path}/data.json"

    os.makedirs(folder_path, exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(init_data, f)
    
    return file_path

# Game Loop
def play_game(rules, players):
    board = []
    for i in range(-1, rules["rows"]+1):
        if i == -1:
            board.append(["X", " ", "X", " ", "X"])
        elif i == rules["rows"]:
            board.append(["x", " ", "x", " ", "x"])
        else:
            board.append(["."] * rules["cols"])

    previous_moves = {
        "W": [[], 0],
        "B": [[], 0]
    }

    active_piece = {
        "W": None,
        "B": None
    }

    scoreboard = {
        "W": 0,
        "B": 0
    }

    state = {
        "board": board,
        "current_player": "W",
        "previous_moves": previous_moves,
        "turns": 0,
        "active_piece": active_piece,
        "scoreboard": scoreboard

    }

    state["board"] = set_board(state["board"], rules["starting_positions"])
    if players[0][0] == 5 or players[1][0] == 5:
        display(state["board"])
    moves = get_legal_moves(state, rules["pieces"])
    result = get_result(state["board"], state["previous_moves"], rules["max_repetitions"], state["turns"], rules["max_turns"], state["scoreboard"])

    while result is None:
        if state["current_player"] == "W":
            if players[0][0] == 1:
                move = random_agent(moves, state["current_player"])
            elif players[0][0] == 2:
                move = greedy_agent(state["board"], moves, state["current_player"])
            elif players[0][0] == 3:
                move = look_ahead_agent(rules["pieces"], state, moves)
            elif players[0][0] == 4:
                move = minimax_agent(players[0][1], moves, state, rules)
            elif players[0][0] == 5:
                move = get_move(moves, state["current_player"])
        else:
            if players[1][0] == 1:
                move = random_agent(moves, state["current_player"])
            elif players[1][0] == 2:
                move = greedy_agent(state["board"], moves, state["current_player"])
            elif players[1][0] == 3:
                move = look_ahead_agent(rules["pieces"], state, moves)
            elif players[1][0] == 4:
                move = minimax_agent(players[1][1], moves, state, rules)
            elif players[1][0] == 5:
                move = get_move(moves, state["current_player"])

        state = apply_action(state, move)
        if players[0][0] == 5 or players[1][0] == 5:
            display(state["board"])
        moves = get_legal_moves(state, rules["pieces"])
        result = get_result(state["board"], state["previous_moves"], rules["max_repetitions"], state["turns"], rules["max_turns"], state["scoreboard"])

    display_win(result)

    return result, state["turns"]

print(f"1. random\n2. greedy\n3. look ahead\n4. minimax\n5. human")
p1 = ""
p2 = ""
games = ""
players = []

while p1 == "":
    p1 = input(f"\nSelect Player W\n>")
    try:
        p1 = int(p1)
    except ValueError:
        p1 = ""
    
    if p1 != "":
        if p1 < 1 or p1 > 5:
            p1 = ""

players.append([p1])

if p1 == 4:
    dep = ""
    while dep == "":
        dep = input(f"Enter Depth\n>")
        try:
            dep = int(dep)
        except ValueError:
            dep = ""
        
        if dep != "":
            if dep < 1:
                dep = ""

    players[0].append(dep)

else:
     players[0].append("")

while p2 == "":
    p2 = input(f"\nSelect Player B\n>")
    try:
        p2 = int(p2)
    except ValueError:
        p2 = ""
    
    if p2 != "":
        if p2 < 1 or p2 > 5:
            p2 = ""

players.append([p2])

if p2 == 4:
    dep = ""
    while dep == "":
        dep = input(f"Enter Depth\n>")
        try:
            dep = int(dep)
        except ValueError:
            dep = ""
        
        if dep != "":
            if dep < 1:
                dep = ""

    players[1].append(dep)

else:
     players[1].append("") 

while games == "":
    games = input(f"Enter Amount of Games\n>")
    try:
        games = int(games)
    except ValueError:
        games = ""
    
    if games != "":
        if games < 1:
            games = ""

file_path = initialize_data(players)

for _ in range(games):
    result, turns = play_game(rules, players)
    record_results(result, turns, file_path)