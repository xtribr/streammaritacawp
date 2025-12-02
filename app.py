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
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS (Identidade XTRI) ---
st.markdown("""
<style>
    .main {background-color: #f8f9fa;}
    h1 {color: #0F172A;}
    .stButton>button {
        background-color: #0F172A;
        color: white;
        border-radius: 8px;
        height: 3em;
        width: 100%;
        font-weight: bold;
        border: 1px solid #1E293B;
    }
    .stButton>button:hover {
        background-color: #1E293B;
        border-color: #334155;
    }
    .stFileUploader {border-radius: 10px; border: 2px dashed #0F172A; padding: 10px;}
    .stSuccess {background-color: #d1e7dd; color: #0f5132;}
    .stInfo {background-color: #e0f2fe; color: #0369a1;}
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO (BRANDING ATUALIZADO) ---
col1, col2 = st.columns([1, 6])
with col1:
    # Placeholder de logo ou ícone cerebral
    st.markdown("## 🧠") 
with col2:
    st.title("BrainX Neural ENEM Architect")
    st.markdown("**Núcleo de Inteligência Artificial | Powered by XTRI**")

# --- SIDEBAR ---
st.sidebar.header("⚙️ Configuração BrainX")

if "api_gpt_assistente" in st.secrets:
    api_key = st.secrets["api_gpt_assistente"]
    st.sidebar.success("✅ BrainX Conectado")
else:
    api_key = st.sidebar.text_input("Chave API:", type="password")

st.sidebar.markdown("---")
modo = st.sidebar.radio("Ferramenta:", 
    ["📸 Resolver Questão (OCR/Print)", "🧭 Rota de Estudos por TRI"]
)
st.sidebar.info("v3.1 Stable | Powered by XTRI")

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
# MÓDULO 1: RESOLVER QUESTÃO (PRINT/IMAGEM)
# ==============================================================================
if modo == "📸 Resolver Questão (OCR/Print)":
    st.subheader("🎓 Resolução Sênior (BrainX)")
    st.markdown("Faça upload do **PRINT** da questão.")
    
    col_upload, col_texto = st.columns([1, 1])
    
    texto_extraido = ""
    
    with col_upload:
        # APENAS IMAGENS AGORA
        arquivo = st.file_uploader("Subir Print da Tela:", type=["png", "jpg", "jpeg"])
        if arquivo:
            with st.spinner("👁️ BrainX analisando imagem..."):
                texto_extraido = extrair_texto_imagem(arquivo)
                if texto_extraido:
                    st.success("Imagem lida com sucesso!")
                    with st.expander("Ver texto extraído"):
                        st.text(texto_extraido)

    with col_texto:
        input_final = st.text_area("Texto da Questão (Editável):", value=texto_extraido if texto_extraido else "", height=300)

    if st.button("Resolver com Protocolo BrainX"):
        if not input_final:
            st.warning("Precisamos da questão (Imagem ou Texto).")
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
                st.markdown(resposta)

# ==============================================================================
# MÓDULO 2: ROTA TRI (UPLOAD DE SLIDE)
# ==============================================================================
elif modo == "🧭 Rota de Estudos por TRI":
    st.subheader("📊 Diagnóstico e Rota Personalizada (TRI)")
    st.markdown("Suba o **Slide de Desempenho** (Print do gráfico ou tabela de erros).")
    
    col_area, col_file = st.columns([1, 2])
    
    with col_area:
        area_foco = st.selectbox("Qual área focar?", ["Matemática", "Natureza", "Humanas", "Linguagens"])
        nivel_atual = st.select_slider("Nível TRI estimado:", options=["< 500", "500-600", "600-700", "700-800", "800+"], value="600-700")

    with col_file:
        # APENAS IMAGENS (SLIDES)
        arquivo_aluno = st.file_uploader("Subir Slide do Boletim (IMG):", type=["png", "jpg", "jpeg"])

    if st.button("Gerar Rota Estratégica XTRI"):
        texto_aluno = ""
        if arquivo_aluno:
            with st.spinner("🔍 BrainX lendo slide..."):
                texto_aluno = extrair_texto_imagem(arquivo_aluno)
        
        contexto_input = texto_aluno if texto_aluno else "Nenhum slide enviado. Gere rota baseada no nível TRI informado."

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
            st.markdown(plano)
            
            st.info("💡 **Dica XTRI:** Domine a base antes de avançar. A TRI penaliza o acerto casual em questões difíceis se você errar as fáceis.")

# --- RODAPÉ ---
st.markdown("---")
st.markdown("© 2025 BrainX | Powered by XTRI")