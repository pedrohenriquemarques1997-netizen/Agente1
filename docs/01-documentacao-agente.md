Saída

# Documentação do Agente — Consultor de Metas Financeiras

## Caso de Uso

O agente atua como um **consultor financeiro pessoal**, ajudando o cliente a:

- Acompanhar o progresso das suas metas financeiras (ex: reserva de emergência, entrada de imóvel)
- Receber recomendações de produtos financeiros compatíveis com seu perfil de risco
- Entender seus padrões de gastos por categoria
- Tirar dúvidas sobre produtos financeiros disponíveis

**Problema que resolve:** clientes muitas vezes não acompanham de perto suas metas financeiras nem sabem quais produtos são adequados ao seu perfil. O agente democratiza esse acompanhamento, oferecendo orientação personalizada.

---

## Persona e Tom de Voz

- **Nome:** Lia (Assistente Financeira)
- **Tom:** Acolhedor, didático e direto. Evita jargões financeiros sem explicação.
- **Postura:** Consultiva, nunca impositiva — apresenta opções e explica trade-offs, mas a decisão final é sempre do cliente.
- **Limites:** Não promete rentabilidade, não recomenda produtos fora do perfil de risco do cliente sem alertar explicitamente.

---

## Arquitetura

```
┌─────────────────────────┐
│   Cliente (via chat)    │
└────────────┬─────────────┘
             │
┌────────────▼─────────────┐
│   Aplicação (Streamlit)   │
└────────────┬─────────────┘
             │
┌────────────▼─────────────┐
│   Orquestração (LangChain)│
└────────────┬─────────────┘
             │
   ┌─────────┴─────────┐
   │                   │
┌──▼───────────┐  ┌────▼────────────┐
│  LLM (Claude/ │  │  Base de Dados   │
│  GPT/Gemini)  │  │  (CSV/JSON)      │
└───────────────┘  └──────────────────┘
                    - transacoes.csv
                    - historico_atendimento.csv
                    - perfil_investidor.json
                    - produtos_financeiros.json
```

**Fluxo de funcionamento:**
1. Cliente envia uma pergunta no chat
2. A aplicação busca dados relevantes nas bases (perfil, transações, produtos)
3. O LLM recebe a pergunta + os dados como contexto (RAG)
4. O LLM gera uma resposta personalizada baseada **apenas** nos dados fornecidos
5. Resposta é exibida ao cliente

---

## Segurança e Anti-Alucinação

- O agente **nunca responde com base em conhecimento genérico de mercado** — sempre usa os dados das bases fornecidas como única fonte de verdade
- System Prompt explicita: *"Se a informação não estiver nos dados fornecidos, responda que não possui essa informação"*
- Recomendações de produtos são **filtradas previamente por código** (não pela IA) considerando o campo `aceita_risco` do perfil do investidor, antes de chegar ao LLM
- Respostas sobre valores monetários são sempre extraídas diretamente dos dados, nunca calculadas "de cabeça" pelo modelo
