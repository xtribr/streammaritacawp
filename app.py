import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import pdfplumber
import pytesseract
from PIL import Image
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Neural ENEM Architect",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    h1 {color: #1E3A8A;}
    .stButton>button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-weight: bold;
    }
    .stFileUploader {border-radius: 10px; border: 2px dashed #1E3A8A; padding: 10px;}
    .stSuccess {background-color: #d1e7dd; color: #0f5132;}
    .stInfo {background-color: #cff4fc; color: #055160;}
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://img.icons8.com/color/96/000000/brain--v1.png", width=80)
with col2:
    st.title("Neural ENEM Architect")
    st.markdown("**Núcleo de Inteligência Artificial | Powered by Sabiá-3**")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Configuração")

if "api_gpt_assistente" in st.secrets:
    api_key = st.secrets["api_gpt_assistente"]
    st.sidebar.success("✅ API Conectada")
else:
    api_key = st.sidebar.text_input("Chave API:", type="password")

st.sidebar.markdown("---")
# Menu simplificado conforme seu pedido
modo = st.sidebar.radio("Ferramenta:", 
    ["📸 Resolver Questão (OCR/PDF)", "🧭 Rota de Estudos por TRI"]
)
st.sidebar.info("v3.0 | Vision Enabled")

# --- FUNÇÕES AUXILIARES (OCR & API) ---

@st.cache_data(show_spinner=False)
def chamar_sabia(prompt, temperatura=0.0):
    if not api_key: return "⚠️ ERRO: Chave API ausente."
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "sabia-3", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperatura,
        "max_tokens": 3000
    }
    
    try:
        response = requests.post("https://chat.maritaca.ai/api/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Erro API ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Erro Conexão: {str(e)}"

def extrair_texto_arquivo(uploaded_file):
    texto = ""
    try:
        if uploaded_file.type == "application/pdf":
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    texto += page.extract_text() + "\n"
        elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            image = Image.open(uploaded_file)
            # Tenta usar OCR. Se falhar no servidor, avisa.
            try:
                texto = pytesseract.image_to_string(image, lang='por')
            except:
                st.error("⚠️ Ocorreu um erro no motor de OCR (Tesseract). O servidor pode não ter a biblioteca instalada.")
                return None
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        return None
    return texto

# ==============================================================================
# MÓDULO 1: RESOLVER QUESTÃO (OCR/PDF)
# ==============================================================================
if modo == "📸 Resolver Questão (OCR/PDF)":
    st.subheader("🎓 Resolução Sênior (Suporte a Print e PDF)")
    st.markdown("Faça upload do print da questão ou digite o texto.")
    
    col_upload, col_texto = st.columns([1, 1])
    
    texto_extraido = ""
    
    with col_upload:
        arquivo = st.file_uploader("Subir Print ou PDF:", type=["png", "jpg", "jpeg", "pdf"])
        if arquivo:
            with st.spinner("🔍 Extraindo texto da imagem/PDF..."):
                texto_extraido = extrair_texto_arquivo(arquivo)
                if texto_extraido:
                    st.success("Texto extraído com sucesso!")
                    with st.expander("Ver texto extraído"):
                        st.text(texto_extraido)

    with col_texto:
        # Se houve upload, preenche a caixa. Se não, deixa digitar.
        input_final = st.text_area("Texto da Questão:", value=texto_extraido if texto_extraido else "", height=300)

    if st.button("Resolver com Protocolo 7 Passos"):
        if not input_final:
            st.warning("Precisamos da questão (Texto ou Arquivo).")
        else:
            prompt_final = f"""
VOCÊ É O SABIÁ-3. RESOLVA SEGUINDO O PROTOCOLO DE ELITE:

PASSO 1: ANÁLISE INICIAL (Dados e Comando)
PASSO 2: PLANEJAMENTO (Conceitos)
PASSO 3: RESOLUÇÃO DETALHADA (Cálculo/Lógica)
PASSO 4: VALIDAÇÃO (Prova real)
PASSO 5: ANÁLISE DAS ALTERNATIVAS (Justifique erros dos distratores)
PASSO 6: ESCOLHA FINAL
PASSO 7: VERIFICAÇÃO FINAL

QUESTÃO DO ALUNO (Pode conter erros de OCR, corrija mentalmente):
{input_final}

RESPOSTA FINAL:
Pule uma linha e escreva: "**GABARITO: [Letra]**"
"""
            with st.spinner("🧠 Sabiá-3 analisando questão..."):
                resposta = chamar_sabia(prompt_final)
                st.markdown(resposta)

# ==============================================================================
# MÓDULO 2: ROTA TRI (UPLOAD DE SLIDE/BOLETIM)
# ==============================================================================
elif modo == "🧭 Rota de Estudos por TRI":
    st.subheader("📊 Diagnóstico e Rota Personalizada (TRI)")
    st.markdown("Suba seu **Slide de Desempenho** ou **Boletim de Erros**. A IA vai cruzar seus erros com a Matriz de Referência.")
    
    col_area, col_file = st.columns([1, 2])
    
    with col_area:
        area_foco = st.selectbox("Qual área focar?", ["Matemática", "Natureza", "Humanas", "Linguagens"])
        nivel_atual = st.select_slider("Seu nível atual (TRI estimada):", options=["< 500", "500-600", "600-700", "700-800", "800+"], value="600-700")

    with col_file:
        arquivo_aluno = st.file_uploader("Subir Slide/Boletim (PDF/IMG):", type=["pdf", "png", "jpg"])

    if st.button("Gerar Rota Estratégica"):
        texto_aluno = ""
        if arquivo_aluno:
            with st.spinner("🔍 Lendo seu desempenho..."):
                texto_aluno = extrair_texto_arquivo(arquivo_aluno)
        
        # Se não tiver arquivo, ele gera uma rota baseada apenas no nível
        contexto_input = texto_aluno if texto_aluno else "Nenhum arquivo enviado. Gere rota baseada no nível TRI informado."

        prompt_rota = f"""
Atue como um Especialista em Psicometria e Matriz do ENEM.
O aluno deseja aumentar sua nota em **{area_foco}**.
Nível Atual estimado: **{nivel_atual}**.

DADOS DO ALUNO (Do arquivo enviado):
{contexto_input[:4000]} 

TAREFA:
1. **Diagnóstico TRI:** Baseado no nível e nos erros (se houver no texto), identifique quais Habilidades da Matriz ele está errando (Básicas, Operacionais ou Global).
2. **Rota de Estudos:** Crie um plano sequencial para subir de nível.
   - Se Nível Baixo: Foque em Matriz de Referência Básica (conteúdos que mais pontuam).
   - Se Nível Alto: Foque em Habilidades de refino e conteúdos de baixa incidência (diferencial).
3. **Tabela:** Liste: Conteúdo | Habilidade BNCC Provável | Importância na TRI.

Seja técnico mas didático.
"""
        with st.spinner("Construindo estratégia pedagógica..."):
            plano = chamar_sabia(prompt_rota, temperatura=0.5)
            st.markdown(plano)
            
            st.info("💡 **Dica TRI:** Para subir de nível, garanta primeiro as questões fáceis (coerência pedagógica) antes de tentar as difíceis.")

# --- RODAPÉ ---
st.markdown("---")
st.markdown("© 2025 Neural ENEM Architect")
