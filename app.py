import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import pytesseract
from PIL import Image
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BrainX Neural Architect",
    page_icon="🧠",
    layout="centered", 
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS (Identidade XTRI) ---
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    h1 {color: #0F172A; font-size: 2.2rem;}
    h2 {color: #1E293B; font-size: 1.5rem;}
    .stButton>button {
        background-color: #0F172A;
        color: white;
        border-radius: 8px;
        height: 3.5em;
        width: 100%;
        font-weight: bold;
        border: 1px solid #1E293B;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background-color: #334155;
        border-color: #475569;
    }
    .stFileUploader {border-radius: 10px; border: 2px dashed #0F172A; padding: 15px;}
    .stSuccess {background-color: #d1e7dd; color: #0f5132; border-radius: 8px;}
    .stInfo {background-color: #e0f2fe; color: #0369a1; border-radius: 8px;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.image("https://img.icons8.com/color/96/000000/brain--v1.png", width=70)
st.title("BrainX Neural Architect")
st.markdown("### Núcleo de Inteligência Artificial | **Powered by XTRI**")
st.markdown("---")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Configuração BrainX")

if "api_gpt_assistente" in st.secrets:
    api_key = st.secrets["api_gpt_assistente"]
    st.sidebar.success("✅ BrainX Conectado")
else:
    api_key = st.sidebar.text_input("Chave API:", type="password")

st.sidebar.markdown("---")
modo = st.sidebar.radio("Ferramenta:", 
    ["📸 Resolver Questão (OCR)", "🧭 Rota de Estudos por TRI"]
)
st.sidebar.info("v3.4 Stable | Powered by XTRI")

# --- FUNÇÕES AUXILIARES ---

@st.cache_data(show_spinner=False)
def chamar_brainx(prompt, temperatura=0.0):
    if not api_key: return "⚠️ ERRO: Chave API ausente."
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "sabia-3", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperatura,
        "max_tokens": 3500
    }
    
    try:
        response = requests.post("https://chat.maritaca.ai/api/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Erro BrainX API ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Erro Conexão: {str(e)}"

def extrair_texto_imagem(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        texto = pytesseract.image_to_string(image, lang='por')
        return texto
    except Exception as e:
        st.error(f"Erro no OCR: {e}")
        return None

# ==============================================================================
# MÓDULO 1: RESOLVER QUESTÃO (OCR)
# ==============================================================================
if modo == "📸 Resolver Questão (OCR)":
    st.header("🎓 Resolução Sênior (BrainX)")
    st.info("Faça upload do **PRINT** da questão ou digite o texto.")
    
    # 1. Upload
    texto_extraido = ""
    arquivo = st.file_uploader("Subir Print da Tela (Imagem):", type=["png", "jpg", "jpeg"])
    
    if arquivo:
        with st.spinner("👁️ BrainX lendo imagem..."):
            texto_extraido = extrair_texto_imagem(arquivo)
            if texto_extraido:
                st.success("Imagem processada!")

    # 2. Texto
    st.markdown("**Confira ou digite o enunciado:**")
    input_final = st.text_area("", value=texto_extraido if texto_extraido else "", height=250, placeholder="Cole a questão aqui...")

    # 3. Ação
    if st.button("Resolver com Protocolo BrainX"):
        if not input_final:
            st.warning("⚠️ Precisamos da questão (Imagem ou Texto).")
        else:
            prompt_final = f"""
VOCÊ É O BRAINX (Powered by XTRI). RESOLVA SEGUINDO O PROTOCOLO DE ELITE:

PASSO 1: ANÁLISE INICIAL (Dados e Comando)
PASSO 2: PLANEJAMENTO (Conceitos)
PASSO 3: RESOLUÇÃO DETALHADA (Cálculo/Lógica)
PASSO 4: VALIDAÇÃO (Prova real)
PASSO 5: ANÁLISE DAS ALTERNATIVAS (Justifique erros dos distratores)
PASSO 6: ESCOLHA FINAL
PASSO 7: VERIFICAÇÃO FINAL

QUESTÃO DO ALUNO (OCR):
{input_final}

RESPOSTA FINAL:
Pule uma linha e escreva: "**GABARITO: [Letra]**"
"""
            with st.spinner("🧠 BrainX processando raciocínio..."):
                resposta = chamar_brainx(prompt_final)
                st.markdown("### 🧠 Resolução Detalhada")
                st.markdown(resposta)

# ==============================================================================
# MÓDULO 2: ROTA TRI (CSV REAL)
# ==============================================================================
elif modo == "🧭 Rota de Estudos por TRI":
    st.header("📊 Rota Estratégica (TRI)")
    st.markdown("O BrainX irá consultar a base **'conteudos ENEM separados por TRI.csv'** para calibrar sua rota.")
    
    # 1. Configurações
    st.markdown("**Defina seu perfil:**")
    area_foco = st.selectbox("Área de Foco:", ["Matemática e suas Tecnologias", "Ciências da Natureza", "Ciências Humanas", "Linguagens e Códigos"])
    nivel_atual = st.select_slider("Seu Nível Atual:", options=["Iniciante (<500)", "Intermediário (500-700)", "Avançado (>700)", "Elite (800+)"], value="Intermediário (500-700)")

    # 2. Ação
    if st.button("Gerar Rota XTRI"):
        
        prompt_rota = f"""
Atue como o BrainX Architect (Especialista em TRI e Matriz de Referência do ENEM).
O aluno deseja aumentar sua nota em **{area_foco}**.
Nível Atual: **{nivel_atual}**.

ACESSO À BASE DE CONHECIMENTO:
Consulte o arquivo "conteudos ENEM separados por TRI.csv" da nossa base XTRI.

TAREFA OBRIGATÓRIA:
1. **Diagnóstico Matriz:** Explique quais competências da Matriz de Referência este nível de aluno precisa dominar.
2. **Tabela de Prioridade (Mínimo 10 Itens):** Liste PELO MENOS 10 conteúdos específicos dessa matéria.
   - Coluna 1: Conteúdo
   - Coluna 2: Habilidade Matriz (Ex: H17, H21)
   - Coluna 3: Classificação TRI (Copie EXATAMENTE o termo que está na coluna de classificação do arquivo CSV. Não invente "Alta/Média", use a nomenclatura do arquivo).
   
3. **Plano de Ação:** Como estudar esses 10 itens na ordem correta para maximizar a nota (TRI prioriza coerência: fáceis primeiro).

Seja técnico e use a terminologia exata da nossa base XTRI.
"""
        with st.spinner("🔄 Consultando CSV 'conteudos ENEM separados por TRI'..."):
            plano = chamar_brainx(prompt_rota, temperatura=0.2) 
            st.markdown("### 🧭 Plano de Ação XTRI")
            st.markdown(plano)
            
            st.info("💡 **Nota do BrainX:** Esta lista respeita a hierarquia da TRI encontrada no arquivo CSV oficial da XTRI.")

# --- RODAPÉ ---
st.markdown("---")
st.markdown("© 2025 BrainX | **Powered by XTRI**")
