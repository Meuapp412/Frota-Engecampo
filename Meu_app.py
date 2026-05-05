import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Frota Engecampo", page_icon="🚗", layout="centered")

# --- LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.subheader("Frota Engecampo - Acesso Restrito")
        password = st.text_input("Senha de Acesso", type="password")
        if st.button("Entrar"):
            if password == "engecampo2024":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Senha incorreta")
        return False
    return True


if check_password():

    # 🔐 AUTENTICAÇÃO GOOGLE
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["connections"]["gsheets"], scopes=scope
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1A-W4nY7mb0M8iUrVWgkrjq4ZN8nHU15TGMGMyYLl9UU/edit"
    )

    sheet_registros = spreadsheet.worksheet("Página1")
    sheet_veiculos = spreadsheet.worksheet("Lista_Veiculos")

    # 📄 VEÍCULOS
    df_veiculos = pd.DataFrame(sheet_veiculos.get_all_records())

    opcoes_veiculos = df_veiculos.apply(
        lambda x: f"{x['Placa']} - {x['Veiculo']}", axis=1
    ).tolist()

    st.title("🚗 Registro de Utilização")

    veiculo_selecionado = st.selectbox("Selecione o Veículo", options=opcoes_veiculos)

    # 📄 REGISTROS
    dados = sheet_registros.get_all_records()
    df_registros = pd.DataFrame(dados)

    # 🔎 KM AUTOMÁTICO POR PLACA
    km_inicial_auto = 0

    if not df_registros.empty:
        placa_atual = veiculo_selecionado.split(" - ")[0]
        df_filtrado = df_registros[df_registros["placa"] == placa_atual]

        if not df_filtrado.empty:
            df_filtrado["kf"] = pd.to_numeric(df_filtrado["kf"], errors="coerce")
            km_inicial_auto = int(df_filtrado["kf"].max())

    st.info(f"Último KM registrado para este veículo: {km_inicial_auto}")

    # 📝 FORMULÁRIO
    with st.form("form_viagem", clear_on_submit=True):

        # 📅 NOVO CAMPO DE DATA
        data_viagem = st.date_input("Data da Viagem", value=datetime.today())

        nome = st.text_input("Nome do Condutor").upper()
        dest = st.text_input("Destino / Percurso").upper()

        col1, col2 = st.columns(2)
        ki = col1.number_input("Km Inicial", value=int(km_inicial_auto), step=1)
        kf = col2.number_input("Km Final", step=1)

        col3, col4 = st.columns(2)
        h1 = col3.time_input("Horário de Saída")
        h2 = col4.time_input("Horário de Chegada")

        submitted = st.form_submit_button("SALVAR REGISTRO")

        if submitted:

            if not nome or not dest:
                st.error("Preencha Nome e Destino")

            elif kf < ki:
                st.error("Km final não pode ser menor que o Km inicial")

            else:
                placa_final = veiculo_selecionado.split(" - ")[0]

                nova_linha = [
                    data_viagem.strftime("%d/%m/%Y"),  # 📅 DATA ESCOLHIDA
                    placa_final,
                    nome,
                    dest,
                    ki,
                    kf,
                    kf - ki,
                    h1.strftime("%H:%M"),
                    h2.strftime("%H:%M")
                ]

                sheet_registros.append_row(nova_linha)

                st.success(f"✅ Registro salvo para o veículo {placa_final}!")

    # =============================
    # 📊 DASHBOARD POR VEÍCULO
    # =============================

    st.divider()
    st.subheader("📊 Dashboard do Veículo")

    if not df_registros.empty:

        placa_atual = veiculo_selecionado.split(" - ")[0]
        df_filtrado = df_registros[df_registros["placa"] == placa_atual]

        if not df_filtrado.empty:

            df_filtrado["km_r"] = pd.to_numeric(df_filtrado["km_r"], errors="coerce")

            total_km = df_filtrado["km_r"].sum()
            total_viagens = len(df_filtrado)

            col1, col2 = st.columns(2)
            col1.metric("Total KM Rodado", f"{total_km:.0f} km")
            col2.metric("Total de Viagens", total_viagens)

            st.line_chart(df_filtrado["km_r"])

        else:
            st.info("Nenhum registro para este veículo ainda.")

    else:
        st.info("Sem dados para exibir.")
