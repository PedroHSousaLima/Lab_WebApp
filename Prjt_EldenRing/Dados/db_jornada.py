import sqlite3
from pathlib import Path

# Caminho para o banco de dados
DB_PATH = Path(__file__).resolve().parent / "dados.db"

def criar_tabela_jornada():
    """Cria a tabela 'jornada' no banco de dados caso não exista."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jornada (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personagem TEXT,
                nome TEXT,
                localidade TEXT,
                location TEXT,
                runes INTEGER,
                loot TEXT,
                stance TEXT,
                tipo_dano_pref TEXT,
                resistencia TEXT,
                level TEXT,
                status_boss TEXT
            )
        """)
        conn.commit()
    print("✅ Tabela 'jornada' criada ou já existente.")

def inserir_jogador(nome_jogador, nome_personagem, nome_usuario_criador):
    """Insere um novo jogador (personagem) na tabela 'jogadores_personagens'."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO jogadores_personagens (nome_jogador, nome_personagem, nome_usuario_criador)
            VALUES (?, ?, ?)
        """, (nome_jogador, nome_personagem, nome_usuario_criador))
        conn.commit()

def listar_jogadores(nome_usuario_criador):
    """Lista jogadores (personagens) associados ao usuário logado."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome_jogador, nome_personagem
            FROM jogadores_personagens
            WHERE nome_usuario_criador = ?
        """, (nome_usuario_criador,))
        return cursor.fetchall()

def atualizar_jogador(id_jogador, novo_nome, novo_personagem, nome_usuario_criador):
    """Atualiza os dados de um jogador (personagem) na tabela 'jogadores_personagens'."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE jogadores_personagens
            SET nome_jogador = ?, nome_personagem = ?
            WHERE id = ? AND nome_usuario_criador = ?
        """, (novo_nome, novo_personagem, id_jogador, nome_usuario_criador))
        conn.commit()

def excluir_jogador(id_jogador, nome_usuario_criador):
    """Exclui um jogador (personagem) da tabela 'jogadores_personagens'."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM jogadores_personagens
            WHERE id = ? AND nome_usuario_criador = ?
        """, (id_jogador, nome_usuario_criador))
        conn.commit()

def obter_jogadores(nome_usuario_criador):
    """Obtém os jogadores (personagens) associados a um usuário logado."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome_jogador, nome_personagem
            FROM jogadores_personagens
            WHERE nome_usuario_criador = ?
        """, (nome_usuario_criador,))
        return cursor.fetchall()

def obter_bosses_com_level():
    """Obtém os bosses com o nível associado e retorna como DataFrame."""
    with sqlite3.connect(DB_PATH) as conn:
        bosses = pd.read_sql_query("SELECT * FROM bosses", conn)
        levels = pd.read_sql_query("SELECT * FROM boss_levels", conn)

    bosses["chave"] = (bosses["localidade"].str.strip() + bosses["nome"].str.strip()).str.lower()
    levels["chave"] = (levels["localidade"].str.strip() + levels["nome"].str.strip()).str.lower()

    merged = pd.merge(bosses, levels[["chave", "level"]], on="chave", how="left")
    return merged.drop(columns=["chave"])

def criar_ou_atualizar_jornada(nome_personagem, df_bosses):
    """Cria ou atualiza a jornada de um personagem, com a inserção de bosses e status 'Vivo'."""
    df_bosses["personagem"] = nome_personagem
    df_bosses["status_boss"] = "Vivo"

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jornada WHERE personagem = ?", (nome_personagem,))
        registros = cursor.fetchone()[0]

        if registros == 0:
            df_bosses.drop(columns=["id"], errors="ignore").to_sql("jornada", conn, if_exists="append", index=False)

def obter_total_bosses_distintos():
    """Obtém o total de bosses distintos, considerando a combinação de nome e localidade."""
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT DISTINCT localidade || nome AS chave FROM bosses", conn)
        return df["chave"].nunique()

def sincronizar_jornada_com_bosses():
    """Sincroniza os dados da jornada com os bosses."""
    with sqlite3.connect(DB_PATH) as conn:
        jornada = pd.read_sql_query("SELECT * FROM jornada", conn)
        bosses = pd.read_sql_query("SELECT * FROM bosses", conn)

    # Criar chave única para identificar cada boss
    jornada["chave"] = (jornada["localidade"].str.strip() + jornada["nome"].str.strip()).str.lower()
    bosses["chave"] = (bosses["localidade"].str.strip() + bosses["nome"].str.strip()).str.lower()

    # Mesclar mantendo o id da jornada e os campos que não serão sobrescritos
    atualizada = pd.merge(
        jornada[["id", "chave", "personagem", "status_boss"]],
        bosses.drop(columns=["id"]),
        on="chave",
        how="left",
        suffixes=("", "_boss")
    )

    # Reorganizar as colunas
    atualizada = atualizada[[
        "id", "personagem", "nome", "localidade", "location",
        "runes", "loot", "stance", "tipo_dano_pref", "resistencia", "status_boss"
    ]]

    # Atualizar os registros na tabela jornada
    with sqlite3.connect(DB_PATH) as conn:
        for _, row in atualizada.iterrows():
            conn.execute("""
                UPDATE jornada
                SET nome = ?, localidade = ?, location = ?, runes = ?, loot = ?,
                    stance = ?, tipo_dano_pref = ?, resistencia = ?
                WHERE id = ?
            """, (
                row["nome"], row["localidade"], row["location"], row["runes"],
                row["loot"], row["stance"], row["tipo_dano_pref"],
                row["resistencia"], row["id"]
            ))
        conn.commit()
