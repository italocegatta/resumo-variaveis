from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import pandas as pd
import numpy as np  
import janitor
import streamlit as st
from io import BytesIO

@st.cache_data
def convert_df(df):
    return df.clean_names().to_csv(sep = ';', index=False, decimal=",").encode('utf-8')

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    df = df.copy()

    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Escolha as colunas para filtrar", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Muitas colunas, informe um padrão... {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df, to_filter_columns

def resume_tabela(df, colunas_agrupar):

    colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()

        # Calculando as estatísticas de resumo
    resultados = df.groupby(colunas_agrupar).agg({
        col: ['count',
            'mean',
            'min',
            lambda x: x.quantile(0.05), 
            lambda x: x.quantile(0.10),
            lambda x: x.quantile(0.15),
            lambda x: x.quantile(0.20), 
            lambda x: x.quantile(0.25),
            lambda x: x.quantile(0.30),
            lambda x: x.quantile(0.35),
            lambda x: x.quantile(0.40), 
            lambda x: x.quantile(0.45),
            lambda x: x.quantile(0.50),
            lambda x: x.quantile(0.55),
            lambda x: x.quantile(0.60),
            lambda x: x.quantile(0.65),
            lambda x: x.quantile(0.70), 
            lambda x: x.quantile(0.75),
            lambda x: x.quantile(0.80),
            lambda x: x.quantile(0.85),
            lambda x: x.quantile(0.90),
            lambda x: x.quantile(0.95),
            'max'] for col in colunas_numericas
    })
    resultados.columns = ['_'.join(col).strip() for col in resultados.columns.values]

    renomear = {}
    for col in colunas_numericas:
        renomear[col+'_count'] = col+'__contagem'
        renomear[col+'_mean'] = col+'__média'
        renomear[col+'_min'] = col+'__mínimo'
        renomear[col+'_max'] = col+'__máximo'
        renomear[col+'_<lambda_0>'] = col+'__p05'
        renomear[col+'_<lambda_1>'] = col+'__p10'        
        renomear[col+'_<lambda_2>'] = col+'__p15'
        renomear[col+'_<lambda_3>'] = col+'__p20'
        renomear[col+'_<lambda_4>'] = col+'__p25'
        renomear[col+'_<lambda_5>'] = col+'__p30'
        renomear[col+'_<lambda_6>'] = col+'__p35'
        renomear[col+'_<lambda_7>'] = col+'__p40'
        renomear[col+'_<lambda_8>'] = col+'__p45'
        renomear[col+'_<lambda_9>'] = col+'__p50'
        renomear[col+'_<lambda_10>'] = col+'__p55'
        renomear[col+'_<lambda_11>'] = col+'__p60'
        renomear[col+'_<lambda_12>'] = col+'__p65'        
        renomear[col+'_<lambda_13>'] = col+'__p70'
        renomear[col+'_<lambda_14>'] = col+'__p75'
        renomear[col+'_<lambda_15>'] = col+'__p80'
        renomear[col+'_<lambda_16>'] = col+'__p85'
        renomear[col+'_<lambda_17>'] = col+'__p90'
        renomear[col+'_<lambda_18>'] = col+'__p95'
    resultados.rename(columns=renomear, inplace=True)

    resultados = (resultados
        .reset_index()
        .pivot_longer(
            index = colunas_agrupar,
            names_to=('Variável', '.value'), 
            names_sep='__', 
            sort_by_appearance=True
        )
    )

    return resultados

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    writer.save()
    processed_data = output.getvalue()
    return processed_data

##############################################

st.set_page_config(layout="wide")

# st.session_state.data = pd.read_excel("pages/exemplo_ceo.xlsx")

def df_to_download(df):
    csv_string = df.to_csv(index=False, sep=';', decimal=',', encoding='utf-8-sig')
    csv_bytes = csv_string.encode('utf-8-sig')
    return csv_bytes


if 'data' in st.session_state:
    
    df_filtrado, lst_fatores = filter_dataframe(st.session_state.data)

    with st.container(): 
        st.title("Tabela filtrada") 
        st.dataframe(df_filtrado)

        st.download_button(
            label="Download",
            data=df_to_download(df_filtrado),
            file_name="tabela_filtrada.csv",
            mime="text/csv",
        )

    if len(lst_fatores) > 0:
        with st.container(): 
            st.title("Estatísticas de resumo")
            df_resumo = resume_tabela(df_filtrado, lst_fatores)
            st.dataframe(df_resumo)

            st.download_button(
                label="Download",
                data=df_to_download(df_resumo),
                file_name='tabela_estatisticas.csv',
                mime='text/csv'
            )
