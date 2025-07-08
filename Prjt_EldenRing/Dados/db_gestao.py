import sqlite3
import os

# Caminho do banco
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, 'dados.db')

# Conexão e limpeza
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jornada")
    conn.commit()

print("✅ Todas as linhas da tabela 'jornada' foram apagadas com sucesso.")
