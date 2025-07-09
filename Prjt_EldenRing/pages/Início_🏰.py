import streamlit as st
import base64
from pathlib import Path

# === Configuração da Página ===
st.set_page_config(page_title="Elden Ring - Home", layout="wide")

# === Função para aplicar imagem de fundo ===
def set_bg_from_local(relative_path):
    image_file = Path(__file__).parent / relative_path
    if image_file.exists():
        with open(image_file, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()
        css = f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
                url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Imagem de fundo não encontrada: {image_file}")


# === Aplicar imagem de fundo ===
set_bg_from_local("../assets/home_background.jpg")

# === Conteúdo da Home ===
st.title("🏰 Elden Ring - Dashboard de Progresso")

st.markdown("""
Bem-vindo ao seu painel de acompanhamento da jornada em **Elden Ring**!

Este espaço foi criado para tornar sua jornada pelas Terras Intermédias mais estratégica, organizada e épica. Aqui você encontrará tudo o que precisa para dominar o game do seu jeito, seja criando builds únicas, registrando sua progressão ou explorando cada chefe escondido no mapa.

### 🎮 Gestão do Personagem
Cadastre seus jogadores e personagens. Organize suas criações e mantenha o controle de quem está em cada jornada. Ideal para quem joga com múltiplas builds ou compartilha o jogo com amigos.

### 👹 Boss List
Uma enciclopédia de chefes! Consulte informações detalhadas sobre cada inimigo, suas localizações, atributos e estratégias. Nunca mais fique perdido se perguntando quem falta derrotar.

### 🔧 Criação de Build
Monte a build perfeita! Selecione atributos, armas, magias e equipamentos para criar combinações personalizadas ou inspiradas em tutoriais lendários. Teste teorias ou traga seu herói dos vídeos para a realidade.

### 🗺 Mapa Interativo
Explore o mundo com clareza. Descubra áreas secretas, mausoléus, locais de itens raros e muito mais. Ideal para exploradores que querem dominar cada centímetro das Terras Intermédias.

### 🧭 Jornada Player
Acompanhe seu progresso, veja o que já conquistou e compare com seus outros personagens. Aqui, você transforma sua gameplay em uma verdadeira saga registrada.

---

🛡️ **Prepare-se, Tarnished.** Este é o seu novo ponto de partida para explorar *Elden Ring* com profundidade, clareza e muita personalidade.
""")

# === Vídeos recomendados ===
st.subheader("📺 Vídeos Recomendados")

col1, col2 = st.columns(2)
with col1:
    st.video("https://www.youtube.com/watch?v=WofIuNn9Exc&ab_channel=LardosGames")
with col2:
    st.video("https://youtu.be/6v7TbpHGc8U")

