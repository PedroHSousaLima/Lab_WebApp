import sqlite3
from pathlib import Path
import pandas as pd
import os

# Caminho para o banco de dados na pasta 'streamlit_data'
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / 'streamlit_data'
DB_PATH = DB_DIR / 'dados.db'

# Cria a pasta streamlit_data se não existir
os.makedirs(DB_DIR, exist_ok=True)

def criar_tabela_build_weapon():
    """Cria a tabela build_weapon, se não existir, para armazenar as builds dos personagens."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS build_weapon (
                personagem TEXT NOT NULL,
                status TEXT NOT NULL,
                slot INTEGER NOT NULL,
                item TEXT,
                valor INTEGER,
                PRIMARY KEY (personagem, status, slot)
            )
        """)
        conn.commit()

def salvar_build_weapon(personagem: str, df_vertical: pd.DataFrame):
    """Salva ou atualiza a build de armas para um personagem."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        for _, row in df_vertical.iterrows():
            cursor.execute("""
                INSERT INTO build_weapon (personagem, status, slot, item, valor)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(personagem, status, slot)
                DO UPDATE SET
                    item = excluded.item,
                    valor = excluded.valor
            """, (
                row["personagem"],
                row["Status"],
                int(row["Slot"]),
                row["Item"],
                int(row["Valor"])
            ))
        conn.commit()

def carregar_build_weapon(personagem: str) -> pd.DataFrame:
    """Carrega os dados da build_weapon para um personagem específico."""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("""
            SELECT * FROM build_weapon WHERE personagem = ?
            ORDER BY status, slot
        """, conn, params=(personagem,))

# Testes locais (opcional)
if __name__ == "__main__":
    criar_tabela_build_weapon()

    # Exemplo de dados para inserir na tabela
    data = {
        "personagem": ["Guerreiro", "Guerreiro", "Guerreiro"],
        "Status": ["Vigor", "Mind", "Strength"],
        "Slot": [1, 2, 3],
        "Item": ["Espada", "Feitiço", "Escudo"],
        "Valor": [50, 30, 40]
    }

    df = pd.DataFrame(data)

    # Salvar build de armas
    salvar_build_weapon("Guerreiro", df)

    # Carregar e exibir a build salva
    build_carregada = carregar_build_weapon("Guerreiro")
    print(build_carregada)
