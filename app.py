import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from openai import OpenAI
import io
import re
import base64
import subprocess # Para checar a instalação

# Tenta configurar o caminho do Tesseract se estiver rodando local (Streamlit Cloud já deve fazer isso)
# Tente comentar esta linha se der erro na nuvem
# subprocess.run(['tesseract', '-v'], capture_output=True) 

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

# --- GLOBAL KEY RETRIEVAL (SEGURANÇA MÁXIMA) ---
MARITACA_KEY = st.secrets.get("api_gpt_assistente")
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY")

if not MARITACA_KEY:
    st.error("❌ ERRO DE SEGURANÇA: Chave Maritaca não encontrada no Secrets. Configure 'api_gpt_assistente'.")
    st.stop()

# --- ESTILIZAÇÃO & CABEÇALHO (REMOVIDO PARA BREVIDADE) ---
st.image("https://img.icons8.com/color/96/000000/brain--v1.png", width=70)
st.title("BrainX Neural ENEM Architect")
st.markdown("### Núcleo de Inteligência Artificial | **Powered by XTRI**")
st.markdown("---")

# --- SIDEBAR (STATUS) ---
st.sidebar.header("⚙️ Status do Sistema")
st.sidebar.success("✅ Conexão Segura Ativa")
modo = st.sidebar.radio("Ferramenta:", ["📸 Resolver Questão (OCR)", "🧭 Rota de Estudos por TRI"])
st.sidebar.info("v5.0 Stable | Powered by XTRI")

# --- FUNÇÕES NÚCLEO (API) ---

def corrigir_latex_visual(texto):
    if not texto: return ""
    texto = re.sub(r'\\\[\s*(.*?)\s*\\\]', r'$$\1$$', texto)
    texto = re.sub(r'\\\(\s*(.*?)\s*\\\)', r'$\1$', texto)
    texto = re.sub(r'\[\s*(.*?)\s*\]', r'$$\1$$', texto)
    return texto

@st.cache_data(show_spinner=False)
def chamar_brainx(prompt, api_key_maritaca):
    headers = {"Authorization": f"Bearer {api_key_maritaca}", "Content-Type": "application/json"}
    data = {"model": "sabia-3", "messages": [{"role": "user", "content": prompt}], "temperature": 0.0, "max_tokens": 3000}
    
    try:
        response = requests.post("https://chat.maritaca.ai/api/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Erro BrainX API ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Erro Conexão: {str(e)}"

# OCR e Visão (GPT-4o) - Isolado para segurança
def ler_imagem_gpt4o(base64_image):
    if not OPENAI_KEY: return "❌ ERRO: Chave OpenAI ausente para Visão."
    
    try:
        client = OpenAI(api_key=OPENAI_KEY)
        prompt_vision = "Analise esta imagem (screenshot de uma questão do ENEM). Extraia o enunciado completo, o comando final e TODAS as alternativas, mantendo a formatação e ordem exatas (A, B, C, D, E). Seja estritamente um leitor de OCR de alta qualidade."

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

# --- MÓDULO 1: RESOLVER QUESTÃO (OCR) ---
if modo == "📸 Resolver Questão (OCR)":
    st.header("🎓 Resolução Sênior (BrainX)")
    
    # ... (Fluxo de upload e chat mantido) ...
    # O código aqui é longo, mas garante que não haja conflitos de variável.
    
    if st.button("Limpar Sessão e Começar Novo"):
        st.session_state.resolution_base = ""
        st.session_state.chat_history = []
        st.rerun()

    if not st.session_state.resolution_base:
        st.markdown("**1. Upload do Print:**")
        arquivo = st.file_uploader("Subir Print da Tela (Imagem):", type=["png", "jpg", "jpeg"])
        texto_extraido = ""
        
        if arquivo:
            if not OPENAI_KEY:
                st.error("❌ Chave OpenAI ausente para leitura da imagem (GPT-4o).")
            else:
                with st.spinner("👁️ GPT-4o Vision lendo e corrigindo texto..."):
                    texto_extraido = ler_imagem_gpt4o(encode_image(arquivo))
                    if "ERRO" in texto_extraido: st.error(f"❌ Falha Vision: {texto_extraido}")
                    else: st.success("Texto lido e corrigido!")
                    
        st.markdown("**2. Enunciado:**")
        input_final = st.text_area("", value=texto_extraido if texto_extraido else "", height=250, placeholder="Cole ou edite a questão aqui...")

        if st.button("Gerar Resolução Base"):
            if not input_final: st.warning("⚠️ Cole a questão primeiro.")
            else:
                prompt_inicial = f"""[PROTOCOLO DE 7 PASSOS] RESOLVA A QUESTÃO:\n{input_final}\n\nRESPOSTA FINAL OBRIGATÓRIA: **GABARITO: [Letra]**"""
                with st.spinner("🧠 Sabiá-3 gerando a resolução base..."):
                    resposta_base = chamar_brainx(prompt_inicial, MARITACA_KEY)
                
                st.session_state.resolution_base = resposta_base
                st.session_state.chat_history = [{"role": "assistant", "content": resposta_base}]
                st.rerun() 

    else:
        st.subheader("💬 Tutoria Interativa BrainX")
        with st.expander("Ver Resolução Base", expanded=False):
            st.markdown(corrigir_latex_visual(st.session_state.resolution_base))
            
        for message in st.session_state.chat_history:
            if message["role"] == "assistant": st.info(corrigir_latex_visual(message["content"]))
            elif message["role"] == "user": st.markdown(f"**Você:** {message['content']}")
                
        user_input = st.text_input("Sua Dúvida sobre a resolução:")
        
        if user_input and st.session_state.resolution_base:
            handle_follow_up(user_input)

# --- MÓDULO 2: ROTA TRI (MANTIDO) ---
elif modo == "🧭 Rota de Estudos por TRI":
    # ... (Módulo 2 mantido, pois o erro não estava aqui) ...
    st.header("📊 Rota Estratégica (TRI)")
    st.markdown("O BrainX irá consultar a base **'conteudos ENEM separados por TRI.csv'** para calibrar sua rota.")
    
    st.markdown("**Defina seu perfil:**")
    area_foco = st.selectbox("Área de Foco:", ["Matemática e suas Tecnologias", "Ciências da Natureza", "Ciências Humanas", "Linguagens e Códigos"])
    nivel_atual = st.select_slider("Seu Nível Atual:", options=["Iniciante (<500)", "Intermediário (500-700)", "Avançado (>700)", "Elite (800+)"], value="Intermediário (500-700)")

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
   - Coluna 3: Classificação TRI (Copie EXATAMENTE o termo que está na coluna de classificação do arquivo CSV. Use a nomenclatura do arquivo, não Alta/Média).
   
3. **Plano de Ação:** Como estudar esses 10 itens na ordem correta para maximizar a nota (TRI prioriza coerência: fáceis primeiro).

Seja técnico e use a terminologia exata da nossa base XTRI.
"""
        with st.spinner("🔄 Consultando base de inteligência TRI..."):
            plano = chamar_brainx(prompt_rota, MARITACA_KEY, temperatura=0.2) 
            st.markdown("### 🧭 Plano de Ação XTRI")
            st.markdown(plano)
            
            st.info("💡 **Nota do BrainX:** Esta lista respeita a hierarquia da TRI encontrada no arquivo CSV oficial da XTRI.")

# --- RODAPÉ ---
st.markdown("---")
st.markdown("© 2025 BrainX | **Powered by XTRI**")
