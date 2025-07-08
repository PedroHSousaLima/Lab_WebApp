import sqlite3
import pandas as pd
import os

# === Caminhos base ===
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'dados.db')
CSV_PATH = os.path.join(BASE_DIR, 'elden_ring_boss_lvl.csv')

def criar_tabela_boss_lvl():
    """Cria a tabela 'boss_levels' e importa o CSV se a tabela estiver vazia."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS boss_levels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    localidade TEXT,
                    nome TEXT,
                    level TEXT
                )
            """)
            conn.commit()

            # Verifica se a tabela já possui dados
            cursor.execute("SELECT COUNT(*) FROM boss_levels")
            registros = cursor.fetchone()[0]

            if registros == 0:
                importar_csv_para_banco(conn)

    except Exception as e:
        print(f"[ERRO] Falha ao criar tabela boss_levels: {e}")

def importar_csv_para_banco(conn):
    """Importa os dados do CSV para a tabela boss_levels, se o arquivo existir."""
    if not os.path.isfile(CSV_PATH):
        print(f"[ERRO] CSV não encontrado em: {CSV_PATH}")
        return

    try:
        df = pd.read_csv(CSV_PATH)

        df = df.rename(columns={
            "Localidade": "localidade",
            "Name": "nome",
            "Level": "level"
        })

        df.to_sql("boss_levels", conn, if_exists="append", index=False)

        print(f"[OK] {len(df)} registros importados para 'boss_levels'.")

    except Exception as e:
        print(f"[ERRO] Falha ao importar CSV: {e}")

def listar_boss_levels():
    """Retorna todos os registros da tabela boss_levels como DataFrame."""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("""
            SELECT id, localidade, nome, level
            FROM boss_levels
        """, conn)
