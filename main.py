from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import Optional
import random
import json
import os
from enum import Enum
from datetime import datetime

app = FastAPI(
    title="API Jokenpô",
    description="Projeto final - Jogo Pedra, Papel e Tesoura contra a CPU",
    version="2.0.0"
)

# --- Configuração de Arquivos ---
DATA_DIR = "data"
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

# Cria pasta data se não existir
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Funções de Persistência ---
def load_json(filename, default=None):
    """Carrega dados de um arquivo JSON"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default if default is not None else {}
    return default if default is not None else {}

def save_json(filename, data):
    """Salva dados em um arquivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- Carrega dados na inicialização ---
db_players = load_json(PLAYERS_FILE, {})
db_history = load_json(HISTORY_FILE, [])

# Calcula o próximo ID
current_id = max([int(k) for k in db_players.keys()], default=0)

# --- Modelos de Dados ---
class JokenpoMove(str, Enum):
    PEDRA = "PEDRA"
    PAPEL = "PAPEL"
    TESOURA = "TESOURA"

class PlayerCreate(BaseModel):
    name: str
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome não pode estar vazio')
        return v.strip()

class PlayRequest(BaseModel):
    player_id: int
    move: JokenpoMove

class PlayResponse(BaseModel):
    player_id: int
    player_move: str
    cpu_move: str
    result: str
    message: str

# --- Lógica do Jogo ---
def calculate_winner(player_move: str, cpu_move: str):
    """Calcula o vencedor da partida"""
    if player_move == cpu_move:
        return "DRAW", "Empate! Ambos escolheram a mesma opção."
    
    wins = {
        "PEDRA": "TESOURA",
        "TESOURA": "PAPEL",
        "PAPEL": "PEDRA"
    }
    
    if wins[player_move] == cpu_move:
        return "WIN", f"{player_move} ganha de {cpu_move}. Você venceu!"
    else:
        return "LOSE", f"{cpu_move} ganha de {player_move}. A CPU venceu!"

# --- Endpoints ---

@app.get("/")
def home():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Bem-vindo ao Jokenpô API",
        "version": "2.0.0",
        "features": ["Jogador vs CPU", "Persistência em arquivos JSON"],
        "docs": "/docs"
    }

@app.post("/players", status_code=201)
def create_player(player: PlayerCreate):
    """Cria um novo jogador no sistema"""
    global current_id
    current_id += 1
    player_id_str = str(current_id)
    
    new_player = {
        "id": current_id,
        "name": player.name,
        "created_at": datetime.now().isoformat()
    }
    
    db_players[player_id_str] = new_player
    save_json(PLAYERS_FILE, db_players)
    
    return new_player

@app.post("/jokenpo/play", response_model=PlayResponse)
def play_jokenpo(jogada: PlayRequest):
    """Realiza uma jogada contra a CPU"""
    player_id_str = str(jogada.player_id)
    
    if player_id_str not in db_players:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    # CPU escolhe aleatoriamente
    options = ["PEDRA", "PAPEL", "TESOURA"]
    cpu_move = random.choice(options)
    
    # Calcula resultado
    result, message = calculate_winner(jogada.move.value, cpu_move)
    
    # Salva no histórico
    match_record = {
        "player_id": jogada.player_id,
        "player_name": db_players[player_id_str]["name"],
        "player_move": jogada.move.value,
        "cpu_move": cpu_move,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
    db_history.append(match_record)
    save_json(HISTORY_FILE, db_history)
    
    return {
        "player_id": jogada.player_id,
        "player_move": jogada.move.value,
        "cpu_move": cpu_move,
        "result": result,
        "message": message
    }

@app.get("/jokenpo/history/{player_id}")
def get_history(player_id: int):
    """Retorna o histórico de partidas de um jogador"""
    player_id_str = str(player_id)
    
    if player_id_str not in db_players:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    player_history = [play for play in db_history if play["player_id"] == player_id]
    return player_history

@app.get("/jokenpo/scoreboard")
def get_scoreboard():
    """Retorna o placar geral com estatísticas de todos os jogadores"""
    scoreboard = []
    
    for p_id, p_data in db_players.items():
        plays = [h for h in db_history if h["player_id"] == int(p_id)]
        
        wins = len([h for h in plays if h["result"] == "WIN"])
        losses = len([h for h in plays if h["result"] == "LOSE"])
        draws = len([h for h in plays if h["result"] == "DRAW"])
        
        scoreboard.append({
            "player_id": int(p_id),
            "name": p_data["name"],
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "total_games": wins + losses + draws
        })
    
    # Ordena por vitórias (decrescente)
    scoreboard.sort(key=lambda x: x["wins"], reverse=True)
    return scoreboard

@app.get("/players")
def list_players():
    """Lista todos os jogadores cadastrados"""
    return list(db_players.values())

@app.delete("/players/{player_id}")
def delete_player(player_id: int):
    """Remove um jogador do sistema"""
    player_id_str = str(player_id)
    
    if player_id_str not in db_players:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    
    player_name = db_players[player_id_str]["name"]
    del db_players[player_id_str]
    save_json(PLAYERS_FILE, db_players)
    
    return {"message": f"Jogador {player_name} removido com sucesso"}
