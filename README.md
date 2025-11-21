

# Jokenpô vs CPU <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Robot.png" alt="Robot" width="25" height="25" />

Este projeto é uma aplicação completa (Fullstack) desenvolvida para a disciplina de Desenvolvimento Rápido de Aplicações em Python. O sistema implementa o jogo "Pedra, Papel e Tesoura" com uma API RESTful no backend e uma Interface Web interativa no frontend.

## Tecnologias Utilizadas

* Linguagem: Python 3
* Backend (API): FastAPI + Uvicorn
* Frontend (Interface): Streamlit + Requests
* Persistência: Em memória (estruturas de dados Python)

## Instalação

Para rodar o projeto, você precisará instalar as bibliotecas listadas. Abra o terminal na pasta do projeto e execute:
```bash
pip install fastapi uvicorn streamlit requests
```
## Como Rodar o Projeto

Como o projeto possui uma arquitetura Cliente-Servidor, é necessário abrir dois terminais diferentes:

### Passo 1: Iniciar a API (Backend)
No primeiro terminal, execute o servidor:
```bash
python -m uvicorn main:app --reload
```
(O servidor rodará em: http://127.0.0.1:8000)

### Passo 2: Iniciar a Interface (Frontend)
Abra um segundo terminal (na mesma pasta) e execute:
```bash
python -m streamlit run frontend.py
```
(O navegador abrirá automaticamente em: http://localhost:8501)

---

## Documentação da API

Além da interface gráfica, a API pode ser testada diretamente via Swagger UI ou ferramentas como Postman.

Link da Documentação Interativa: http://127.0.0.1:8000/docs

### Principais Endpoints

1. Criar Jogador
POST /players
Body:
{
  "name": "Seu Nome"
}

2. Jogar (Jokenpô)
POST /jokenpo/play
Body:
{
  "player_id": 1,
  "move": "PEDRA"
}
(Opções válidas: "PEDRA", "PAPEL", "TESOURA")

3. Ver Histórico
GET /jokenpo/history/{player_id}

4. Ver Placar Geral
GET /jokenpo/scoreboard
