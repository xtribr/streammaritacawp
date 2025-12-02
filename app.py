import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(page_title="Demo Streamlit", layout="wide")

st.title("Demo Streamlit — Exemplo simples")
st.write("Carregue um CSV por URL ou use os dados de exemplo abaixo.")

url = st.text_input("URL do CSV (opcional):")

df = None
if url:
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        df = pd.read_csv(StringIO(resp.text))
        st.success("CSV carregado com sucesso")
    except Exception as e:
        st.error(f"Falha ao carregar o CSV: {e}")

if df is None:
    df = pd.DataFrame({"x": list(range(10)), "y": [i ** 2 for i in range(10)]})
    st.info("Usando dados de exemplo")

st.subheader("Visualização dos dados")
st.dataframe(df)

st.subheader("Gráfico")
if st.button("Gerar gráfico"):
    fig, ax = plt.subplots()
    # Se encontrar colunas x e y, usa-as; caso contrário, plota todas as colunas numéricas
    if "x" in df.columns and "y" in df.columns:
        ax.plot(df["x"], df["y"], marker="o")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
    else:
        df.select_dtypes("number").plot(ax=ax)
    ax.set_title("Gráfico gerado")
    st.pyplot(fig)

st.write("Executar: `streamlit run app.py`")
