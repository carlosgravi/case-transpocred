# Case Técnico - Análise de Dados | Transpocred

**Candidato:** Carlos Gravi
**Data:** Abril 2026

---

## 1. Visão Geral dos Dados

A base fornecida contém **58.913 associados** distribuídos em **50 PAs (Postos de Atendimento)**, com **733.682 registros de receita** ao longo de **6 meses** (Out/2025 a Mar/2026), totalizando **R$ 143,5 milhões** em receita.

### Estrutura

| Dimensão | Valores |
|----------|---------|
| **Associados** | 58.913 únicos |
| **PAs** | 50 postos (maioria SC, RS, PR) |
| **Score de Risco** | 6 níveis (Baixissimo a Altissimo + Sem Classificação) |
| **Produtos** | 11 categorias |
| **Perfil** | Alegre (70,3%) e Triste (29,7%) |
| **Naturalidade** | 11 origens (38,6% Catarinense, 19,3% Cearense) |

---

## 2. Oportunidades Identificadas

### 2.1 Classificar os "Sem Classificação" - Maior Oportunidade de Receita Protegida

**O que encontrei:** 8.529 associados (14,5%) estão "SEM CLASSIFICACAO" de score, mas geram **R$ 44,4 milhões (31% da receita total)** com o maior ticket médio da base (R$ 504).

**Por que importa:** Esses associados não possuem avaliação de risco, impossibilitando decisões de crédito, pricing e gestão de carteira adequadas. E o segmento mais rentável da cooperativa operando "no escuro".

**Recomendação:** Priorizar a classificação de risco desses 8.529 associados. Identificar o motivo da ausência de score (cadastro incompleto? migração de sistema?) e implementar processo de reclassificação. Cada mes sem classificação é um mes de exposição não mensurada a risco de crédito sobre R$ 7,4M/mes.

---

### 2.2 Converter "Triste" em "Alegre" - Retencao dos Maiores Geradores de Receita

**O que encontrei:** Associados com perfil "Triste" geram **R$ 93,9 milhões (65,7% da receita)** apesar de serem apenas 29,7% das transações. O ticket médio do Triste (R$ 441) e **4,5x maior** que o do Alegre (R$ 98).

**Por que importa:** Os associados mais valiosos da cooperativa estão insatisfeitos. Se houver evasão desse grupo, o impacto na receita seria desproporcional. Perder 10% dos Tristes = perder R$ 9,4M. Perder 10% dos Alegres = perder R$ 4,9M.

**Recomendação:** Investigar as causas da insatisfação (atendimento? taxas? produtos?). Criar programa de retenção focado nos Tristes de alto valor. Realizar pesquisa de satisfação segmentada por PA para identificar padrões locais.

---

### 2.3 Replicar Eficiência dos PAs de Alto Desempenho

**O que encontrei:** Há grande disparidade de eficiência entre PAs:

| PA | Receita/Cliente | Clientes |
|----|----------------|----------|
| Sao Paulo | R$ 8.315 | 533 |
| Bento Goncalves | R$ 3.847 | 1.847 |
| Passo Fundo | R$ 3.249 | 1.271 |
| Zona Industrial | R$ 2.959 | 2.491 |
| Blumenau | R$ 2.738 | 2.247 |

**Por que importa:** Sao Paulo gera R$ 8.315/cliente enquanto Tubarao gera R$ 1.481/cliente (5,6x menos). Existe um modelo de sucesso que pode ser replicado.

**Recomendação:** Estudar as práticas dos PAs mais eficientes (mix de produtos, perfil dos associados, estratégia de relacionamento) e criar playbook para PAs com baixa receita por cliente. Avaliar viabilidade de expandir operação em Sao Paulo e Curitiba (poucos clientes, alto valor).

---

### 2.4 Diversificar a Dependência do Produto Principal

**O que encontrei:** Um único produto ("Maca") concentra **R$ 108,9 milhões (76% da receita total)**, embora represente apenas 14% das transações. Os demais 10 produtos somados geram apenas R$ 34,6M.

**Por que importa:** A extrema dependência de um produto cria vulnerabilidade. Qualquer mudança regulatória, competitiva ou de mercado que afete esse produto impacta 3/4 da receita.

**Recomendação:** Desenvolver estratégia de cross-sell para aumentar a penetração dos produtos secundários (especialmente "Alface" com R$ 25,6M e "Cebola" com R$ 3,4M). Criar bundles ou incentivos para associados que usam apenas o produto principal.

---

## 3. Pontos de Atenção

### 3.1 Queda de Receita em Marco/2026 (-19%)

**Dados:** A receita caiu de R$ 24,3M (média dos 5 meses anteriores) para R$ 20,2M em marco/2026. E a primeira queda significativa na série.

**Impacto:** Se a tendência se mantiver, projeção anual cai de R$ 290M para R$ 242M (-R$ 48M).

**Ação:** Investigar se é sazonal, perda de associados, redução de ticket ou combinação. Cruzar com entrada/saida de associados e mudanças de perfil.

---

### 3.2 Concentração Extrema de Receita

**Dados:** 
- Top 10% dos associados (5.812) = **84,5% da receita**
- Top 20% (11.624) = **95,4%**
- Bottom 50% (29.062) = **receita negativa (-R$ 115K)**

**Impacto:** A cooperativa depende de poucos associados para gerar receita. A perda de poucos clientes-chave teria impacto catastrófico.

**Ação:** Criar programa de relacionamento premium para os Top 20%. Monitorar sinais de evasão com frequência mensal. Investigar por que 50% da base não gera receita (inativos? produtos inadequados?).

---

### 3.3 Associados com Receita Negativa

**Dados:** 473 associados geram receita negativa total de R$ -187K. Adicionalmente, 6.643 associados tem receita zero no período.

**Impacto:** 12,1% da base (7.116 associados) não gera nenhuma receita ou gera prejuízo nos 6 meses analisados.

**Ação:** Classificar os negativos (reversões? estornos? provisões?) e os zeros (inativos? recentes?). Desenvolver estratégia de ativação para inativos e política de acompanhamento para negativos.

---

### 3.4 Qualidade dos Dados

**Dados:** 17.428 transações (2,4%) estão vinculadas a "não localizado" - IDs que não existem na base de associados. Além disso, 179 registros de score estão vazios.

**Impacto:** Receita não rastreável a associados impede análise completa e pode indicar falhas no processo de registro ou integração de sistemas.

**Ação:** Mapear a origem dos registros "não localizado". Verificar se são associados desligados, migrados de outro sistema ou erro de integração. Implementar validação na entrada de dados.

---

## 4. Insights sobre a Base de Dados

### 4.1 O Paradoxo do Perfil "Triste"

O dado mais contraintuitivo da base: **associados insatisfeitos geram mais receita**. Isso sugere que:
- Podem ser clientes de produtos de crédito (juros/taxas maiores = mais receita, mas mais insatisfação)
- A insatisfação pode ser proporcional ao engajamento (quem usa mais, reclama mais)
- Há risco sistêmico: se os Tristes forem embora, levam 66% da receita

### 4.2 "SEM CLASSIFICACAO" é o Ponto Cego da Gestão

Com 75,1% de perfil Triste e R$ 504 de ticket médio, o segmento Sem Classificação combina **alto valor + alto risco + zero visibilidade**. E o segmento que mais precisa de atenção imediata.

### 4.3 Geoestratégia: Fora do Eixo SC

Apesar de a base ser predominantemente catarinense (38,6%), as maiores receitas per capita vem de **Goianos (R$ 2.384/associado)**, **Paraenses (R$ 815)** e **Cariocas (R$ 329)**. Associados de fora do eixo tradicional SC/RS tem perfil de maior valor.

### 4.4 Sazonalidade e Tendência

A receita mensal ficou estável entre R$ 24-25M de outubro a fevereiro, com queda para R$ 20,2M em marco. Padrões a monitorar:
- Dezembro não mostrou pico (esperado em cooperativas de crédito)
- Janeiro manteve-se estável (sem queda pos-festas)
- Marco é o primeiro sinal de alerta

### 4.5 Eficiência vs Volume nos PAs

Há dois perfis claros de PAs de sucesso:
- **Volume:** Chapeco (4.119 clientes, R$ 7,7M) e Joinville (4.077, R$ 7,6M) - muitos clientes, ticket médio
- **Eficiência:** Sao Paulo (533 clientes, R$ 4,4M) e Bento Goncalves (1.847, R$ 7,1M) - poucos clientes, alto valor

A estratégia ideal depende do custo operacional de cada PA.

---

## 5. Metodologia

### Ferramentas
- **Python** (pandas, plotly) para processamento e visualização
- **Streamlit** para dashboard interativo
- Análise exploratória com foco em concentração, risco e segmentação

### Tratamento de Dados
- Registros "não localizado" separados para análise de qualidade (não excluidos da receita total)
- Receitas negativas mantidas na análise (podem representar estornos ou provisões)
- Encoding corrigido para caracteres especiais (acentos)

### Dashboard
O painel interativo acompanha esta análise é permite exploração livre dos dados com filtros por PA, Score, Perfil e Produto. Para executar:

```bash
pip install streamlit pandas plotly openpyxl
streamlit run dashboard.py
```

---

## 6. Recomendações Priorizadas

| Prioridade | Ação | Impacto Estimado | Esforco |
|:---:|------|-----------------|---------|
| 1 | Classificar os 8.529 associados "Sem Classificação" | Visibilidade sobre R$ 44,4M/semestre | Médio |
| 2 | Programa de retenção para Tristes de alto valor | Proteger R$ 93,9M/semestre | Alto |
| 3 | Investigar queda de marco/2026 | Evitar perda recorrente de ~R$ 5M/mes | Baixo |
| 4 | Replicar modelo dos PAs eficientes | Potencial de +R$ 10-20M/ano | Alto |
| 5 | Diversificar receita além do produto principal | Reduzir risco de concentração (76%) | Médio |

---

*Análise realizada com base nos dados fornecidos. O dashboard interativo permite aprofundamento em cada dimensão com filtros dinâmicos.*
