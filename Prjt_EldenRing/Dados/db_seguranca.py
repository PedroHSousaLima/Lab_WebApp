import sqlite3
import os
import hashlib

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados.db")

# === Criação da Tabela ===
def criar_tabela_usuarios():
    """Cria a tabela de usuários no banco de dados se não existir."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_jogador (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_completo TEXT NOT NULL,
                    nome_usuario TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,  -- Usar senha_hash se implementar hashing
                    permissao TEXT NOT NULL DEFAULT 'USER'
                )
            """)
            conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO] criar_tabela_usuarios: {e}")

# === Obter nome completo pelo login ===
def obter_nome_completo_do_usuario(nome_usuario_login):
    """Obtém o nome completo do usuário pelo nome de usuário (login)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nome_completo FROM user_jogador WHERE nome_usuario = ?
            """, (nome_usuario_login,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"[ERRO] obter_nome_completo_do_usuario: {e}")
        return None

# === Obter permissão do usuário ===
def obter_permissao_do_usuario(nome_usuario_login):
    """Obtém a permissão do usuário pelo nome de usuário (login)."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT permissao FROM user_jogador WHERE nome_usuario = ?
            """, (nome_usuario_login,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"[ERRO] obter_permissao_do_usuario: {e}")
        return None

# === Autenticar Usuário ===
def autenticar_usuario(nome_usuario, senha):
    """
    Autentica o usuário verificando o nome de usuário e a senha no banco de dados.
    Se desejar, substitua a verificação da senha simples para a versão com hashing.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Para senha com hash (recomendado):
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()  # Use hashing para segurança
            cursor.execute("""
                SELECT nome_completo FROM user_jogador
                WHERE nome_usuario = ? AND senha = ?
            """, (nome_usuario, senha_hash))  # Verifica usando o hash da senha
            usuario = cursor.fetchone()
            return usuario[0] if usuario else None
    except sqlite3.Error as e:
        print(f"[ERRO] autenticar_usuario: {e}")
        return None

# === Cadastro de novo usuário ===
def cadastrar_usuario(nome_completo, nome_usuario, senha):
    """
    Cadastra um novo usuário no banco de dados.
    Se for usar senha com hash, substitua a lógica de senha simples.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Para senha com hash (recomendado):
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()  # Hash da senha para segurança
            cursor.execute("""
                INSERT INTO user_jogador (nome_completo, nome_usuario, senha)
                VALUES (?, ?, ?)
            """, (nome_completo, nome_usuario, senha_hash))  # Inserir com senha hash
            conn.commit()
            return True, "Usuário cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "❌ Nome de usuário já existe."
    except Exception as e:
        return False, f"❌ Erro ao cadastrar: {str(e)}"
