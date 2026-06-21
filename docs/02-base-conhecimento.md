# Base de Conhecimento

## Fontes de Dados

O agente utiliza 4 fontes de dados mockadas, simulando uma integração real com sistemas bancários:

| Arquivo | Formato | Conteúdo |
|---|---|---|
| `perfil_investidor.json` | JSON | Dados cadastrais, perfil de risco e metas financeiras do cliente |
| `transacoes.csv` | CSV | Histórico de movimentações financeiras (entradas e saídas) |
| `produtos_financeiros.json` | JSON | Catálogo de produtos disponíveis, com risco e rentabilidade |
| `historico_atendimento.csv` | CSV | Registro de interações anteriores do cliente com o suporte |

---

## Estratégia de Uso de Cada Fonte

### `perfil_investidor.json`
Usado para **personalizar** todas as respostas do agente. Define:
- Quais produtos podem ser recomendados (via `aceita_risco` e `perfil_investidor`)
- O progresso das metas (comparando `valor_necessario` com `reserva_emergencia_atual`/`patrimonio_total`)

### `transacoes.csv`
Usado para **analisar padrões de gastos**. O agente agrupa os dados por `categoria` para responder perguntas como:
> "Em que categoria eu mais gasto?"
> "Quanto sobrou esse mês?"

Cálculo de saldo: soma de `entrada` menos soma de `saida`.

### `produtos_financeiros.json`
Usado para **recomendação de produtos**. Antes de chegar ao LLM, o código filtra produtos com `risco` compatível ao campo `aceita_risco` do perfil — o LLM nunca recebe produtos fora do perfil do cliente.

### `historico_atendimento.csv`
Usado para dar **contexto de continuidade** — o agente pode referenciar conversas anteriores, evitando repetir explicações já dadas (ex: "Como conversamos no dia 01/10 sobre o Tesouro Selic...").

---

## Pipeline de Preparação dos Dados

```python
import pandas as pd
import json

# Carrega os dados estruturados (CSV)
transacoes = pd.read_csv("data/transacoes.csv")
atendimentos = pd.read_csv("data/historico_atendimento.csv")

# Carrega os dados semiestruturados (JSON)
with open("data/perfil_investidor.json", "r", encoding="utf-8") as f:
    perfil = json.load(f)

with open("data/produtos_financeiros.json", "r", encoding="utf-8") as f:
    produtos = json.load(f)

# Filtra produtos compatíveis com o perfil de risco do cliente
def filtrar_produtos_por_risco(produtos, aceita_risco):
    if not aceita_risco:
        return [p for p in produtos if p["risco"] == "baixo"]
    return produtos

produtos_compativeis = filtrar_produtos_por_risco(produtos, perfil["aceita_risco"])
```

---

## Limitações Conhecidas

- Os dados são **mockados** — em produção, viriam de integração direta com o core bancário via API
- Não há atualização em tempo real — os CSVs/JSONs precisariam ser substituídos por consultas SQL a um banco de dados
- O histórico de atendimento é limitado a poucos registros — em escala real, demandaria um Vector Database para busca semântica eficiente
