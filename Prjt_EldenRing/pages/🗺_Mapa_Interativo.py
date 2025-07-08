import streamlit as st

st.set_page_config(page_title="Mapa Interativo", layout="wide")

st.title("🗺️ Mapa Interativo - The Lands Between")
st.markdown("""
Explore o mapa interativo completo de Elden Ring com todos os marcadores, locais e segredos.
O mapa é fornecido pelo site [MapGenie.io](https://mapgenie.io/elden-ring/maps/the-lands-between).

Este mapa serve para te auxiliar em sua jornada, o mesmo contém uma versão pagar com mais possibilidades de uso.
""")

st.markdown("---")

# Incorpora o mapa do MapGenie
map_url = "https://mapgenie.io/elden-ring/maps/the-lands-between"
st.components.v1.iframe(map_url, height=800, scrolling=True)
