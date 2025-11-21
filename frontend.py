import streamlit as st
import requests
import time

# Configuração da página
st.set_page_config(
    page_title="Jokenpô Arena", 
    page_icon="🎮",
    layout="wide"
)

# Endereço da API
API_URL = "http://127.0.0.1:8000"

# Estilos customizados
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 Jokenpô Arena")
st.markdown("**Pedra, Papel e Tesoura** - Desafie a CPU!")
st.markdown("---")

# Inicializa variáveis de sessão
if 'player_id' not in st.session_state:
    st.session_state['player_id'] = None
if 'player_name' not in st.session_state:
    st.session_state['player_name'] = ""

# ========== TELA 1: LOGIN / CADASTRO ==========
if st.session_state['player_id'] is None:
    col1, col2, col3 = st.columns([1,2,1])
    
    with col2:
        st.subheader("👤 Quem vai jogar?")
        name_input = st.text_input("Digite seu nome:", max_chars=30)
        
        if st.button("🚀 Entrar na Arena", use_container_width=True, type="primary"):
            if name_input and name_input.strip():
                try:
                    response = requests.post(
                        f"{API_URL}/players", 
                        json={"name": name_input.strip()}
                    )
                    if response.status_code == 201:
                        data = response.json()
                        st.session_state['player_id'] = data['id']
                        st.session_state['player_name'] = data['name']
                        st.success(f"✅ Bem-vindo, {data['name']}!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Erro ao criar jogador: {response.text}")
                except Exception as e:
                    st.error("⚠️ A API parece estar desligada. Execute: `uvicorn main:app --reload`")
                    st.code("uvicorn main:app --reload", language="bash")
            else:
                st.warning("⚠️ Por favor, digite um nome válido.")

# ========== TELA 2: O JOGO ==========
else:
    st.success(f"👤 Jogador: **{st.session_state['player_name']}** (ID: {st.session_state['player_id']})")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Faça sua jogada")
        
        # Interface com botões grandes e emojis
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("🪨\n\nPEDRA", use_container_width=True, key="btn_pedra"):
                st.session_state['selected_move'] = "PEDRA"
        
        with col_b:
            if st.button("📄\n\nPAPEL", use_container_width=True, key="btn_papel"):
                st.session_state['selected_move'] = "PAPEL"
        
        with col_c:
            if st.button("✂️\n\nTESOURA", use_container_width=True, key="btn_tesoura"):
                st.session_state['selected_move'] = "TESOURA"
        
        # Mostra jogada selecionada e botão de confirmação
        if 'selected_move' in st.session_state:
            st.info(f"✋ Jogada selecionada: **{st.session_state['selected_move']}**")
            
            if st.button("⚡ JOGAR AGORA!", type="primary", use_container_width=True):
                try:
                    payload = {
                        "player_id": st.session_state['player_id'],
                        "move": st.session_state['selected_move']
                    }
                    response = requests.post(f"{API_URL}/jokenpo/play", json=payload)
                    
                    if response.status_code == 200:
                        result_data = response.json()
                        
                        st.markdown("---")
                        
                        # Resultado visual com cores
                        if result_data['result'] == "WIN":
                            st.balloons()
                            st.success(f"🎉 {result_data['message']}")
                        elif result_data['result'] == "LOSE":
                            st.error(f"😢 {result_data['message']}")
                        else:
                            st.warning(f"🤝 {result_data['message']}")
                        
                        # Mostra as jogadas lado a lado
                        col_res1, col_res2 = st.columns(2)
                        with col_res1:
                            emoji_map = {"PEDRA": "🪨", "PAPEL": "📄", "TESOURA": "✂️"}
                            st.metric(
                                "Você jogou", 
                                f"{emoji_map[result_data['player_move']]} {result_data['player_move']}"
                            )
                        with col_res2:
                            st.metric(
                                "CPU jogou", 
                                f"{emoji_map[result_data['cpu_move']]} {result_data['cpu_move']}"
                            )
                        
                        # Limpa seleção
                        del st.session_state['selected_move']
                    else:
                        st.error(f"❌ Erro na jogada: {response.text}")
                except Exception as e:
                    st.error(f"❌ Erro de conexão: {e}")
    
    with col2:
        st.subheader("📊 Suas Estatísticas")
        try:
            response = requests.get(f"{API_URL}/jokenpo/history/{st.session_state['player_id']}")
            if response.status_code == 200:
                history = response.json()
                wins = len([h for h in history if h['result'] == 'WIN'])
                losses = len([h for h in history if h['result'] == 'LOSE'])
                draws = len([h for h in history if h['result'] == 'DRAW'])
                total = wins + losses + draws
                
                st.metric("🏆 Vitórias", wins)
                st.metric("💔 Derrotas", losses)
                st.metric("🤝 Empates", draws)
                st.metric("🎮 Total de Jogos", total)
                
                # Taxa de vitória
                if total > 0:
                    win_rate = (wins / total) * 100
                    st.metric("📈 Taxa de Vitória", f"{win_rate:.1f}%")
                    
        except:
            st.error("❌ Erro ao carregar estatísticas")
        
        st.markdown("---")
        
        # Histórico recente
        st.subheader("📜 Últimas Jogadas")
        try:
            response = requests.get(f"{API_URL}/jokenpo/history/{st.session_state['player_id']}")
            if response.status_code == 200:
                history = response.json()
                recent = history[-5:][::-1]  # Últimas 5, ordem reversa
                
                if recent:
                    for match in recent:
                        result_emoji = "🏆" if match['result'] == "WIN" else "💔" if match['result'] == "LOSE" else "🤝"
                        st.text(f"{result_emoji} {match['player_move']} vs {match['cpu_move']}")
                else:
                    st.info("Nenhuma jogada ainda")
        except:
            pass
        
        st.markdown("---")
        if st.button("🚪 Sair / Trocar Jogador", use_container_width=True):
            st.session_state['player_id'] = None
            st.session_state['player_name'] = ""
            if 'selected_move' in st.session_state:
                del st.session_state['selected_move']
            st.rerun()

# ========== SIDEBAR: PLACAR GERAL ==========
with st.sidebar:
    st.header("🏆 Placar Geral")
    
    if st.button("🔄 Atualizar Placar", use_container_width=True):
        st.rerun()
    
    try:
        response = requests.get(f"{API_URL}/jokenpo/scoreboard")
        if response.status_code == 200:
            scoreboard = response.json()
            
            if scoreboard:
                st.markdown("---")
                for idx, player in enumerate(scoreboard[:10], 1):
                    # Medalhas para os 3 primeiros
                    if idx == 1:
                        medal = "🥇"
                    elif idx == 2:
                        medal = "🥈"
                    elif idx == 3:
                        medal = "🥉"
                    else:
                        medal = f"{idx}º"
                    
                    # Destaca o jogador atual
                    if st.session_state['player_id'] and player['player_id'] == st.session_state['player_id']:
                        st.success(f"**{medal} {player['name']} (VOCÊ)**")
                    else:
                        st.write(f"**{medal} {player['name']}**")
                    
                    # Estatísticas
                    st.write(f"✅ {player['wins']} | ❌ {player['losses']} | 🤝 {player['draws']}")
                    st.caption(f"Total: {player['total_games']} jogos")
                    st.markdown("---")
            else:
                st.info("📭 Nenhum jogo registrado ainda!")
    except:
        st.error("❌ Erro ao carregar placar")
    
    st.markdown("---")
    st.caption("💾 Dados salvos em arquivos JSON")
    st.caption("v2.0.0")
