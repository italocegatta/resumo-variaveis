import streamlit as st
import pandas as pd

st.title("Upload de Dados")
    
uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    selected_sheet = st.selectbox("Selecione a aba", sheet_names)
    
    if st.button("Carregar dados"):
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        st.session_state.data = df  # Salva o DataFrame no estado da sessão
        st.write(f"Aba {selected_sheet} carregada com sucesso!")

        st.write(df)
