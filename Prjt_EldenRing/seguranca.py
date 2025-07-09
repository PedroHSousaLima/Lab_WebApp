import streamlit as st
import sqlite3
from db_seguranca import criar_tabela_usuarios, autenticar_usuario, cadastrar_usuario

# --- CRÍTICO: POR FAVOR, implemente hashing de senhas em db_seguranca.py ---
# A segurança do seu app depende disso!

# === Inicializa a tabela de usuários ===
# Esta função cria a tabela se ela não existir.
# É uma boa prática chamá-la no início.
criar_tabela_usuarios()

# --- Controle de autenticação e estado da sessão ---
# Inicializa 'autenticado' na session_state se não existir.
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
# Inicializa 'usuario' na session_state se não existir.
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None

# --- Interface ---
st.title("🔐 Acesso ao Sistema")

# Se o usuário não está autenticado, mostra as opções de Login/Cadastro
if not st.session_state['autenticado']:
    opcao = st.radio("Escolha uma opção:", ["Login", "Cadastre-se"], horizontal=True)

    if opcao == "Login":
        st.subheader("🚪 Login")
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            # A função autenticar_usuario agora retorna o nome do usuário ou None
            usuario_autenticado = autenticar_usuario(usuario_input, senha_input)
            if usuario_autenticado:
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = usuario_autenticado
                st.success(f"Bem-vindo(a), {usuario_autenticado}!")
                st.rerun() # Redireciona/recarrega a página para refletir o login
            else:
                st.error("Usuário ou senha inválidos.")

    elif opcao == "Cadastre-se":
        st.subheader("📝 Cadastre-se")
        novo_nome_completo = st.text_input("Nome completo")
        novo_usuario_input = st.text_input("Nome de usuário (único)")
        nova_senha_input = st.text_input("Senha", type="password")
        confirmar_senha_input = st.text_input("Confirme a Senha", type="password")


        if st.button("Cadastrar"):
            if not novo_nome_completo or not novo_usuario_input or not nova_senha_input or not confirmar_senha_input:
                st.warning("Por favor, preencha todos os campos para cadastro.")
            elif nova_senha_input != confirmar_senha_input:
                st.error("As senhas não coincidem. Por favor, tente novamente.")
            else:
                # 'cadastrar_usuario' agora retorna (True/False, mensagem)
                sucesso_cadastro, msg_cadastro = cadastrar_usuario(novo_nome_completo, novo_usuario_input, nova_senha_input)
                if sucesso_cadastro:
                    st.success(f"Cadastro realizado com sucesso! Agora você pode fazer login com o usuário '{novo_usuario_input}'.")
                    # Opcional: limpar campos após o cadastro
                    # (requer um pouco mais de lógica com Streamlit, ou confiar no rerun)
                else:
                    st.error(f"Erro ao cadastrar: {msg_cadastro}") # Usa a mensagem de erro do db_seguranca
else:
    # --- Conteúdo do aplicativo principal APÓS o login ---
    st.sidebar.success(f"Logado como: {st.session_state['usuario']}")
    st.write(f"Olá, {st.session_state['usuario']}! Este é o seu painel principal.")
    st.write("Aqui você pode adicionar o conteúdo do seu aplicativo Elden Ring.")

    # Botão de Logout
    if st.sidebar.button("Sair"):
        st.session_state['autenticado'] = False
        st.session_state['usuario'] = None
        st.success("Você saiu do sistema.")
        st.rerun() # Recarrega a página para voltar à tela de login