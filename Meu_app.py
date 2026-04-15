import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "registro_veiculos.db")
EXCEL_PATH = os.path.join(BASE_DIR, "relatorio_utilizacao.xlsx")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS utilizacao 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, condutor TEXT, 
                  destino TEXT, km_i REAL, km_f REAL, km_r REAL, h_de TEXT, h_as TEXT)''')
    conn.commit()
    conn.close()

def salvar(d):
    conn = sqlite3.connect(DB_PATH)
    # Calcula km rodado
    km_r = d['km_f'] - d['km_i']
    c = conn.cursor()
    c.execute('''INSERT INTO utilizacao (data, condutor, destino, km_i, km_f, km_r, h_de, h_as)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (d['data'], d['condutor'], d['destino'], d['km_i'], d['km_f'], km_r, d['h_de'], d['h_as']))
    conn.commit()
    conn.close()
    # Gera o Excel
    conn = sqlite3.connect(DB_PATH)
    pd.read_sql("SELECT * FROM utilizacao", conn).to_excel(EXCEL_PATH, index=False)
    conn.close()

init_db()

st.set_page_config(page_title="Frota Engecampo", layout="centered")
st.title("🚗 Registro de Utilização")
st.info("**Veículo:** POLO TRACK | **Placa:** SCE5C86 | **Op:** 23350-LOGUN")

with st.form("form_viagem", clear_on_submit=True):
    nome = st.text_input("Nome do Condutor").upper()
    dest = st.text_input("Destino").upper()
    col1, col2 = st.columns(2)
    ki = col1.number_input("Km Inicial", step=1.0)
    kf = col2.number_input("Km Final", step=1.0)
    col3, col4 = st.columns(2)
    h1 = col3.time_input("Horário Saída")
    h2 = col4.time_input("Horário Chegada")
    
    if st.form_submit_button("SALVAR REGISTRO"):
        if nome and dest and kf > ki:
            dados = {
                "data": datetime.now().strftime("%d/%m/%Y"),
                "condutor": nome, "destino": dest,
                "km_i": ki, "km_f": kf,
                "h_de": h1.strftime("%H:%M"), "h_as": h2.strftime("%H:%M")
            }
            salvar(dados)
            st.success(f"✅ Salvo! Excel atualizado em: {EXCEL_PATH}")
        else:
            st.error("Preencha tudo corretamente (Km Final deve ser maior que Inicial)")