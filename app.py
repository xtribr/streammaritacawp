import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from openai import OpenAI # Importa o cliente OpenAI
import io
import re
import base64

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="BrainX Neural Architect",
    page_icon="🧠",
    layout="centered", 
    initial_sidebar_state="expanded"
)

# --- INICIALIZAÇÃO DO ESTADO DE SESSÃO (MEMÓRIA) ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'resolution_base' not in st.session_state:
    st.session_state.resolution_base = ""

# --- ESTILIZAÇÃO & CABEÇALHO ---
st.markdown("""
<style>
    /* ... (CSS mantido) ... */
    .main {background-color: #f8f9fa;}
    h1 {color: #0F172A; font-size: 2.2rem;}
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
    .stFileUploader {border-radius: 10px; border: 2px dashed #0F172A; padding: 15px;}
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)

st.image("https://img.icons8.com/color/96/000000/brain--v1.png", width=70)
st.title("BrainX Neural ENEM Architect")
st.markdown("### Núcleo de Inteligência Artificial | **Powered by XTRI**")
st.markdown("---")

# --- SIDEBAR (CONFIGURAÇÃO) ---
st.sidebar.header("⚙️ Configuração Híbrida")

# Chave 1: Maritaca (Sabiá-3)
maritaca_key = st.sidebar.text_input("Maritaca KEY (Sabiá-3):", type="password", 
    value=st.secrets.get("api_gpt_assistente") or st.secrets.get("MARITACA_KEY"))

# Chave 2: OpenAI (Visão)
openai_key = st.sidebar.text_input("OpenAI KEY (Visão GPT-4o):", type="password", 
    value=st.secrets.get("OPENAI_API_KEY"))

st.sidebar.markdown("---")
modo = st.sidebar.radio("Ferramenta:", 
    ["📸 Resolver Questão (OCR)", "🧭 Rota de Estudos por TRI"]
)
st.sidebar.info("v4.0 Stable | Powered by XTRI")

# --- FUNÇÕES CORE ---

def corrigir_latex_visual(texto):
    if not texto: return ""
    texto = re.sub(r'\\\[\s*(.*?)\s*\\\]', r'$$\1$$', texto) # Padrão acadêmico
    texto = re.sub(r'\\\(\s*(.*?)\s*\\\)', r'$\1$', texto) # Padrão acadêmico inline
    texto = re.sub(r'\[\s*(.*?)\s*\]', r'$$\1$$', texto) # Padrão brackets que o modelo usa
    return texto

@st.cache_data(show_spinner=False)
def chamar_brainx(prompt, api_key_maritaca):
    # ... (API call logic, mantida) ...
    if not api_key_maritaca: return "⚠️ ERRO: Chave Maritaca ausente."
    
    headers = {"Authorization": f"Bearer {api_key_maritaca}", "Content-Type": "application/json"}
    data = {
        "model": "sabia-3", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 3000
    }
    
    try:
        response = requests.post("https://chat.maritaca.ai/api/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Erro BrainX API ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Erro Conexão: {str(e)}"

# OCR e Visão (GPT-4o)
def vision_ocr_and_description(base64_image, api_key):
    # ... (Vision call logic, mantida) ...
    try:
        client = OpenAI(api_key=api_key)
        prompt_vision = "Analise esta imagem (screenshot de uma questão do ENEM). Extraia o enunciado completo, o comando final e TODAS as alternativas, mantendo a formatação e ordem exatas (A, B, C, D, E). Não adicione nenhum comentário ou texto extra. Seja estritamente um leitor de OCR de alta qualidade."

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt_vision}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
            max_tokens=1024,
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERRO VISION API: {e}"

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# FUNÇÃO CENTRAL DE INTERAÇÃO (Para uso na caixa de chat)
def handle_follow_up(user_input):
    # Constrói o contexto da conversa: Resolução anterior + Nova Pergunta
    contexto_completo = f"CONTEÚDO BASE (RESOLUÇÃO ANTERIOR): {st.session_state.resolution_base}\n\nDÚVIDA DO ALUNO: {user_input}"
    
    response = chamar_brainx(contexto_completo, maritaca_key)
    
    # Atualiza o histórico
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response})

    st.rerun() # <<< CORREÇÃO CRÍTICA AQUI: Usando st.rerun()


# ==============================================================================
# MÓDULO 1: RESOLVER QUESTÃO (O CHAT É IMPLEMENTADO)
# ==============================================================================
if modo == "📸 Resolver Questão (OCR)":
    st.header("🎓 Resolução Sênior (BrainX)")

    # Botão de Reset
    if st.button("Limpar Sessão e Começar Novo"):
        st.session_state.resolution_base = ""
        st.session_state.chat_history = []
        st.rerun() # <<< CORREÇÃO CRÍTICA AQUI

    # --- FLUXO INICIAL (Aparece se não houver resolução) ---
    if not st.session_state.resolution_base:
        st.markdown("**1. Upload do Print:**")
        arquivo = st.file_uploader("Subir Print da Tela (Imagem):", type=["png", "jpg", "jpeg"])
        texto_extraido = ""
        
        if arquivo:
            if not openai_key:
                st.error("❌ Por favor, configure a chave OpenAI para leitura da imagem (GPT-4o).")
            else:
                with st.spinner("👁️ GPT-4o lendo e corrigindo texto..."):
                    texto_extraido = vision_ocr_and_description(encode_image(arquivo), openai_key)
                    if "ERRO" in texto_extraido: st.error(texto_extraido)
                    else: st.success("Texto lido e corrigido!")
                    
        st.markdown("**2. Enunciado:**")
        input_final = st.text_area("...", value=texto_extraido if texto_extraido else "", height=250, placeholder="Cole ou edite a questão aqui...")

        if st.button("Gerar Resolução Base"):
            if not input_final: st.warning("⚠️ Cole a questão primeiro.")
            else:
                prompt_inicial = f"[PROTOCOLO DE 7 PASSOS] RESOLVA A QUESTÃO:\n{input_final}\n\nRESPOSTA FINAL OBRIGATÓRIA: **GABARITO: [Letra]**"
                with st.spinner("🧠 Sabiá-3 gerando a resolução base..."):
                    resposta_base = chamar_brainx(prompt_inicial, maritaca_key)
                
                # Armazena a resolução base e reinicia o fluxo para mostrar o chat
                st.session_state.resolution_base = resposta_base
                st.session_state.chat_history = [{"role": "assistant", "content": resposta_base}]
                st.rerun() # <<< CORREÇÃO CRÍTICA AQUI

    # --- CHAT DE TUTORIA INTERATIVA (Aparece após a primeira resolução) ---
    else:
        st.subheader("💬 Tutoria Interativa BrainX")
        st.info("Resolução Base Concluída. Pergunte sobre os passos ou conceitos!")
        
        # 1. Exibir Resolução Base
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
            # O handle_follow_up já chama st.rerun()

# [O restante dos módulos (ROTA TRI) ficam inalterados, pois não precisam de chat]
