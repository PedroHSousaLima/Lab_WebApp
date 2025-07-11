import sqlite3
from pathlib import Path
import os

# === Caminho do banco de dados com persistência ===
# O banco de dados será armazenado em uma pasta persistente no diretório do usuário.
DB_PATH = Path(os.path.expanduser("~")) / "streamlit_data" / "dados.db"

# Cria o diretório onde o banco de dados será salvo, caso não exista
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# === Criação da Tabela de Builds ===
def criar_tabela_build():
    """Cria a tabela de builds no banco de dados, caso não exista."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS build (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    personagem TEXT UNIQUE,
                    vigor INTEGER DEFAULT 0,
                    mind INTEGER DEFAULT 0,
                    endurance INTEGER DEFAULT 0,
                    strength INTEGER DEFAULT 0,
                    dexterity INTEGER DEFAULT 0,
                    intelligence INTEGER DEFAULT 0,
                    faith INTEGER DEFAULT 0,
                    arcane INTEGER DEFAULT 0
                )
            """)
            conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO] criar_tabela_build: {e}")

# === Inicializa Build de um Personagem (se ainda não existir) ===
def inicializar_build_para_personagem(personagem: str):
    """Inicializa os valores da build de um personagem, se ainda não existir."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM build WHERE personagem = ?", (personagem,))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO build (
                        personagem, vigor, mind, endurance, strength,
                        dexterity, intelligence, faith, arcane
                    ) VALUES (?, 0, 0, 0, 0, 0, 0, 0, 0)
                """, (personagem,))
                conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO] inicializar_build_para_personagem: {e}")

# === Obter os valores da Build de um personagem ===
def obter_build(personagem: str):
    """Retorna os valores da build de um personagem."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT vigor, mind, endurance, strength, dexterity,
                       intelligence, faith, arcane
                FROM build
                WHERE personagem = ?
            """, (personagem,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"[ERRO] obter_build: {e}")
        return None

# === Atualizar os valores da Build ===
def atualizar_build(personagem: str, valores: dict):
    """Atualiza os valores da build de um personagem."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE build
                SET vigor = ?, mind = ?, endurance = ?, strength = ?,
                    dexterity = ?, intelligence = ?, faith = ?, arcane = ?
                WHERE personagem = ?
            """, (
                valores["vigor"], valores["mind"], valores["endurance"],
                valores["strength"], valores["dexterity"], valores["intelligence"],
                valores["faith"], valores["arcane"], personagem
            ))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO] atualizar_build: {e}")

