import pandas as pd
import sqlite3
from pathlib import Path

# === Caminhos relativos ===
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "elden_ring_weapon.csv"
DB_PATH = BASE_DIR / "dados.db"

def criar_tabela_weapons():
    """Cria e popula a tabela 'weapons' no banco de dados com nova estrutura simplificada."""

    # Conecta ao banco e verifica se a tabela já existe
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='weapons'
        """)
        existe = cursor.fetchone()

        if existe:
            print("🔎 Tabela 'weapons' já existe. Atualizando com novos dados...")
            atualizar_tabela_weapons(conn)
        else:
            # Carrega os dados e cria a tabela
            df = pd.read_csv(CSV_PATH)
            df.columns = [
                "type", "name", "vigor", "mind", "vitality",
                "strength", "dexterity", "intelligence", "faith", "arcane"
            ]
            atributos = ["vigor", "mind", "vitality", "strength", "dexterity", "intelligence", "faith", "arcane"]
            df[atributos] = df[atributos].apply(pd.to_numeric, errors="coerce")

            cursor.execute("""
                CREATE TABLE weapons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    name TEXT,
                    vigor INTEGER,
                    mind INTEGER,
                    vitality INTEGER,
                    strength INTEGER,
                    dexterity INTEGER,
                    intelligence INTEGER,
                    faith INTEGER,
                    arcane INTEGER
                )
            """)
            df.to_sql("weapons", conn, if_exists="append", index=False)
            print("✅ Nova tabela 'weapons' criada e populada com sucesso.")

def atualizar_tabela_weapons(conn):
    """Atualiza a tabela 'weapons' no banco com dados do CSV, mantendo linhas distintas."""
    df = pd.read_csv(CSV_PATH)
    df.columns = [
        "type", "name", "vigor", "mind", "vitality",
        "strength", "dexterity", "intelligence", "faith", "arcane"
    ]
    atributos = ["vigor", "mind", "vitality", "strength", "dexterity", "intelligence", "faith", "arcane"]
    df[atributos] = df[atributos].apply(pd.to_numeric, errors="coerce")

    # Obtém as armas atuais do banco de dados
    armas_banco = pd.read_sql_query("SELECT name FROM weapons", conn)
    
    # Filtra as armas do CSV que ainda não estão no banco
    armas_novas = df[~df["name"].isin(armas_banco["name"])]

    # Insere as novas armas na tabela do banco
    if not armas_novas.empty:
        armas_novas.to_sql("weapons", conn, if_exists="append", index=False)
        print(f"✅ {len(armas_novas)} novas armas adicionadas à tabela.")
    else:
        print("🔄 Nenhuma nova arma encontrada para adicionar ao banco.")

def obter_weapons():
    """Retorna o DataFrame com todas as armas cadastradas."""
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM weapons", conn)
