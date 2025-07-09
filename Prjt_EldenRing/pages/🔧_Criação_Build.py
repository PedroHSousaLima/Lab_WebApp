import streamlit as st
import pandas as pd
import base64
from pathlib import Path

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

from db_build import (
    criar_tabela_build,
    inicializar_build_para_personagem,
    obter_build,
    atualizar_build
)
from db import obter_personagens
from db_weapon import criar_tabela_weapons, obter_weapons
from db_build_weapon import criar_tabela_build_weapon, salvar_build_weapon, carregar_build_weapon

# === Fundo ===
# === Configuração da Página ===
st.set_page_config(page_title="Elden Ring - Home", layout="wide")

# === Função para definir imagem de fundo com escurecimento ===
caminho_atual = Path(__file__).resolve().parent
def set_bg_from_local(relative_path):
    image_file = caminho_atual / relative_path
    if image_file.exists():
        with open(image_file, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()
        css = f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.9)),
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

# === Aplica fundo ===
set_bg_from_local("../assets/build_background.jpg")


# === Configuração da Página ===
st.set_page_config(page_title="🔧 Build do Personagem", layout="wide")
st.title("🔧 Criação de Build")
st.text('''
🎮 Crie, Copie e Evolua: Sua Jornada Começa Aqui!

Seja bem-vindo à nossa forja de ideias, onde cada build é uma nova lenda forjada nas chamas do Elden Ring. Aqui você vai encontrar o espaço ideal para criar personagens únicos, testar combinações épicas e até mesmo reproduzir as builds mais insanas da comunidade e dos tutoriais do YouTube.

Não importa se você é fã de espadões colossais, magias sombrias ou builds ousadas que desafiam a lógica: o importante é explorar ao máximo as possibilidades e curtir cada batalha com o seu estilo.

💡 Se inspire. 🔧 Experimente. ⚔️ Enfrente os deuses.

Essa é a sua jornada. Faça dela uma história digna de ser contada.

⚠ Primeiro registre-se como Jorgador e Personagem na página 🎮 Gestão Personagem.
        ''')

# === Inicialização das Tabelas ===
criar_tabela_build()
criar_tabela_weapons()
criar_tabela_build_weapon()

# === Seleção do Personagem ===
personagens = obter_personagens()
personagem_escolhido = st.selectbox("Escolha um personagem:", personagens)

if personagem_escolhido:
    inicializar_build_para_personagem(personagem_escolhido)
    valores = obter_build(personagem_escolhido)
    df_carregada = carregar_build_weapon(personagem_escolhido)

    if valores:
        col1, col2, col3, col4 = st.columns(4)
        with st.form("form_build"):
            with col1:
                vigor = st.number_input("Vigor", 0, 99, valores[0])
                mind = st.number_input("Mind", 0, 99, valores[1])
            with col2:
                endurance = st.number_input("Endurance", 0, 99, valores[2])
                strength = st.number_input("Strength", 0, 99, valores[3])
            with col3:
                dexterity = st.number_input("Dexterity", 0, 99, valores[4])
                intelligence = st.number_input("Intelligence", 0, 99, valores[5])
            with col4:
                faith = st.number_input("Faith", 0, 99, valores[6])
                arcane = st.number_input("Arcane", 0, 99, valores[7])

            if st.form_submit_button("Salvar Build"):
                atualizar_build(personagem_escolhido, {
                    "vigor": vigor, "mind": mind, "endurance": endurance,
                    "strength": strength, "dexterity": dexterity,
                    "intelligence": intelligence, "faith": faith, "arcane": arcane
                })
                st.success("Build salva com sucesso!")

        st.subheader("📊 Status Atual da Build")
        build_df = pd.DataFrame([{ "Personagem": personagem_escolhido,
            "Vigor": vigor, "Mind": mind, "Endurance": endurance,
            "Strength": strength, "Dexterity": dexterity,
            "Intelligence": intelligence, "Faith": faith, "Arcane": arcane
        }])
        st.dataframe(build_df, use_container_width=True)

        df_weapons = obter_weapons()

        st.subheader("🎯 Escolha suas Armas/Slots")
        weapon_options = df_weapons["name"].dropna().unique().tolist()

        armas_pre_selecionadas = [""] * 10
        if not df_carregada.empty:
            try:
                nomes_slots = df_carregada.drop_duplicates(subset=["slot"]).sort_values("slot")
                for i in range(1, 11):
                    item = nomes_slots[nomes_slots["slot"] == i]["item"]
                    armas_pre_selecionadas[i - 1] = item.values[0] if not item.empty else ""
            except:
                pass

        cols = st.columns(5)
        armas_escolhidas = []
        for i in range(10):
            col = cols[i % 5]
            arma = col.selectbox(
                f"Slot {i+1}",
                [""] + weapon_options,
                index=(weapon_options.index(armas_pre_selecionadas[i]) + 1) if armas_pre_selecionadas[i] in weapon_options else 0,
                key=f"slot{i+1}"
            )
            armas_escolhidas.append(arma)

        colunas_status = ["vigor", "mind", "vitality", "strength", "dexterity", "intelligence", "faith", "arcane"]
        nomes_status = [col.capitalize() for col in colunas_status]

        dfs_arma = []
        for nome in armas_escolhidas:
            if nome:
                linha = df_weapons[df_weapons["name"] == nome][colunas_status]
                dfs_arma.append(linha.iloc[0].tolist())
            else:
                dfs_arma.append([0] * len(colunas_status))

        df_resultado = pd.DataFrame(dfs_arma, columns=colunas_status).T
        df_resultado.columns = [f"Slot {i+1}" for i in range(len(armas_escolhidas))]
        df_resultado.insert(0, "Status", nomes_status)
        df_resultado.iloc[:, 1:] = df_resultado.iloc[:, 1:].fillna(0)
        df_resultado["Valor Máximo"] = df_resultado.iloc[:, 1:].max(axis=1, numeric_only=True)

        for col in df_resultado.columns[1:]:
            df_resultado[col] = pd.to_numeric(df_resultado[col], errors="coerce").round(0).astype("Int64")

        cols_ordenadas = ["Status", "Valor Máximo"] + [col for col in df_resultado.columns if col not in ["Status", "Valor Máximo"]]
        df_resultado = df_resultado[cols_ordenadas]

        st.subheader("📋 Comparativo dos Requisitos das Armas Selecionadas")
        nomes_visuais = [nome if nome else f"Slot {i+1}" for i, nome in enumerate(armas_escolhidas)]

        df_exibicao = df_resultado.copy()
        df_exibicao.columns = ["Status", "Valor Máximo"] + nomes_visuais

        st.dataframe(
            df_exibicao.style.background_gradient(
                axis=1,
                cmap="RdYlGn_r",
                subset=nomes_visuais
            ),
            use_container_width=True
        )

        if st.button("💾 Salvar Armas Selecionadas"):
            registros = []
            for i, arma in enumerate(armas_escolhidas):
                slot_num = i + 1
                for idx, row in df_resultado.iterrows():
                    status = row["Status"]
                    valor = int(row.get(f"Slot {slot_num}", 0) or 0)
                    registros.append({
                        "personagem": personagem_escolhido,
                        "Status": status,
                        "Slot": slot_num,
                        "Item": arma or f"Slot {slot_num}",
                        "Valor": valor
                    })
            df_vertical = pd.DataFrame(registros)
            salvar_build_weapon(personagem_escolhido, df_vertical)
            st.success("Armas atribuídas à build com sucesso!")

        st.subheader("🗁️ Base de Armas Disponíveis")
        tipos_disponiveis = df_weapons["type"].dropna().unique().tolist()
        tipo_selecionado = st.selectbox("Filtrar por tipo de arma:", ["Todos"] + tipos_disponiveis)

        if tipo_selecionado != "Todos":
            df_filtrado = df_weapons[df_weapons["type"] == tipo_selecionado]
        else:
            df_filtrado = df_weapons

        st.dataframe(
            df_filtrado[["name", "type", "vigor", "mind", "vitality", "strength", "dexterity", "intelligence", "faith", "arcane"]],
            use_container_width=True
        )
