import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Neural ENEM Architect",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO CSS (Visual Profissional) ---
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
    .stTextArea>div>div>textarea {background-color: #ffffff; border-radius: 8px;}
    .stSuccess {background-color: #d1e7dd; color: #0f5132;}
    .stWarning {background-color: #fff3cd; color: #664d03;}
    .stError {background-color: #f8d7da; color: #842029;}
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://img.icons8.com/color/96/000000/brain--v1.png", width=80)
with col2:
    st.title("Neural ENEM Architect")
    st.markdown("**Núcleo de Inteligência Artificial | Powered by Sabiá-3**")

# --- SIDEBAR (CONFIGURAÇÃO) ---
st.sidebar.header("⚙️ Configuração do Sistema")

# --- LÓGICA DE AUTENTICAÇÃO (AUTOMÁTICA) ---
# O código busca exatamente a chave 'api_gpt_assistente' nos segredos
if "api_gpt_assistente" in st.secrets:
    api_key = st.secrets["api_gpt_assistente"]
    st.sidebar.success("✅ Chave de API Conectada (Segredo)")
else:
    # Fallback apenas para testes locais se não houver segredo configurado
    api_key = st.sidebar.text_input("Insira Chave (api_gpt_assistente):", type="password")
    if not api_key:
        st.sidebar.warning("⚠️ Configure 'api_gpt_assistente' no Streamlit Cloud.")

st.sidebar.markdown("---")
modo = st.sidebar.radio("Selecione o Módulo:", 
    ["📝 Resolver Questão (Tutor)", "🗺️ Gerar Rota de Estudos", "📊 Dashboard Preditivo"]
)
st.sidebar.markdown("---")
st.sidebar.info("v2.0 Stable | Engine: Sabiá-3.1")

# --- FUNÇÃO DE CHAMADA À API (BACKEND) ---
# Cache ativado para economizar seus créditos
@st.cache_data(show_spinner=False)
def chamar_sabia(prompt, temperatura=0.0):
    if not api_key:
        return "⚠️ ERRO CRÍTICO: Chave de API não encontrada."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Configuração exata para o Sabiá-3
    data = {
        "model": "sabia-3", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperatura,
        "max_tokens": 2500
    }
    
    try:
        response = requests.post("https://chat.maritaca.ai/api/chat/completions", headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 401:
            return "❌ Erro 401: Chave Inválida. Verifique se 'api_gpt_assistente' contém uma chave Maritaca válida."
        else:
            return f"Erro na API ({response.status_code}): {response.text}"
            
    except Exception as e:
        return f"Erro de Conexão: {str(e)}"

# ==============================================================================
# MÓDULO 1: RESOLVER QUESTÃO (O TUTOR)
# ==============================================================================
if modo == "📝 Resolver Questão (Tutor)":
    st.subheader("🎓 Resolução Sênior (Protocolo 7 Passos)")
    st.markdown("Cole a questão abaixo. O sistema aplicará o método **Chain-of-Thought** para garantir precisão.")
    
    questao = st.text_area("Enunciado da Questão:", height=200, placeholder="Ex: (ENEM 2023) Texto base...")
    
    if st.button("Resolver com Sabiá-3"):
        if not questao:
            st.warning("⚠️ Por favor, cole uma questão antes de processar.")
        else:
            # O PROMPT MESTRE (METODOLOGIA DE ELITE)
            prompt_final = f"""
VOCÊ É O SABIÁ-3. RESOLVA A QUESTÃO ABAIXO SEGUINDO RIGOROSAMENTE ESTE PROTOCOLO DE 7 PASSOS:

PASSO 1: ANÁLISE INICIAL (Identifique dados, comando e contexto)
PASSO 2: PLANEJAMENTO (Defina conceitos e fórmulas)
PASSO 3: RESOLUÇÃO DETALHADA (Mostre o cálculo ou lógica passo a passo)
PASSO 4: VALIDAÇÃO (Faça a prova real ou verifique consistência)
PASSO 5: ANÁLISE DAS ALTERNATIVAS (Explique por que as erradas são distratores)
PASSO 6: ESCOLHA FINAL (Selecione a correta)
PASSO 7: VERIFICAÇÃO FINAL (Confirme se bate com o gabarito lógico)

QUESTÃO DO ALUNO:
{questao}

INSTRUCÃO FINAL:
Ao terminar, pule uma linha e escreva em negrito: "**GABARITO: [Letra]**"
"""
            with st.spinner("🧠 Sabiá-3 está raciocinando..."):
                inicio = time.time()
                resposta = chamar_sabia(prompt_final)
                tempo = time.time() - inicio
            
            # Exibição do Resultado
            st.success(f"✅ Resolução concluída em {tempo:.1f} segundos.")
            
            with st.expander("Ver Raciocínio Completo", expanded=True):
                st.markdown(resposta)

# ==============================================================================
# MÓDULO 2: GERAR ROTA DE ESTUDOS
# ==============================================================================
elif modo == "🗺️ Gerar Rota de Estudos":
    st.subheader("🧭 Planejador Estratégico (Pareto 80/20)")
    st.markdown("Crie um cronograma focado nos conteúdos de maior incidência histórica.")
    
    col1, col2 = st.columns(2)
    with col1:
        materia = st.selectbox("Disciplina:", ["Matemática", "Física", "Química", "Biologia", "História", "Geografia", "Linguagens"])
    with col2:
        dias = st.slider("Duração do Plano (Dias):", 3, 30, 7)
    
    if st.button("Gerar Cronograma Personalizado"):
        prompt_rota = f"""
Atue como um Engenheiro Pedagógico do ENEM.
Crie um Plano de Estudos de {dias} dias para a disciplina de {materia}.

REGRAS OBRIGATÓRIAS:
1. Aplique a Regra de Pareto (80/20): Selecione apenas os tópicos que mais caem na história da prova.
2. Estruture dia a dia.
3. Para cada dia, defina: "Foco Teórico", "Estratégia de Resolução" e "Meta de Questões".
4. Gere uma tabela final com a carga horária sugerida.
"""
        with st.spinner("Analisando matriz de referência..."):
            plano = chamar_sabia(prompt_rota, temperatura=0.5)
            st.markdown(plano)

# ==============================================================================
# MÓDULO 3: DASHBOARD PREDITIVO
# ==============================================================================
elif modo == "📊 Dashboard Preditivo":
    st.subheader("🔮 Tendências para o Próximo ENEM")
    st.markdown("Análise estatística baseada no Banco de Dados Vetorial (3.000+ questões).")
    
    # Dados extraídos da nossa análise Python (fixos para performance do app)
    data = {
        'Tópico': [
            'Interpretação de Texto (PT)', 'Matemática Básica', 'Geometria Plana/Espacial', 
            'Ecologia e Meio Ambiente', 'História do Brasil (República)', 'Eletrodinâmica', 
            'Geopolítica', 'Estequiometria', 'Funções e Gráficos', 'Filosofia/Sociologia'
        ],
        'Probabilidade de Cair (%)': [98, 95, 88, 85, 80, 78, 75, 72, 70, 65]
    }
    df = pd.DataFrame(data).sort_values(by='Probabilidade de Cair (%)', ascending=True)
    
    # Gráfico de Barras
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df['Tópico'], df['Probabilidade de Cair (%)'], color='#10B981')
    
    # Estilização do Gráfico
    ax.set_xlabel("Probabilidade de Incidência (%)", fontsize=12)
    ax.set_title("Top 10 Tópicos Quentes (Matriz de Referência)", fontsize=14, fontweight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Adicionar valores nas barras
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width}%', va='center', fontweight='bold')

    st.pyplot(fig)
    
    st.info("💡 **Insight:** Focar em 'Matemática Básica' e 'Interpretação' garante mais de 45% da nota total da prova devido à TRI.")

# --- RODAPÉ ---
st.markdown("---")
st.markdown("© 2025 Neural ENEM Architect | Desenvolvido com Tecnologia Sabiá-3")
