# Avaliação e Métricas

## Métricas Definidas

### 1. Precisão/Assertividade das Respostas

O agente foi testado com perguntas reais baseadas nos dados mockados do cliente João Silva, avaliando se as respostas refletiam corretamente os dados fornecidos.

| Pergunta testada | Dado esperado | Resultado |
|---|---|---|
| "Em que categoria eu mais gasto?" | Moradia (R$ 1.380,00) | ✅ Correto |
| "Que produtos você recomenda pra mim?" | Apenas produtos de risco baixo | ✅ Correto |
| "Como está minha reserva de emergência?" | R$ 10.000,00 de R$ 15.000,00 | ✅ Correto |

**Taxa de assertividade observada:** 100% nos testes realizados (3/3 respostas corretas e fundamentadas nos dados).

---

### 2. Taxa de Respostas Seguras (Anti-Alucinação)

Avalia se o agente respeita as regras de segurança definidas no System Prompt, especialmente:
- Não recomendar produtos fora do perfil de risco do cliente
- Não inventar dados que não estão na base
- Redirecionar para consultor humano quando apropriado

**Resultado dos testes:**
- O agente recomendou **exclusivamente** produtos de risco baixo (Tesouro Selic, CDB Liquidez Diária, LCI/LCA), respeitando o campo `aceita_risco: false` do perfil — nenhum produto de risco médio ou alto foi sugerido.
- O agente sugeriu contato com consultor humano para questões financeiras mais complexas, conforme definido no prompt.

---

### 3. Coerência com o Perfil do Cliente

Avalia se as respostas consideram o contexto específico do cliente (não são genéricas).

**Evidências observadas:**
- O agente conectou recomendações de produtos diretamente com a meta declarada do cliente ("reserva de emergência até junho de 2026")
- Usou o nome do cliente (João Silva) de forma natural nas respostas
- Citou valores exatos extraídos dos dados (R$ 1.380,00, R$ 10.000,00, R$ 5.000,00 restantes) em vez de estimativas genéricas

---

## Metodologia de Avaliação

Os testes foram realizados manualmente, simulando 3 cenários de uso real:
1. Consulta de progresso de meta financeira
2. Análise de padrão de gastos por categoria
3. Solicitação de recomendação de produtos financeiros

Cada resposta foi comparada com os dados brutos das fontes (`perfil_investidor.json`, `transacoes.csv`, `produtos_financeiros.json`) para verificar fidelidade às regras do System Prompt.

---

## Limitações Identificadas

- Os testes foram realizados em **pequena escala** (3 cenários), não cobrindo todos os edge cases documentados em `03-prompts.md`
- Não houve teste automatizado — uma evolução natural seria criar um conjunto de perguntas padronizadas com respostas esperadas para regressão automática
- A filtragem de produtos por risco é feita em código (não pela IA), o que garante segurança mas exigiria expansão caso novos critérios de filtro sejam necessários no futuro

---

## Próximos Passos para Evolução das Métricas

- Implementar testes automatizados com casos de teste fixos (regressão)
- Adicionar métrica de tempo de resposta do agente
- Coletar feedback estruturado de usuários reais (ex: avaliação 👍/👎 após cada resposta)
