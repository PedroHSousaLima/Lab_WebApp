import os
import sys
import streamlit as st
import pandas as pd

# === Caminho absoluto para a pasta 'Dados' (onde está o db.py e o dados.db) ===
# Isso garante compatibilidade ao rodar de qualquer lugar
CAMINHO_ATUAL = os.path.dirname(__file__)
CAMINHO_DADOS = os.path.abspath(os.path.join(CAMINHO_ATUAL, "..", "Dados"))

# Adiciona a pasta Dados ao sys.path para importar db.py corretamente
if CAMINHO_DADOS not in sys.path:
    sys.path.append(CAMINHO_DADOS)

# === Importa funções do db.py ===
from db import (
    criar_tabela,
    inserir_jogador,
    listar_jogadores,
    atualizar_jogador,
    excluir_jogador
)

# === Garante que a tabela exista ===
criar_tabela()

st.title("🎮 Gerenciar Jogador e Personagem")

# === Formulário de Cadastro ===
with st.form("form_cadastro"):
    st.subheader("➕ Cadastrar novo jogador")
    nome_jogador = st.text_input("👤 Nome do Jogador")
    nome_personagem = st.text_input("🧝 Nome do Personagem")
    submitted = st.form_submit_button("Cadastrar")

    if submitted:
        if nome_jogador.strip() and nome_personagem.strip():
            inserir_jogador(nome_jogador.strip(), nome_personagem.strip())
            st.success("Cadastro realizado com sucesso!")
            st.rerun()
        else:
            st.warning("Preencha todos os campos.")

# === Interface de edição agrupada ===
with st.expander("🛠 Clique aqui para editar ou excluir um jogador"):
    dados = listar_jogadores()
    
    if not dados:
        st.info("Nenhum jogador cadastrado.")
    else:
        jogadores_dict = {f"{j[1]} - {j[2]}": j[0] for j in dados}  # Ex: "João - Guerreiro": id
        selecionado = st.selectbox("Selecione um jogador para editar:", list(jogadores_dict.keys()))

        if selecionado:
            id_jogador = jogadores_dict[selecionado]
            jogador = next(j for j in dados if j[0] == id_jogador)

            with st.form("form_edit_unico"):
                novo_nome = st.text_input("Nome do Jogador", value=jogador[1])
                novo_personagem = st.text_input("Nome do Personagem", value=jogador[2])

                col1, col2 = st.columns(2)
                with col1:
                    salvar = st.form_submit_button("💾 Salvar Alterações")
                with col2:
                    excluir = st.form_submit_button("🗑️ Excluir Jogador")

                if salvar:
                    atualizar_jogador(id_jogador, novo_nome.strip(), novo_personagem.strip())
                    st.success("Alterações salvas com sucesso.")
                    st.rerun()

                if excluir:
                    excluir_jogador(id_jogador)
                    st.success("Jogador excluído com sucesso.")
                    st.rerun()

# === Visualização geral atualizada ===
st.subheader("📊 Visualização Geral da Tabela")
dados_finais = listar_jogadores()

if dados_finais:
    df = pd.DataFrame(dados_finais, columns=["ID", "Nome do Jogador", "Nome do Personagem"])
    st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
else:
    st.info("Tabela está vazia.")
