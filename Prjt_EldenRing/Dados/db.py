import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "dados.db")

# Conecta ao banco e garante a criação da tabela
def criar_tabela():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jogadores_personagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_jogador TEXT NOT NULL,
                nome_personagem TEXT NOT NULL
            )
        """)
        conn.commit()

# Inserir novo jogador
def inserir_jogador(nome_jogador, nome_personagem):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jogadores_personagens (nome_jogador, nome_personagem)
            VALUES (?, ?)
        """, (nome_jogador, nome_personagem))
        conn.commit()

# Listar todos os jogadores
def listar_jogadores():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_jogador, nome_personagem FROM jogadores_personagens")
        return cursor.fetchall()

# Atualizar jogador por ID
def atualizar_jogador(id, novo_nome, novo_personagem):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE jogadores_personagens
            SET nome_jogador = ?, nome_personagem = ?
            WHERE id = ?
        """, (novo_nome, novo_personagem, id))
        conn.commit()

# Excluir jogador por ID
def excluir_jogador(id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jogadores_personagens WHERE id = ?", (id,))
        conn.commit()
