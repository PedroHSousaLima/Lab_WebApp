import streamlit as st
import pandas as pd
import os

st.title("🧭 Jornada do Jogador")

try:
    df = pd.read_csv("Dados/jornada_player.csv")
    st.dataframe(df)
except FileNotFoundError:
    st.error("Arquivo 'jornada_player.csv' não encontrado.")
