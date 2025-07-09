import streamlit as st
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Dados'))

from db_seguranca import criar_tabela_usuarios, autenticar_usuario, cadastrar_usuario

# === Inicializa a tabela de usuários ===
criar_tabela_usuarios()

# --- Controle de autenticação e estado da sessão ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = None
if 'usuario_logado' not in st.session_state:
    st.session_state['usuario_logado'] = None  # 🔒 Usado para controlar permissões no restante do app

# === Interface Principal ===
st.set_page_config(page_title="🛡️ Guia do Maculado - Elden Ring", layout="wide")
st.title("🛡️ Guia do Maculado - Elden Ring")

# === TELA DE LOGIN OU CADASTRO ===
if not st.session_state['autenticado']:
    st.markdown("---")
    st.subheader("Bem-vindo(a)! Faça login ou cadastre-se para acessar o guia.")
    opcao = st.radio("Escolha uma opção:", ["Login", "Cadastre-se"], horizontal=True, key="login_option")

    if opcao == "Login":
        st.markdown("### 🚪 Acessar Conta")
        usuario_input = st.text_input("Nome de Usuário", key="login_user")
        senha_input = st.text_input("Senha", type="password", key="login_password")

        if st.button("Entrar", key="login_button"):
            nome_completo = autenticar_usuario(usuario_input, senha_input)
            if nome_completo:
                # === Login bem-sucedido ===
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = nome_completo  # Exibe o nome completo no app
                st.session_state['usuario_logado'] = usuario_input  # 🔑 login usado internamente para filtros
                st.success(f"Bem-vindo(a), Maculado(a) {nome_completo}!")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos. Tente novamente.")

    elif opcao == "Cadastre-se":
        st.markdown("### 📝 Criar Nova Conta")
        novo_nome_completo = st.text_input("Nome Completo", key="register_full_name")
        novo_usuario_input = st.text_input("Nome de Usuário (será seu login)", key="register_user")
        nova_senha_input = st.text_input("Crie uma Senha", type="password", key="register_password")
        confirmar_senha_input = st.text_input("Confirme a Senha", type="password", key="confirm_password")

        if st.button("Cadastrar", key="register_button"):
            if not novo_nome_completo or not novo_usuario_input or not nova_senha_input or not confirmar_senha_input:
                st.warning("Por favor, preencha todos os campos para se cadastrar.")
            elif nova_senha_input != confirmar_senha_input:
                st.error("As senhas não coincidem. Verifique e tente novamente.")
            else:
                sucesso_cadastro, msg_cadastro = cadastrar_usuario(novo_nome_completo, novo_usuario_input, nova_senha_input)
                if sucesso_cadastro:
                    st.success(f"Conta criada com sucesso! Faça login com o usuário '{novo_usuario_input}'.")
                    st.rerun()
                else:
                    st.error(f"Erro ao cadastrar: {msg_cadastro}")

# === INTERFACE PÓS-LOGIN ===
else:
    st.sidebar.success(f"Logado como: {st.session_state['usuario']}")
    st.sidebar.markdown("---")
    st.sidebar.write("Navegue pelas páginas:")

    st.markdown("## 🌟 Bem-vindo(a) à sua Jornada em Elden Ring!")
    st.write(f"Olá, Maculado(a) **{st.session_state['usuario']}**! Use o menu lateral para explorar as diferentes seções do seu guia.")
    st.write("Comece sua aventura pela **Jornada do Player** ou acesse outras funcionalidades.")
    st.info("As páginas do seu guia agora estão disponíveis no menu lateral à esquerda.")

    st.markdown("---")
    st.markdown("### ℹ️ Informações Importantes:")
    st.write("- Lembre-se de salvar seu progresso, se aplicável.")
    st.write("- Explore cada canto das Terras Intermédias!")

    if st.sidebar.button("Sair da Conta", key="logout_button"):
        st.session_state['autenticado'] = False
        st.session_state['usuario'] = None
        st.session_state['usuario_logado'] = None
        st.success("Você saiu do sistema. Até logo, Maculado(a)!")
        st.rerun()  # Recarrega a página para voltar à tela de login
