from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import game as engine

current_game = None

app = FastAPI()

@app.get("/message")
async def root():
    return {"message": "Hello World"}

class Settings(BaseModel):
    opp: str
    depth: int | None = None
    color: str

@app.post("/game")
async def start_game(settings: Settings):
    global current_game

    current_game = {
        "state": engine.create_initial_state(engine.rules),
        "opp": settings.opp,
        "depth": settings.depth,
        "color": settings.color,
        "result": None
    }

    if settings.color == "B" and settings.opp != "none":
        state = current_game["state"]
        legal_moves = engine.get_legal_moves(state, engine.rules["pieces"])
        
        if current_game["opp"] == "random":
            move = engine.random_agent(legal_moves, state["current_player"])
        elif current_game["opp"] == "greedy":
            move = engine.greedy_agent(state["board"], legal_moves, state["current_player"])
        elif current_game["opp"] == "look-ahead":
            move = engine.look_ahead_agent(engine.rules["pieces"], state, legal_moves)
        elif current_game["opp"] == "minimax":
            move = engine.minimax_agent(current_game["depth"], legal_moves, state, engine.rules)
        
        state = engine.apply_action(state, move)

        current_game["state"] = state

    return current_game

@app.get("/game")
async def get_game():
    if current_game is None:
        raise HTTPException(status_code=404, detail="No game started")
    
    return current_game

class MoveRequest(BaseModel):
    move: list

@app.post("/game/move")
async def make_move(request: MoveRequest):
    global current_game
    if current_game is None:
        raise HTTPException(status_code=404, detail="No game started")

    state = current_game["state"]
    result = engine.get_result(state["board"], state["previous_moves"], engine.rules["max_repetitions"], state["turns"], engine.rules["max_turns"], state["scoreboard"])
    
    if result is not None:
        current_game["result"] = result
        return current_game

    legal_moves = engine.get_legal_moves(state, engine.rules["pieces"])

    if request.move not in legal_moves[state["current_player"]]:
        raise HTTPException(status_code=400, detail="Illegal move")

    state = engine.apply_action(state, request.move)
    result = engine.get_result(state["board"], state["previous_moves"], engine.rules["max_repetitions"], state["turns"], engine.rules["max_turns"], state["scoreboard"])

    if result is not None:
        current_game["state"] = state
        current_game["result"] = result
        return current_game

    legal_moves = engine.get_legal_moves(state, engine.rules["pieces"])
        
    if current_game["opp"] == "random":
        move = engine.random_agent(legal_moves, state["current_player"])
    elif current_game["opp"] == "greedy":
        move = engine.greedy_agent(state["board"], legal_moves, state["current_player"])
    elif current_game["opp"] == "look-ahead":
        move = engine.look_ahead_agent(engine.rules["pieces"], state, legal_moves)
    elif current_game["opp"] == "minimax":
        move = engine.minimax_agent(current_game["depth"], legal_moves, state, engine.rules)
    else:
        current_game["state"] = state
        return current_game
        
    state = engine.apply_action(state, move)

    current_game["state"] = state

    result = engine.get_result(state["board"], state["previous_moves"], engine.rules["max_repetitions"], state["turns"], engine.rules["max_turns"], state["scoreboard"])
    if result is not None:
        current_game["result"] = result

    return current_game
    
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")