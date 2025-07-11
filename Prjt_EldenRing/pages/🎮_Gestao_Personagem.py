import os
import sys
import streamlit as st
import base64
import pandas as pd
from pathlib import Path

# Caminho do banco de dados persistente
DB_PATH = os.path.join(os.path.expanduser("~"), "streamlit_data", "dados.db")

# Cria a pasta de dados, caso não exista
if not os.path.exists(os.path.dirname(DB_PATH)):
    os.makedirs(os.path.dirname(DB_PATH))

# Verifica se o usuário está autenticado e tem login válido
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'usuario_logado' not in st.session_state:
    st.session_state['usuario_logado'] = None

if not st.session_state['autenticado'] or not st.session_state['usuario_logado']:
    st.warning("⚠️ Você precisa fazer login para acessar esta página.")
    st.info("Por favor, retorne à página inicial para fazer login.")
    st.stop()

# === Caminhos Absolutos ===
# Garante compatibilidade multiplataforma e ao mover para produção
caminho_atual = Path(__file__).resolve().parent
caminho_dados = caminho_atual.parent / "Dados"

# Adiciona a pasta Dados ao sys.path para importar módulos
if str(caminho_dados) not in sys.path:
    sys.path.append(str(caminho_dados))

# === Importações de banco ===
from db import (
    criar_tabela,
    inserir_jogador,
    listar_jogadores,
    atualizar_jogador,
    excluir_jogador
)

# === Inicializa banco de dados se necessário ===
criar_tabela()

# === Configuração da Página ===
st.set_page_config(page_title="Elden Ring - Home", layout="wide")

# === Função para definir imagem de fundo com escurecimento ===
def set_bg_from_local(relative_path):
    image_file = caminho_atual / relative_path
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

# === Aplica fundo ===
set_bg_from_local("../assets/gp_background.jpg")

# === Título da Página ===
st.title("🎮 Gerenciar Jogador e Personagem")

# === Formulário de Cadastro ===
with st.form("form_cadastro"):
    st.subheader("➕ Cadastrar novo jogador")
    nome_jogador = st.text_input("👤 Nome do Jogador")
    nome_personagem = st.text_input("🧝 Nome do Personagem")
    submitted = st.form_submit_button("Cadastrar")

    if submitted:
        if nome_jogador.strip() and nome_personagem.strip():
            inserir_jogador(nome_jogador.strip(), nome_personagem.strip(), st.session_state['usuario_logado'])
            st.success("Cadastro realizado com sucesso!")
            st.rerun()
        else:
            st.warning("Preencha todos os campos.")

# === Interface de edição agrupada ===
with st.expander("🛠 Clique aqui para editar ou excluir um jogador"):
    dados_finais = listar_jogadores(st.session_state['usuario_logado'])
    
    if not dados_finais:
        st.info("Nenhum jogador cadastrado.")
    else:
        jogadores_dict = {f"{j[1]} - {j[2]}": j[0] for j in dados_finais}  # Ex: "João - Guerreiro": id
        selecionado = st.selectbox("Selecione um jogador para editar:", list(jogadores_dict.keys()))

        if selecionado:
            id_jogador = jogadores_dict[selecionado]
            jogador = next(j for j in dados_finais if j[0] == id_jogador)

            with st.form("form_edit_unico"):
                novo_nome = st.text_input("Nome do Jogador", value=jogador[1])
                novo_personagem = st.text_input("Nome do Personagem", value=jogador[2])

                col1, col2 = st.columns(2)
                with col1:
                    salvar = st.form_submit_button("💾 Salvar Alterações")
                with col2:
                    excluir = st.form_submit_button("🗑️ Excluir Jogador")

                if salvar:
                    atualizar_jogador(id_jogador, novo_nome.strip(), novo_personagem.strip(), st.session_state['usuario_logado'])
                    st.success("Alterações salvas com sucesso.")
                    st.rerun()

                if excluir:
                    excluir_jogador(id_jogador, st.session_state['usuario_logado'])
                    st.success("Jogador excluído com sucesso.")
                    st.rerun()

# === Visualização geral atualizada ===
st.subheader("📊 Visualização Geral da Tabela")
dados_finais = listar_jogadores(st.session_state['usuario_logado'])

if dados_finais:
    df = pd.DataFrame(dados_finais, columns=["ID", "Nome do Jogador", "Nome do Personagem"])
    st.dataframe(df.drop(columns=["ID"]), use_container_width=True)
else:
    st.info("Tabela está vazia.")
