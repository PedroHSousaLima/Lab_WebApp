import sqlite3
import pandas as pd
import os

# === Caminhos base ===
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'dados.db')
CSV_PATH = os.path.join(BASE_DIR, 'elden_ring_boss_list.csv')


def criar_tabela_boss():
    """Cria a tabela 'bosses' e importa o CSV se o banco for recém-criado."""
    banco_existe = os.path.exists(DB_PATH)

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
        importar_csv_para_banco()


def importar_csv_para_banco():
    """Importa os dados do CSV para a tabela, apenas se estiver vazia."""
    if not os.path.isfile(CSV_PATH):
        print(f"[WARN] CSV não encontrado: {CSV_PATH}")
        return

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bosses")
        if cursor.fetchone()[0] > 0:
            return  # Tabela já populada

        df = pd.read_csv(CSV_PATH)

        # Tratamento da coluna 'Runes'
        df["Runes"] = (
            df["Runes"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
            .replace("", "0")
            .astype(int)
        )

        # Renomeia colunas conforme esperado pelo banco
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

        df.to_sql("bosses", conn, if_exists="append", index=False)


def listar_bosses():
    """Retorna todos os bosses com nomes de colunas compatíveis com a visualização."""
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



def inserir_boss(nome, localidade, location, runes, loot, stance, tipo_dano_pref, resistencia):
    """Insere um novo boss no banco."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO bosses (
                nome, localidade, location, runes,
                loot, stance, tipo_dano_pref, resistencia
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, localidade, location, runes, loot, stance, tipo_dano_pref, resistencia))
        conn.commit()


def atualizar_boss(id, nome, localidade, location, runes, loot, stance, tipo_dano_pref, resistencia):
    """Atualiza um boss existente com base no ID."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE bosses SET
                nome = ?, localidade = ?, location = ?, runes = ?,
                loot = ?, stance = ?, tipo_dano_pref = ?, resistencia = ?
            WHERE id = ?
        """, (nome, localidade, location, runes, loot, stance, tipo_dano_pref, resistencia, id))
        conn.commit()


def excluir_boss(id):
    """Remove um boss do banco com base no ID."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM bosses WHERE id = ?", (id,))
        conn.commit()
