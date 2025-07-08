import pandas as pd
import sqlite3
from pathlib import Path

# === Caminhos relativos ===
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "elden_ring_weapon.csv"
DB_PATH = BASE_DIR / "dados.db"


def criar_tabela_weapons():
    """Cria e popula a tabela 'weapons' no banco de dados."""

    # Lê o CSV com nomes de colunas padronizados
    df = pd.read_csv(CSV_PATH)
    df.columns = [
        "name", "type", "phy", "mag", "fir", "lit", "hol", "cri", "sta",
        "str", "dex", "int", "fai", "arc", "any",
        "phy_def", "mag_def", "fir_def", "lit_def", "hol_def",
        "bst", "rst", "wgt", "upgrade"
    ]

    # Converte atributos para float (valores numéricos)
    atributos = ["str", "dex", "int", "fai", "arc", "any"]
    df[atributos] = df[atributos].apply(pd.to_numeric, errors="coerce")

    # Criação da tabela no banco
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS weapons")  # Recriação garantida
        cursor.execute("""
            CREATE TABLE weapons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                type TEXT,
                phy INTEGER,
                mag INTEGER,
                fir INTEGER,
                lit INTEGER,
                hol INTEGER,
                cri INTEGER,
                sta INTEGER,
                str REAL,
                dex REAL,
                int REAL,
                fai REAL,
                arc REAL,
                any REAL,
                phy_def INTEGER,
                mag_def INTEGER,
                fir_def INTEGER,
                lit_def INTEGER,
                hol_def INTEGER,
                bst INTEGER,
                rst INTEGER,
                wgt REAL,
                upgrade TEXT
            )
        """)
        df.to_sql("weapons", conn, if_exists="append", index=False)
        print("✅ Tabela 'weapons' criada e populada com sucesso.")

def obter_weapons():
    """Retorna o DataFrame com todas as armas cadastradas."""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM weapons", conn)
