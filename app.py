import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BrainX Neural Architect",
    page_icon="🧠",
    layout="centered", 
    initial_sidebar_state="expanded"
)

# --- INICIALIZAÇÃO DO ESTADO DE SESSÃO (MEMÓRIA) ---
# Aqui guardamos o histórico da conversa e a resolução base
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'resolution_base' not in st.session_state:
    st.session_state.resolution_base = ""

# --- ESTILIZAÇÃO & CABEÇALHO (Omitido para brevidade, sem alterações) ---
st.image("https://img.icons8.com/color/96/000000/brain--v1.png", width=70)
st.title("BrainX Neural ENEM Architect")
st.markdown("### Núcleo de Inteligência Artificial | **Powered by XTRI**")
st.markdown("---")

# --- SIDEBAR (CONFIGURAÇÃO) ---
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
st.sidebar.info("v3.8 Chat Enabled | Powered by XTRI")

# --- FUNÇÕES NÚCLEO ---

def corrigir_latex_visual(texto):
    if not texto: return ""
    texto = re.sub(r'\[\s*(.*?)\s*\]', r'$$\1$$', texto)
    texto = re.sub(r'\\\(\s*(.*?)\s*\\\)', r'$\1$', texto)
    texto = re.sub(r'\\\[\s*(.*?)\s*\\\]', r'$$\1$$', texto)
    return texto

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
        image = image.convert('L')
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        image = image.filter(ImageFilter.SHARPEN)
        texto = pytesseract.image_to_string(image, lang='por')
        return texto
    except Exception as e:
        # Se o OCR falhar, retorna None para o usuário usar a caixa de texto
        return None

# FUNÇÃO CENTRAL DE INTERAÇÃO (Para uso na caixa de chat)
def handle_follow_up(user_input):
    # 1. Constrói o contexto da conversa: Resolução anterior + Histórico do Chat + Nova Pergunta
    contexto_completo = f"""
    [CONTEÚDO BASE - RESOLUÇÃO INICIAL DO ENEM]
    {st.session_state.resolution_base}
    ---------------------------------
    [INSTRUÇÕES DO TUTOR]
    Responda a dúvida do aluno com base estritamente na RESOLUÇÃO acima. Seja didático.
    DÚVIDA DO ALUNO: {user_input}
    """
    
    # 2. Chama a API
    response = chamar_brainx(contexto_completo, temperatura=0.1) # Temperatura baixa para ser factual

    # 3. Atualiza o histórico
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# ==============================================================================
# MÓDULO 1: RESOLVER QUESTÃO (AQUI O CHAT É IMPLEMENTADO)
# ==============================================================================
if modo == "📸 Resolver Questão (OCR)":
    st.header("🎓 Resolução Sênior (BrainX)")
    st.info("Faça upload do **PRINT** da questão para iniciar o modo de tutoria interativa.")
    
    # Se uma nova questão for submetida, resetamos a memória
    if st.button("Limpar Sessão e Começar Novo"):
        st.session_state.resolution_base = ""
        st.session_state.chat_history = []
        st.experimental_rerun()
        
    # --- FORMULÁRIO PRINCIPAL (Aparece se não houver resolução) ---
    if not st.session_state.resolution_base:
        col_upload, col_texto = st.columns([1, 1])
        
        with col_upload:
            arquivo = st.file_uploader("Subir Print da Tela:", type=["png", "jpg", "jpeg"])
            texto_extraido = ""
            if arquivo:
                with st.spinner("👁️ BrainX Vision processando..."):
                    texto_extraido = extrair_texto_imagem(arquivo)
        
        with col_texto:
            input_final = st.text_area("Texto da Questão:", value=texto_extraido if texto_extraido else "", height=250, placeholder="Cole a questão aqui...")

        if st.button("Resolver com Protocolo BrainX"):
            if not input_final:
                st.warning("⚠️ Cole a questão primeiro.")
            else:
                # Prompt de primeira passada
                prompt_inicial = f"""[PROTOCOLO DE 7 PASSOS] RESOLVA A QUESTÃO:\n{input_final}\n\nRESPOSTA FINAL OBRIGATÓRIA: **GABARITO: [Letra]**"""
                
                with st.spinner("🧠 Sabiá-3 está gerando a resolução base..."):
                    resposta_base = chamar_brainx(prompt_inicial)
                
                # Armazena a resolução base e reinicia o fluxo para mostrar a saída
                st.session_state.resolution_base = resposta_base
                st.session_state.chat_history = [{"role": "assistant", "content": resposta_base}]
                st.experimental_rerun()

    # --- CHAT DE TUTORIA INTERATIVA (Aparece após a primeira resolução) ---
    else:
        st.subheader("💬 Tutoria Interativa BrainX")
        st.success("Resolução Base Concluída. Pergunte sobre os passos ou conceitos!")
        
        # 1. Exibir Resolução Base (Em um expander para não poluir)
        with st.expander("Ver Resolução Completa", expanded=False):
            st.markdown(corrigir_latex_visual(st.session_state.resolution_base))
            
        # 2. Exibir Histórico do Chat
        for message in st.session_state.chat_history:
            if message["role"] == "assistant":
                st.info(corrigir_latex_visual(message["content"]))
            elif message["role"] == "user":
                st.markdown(f"**Você:** {message['content']}")
                
        # 3. Caixa de Input para o Aluno
        user_input = st.text_input("Sua Dúvida sobre a resolução:")
        
        if user_input and st.session_state.resolution_base:
            handle_follow_up(user_input)
            st.experimental_rerun()


# [O restante dos módulos (ROTA TRI) ficam inalterados, pois não precisam de chat]
