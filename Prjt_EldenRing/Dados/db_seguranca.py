import sqlite3
import os

# === Caminho do banco de dados ===
# BASE_DIR é o diretório do arquivo atual (db_seguranca.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DB_PATH navega para a pasta 'Dados' que está um nível acima de BASE_DIR
DB_PATH = os.path.join(BASE_DIR, '..', 'Dados', 'dados.db')

def criar_tabela_usuarios():
    """
    Cria a tabela 'user_jogador' se ela não existir.
    Inclui um campo 'permissao' com valor padrão 'USER'.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_jogador (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_completo TEXT NOT NULL,
                    nome_usuario TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,
                    permissao TEXT NOT NULL DEFAULT 'USER' -- Corrigido para DEFAULT
                )
            """)
            conn.commit()
        print("Tabela 'user_jogador' verificada/criada com sucesso.")
    except sqlite3.Error as e:
        print(f"Erro ao criar/verificar tabela de usuários: {e}")

def cadastrar_usuario(nome_completo, nome_usuario, senha):
    """
    Cadastra um novo usuário no banco de dados.
    A senha é armazenada em texto puro.
    Retorna True e mensagem de sucesso, ou False e mensagem de erro.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_jogador (nome_completo, nome_usuario, senha)
                VALUES (?, ?, ?)
            """, (nome_completo, nome_usuario, senha)) # Senha armazenada como texto puro
            conn.commit()
        return True, "Usuário cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Nome de usuário já existe. Por favor, escolha outro."
    except sqlite3.Error as e:
        return False, f"Erro no banco de dados ao cadastrar: {e}"
    except Exception as e:
        return False, f"Erro inesperado ao cadastrar: {e}"

def autenticar_usuario(nome_usuario, senha):
    """
    Autentica um usuário comparando a senha fornecida com a senha armazenada (texto puro).
    Retorna o nome_usuario se a autenticação for bem-sucedida, caso contrário, None.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nome_usuario FROM user_jogador WHERE nome_usuario = ? AND senha = ?
        """, (nome_usuario, senha)) # Comparação de senha em texto puro
        resultado = cursor.fetchone()

    if resultado:
        return resultado[0] # Retorna o nome_usuario
    return None # Autenticação falhou ou usuário não encontrado

