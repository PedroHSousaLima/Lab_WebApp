import streamlit as st
import pandas as pd
import os
import sys
import base64
from pathlib import Path

# === Adiciona caminho do módulo db_boss.py ===
caminho_atual = Path(__file__).resolve().parent
CAMINHO_DADOS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Dados'))
if CAMINHO_DADOS not in sys.path:
    sys.path.append(CAMINHO_DADOS)

from db_boss import criar_tabela_boss, listar_bosses, atualizar_boss

# === Inicializa banco e tabela ===
criar_tabela_boss()

# === Configuração da Página ===
st.set_page_config(page_title="Elden Ring - Home", layout="wide")

# === Função para definir imagem de fundo com escurecimento ===
def set_bg_from_local(relative_path):
    image_file = caminho_atual / relative_path
    if image_file.exists():
        with open(image_file, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()
        css = f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)),
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
set_bg_from_local("../assets/boss_background.jpg")

# === Título da página ===
st.title("👹 Lista de Bosses")

# === Feedback de atualização ===
if "atualizado" not in st.session_state:
    st.session_state["atualizado"] = False

if st.session_state["atualizado"]:
    st.success("✅ Dados atualizados com sucesso.")
    st.session_state["atualizado"] = False

# === Carrega dados do banco ===
try:
    df = listar_bosses()

    if df.empty:
        st.warning("Nenhum boss encontrado no banco.")
    else:
        # === Métricas resumo ===
        col1, col2, col3 = st.columns(3)
        col1.metric("🧟 Total de Bosses", len(df))
        col2.metric("💰 Total de Runes", f"{pd.to_numeric(df['Runes'], errors='coerce').fillna(0).sum():,.0f}".replace(",", "."))
        col3.metric("📍 Localidades únicas", df["Localidade"].nunique())

        # === Filtros ===
        with st.expander("🎯 Filtrar Bosses", expanded=True):
            c1, c2 = st.columns(2)
            nome_boss = c1.text_input("🔎 Buscar por nome do Boss").strip().lower()
            localidades = ["Todas"] + sorted(df["Localidade"].dropna().unique())
            localidade_escolhida = c2.selectbox("📍 Escolha a Localidade", localidades)

        df_filtrado = df.copy()
        if nome_boss:
            df_filtrado = df_filtrado[df_filtrado["Nome"].str.lower().str.contains(nome_boss)]
        if localidade_escolhida != "Todas":
            df_filtrado = df_filtrado[df_filtrado["Localidade"] == localidade_escolhida]

        # === Resultado dos Filtros ===
        st.subheader("📋 Resultado dos Filtros")
        if df_filtrado.empty:
            st.warning("Nenhum boss encontrado com os critérios selecionados.")
        else:
            st.dataframe(df_filtrado.drop(columns=["ID"]), use_container_width=True)

            if len(df_filtrado) == 1:
                boss = df_filtrado.iloc[0]
                
                st.markdown("---")
                st.markdown(f"""
                <div style="background-color:#0E1117; padding: 20px; border-radius: 10px; border: 1px solid #ccc;">
                    <h4 style="color:#b30000;">👹 Boss Escolhido: <span style="color:#fafafa;">{boss['Nome']}</span></h4>
                    <ul>
                        <li><strong>📍 Localização:</strong> {boss['Localidade']}</li>
                        <li><strong>🗺 Área:</strong> {boss['Location']}</li>
                        <li><strong>💰 Runes:</strong> {boss['Runes']:,}</li>
                        <li><strong>🛡️ Resistência:</strong> {boss['Resistência']}</li>
                        <li><strong>⚔️ Fraqueza:</strong> {boss['Tipo de Dano Preferido']}</li>
                        <li><strong>🎁 Loot:</strong> {boss['Loot']}</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                st.divider()

        # === Atualizar dados ===
        with st.expander("✏️ Atualizar Dados de um Boss"):
            # Mapeia: "ID - Nome" -> ID
            boss_opcoes = {f"{row['ID']} - {row['Nome']}": row['ID'] for _, row in df.iterrows()}
            boss_selecionado_str = st.selectbox("Escolha o Boss para editar:", list(boss_opcoes.keys()))

            if boss_selecionado_str:
                id_boss = boss_opcoes[boss_selecionado_str]
                boss_dados = df[df["ID"] == id_boss].iloc[0]

                with st.form("form_update_boss", clear_on_submit=False):
                    novo_nome = st.text_input("Nome", boss_dados["Nome"])
                    nova_localidade = st.text_input("Localidade", boss_dados["Localidade"])
                    nova_location = st.text_input("Location", boss_dados["Location"])
                    novas_runes = st.number_input("Runes", min_value=0, value=int(boss_dados["Runes"]), step=100)
                    novo_loot = st.text_input("Loot", boss_dados["Loot"])
                    nova_stance = st.text_input("Stance", boss_dados["Stance"])
                    novo_dano = st.text_input("Tipo de Dano Preferido", boss_dados["Tipo de Dano Preferido"])
                    nova_resistencia = st.text_input("Resistência", boss_dados["Resistência"])

                    if st.form_submit_button("💾 Salvar Alterações"):
                        try:
                            atualizar_boss(
                                id_boss,
                                novo_nome.strip(),
                                nova_localidade.strip(),
                                nova_location.strip(),
                                novas_runes,
                                novo_loot.strip(),
                                nova_stance.strip(),
                                novo_dano.strip(),
                                nova_resistencia.strip()
                            )
                            st.session_state["atualizado"] = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar boss: {e}")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")

# === Tabela completa ===
st.subheader("📊 Visualização Completa da Tabela de Bosses")
try:
    st.dataframe(df, use_container_width=True, hide_index=True)
except Exception as e:
    st.error(f"Erro ao exibir a visualização: {e}")
