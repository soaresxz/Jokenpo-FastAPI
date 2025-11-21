from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import random
from enum import Enum

app = FastAPI(
    title="API Jokenpô",
    description="Projeto final de Análise e Desenvolvimento de Sistemas - Jogo contra a CPU",
    version="1.0.0"
)

# --- Modelos de Dados (Pydantic) ---
# Define como os dados devem chegar e sair da API

class JokenpoMove(str, Enum):
    PEDRA = "PEDRA"
    PAPEL = "PAPEL"
    TESOURA = "TESOURA"

class PlayerCreate(BaseModel):
    name: str

class PlayRequest(BaseModel):
    player_id: int
    move: JokenpoMove

class PlayResponse(BaseModel):
    player_id: int
    player_move: str
    cpu_move: str
    result: str
    message: str

# --- Persistência em Memória ---
# Dicionários e Listas para guardar os dados enquanto a API roda
db_players = {}  # Formato: {id: {"id": 1, "name": "Gabriel"}}
db_history = []  # Lista de todas as jogadas
current_id = 0   # Contador para gerar IDs

# --- Lógica do Jogo ---
def calculate_winner(player_move: str, cpu_move: str):
    if player_move == cpu_move:
        return "DRAW", "Empate! Ambos escolheram a mesma opção."
    
    wins = {
        "PEDRA": "TESOURA",   # Pedra ganha de Tesoura
        "TESOURA": "PAPEL",   # Tesoura ganha de Papel
        "PAPEL": "PEDRA"      # Papel ganha de Pedra
    }
    
    if wins[player_move] == cpu_move:
        return "WIN", f"{player_move} ganha de {cpu_move}. Você venceu!"
    else:
        return "LOSE", f"{cpu_move} ganha de {player_move}. A CPU venceu!"

# --- Endpoints ---

@app.get("/")
def home():
    return {"message": "Bem-vindo ao Jokenpô API. Acesse /docs para jogar."}

# 1. POST /players - Cria jogador
@app.post("/players", status_code=201)
def create_player(player: PlayerCreate):
    global current_id
    current_id += 1
    new_player = {"id": current_id, "name": player.name}
    db_players[current_id] = new_player
    return new_player

# 2. POST /jokenpo/play - Realiza a jogada
@app.post("/jokenpo/play", response_model=PlayResponse)
def play_jokenpo(jogada: PlayRequest):
    # Valida se jogador existe
    if jogada.player_id not in db_players:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    # Lógica da CPU
    options = ["PEDRA", "PAPEL", "TESOURA"]
    cpu_move = random.choice(options)
    
    # Calcula resultado
    result, message = calculate_winner(jogada.move.value, cpu_move)
    
    # Salva no histórico
    match_record = {
        "player_id": jogada.player_id,
        "player_name": db_players[jogada.player_id]["name"],
        "player_move": jogada.move.value,
        "cpu_move": cpu_move,
        "result": result
    }
    db_history.append(match_record)
    
    return {
        "player_id": jogada.player_id,
        "player_move": jogada.move.value,
        "cpu_move": cpu_move,
        "result": result,
        "message": message
    }

# 3. GET /jokenpo/history/{player_id} - Histórico do jogador
@app.get("/jokenpo/history/{player_id}")
def get_history(player_id: int):
    if player_id not in db_players:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    # Filtra a lista global pegando apenas as jogadas deste ID
    player_history = [play for play in db_history if play["player_id"] == player_id]
    return player_history

# 4. GET /jokenpo/scoreboard - Placar geral
@app.get("/jokenpo/scoreboard")
def get_scoreboard():
    scoreboard = []
    
    for p_id, p_data in db_players.items():
        # Filtra jogadas deste player
        plays = [h for h in db_history if h["player_id"] == p_id]
        
        wins = len([h for h in plays if h["result"] == "WIN"])
        losses = len([h for h in plays if h["result"] == "LOSE"])
        draws = len([h for h in plays if h["result"] == "DRAW"])
        
        scoreboard.append({
            "player_id": p_id,
            "name": p_data["name"],
            "wins": wins,
            "losses": losses,
            "draws": draws
        })
        
    return scoreboard