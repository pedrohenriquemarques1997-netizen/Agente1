
import streamlit as st
import pandas as pd
import json
import google.generativeai as genai

# ============================================
# CONFIGURAÇÃO
# ============================================
st.set_page_config(page_title="Lia - Assistente Financeira", page_icon="💰")

# Configura a API do Gemini
# IMPORTANTE: nunca deixe a chave exposta em código público.
# Aqui usamos st.secrets, que lê de um arquivo .streamlit/secrets.toml (não vai pro GitHub)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-flash-lite-latest")

# ============================================
# CARREGAMENTO DOS DADOS
# ============================================
@st.cache_data
def carregar_dados():
    transacoes = pd.read_csv("data/transacoes.csv")
    atendimentos = pd.read_csv("data/historico_atendimento.csv")

    with open("data/perfil_investidor.json", "r", encoding="utf-8") as f:
        perfil = json.load(f)

    with open("data/produtos_financeiros.json", "r", encoding="utf-8") as f:
        produtos = json.load(f)

    return transacoes, atendimentos, perfil, produtos


transacoes, atendimentos, perfil, produtos = carregar_dados()


# ============================================
# FUNÇÕES AUXILIARES (regras de negócio em código, não na IA)
# ============================================
def filtrar_produtos_por_risco(produtos, aceita_risco):
    """Filtra produtos compatíveis com o perfil de risco do cliente."""
    if not aceita_risco:
        return [p for p in produtos if p["risco"] == "baixo"]
    return produtos


def calcular_resumo_transacoes(df):
    """Calcula saldo e gastos por categoria."""
    entradas = df[df["tipo"] == "entrada"]["valor"].sum()
    saidas = df[df["tipo"] == "saida"]["valor"].sum()
    saldo = entradas - saidas
    gastos_por_categoria = (
        df[df["tipo"] == "saida"].groupby("categoria")["valor"].sum().to_dict()
    )
    return {
        "entradas": entradas,
        "saidas": saidas,
        "saldo": saldo,
        "gastos_por_categoria": gastos_por_categoria,
    }


produtos_compativeis = filtrar_produtos_por_risco(produtos, perfil["aceita_risco"])
resumo_financeiro = calcular_resumo_transacoes(transacoes)


# ============================================
# SYSTEM PROMPT
# ============================================
SYSTEM_PROMPT = f"""
Você é Lia, assistente financeira virtual especializada em ajudar clientes a
acompanhar suas metas financeiras e tomar decisões de investimento mais informadas.

REGRAS OBRIGATÓRIAS:
1. Use APENAS as informações fornecidas no contexto abaixo. NUNCA invente dados,
   valores ou produtos que não estejam explicitamente listados.
2. Se a informação solicitada não estiver disponível, responda que não possui
   essa informação e sugira falar com um consultor humano.
3. NUNCA recomende produtos fora da lista de "produtos compatíveis" abaixo.
4. NUNCA prometa rentabilidade garantida.
5. Tom de voz: acolhedor, didático e direto, sem jargões sem explicação.
6. Se a pergunta for fora do escopo financeiro, redirecione educadamente.
7. Sempre explique o PORQUÊ de uma recomendação, relacionando com a meta do cliente.

=== DADOS DO CLIENTE ===
Nome: {perfil['nome']}
Idade: {perfil['idade']}
Profissão: {perfil['profissao']}
Renda mensal: R$ {perfil['renda_mensal']:.2f}
Perfil de investidor: {perfil['perfil_investidor']}
Aceita risco: {perfil['aceita_risco']}
Patrimônio total: R$ {perfil['patrimonio_total']:.2f}
Reserva de emergência atual: R$ {perfil['reserva_emergencia_atual']:.2f}

Metas:
{json.dumps(perfil['metas'], indent=2, ensure_ascii=False)}

=== RESUMO FINANCEIRO (último período) ===
Entradas: R$ {resumo_financeiro['entradas']:.2f}
Saídas: R$ {resumo_financeiro['saidas']:.2f}
Saldo: R$ {resumo_financeiro['saldo']:.2f}
Gastos por categoria: {json.dumps(resumo_financeiro['gastos_por_categoria'], ensure_ascii=False)}

=== PRODUTOS FINANCEIROS COMPATÍVEIS COM O PERFIL ===
{json.dumps(produtos_compativeis, indent=2, ensure_ascii=False)}

=== HISTÓRICO DE ATENDIMENTOS ANTERIORES ===
{atendimentos.to_string(index=False)}
"""


# ============================================
# INTERFACE
# ============================================
st.title("💰 Lia - Assistente Financeira")
st.caption(f"Olá, {perfil['nome']}! Estou aqui para ajudar com suas finanças.")

# Mostra resumo rápido na barra lateral
with st.sidebar:
    st.subheader("📊 Resumo Rápido")
    st.metric("Patrimônio Total", f"R$ {perfil['patrimonio_total']:.2f}")
    st.metric("Reserva de Emergência", f"R$ {perfil['reserva_emergencia_atual']:.2f}")
    st.metric("Saldo do período", f"R$ {resumo_financeiro['saldo']:.2f}")

# Histórico de chat na sessão
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Exibe mensagens anteriores
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do usuário
pergunta = st.chat_input("Pergunte algo sobre suas finanças...")

if pergunta:
    # Mostra a pergunta do usuário
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    # Gera resposta com o Gemini
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            prompt_completo = f"{SYSTEM_PROMPT}\n\n=== PERGUNTA DO CLIENTE ===\n{pergunta}"
            resposta = model.generate_content(prompt_completo)
            st.markdown(resposta.text)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta.text})