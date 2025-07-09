import os
import sys
import sqlite3
import base64
from pathlib import Path

import pandas as pd
import streamlit as st

# Visualização
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import cm

import plotly.express as px
import plotly.graph_objects as go

# --- Início da Lógica de Controle de Acesso (ADICIONADO) ---
# Certifica-se que 'autenticado' está no session_state para evitar erros
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# Se o usuário NÃO ESTIVER AUTENTICADO, exibe aviso e interrompe
if not st.session_state['autenticado']:
    st.warning("⚠️ Você precisa fazer login para acessar esta página.")
    st.info("Por favor, retorne à página inicial para fazer login.")
    st.stop() # Interrompe a execução do resto do script da página
# --- Fim da Lógica de Controle de Acesso ---

# === Caminhos ===
BASE_DIR = os.path.dirname(__file__)
DADOS_PATH = os.path.abspath(os.path.join(BASE_DIR, '..', 'Dados'))
DB_PATH = os.path.join(DADOS_PATH, 'dados.db')

# Garante que a pasta Dados seja visível para importações
sys.path.append(DADOS_PATH)
from db_boss_lvl import criar_tabela_boss_lvl, listar_boss_levels

# === Inicializa a tabela boss_levels ===
criar_tabela_boss_lvl()

# === Funções auxiliares ===
def sincronizar_jornada_com_bosses():
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

def obter_jogadores():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT id, nome_jogador, nome_personagem FROM jogadores_personagens", conn)

def obter_bosses_com_level():
    with sqlite3.connect(DB_PATH) as conn:
        bosses = pd.read_sql_query("SELECT * FROM bosses", conn)
        levels = pd.read_sql_query("SELECT * FROM boss_levels", conn)

    bosses["chave"] = (bosses["localidade"].str.strip() + bosses["nome"].str.strip()).str.lower()
    levels["chave"] = (levels["localidade"].str.strip() + levels["nome"].str.strip()).str.lower()

    merged = pd.merge(bosses, levels[["chave", "level"]], on="chave", how="left")
    return merged.drop(columns=["chave"])

def criar_ou_atualizar_jornada(nome_personagem, df_bosses):
    df_bosses["personagem"] = nome_personagem
    df_bosses["status_boss"] = "Vivo"

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
        cursor.execute("SELECT COUNT(*) FROM jornada WHERE personagem = ?", (nome_personagem,))
        registros = cursor.fetchone()[0]

        if registros == 0:
            df_bosses.drop(columns=["id"], errors="ignore").to_sql("jornada", conn, if_exists="append", index=False)

def obter_total_bosses_distintos():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT DISTINCT localidade || nome AS chave FROM bosses", conn)
        return df["chave"].nunique()

# === Fundo ===

# === Função para definir imagem de fundo com escurecimento ===
caminho_atual = Path(__file__).resolve().parent
def set_bg_from_local(relative_path):
    image_file = caminho_atual / relative_path
    if image_file.exists():
        with open(image_file, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()
        css = f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
                url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Imagem de fundo não encontrada: {image_file}")

# === Aplica fundo ===
set_bg_from_local("../assets/jrnd_background.jpg")

# === Interface Streamlit ===
st.title("🧭 Jornada do Personagem")
st.text('''
🧭 Jornada do Personagem: Acompanhe Sua Lenda em Tempo Real

Aqui é onde sua história em Elden Ring ganha forma e memória. A página Jornada do Personagem foi criada para que você acompanhe de perto o seu progresso no jogo — quais chefes já derrotou, quais áreas explorou e qual o status atual da sua aventura.

Mas não para por aí: compare sua jornada com outros personagens que você criou ou com builds diferentes que está testando. Descubra quais estilos de jogo funcionam melhor para cada situação, veja o que falta conquistar e transforme sua experiência em algo estratégico e recompensador.

🌟 Seja um mago imbatível, um guerreiro imortal ou algo entre os dois — aqui você vê tudo isso acontecer, passo a passo.        
        ''')

jogadores_df = obter_jogadores()
personagens = jogadores_df["nome_personagem"].tolist()

if not personagens:
    st.warning("Nenhum personagem cadastrado.")
else:
    personagem_escolhido = st.selectbox("🎮 Escolha seu personagem", personagens)

    if personagem_escolhido:
        sincronizar_jornada_com_bosses()
        df_bosses_lvl = obter_bosses_com_level()
        criar_ou_atualizar_jornada(personagem_escolhido, df_bosses_lvl)
        st.success(f"Jornada ativa para: {personagem_escolhido}")


        # === Métricas ===
        col1, col2, col3 = st.columns(3)
        col1.metric("👹 Total de Bosses Únicos", obter_total_bosses_distintos())

        with sqlite3.connect(DB_PATH) as conn:
            vivos = pd.read_sql_query(
                "SELECT COUNT(*) as total FROM jornada WHERE personagem = ? AND status_boss = 'Vivo'",
                conn, params=(personagem_escolhido,)
            )["total"][0]
            mortos = pd.read_sql_query(
                "SELECT COUNT(*) as total FROM jornada WHERE personagem = ? AND status_boss = 'Morto'",
                conn, params=(personagem_escolhido,)
            )["total"][0]

        col2.metric("😡 Bosses a sua espera", vivos)
        col3.metric("☠️ Bosses Exterminados", mortos)

        # === Preparação dos dados para o gráfico de barras ===
        with sqlite3.connect(DB_PATH) as conn:
            df_bar = pd.read_sql_query("""
                SELECT level, status_boss, COUNT(*) as total
                FROM jornada
                WHERE personagem = ?
                GROUP BY level, status_boss
            """, conn, params=(personagem_escolhido,))

        pivot_df = pd.DataFrame()
        if not df_bar.empty:
            pivot_df = df_bar.pivot_table(
                index="level", columns="status_boss", values="total", fill_value=0
            )
            pivot_df["total"] = pivot_df.sum(axis=1)
            for status in ["Vivo", "Morto"]:
                if status not in pivot_df:
                    pivot_df[status] = 0
                pivot_df[status + "_pct"] = (pivot_df[status] / pivot_df["total"]) * 100
            pivot_df = pivot_df.reset_index()
            # Extrai prefixo numérico do nível para ordenação
            pivot_df["level_ord"] = pivot_df["level"].str.extract(r"^(\d{2})").astype(float)
            pivot_df = pivot_df.sort_values(by="level_ord", ascending=False, na_position="last")


        # Altura proporcional ao número de níveis (mesmo para o gráfico de rosca)
        altura_grafico = max(4, len(pivot_df)*0.4)

        # === Gráficos ===
        st.subheader("📊 Progresso de Extermínio")
        col1, col2 = st.columns(2)

        # === Gráfico de Rosca ===
        with col1:
            contagem = pd.DataFrame({
                "status_boss": ["Vivo", "Morto"],
                "total": [vivos, mortos]
            })

            if contagem["total"].sum() > 0:
                fig = px.pie(
                    contagem,
                    names="status_boss",
                    values="total",
                    color="status_boss",
                    color_discrete_map={
                        "Vivo": "#EBA300",
                        "Morto": "#919191"
                    },
                    hole=0.4,
                    hover_data=["total", "status_boss"]
                )
                fig.update_traces(textinfo='percent+label')
                fig.update_layout(height=altura_grafico * 80)  # altura ajustada
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Nenhum progresso registrado para este personagem ainda.")

        # === Gráfico de Barras Horizontais por Level e Status (%) ===
        with col2:
            if not pivot_df.empty:
                fig2 = go.Figure()

                fig2.add_trace(go.Bar(
                    y=pivot_df["level"],
                    x=pivot_df["Vivo_pct"],
                    name="Vivo",
                    orientation='h',
                    marker_color="#EBA300",
                    hovertemplate="% de Bosses Vivo: %{x:.1f}%<br>Level: %{y}<extra></extra>"
                ))

                fig2.add_trace(go.Bar(
                    y=pivot_df["level"],
                    x=pivot_df["Morto_pct"],
                    name="Morto",
                    orientation='h',
                    marker_color="#919191",
                    hovertemplate="% de Bosses Morto: %{x:.1f}%<br>Level: %{y}<extra></extra>"
                ))

                fig2.update_layout(
                    barmode='stack',
                    title="Distribuição por Nível",
                    xaxis=dict(title="% de Bosses", range=[0, 100]),
                    yaxis=dict(title="Level"),
                    height=int(altura_grafico * 100),  # ajusta dinamicamente altura
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )

                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("📉 Nenhum dado para exibir gráfico por nível.")

        # === Linha 02: Gráfico de Barras Verticais (% por Localidade) ===
        st.markdown("### 🏙️ Distribuição por Localidade")

        with sqlite3.connect(DB_PATH) as conn:
            df_locais = pd.read_sql_query("""
                SELECT localidade, status_boss, COUNT(*) as total
                FROM jornada
                WHERE personagem = ?
                GROUP BY localidade, status_boss
            """, conn, params=(personagem_escolhido,))

        if not df_locais.empty:
            # Total por localidade
            total_por_local = df_locais.groupby("localidade")["total"].sum().reset_index(name="total_local")

            # Junta para cálculo de percentual
            df_locais = pd.merge(df_locais, total_por_local, on="localidade")
            df_locais["percentual"] = (df_locais["total"] / df_locais["total_local"]) * 100

            # Extrai ordem do level para ordenação
            with sqlite3.connect(DB_PATH) as conn:
                levels = pd.read_sql_query("SELECT DISTINCT localidade, level FROM boss_levels", conn)
            levels["level_ord"] = levels["level"].str.extract(r"^(\d+)").astype(float)
            df_locais = pd.merge(df_locais, levels[["localidade", "level_ord"]], on="localidade", how="left")
            df_locais = df_locais.sort_values(by="level_ord", na_position="last")

            # Gráfico com tooltips
            fig3 = px.bar(
                df_locais,
                x="localidade",
                y="percentual",
                color="status_boss",
                text_auto=".1f",
                labels={"percentual": "% de Bosses", "localidade": "Localidade", "status_boss": "Status"},
                hover_data={
                    "localidade": True,
                    "status_boss": True,
                    "percentual": ':.2f',
                    "total": True,
                },
                barmode="stack",
                color_discrete_map={
                    "Vivo": "#EBA300",
                    "Morto": "#919191"
                }
            )
            fig3.update_layout(
                yaxis=dict(range=[0, 100]),
                title="Distribuição de Status por Localidade",
                xaxis_tickangle=-45,
                height=500,
                legend_title="Status"
            )
            st.plotly_chart(fig3, use_container_width=True)

        else:
            st.info("📊 Nenhuma localidade com dados suficientes para o gráfico de barras verticais.")

        # === Gráfico de Boss por runas ===
        st.markdown("### 💰 Bosses por Quantidade de Runas")

        # === Obtem localidades com level_ord para ordenação ===
        with sqlite3.connect(DB_PATH) as conn:
            localidades_df = pd.read_sql_query("""
                SELECT DISTINCT j.localidade, bl.level
                FROM jornada j
                LEFT JOIN boss_levels bl
                    ON LOWER(TRIM(j.localidade)) = LOWER(TRIM(bl.localidade))
                WHERE j.personagem = ?
            """, conn, params=(personagem_escolhido,))

        # Extrai número de ordem (os dois primeiros dígitos) do level
        localidades_df["level_ord"] = localidades_df["level"].str.extract(r"^(\d+)").astype(float)

        # Ordena as localidades pela ordem do level
        localidades_ordenadas = (
            localidades_df.sort_values(by="level_ord", na_position="last")["localidade"]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        # === Filtro ordenado ===
        localidade_escolhida = st.selectbox("📍 Filtrar por Localidade", localidades_ordenadas, key="filtro_localidade_runas")

        # === Consulta bosses da localidade com runas ===
        with sqlite3.connect(DB_PATH) as conn:
            df_runas = pd.read_sql_query("""
                SELECT nome, runes
                FROM jornada
                WHERE personagem = ? AND localidade = ?
            """, conn, params=(personagem_escolhido, localidade_escolhida))

        df_runas = df_runas.dropna(subset=["runes"]).sort_values(by="runes", ascending=False)

        if not df_runas.empty:
            fig4 = px.bar(
                df_runas,
                x="nome",
                y="runes",
                text="runes",
                title=f"💰 Bosses em {localidade_escolhida} - Runas",
                labels={"nome": "Boss", "runes": "Quantidade de Runas"},
                color_discrete_sequence=["#EBA300"]
            )

            fig4.update_traces(
                hovertemplate="Boss: %{x}<br>Runas: %{y}<extra></extra>",
                textposition="outside"
            )
            fig4.update_layout(
                yaxis=dict(range=[0, df_runas["runes"].max() * 1.1]),
                xaxis_tickangle=-45,
                xaxis_title="Boss",
                yaxis_title="Runas",
                height=500
            )

            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("📉 Nenhum dado de runas para essa localidade.")


        # === Tabela de progresso ===    
 
        st.subheader(f"📋 Progresso de {personagem_escolhido} (Vivos ordenados por Level e Runas)")

        # === Carrega e filtra ===
        with sqlite3.connect(DB_PATH) as conn:
            df_jornada = pd.read_sql_query("""
                SELECT * FROM jornada
                WHERE personagem = ? AND status_boss = 'Vivo'
            """, conn, params=(personagem_escolhido,))

        # Verifica se 'localidade' está presente
        if "localidade" not in df_jornada.columns:
            st.warning("⚠️ A coluna 'localidade' não está presente na jornada.")
            st.stop()

        # Ordena por level e runes
        df_jornada["level_ord"] = df_jornada["level"].str.extract(r"^(\d{2})").astype(float)
        df_jornada = df_jornada.sort_values(by=["level_ord", "runes"], ascending=[True, True])
        df_jornada.drop(columns=["id", "level_ord"], errors="ignore", inplace=True)
        df_jornada.reset_index(drop=True, inplace=True)

        # === Estilo com gradiente por localidade ===
        from matplotlib import cm
        import matplotlib.colors as mcolors

        def cor_por_runes(runes, localidade):
            grupo = df_jornada[df_jornada["localidade"] == localidade]
            min_r = grupo["runes"].min()
            max_r = grupo["runes"].max()
            if pd.isna(runes) or max_r == min_r:
                return ""
            norm = (runes - min_r) / (max_r - min_r)
            rgba = cm.get_cmap("RdYlGn_r")(norm)  # verde (baixo) a vermelho (alto)
            hex_color = mcolors.to_hex(rgba)
            return f"background-color: {hex_color}; color: black"

        # Aplica gradiente nas colunas 'nome' e 'runes' com base nas runas por localidade
        styled_df = df_jornada.style.apply(
            lambda row: pd.Series({
                "nome": cor_por_runes(row["runes"], row["localidade"]),
                "runes": cor_por_runes(row["runes"], row["localidade"])
            }),
            axis=1
        )

        st.dataframe(styled_df, use_container_width=True)




        # === Formulário para atualização ===
        st.markdown("---")
        st.subheader("🔪 Atualizar Progresso de Bosses")
        st.text("Clique em Confirmar para aplicar filtro e salvar alteração.")

        with sqlite3.connect(DB_PATH) as conn:
            df_jornada_vivos = pd.read_sql_query("""
                SELECT j.id, j.nome, j.localidade, j.status_boss, bl.level
                FROM jornada j
                LEFT JOIN boss_levels bl
                    ON LOWER(TRIM(j.localidade)) = LOWER(TRIM(bl.localidade))
                   AND LOWER(TRIM(j.nome)) = LOWER(TRIM(bl.nome))
                WHERE j.personagem = ? AND j.status_boss = 'Vivo'
            """, conn, params=(personagem_escolhido,))

        if df_jornada_vivos.empty:
            st.info("🎉 Todos os bosses deste personagem já foram exterminados!")
        else:
            df_localidades = (
                df_jornada_vivos[["localidade", "level"]]
                .drop_duplicates()
                .sort_values(by="level", na_position="last")
            )
            localidades_ordenadas = df_localidades["localidade"].tolist()

            with st.form("form_exterminio_boss"):
                col1, col2 = st.columns(2)

                localidade_escolhida = col1.selectbox("📍 Escolha a Localidade", localidades_ordenadas)
                df_filtrado = df_jornada_vivos[df_jornada_vivos["localidade"] == localidade_escolhida]

                if df_filtrado.empty:
                    col2.warning("Nenhum boss vivo nesta localidade.")
                else:
                    # Adiciona opção extra
                    nomes_boss = ["Todos os Boss da Localidade"] + df_filtrado["nome"].tolist()
                    nome_boss_escolhido = col2.selectbox("👹 Escolha o Boss", nomes_boss)

                    confirmacao = st.radio("Boss foi exterminado?", ["Não", "Sim"], horizontal=True)

                    if st.form_submit_button("✅ Confirmar") and confirmacao == "Sim":
                        
                        with sqlite3.connect(DB_PATH) as conn:
                            if nome_boss_escolhido == "Todos os Boss da Localidade":
                                ids_para_atualizar = df_filtrado["id"].tolist()
                                conn.executemany(
                                    "UPDATE jornada SET status_boss = 'Morto' WHERE id = ?",
                                    [(int(boss_id),) for boss_id in ids_para_atualizar]
                                )
                                st.success(f"Todos os bosses da localidade '{localidade_escolhida}' foram marcados como exterminados.")
                            else:
                                id_boss = df_filtrado[df_filtrado["nome"] == nome_boss_escolhido]["id"].values[0]
                                conn.execute(
                                    "UPDATE jornada SET status_boss = 'Morto' WHERE id = ?",
                                    (int(id_boss),)
                                )
                                st.success(f"Boss '{nome_boss_escolhido}' foi marcado como exterminado.")
                            conn.commit()
                        st.rerun()
