import sqlite3
from pathlib import Path
import pandas as pd

# Caminho para o banco de dados
db_path = Path(__file__).resolve().parent / "dados.db"

def criar_tabela_build_weapon():
    with sqlite3.connect(db_path) as conn:
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
    with sqlite3.connect(db_path) as conn:
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
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query("""
            SELECT * FROM build_weapon WHERE personagem = ?
            ORDER BY status, slot
        """, conn, params=(personagem,))
