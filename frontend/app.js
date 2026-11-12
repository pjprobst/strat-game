document.addEventListener('DOMContentLoaded', () => {
    setOpp();
});

let currentGame = null;
let selectedSquare = null;

async function setOpp() {
    const form = document.getElementById('game-settings');
    const oppRadios = document.querySelectorAll('input[name="opp"]');
    const minimaxWrapper = document.getElementById('minimaxWrapper');
    const depthInput = document.getElementById('depth');
    const depthValue = document.getElementById('depthValue');

    oppRadios.forEach((radio) => {
        radio.addEventListener('change', (event) => {
          const isMinimax = event.target.value === 'minimax';
          minimaxWrapper.classList.toggle('hidden', !isMinimax);
          depthInput.disabled = !isMinimax;
        });
    });

    depthInput.addEventListener('input', () => {
        depthValue.textContent = depthInput.value;
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(form);

        const color = formData.get('color');
        const opponent = formData.get('opp');
        const depth = formData.get('depth');

        const payload = {
            opp: opponent,
            depth: depth,
            color: color
        }

        try {
            const response = await fetch("/game", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            console.log("Server response:", result);

            const setupScreen = document.getElementById("setup-screen");
            const gameScreen = document.getElementById("game-screen");

            setupScreen.classList.add("hidden");
            gameScreen.classList.remove("hidden")

            renderGame(result);
        }
            catch (error) {
                console.error("Failed to send data:", error);
            }
    });
}

function renderGame(game) {
    const classByValue = {
        "W": "white-piece",
        "B": "black-piece",
        "X": "white-goal",
        "x": "black-goal",
        "#": "completed-goal",
        " ": "blocked",
        ".": "empty"
    };

    currentGame = game;

    const board = document.getElementById("board");
    const status = document.getElementById("game-status");

    board.innerHTML = "";

    if (game.result) {
        status.textContent =
            `Winner: ${game.result.winner} (${game.result.reason})`;
    } else {
        status.textContent =
            `Current player: ${game.state.current_player}`;
    }

    const opponent =
        game.state.current_player === "W" ? "B" : "W";
    const activePiece =
        game.state.active_piece[game.state.current_player];
    const opponentActivePiece =
        game.state.active_piece[opponent];

    game.state.board.forEach((row, rowIndex) => {
        row.forEach((value, colIndex) => {
            const square = document.createElement("div");

            square.classList.add(
                "square",
                classByValue[value]
            );

            square.dataset.row = rowIndex;
            square.dataset.col = colIndex;

            const isSelected =
                selectedSquare &&
                selectedSquare.row === rowIndex &&
                selectedSquare.col === colIndex;

            const isActivePiece =
                activePiece &&
                activePiece[0] === rowIndex &&
                activePiece[1] === colIndex;

            const isOpponentActivePiece =
                opponentActivePiece &&
                opponentActivePiece[0] === rowIndex &&
                opponentActivePiece[1] === colIndex;

            const isMoveOrigin = game.legal_moves.some(
                move =>
                    move.length === 4 &&
                    move[0] === rowIndex &&
                    move[1] === colIndex
            );

            const isLegalDestination =
                selectedSquare &&
                game.legal_moves.some(
                    move =>
                        move.length === 4 &&
                        move[0] === selectedSquare.row &&
                        move[1] === selectedSquare.col &&
                        move[2] === rowIndex &&
                        move[3] === colIndex
                );

            const isSwitchOption = game.legal_moves.some(
                move =>
                    move.length === 3 &&
                    move[0] === "s" &&
                    move[1] === rowIndex &&
                    move[2] === colIndex
            );

            const isCaptureDestination =
                isLegalDestination &&
                (value === "W" || value === "B");

            if (isActivePiece) {
                square.classList.add("active-piece");
            }

            if (isOpponentActivePiece) {
                square.classList.add("opponent-active-piece");
            }

            if (isSelected) {
                square.classList.add("selected");
            }

            if (isLegalDestination && !isCaptureDestination) {
                square.classList.add("legal-destination");
            }

            if (isCaptureDestination) {
                square.classList.add("legal-capture");
            }

            if (isMoveOrigin) {
                square.classList.add("network-piece");
            }

            if (isSwitchOption) {
                square.classList.add("switch-option");
            }

            if (isMoveOrigin || isSwitchOption) {
                square.classList.add("selectable");
            }

            if (!game.result) {
                square.addEventListener("click", () => {
                    handleSquareClick(rowIndex, colIndex);
                });
            }

            board.appendChild(square);
        });
    });
}

function handleSquareClick(row, col) {
    const switchMove = currentGame.legal_moves.find(
        move =>
            move.length === 3 &&
            move[0] === "s" &&
            move[1] === row &&
            move[2] === col
    );

    if (switchMove) {
        selectedSquare = null;
        sendMove(switchMove);
        return;
    }

    const movesFromSquare = currentGame.legal_moves.filter(
        move =>
            move.length === 4 &&
            move[0] === row &&
            move[1] === col
    );

    if (!selectedSquare) {
        if (movesFromSquare.length > 0) {
            selectedSquare = { row, col };
            renderGame(currentGame);
        }

        return;
    }

    const move = currentGame.legal_moves.find(
        candidate =>
            candidate.length === 4 &&
            candidate[0] === selectedSquare.row &&
            candidate[1] === selectedSquare.col &&
            candidate[2] === row &&
            candidate[3] === col
    );

    if (move) {
        sendMove(move);
    } else if (movesFromSquare.length > 0) {
        selectedSquare = { row, col };
        renderGame(currentGame);
    } else {
        selectedSquare = null;
        renderGame(currentGame);
    }
}

async function sendMove(move) {
    const response = await fetch("/game/move", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ move })
    });

    if (!response.ok) {
        throw new Error(`Move failed: ${response.status}`);
    }

    selectedSquare = null;
    const game = await response.json();
    renderGame(game);
}
