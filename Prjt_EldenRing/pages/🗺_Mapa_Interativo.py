import streamlit as st

# --- Início da Lógica de Controle de Acesso (ADICIONADO) ---
# Certifica-se que 'autenticado' está no session_state para evitar erros
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Se o usuário NÃO ESTIVER AUTENTICADO, exibe aviso e interrompe
if not st.session_state['autenticado']:
    st.warning("⚠️ Você precisa fazer login para acessar esta página.")
    st.info("Por favor, retorne à página inicial para fazer login.")
    st.stop() # Interrompe a execução do resto do script da página
# --- Fim da Lógica de Controle de Acesso ---

st.set_page_config(page_title="Mapa Interativo", layout="wide")

st.title("🗺️ Mapa Interativo - The Lands Between")
st.markdown("""
Explore o mapa interativo completo de Elden Ring com todos os marcadores, locais e segredos.
O mapa é fornecido pelo site [MapGenie.io](https://mapgenie.io/elden-ring/maps/the-lands-between).

Este mapa serve para te auxiliar em sua jornada, o mesmo contém uma versão pagar com mais possibilidades de uso.
""")

st.markdown("---")

# Incorpora o mapa do MapGenie
map_url = "https://mapgenie.io/elden-ring/maps/the-lands-between"
st.components.v1.iframe(map_url, height=800, scrolling=True)
