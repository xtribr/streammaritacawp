import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import pytesseract
from PIL import Image
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
# Mudei para "centered" para ficar mais elegante no meio da tela do iframe
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
    /* Ajuste para mobile no iframe */
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO (Vertical) ---
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
st.sidebar.info("v3.2 Stable | Powered by XTRI")

# --- FUNÇÕES AUXILIARES ---

@st.cache_data(show_spinner=False)
def chamar_brainx(prompt, temperatura=0.0):
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
# MÓDULO 1: RESOLVER QUESTÃO (OCR/Print) - LAYOUT VERTICAL
# ==============================================================================
if modo == "📸 Resolver Questão (OCR)":
    st.header("🎓 Resolução Sênior (BrainX)")
    st.info("Faça upload do **PRINT** da questão ou digite o texto abaixo.")
    
    # 1. Upload
    texto_extraido = ""
    arquivo = st.file_uploader("Subir Print da Tela (Imagem):", type=["png", "jpg", "jpeg"])
    
    if arquivo:
        with st.spinner("👁️ BrainX lendo imagem..."):
            texto_extraido = extrair_texto_imagem(arquivo)
            if texto_extraido:
                st.success("Imagem processada!")

    # 2. Área de Texto (Preenchida auto ou manual)
    st.markdown("**Confira ou digite o enunciado:**")
    input_final = st.text_area("", value=texto_extraido if texto_extraido else "", height=250, placeholder="Cole a questão aqui...")

    # 3. Botão de Ação
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
# MÓDULO 2: ROTA TRI (SLIDE APENAS) - LAYOUT VERTICAL
# ==============================================================================
elif modo == "🧭 Rota de Estudos por TRI":
    st.header("📊 Rota Personalizada (TRI)")
    st.markdown("Suba o **Slide de Desempenho** (Print do gráfico/erros). O BrainX cruzará seus dados com a Matriz de Referência.")
    
    # 1. Configurações (Empilhadas)
    st.markdown("**1. Defina seu perfil:**")
    area_foco = st.selectbox("Qual área focar?", ["Matemática", "Natureza", "Humanas", "Linguagens"])
    nivel_atual = st.select_slider("Nível TRI estimado:", options=["< 500", "500-600", "600-700", "700-800", "800+"], value="600-700")

    # 2. Upload (APENAS IMAGEM)
    st.markdown("**2. Anexar Boletim (Slide/Print):**")
    arquivo_aluno = st.file_uploader("Subir Imagem:", type=["png", "jpg", "jpeg"])

    # 3. Botão de Ação
    if st.button("Gerar Rota Estratégica XTRI"):
        texto_aluno = ""
        if arquivo_aluno:
            with st.spinner("🔍 BrainX analisando slide..."):
                texto_aluno = extrair_texto_imagem(arquivo_aluno)
        
        contexto_input = texto_aluno if texto_aluno else "Nenhum slide enviado. Gere rota baseada apenas no nível TRI informado."

        prompt_rota = f"""
Atue como o BrainX Architect (Especialista em TRI e Matriz do ENEM).
O aluno deseja aumentar sua nota em **{area_foco}**.
Nível Atual: **{nivel_atual}**.

DADOS DO SLIDE/BOLETIM:
{contexto_input[:4000]} 

TAREFA:
1. **Diagnóstico TRI:** Identifique quais Habilidades da Matriz o aluno está errando.
2. **Rota de Estudos XTRI:** Crie um plano sequencial para subir de nível.
   - Foque nas habilidades que dão mais pontos na TRI para o nível dele.
3. **Tabela:** Liste: Conteúdo | Habilidade BNCC | Importância na TRI.

Seja técnico, direto e estratégico.
"""
        with st.spinner("Construindo estratégia pedagógica..."):
            plano = chamar_brainx(prompt_rota, temperatura=0.5)
            st.markdown("### 🧭 Plano de Ação")
            st.markdown(plano)
            
            st.info("💡 **Dica XTRI:** Domine a base antes de avançar. A TRI penaliza o acerto casual em questões difíceis se você errar as fáceis.")

# --- RODAPÉ ---
st.markdown("---")
st.markdown("© 2025 BrainX | **Powered by XTRI**")
