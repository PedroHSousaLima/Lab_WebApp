# db_build.py

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "dados.db"

def criar_tabela_build():
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

def inicializar_build_para_personagem(personagem: str):
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

def obter_build(personagem: str):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""
            SELECT vigor, mind, endurance, strength, dexterity,
                   intelligence, faith, arcane
            FROM build WHERE personagem = ?
        """, (personagem,)).fetchone()

def atualizar_build(personagem: str, valores: dict):
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
