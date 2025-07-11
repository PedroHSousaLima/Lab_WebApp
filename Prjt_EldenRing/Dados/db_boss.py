import sqlite3
import pandas as pd
import os
from pathlib import Path

# === Caminho para o banco de dados persistente ===
# O banco de dados será armazenado no diretório do usuário, garantindo persistência.
DB_PATH = Path(os.path.expanduser("~")) / "streamlit_data" / "dados.db"
CSV_PATH = Path(__file__).resolve().parent / "elden_ring_boss_list.csv"  # Caminho para o CSV

# Cria o diretório onde o banco de dados será salvo, caso não exista
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# === Criação da Tabela de Bosses ===
def criar_tabela_boss():
    """Cria a tabela 'bosses' e importa o CSV se o banco for recém-criado."""
    banco_existe = os.path.exists(DB_PATH)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bosses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    localidade TEXT,
                    location TEXT,
                    runes INTEGER,
                    loot TEXT,
                    stance TEXT,
                    tipo_dano_pref TEXT,
                    resistencia TEXT
                )
            """)
            conn.commit()

        if not banco_existe:
            importar_csv_para_banco()  # Importa dados do CSV se o banco for recém-criado

    except sqlite3.Error as e:
        print(f"[ERRO] Criar Tabela Boss: {e}")

# === Importar dados do CSV para o banco ===
def importar_csv_para_banco():
    """Importa os dados do CSV para a tabela de bosses, apenas se estiver vazia."""
    if not os.path.isfile(CSV_PATH):
        print(f"[WARN] CSV não encontrado: {CSV_PATH}")
        return

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bosses")
            if cursor.fetchone()[0] > 0:
                return  # Tabela já está populada, evita importar novamente

            # Lê o CSV
            df = pd.read_csv(CSV_PATH)

            # Tratamento da coluna 'Runes' (remover vírgulas e converter para inteiro)
            df["Runes"] = (
                df["Runes"]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip()
                .replace("", "0")
                .astype(int)
            )

            # Renomeia as colunas para os nomes que o banco espera
            df = df.rename(columns={
                "Name": "nome",
                "Localidade": "localidade",
                "Location": "location",
                "Runes": "runes",
                "Loot": "loot",
                "Stance": "stance",
                "Pref. dmg. type": "tipo_dano_pref",
                "Resistencia": "resistencia"
            })

            # Insere os dados no banco
            df.to_sql("bosses", conn, if_exists="append", index=False)
            print(f"[INFO] Dados do CSV importados com sucesso.")

    except sqlite3.Error as e:
        print(f"[ERRO] Importar CSV para Banco: {e}")
    except Exception as e:
        print(f"[ERRO] {e}")

# === Listar todos os Bosses ===
def listar_bosses():
    """Retorna todos os bosses com nomes de colunas compatíveis com a visualização."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query("""
                SELECT
                    id AS ID,
                    nome AS Nome,
                    localidade AS Localidade,
                    location AS Location,
                    runes AS Runes,
                    loot AS Loot,
                    stance AS Stance,
                    tipo_dano_pref AS "Tipo de Dano Preferido",
                    resistencia AS "Resistência"
                FROM bosses
            """, conn)
            return df
    except sqlite3.Error as e:
        print(f"[ERRO] Listar Bosses: {e}")
        return None

# === Inserir um novo Boss ===
def inserir_boss(nome, localidade, location, runes, loot, stance, tipo_dano_pref, resistencia):
    """Insere um novo boss no banco."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO bosses (
                    nome, localidade, location, runes,
                    loot, stance, tipo_dano_pref, resistencia
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, localidade, location, runes, loot, stance, tipo_dano_pref, resistencia))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO] Inserir Boss: {e}")

# === Atualizar Boss ===
def atualizar_boss(id, nome, localidade, location, runes, loot, stance, tipo_dano_pref, resistencia):
    """Atualiza um boss existente com base no ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                UPDATE bosses SET
                    nome = ?, localidade = ?, location = ?, runes = ?,
                    loot = ?, stance = ?, tipo_dano_pref = ?, resistencia = ?
                WHERE id = ?
            """, (nome, localidade, location, runes, loot, stance, tipo_dano_pref, resistencia, id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO] Atualizar Boss: {e}")

# === Excluir Boss ===
def excluir_boss(id):
    """Remove um boss do banco com base no ID."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM bosses WHERE id = ?", (id,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[ERRO] Excluir Boss: {e}")
