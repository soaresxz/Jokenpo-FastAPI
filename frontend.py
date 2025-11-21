import streamlit as st
import requests

# Configuração da página
st.set_page_config(page_title="Jokenpô Arena", page_icon="🎮")

# Endereço da sua API (garanta que o uvicorn esteja rodando)
API_URL = "http://127.0.0.1:8000"

st.title("🎮 Jokenpô vs CPU")
st.markdown("---")

# Inicializa variáveis de sessão (memória do navegador)
if 'player_id' not in st.session_state:
    st.session_state['player_id'] = None
if 'player_name' not in st.session_state:
    st.session_state['player_name'] = ""

# --- TELA 1: LOGIN / CADASTRO ---
if st.session_state['player_id'] is None:
    st.subheader("Quem vai jogar?")
    name_input = st.text_input("Digite seu nome:")
    
    if st.button("Entrar na Arena"):
        if name_input:
            try:
                # Faz a requisição POST /players
                response = requests.post(f"{API_URL}/players", json={"name": name_input})
                if response.status_code == 201:
                    data = response.json()
                    st.session_state['player_id'] = data['id']
                    st.session_state['player_name'] = data['name']
                    st.rerun() # Recarrega a página para ir pro jogo
                else:
                    st.error("Erro ao criar jogador.")
            except:
                st.error("A API parece estar desligada. Verifique o terminal do uvicorn.")
        else:
            st.warning("Por favor, digite um nome.")

# --- TELA 2: O JOGO ---
else:
    st.success(f"Logado como: **{st.session_state['player_name']}** (ID: {st.session_state['player_id']})")
    
    # Colunas para organizar o layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Faça sua jogada")
        move = st.selectbox("Escolha:", ["PEDRA", "PAPEL", "TESOURA"])
        
        if st.button("JOGAR AGORA!", type="primary"):
            try:
                payload = {
                    "player_id": st.session_state['player_id'],
                    "move": move
                }
                # Faz a requisição POST /jokenpo/play
                response = requests.post(f"{API_URL}/jokenpo/play", json=payload)
                
                if response.status_code == 200:
                    result_data = response.json()
                    
                    # Exibe o resultado com destaque
                    st.divider()
                    if result_data['result'] == "WIN":
                        st.balloons()
                        st.success(f"RESULTADO: {result_data['message']}")
                    elif result_data['result'] == "LOSE":
                        st.error(f"RESULTADO: {result_data['message']}")
                    else:
                        st.warning(f"RESULTADO: {result_data['message']}")
                        
                    st.info(f"Você: {result_data['player_move']} | CPU: {result_data['cpu_move']}")
                    
                else:
                    st.error(f"Erro na jogada: {response.text}")
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

    # --- TELA 3: PLACAR ---
    with col2:
        st.subheader("📊 Placar Geral")
        if st.button("Atualizar Placar"):
            try:
                res = requests.get(f"{API_URL}/jokenpo/scoreboard")
                if res.status_code == 200:
                    placar = res.json()
                    st.dataframe(placar)
                else:
                    st.write("Erro ao buscar placar")
            except:
                st.write("API Offline")

    if st.button("Sair / Trocar Jogador"):
        st.session_state['player_id'] = None
        st.rerun()