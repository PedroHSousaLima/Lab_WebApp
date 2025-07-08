import streamlit as st
import pandas as pd
from db_build import (
    criar_tabela_build,
    inicializar_build_para_personagem,
    obter_build,
    atualizar_build
)
from db import obter_personagens
from db_weapon import criar_tabela_weapons, obter_weapons

# === Configuração da Página ===
st.set_page_config(page_title="🔧 Build do Personagem", layout="wide")
st.title("🔧 Criação de Build")

# === Inicialização das Tabelas ===
criar_tabela_build()
criar_tabela_weapons()

# === Seleção do Personagem ===
personagens = obter_personagens()
personagem_escolhido = st.selectbox("Escolha um personagem:", personagens)

if personagem_escolhido:
    inicializar_build_para_personagem(personagem_escolhido)
    valores = obter_build(personagem_escolhido)

    if valores:
        # === Formulário para Alteração da Build ===
        col1, col2, col3, col4 = st.columns(4)
        with st.form("form_build"):
            with col1:
                vigor = st.number_input("Vigor", min_value=0, max_value=99, value=valores[0])
                mind = st.number_input("Mind", min_value=0, max_value=99, value=valores[1])
            with col2:
                endurance = st.number_input("Endurance", min_value=0, max_value=99, value=valores[2])
                strength = st.number_input("Strength", min_value=0, max_value=99, value=valores[3])
            with col3:
                dexterity = st.number_input("Dexterity", min_value=0, max_value=99, value=valores[4])
                intelligence = st.number_input("Intelligence", min_value=0, max_value=99, value=valores[5])
            with col4:
                faith = st.number_input("Faith", min_value=0, max_value=99, value=valores[6])
                arcane = st.number_input("Arcane", min_value=0, max_value=99, value=valores[7])

            submitted = st.form_submit_button("Salvar Build")
            if submitted:
                atualizar_build(personagem_escolhido, {
                    "vigor": vigor,
                    "mind": mind,
                    "endurance": endurance,
                    "strength": strength,
                    "dexterity": dexterity,
                    "intelligence": intelligence,
                    "faith": faith,
                    "arcane": arcane,
                })
                st.success("Build salva com sucesso!")

        # === Exibição da Build Atual ===
        st.subheader("📊 Status Atual da Build")
        build_df = pd.DataFrame([{
            "Personagem": personagem_escolhido,
            "Vigor": vigor,
            "Mind": mind,
            "Endurance": endurance,
            "Strength": strength,
            "Dexterity": dexterity,
            "Intelligence": intelligence,
            "Faith": faith,
            "Arcane": arcane,
        }])
        st.dataframe(build_df, use_container_width=True)

        # === Exibição das Armas Disponíveis ===
        st.subheader("🗡️ Base de Armas Disponíveis")
        df_weapons = obter_weapons()
        st.dataframe(
            df_weapons[["name", "type", "str", "dex", "int", "fai", "arc"]],
            use_container_width=True
        )
