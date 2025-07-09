import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "dados.db")

def criar_tabela():
    """
    Cria a tabela jogadores_personagens, se não existir, com controle por nome de usuário.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jogadores_personagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_jogador TEXT NOT NULL,
                nome_personagem TEXT NOT NULL,
                nome_usuario_criador TEXT NOT NULL
            )
        """)
        # Adiciona a coluna nome_usuario_criador caso não exista (evita falhas em bancos antigos)
        try:
            cursor.execute("ALTER TABLE jogadores_personagens ADD COLUMN nome_usuario_criador TEXT")
            conn.commit()
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e):
                print(f"Erro ao adicionar coluna 'nome_usuario_criador': {e}")

# Inserir novo jogador
def inserir_jogador(nome_jogador, nome_personagem, nome_usuario_criador):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jogadores_personagens (nome_jogador, nome_personagem, nome_usuario_criador)
            VALUES (?, ?, ?)
        """, (nome_jogador, nome_personagem, nome_usuario_criador))
        conn.commit()

# Listar jogadores apenas do usuário logado
def listar_jogadores(nome_usuario_criador):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome_jogador, nome_personagem 
            FROM jogadores_personagens 
            WHERE nome_usuario_criador = ?
        """, (nome_usuario_criador,))
        return cursor.fetchall()

# Atualizar jogador
def atualizar_jogador(id_jogador, novo_nome, novo_personagem, nome_usuario_criador):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE jogadores_personagens
            SET nome_jogador = ?, nome_personagem = ?
            WHERE id = ? AND nome_usuario_criador = ?
        """, (novo_nome, novo_personagem, id_jogador, nome_usuario_criador))
        conn.commit()

# Excluir jogador
def excluir_jogador(id_jogador, nome_usuario_criador):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM jogadores_personagens 
            WHERE id = ? AND nome_usuario_criador = ?
        """, (id_jogador, nome_usuario_criador))
        conn.commit()

# Obter personagens únicos do usuário
def obter_personagens(nome_usuario_criador):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT nome_personagem 
            FROM jogadores_personagens 
            WHERE nome_usuario_criador = ?
        """, (nome_usuario_criador,))
        personagens = cursor.fetchall()
        return [p[0] for p in personagens]

# Testes locais
if __name__ == "__main__":
    criar_tabela()

    # Cadastro de jogadores para testes
    inserir_jogador("PlayerOne", "Warrior", "teste_user")
    inserir_jogador("PlayerTwo", "Mage", "teste_user")
    inserir_jogador("OtherGuy", "Rogue", "outro_user")

    print("\nJogadores de 'teste_user':")
    for j in listar_jogadores("teste_user"):
        print(j)

    print("\nJogadores de 'outro_user':")
    for j in listar_jogadores("outro_user"):
        print(j)

    # Atualização
    jogadores_teste = listar_jogadores("teste_user")
    if jogadores_teste:
        id_para_atualizar = jogadores_teste[0][0]
        atualizar_jogador(id_para_atualizar, "UpdatedPlayer", "NewClass", "teste_user")
        print(f"\nAtualizado ID {id_para_atualizar}:")
        print(listar_jogadores("teste_user"))

    # Exclusão
    jogadores_teste_apagar = listar_jogadores("teste_user")
    if jogadores_teste_apagar:
        id_para_excluir = jogadores_teste_apagar[0][0]
        excluir_jogador(id_para_excluir, "teste_user")
        print(f"\nExcluído ID {id_para_excluir}:")
        print(listar_jogadores("teste_user"))

    print("\nPersonagens únicos de 'teste_user':")
    print(obter_personagens("teste_user"))
