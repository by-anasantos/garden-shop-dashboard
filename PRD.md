# PRD — Dashboard de Estoque e Reposição da Garden Shop

> **Objetivo deste documento:** registrar o problema, os usuários, os objetivos, o escopo e os requisitos do dashboard antes da implementação. As regras aqui descritas são detalhadas tecnicamente em [`SPEC.md`](SPEC.md).

## 1. Identificação do projeto

- **Nome do projeto:** Garden Shop — Dashboard de Estoque e Reposição
- **Autora:** Ana Santos
- **Versão do documento:** 1.1
- **Status:** Aprovado
- **Data:** 2026-10-26
- **Origem:** continuação da proposta da Aula 1 (`lista_01_ana_santos.docx`), implementada na Aula 2 (`lista_02.docx`).

## 2. Visão geral

### 2.1. Contexto

A Garden Shop é uma loja virtual de produtos de jardinagem (plantas, sementes, ferramentas, vasos, substratos, irrigação, fertilizantes e decoração). A empresa dispõe de uma base em CSV com produtos, categorias, fornecedores, pedidos, itens de pedidos e clientes, acompanhada de um dicionário de dados.

Hoje, a equipe de gestão não tem uma visão consolidada do estoque. Para saber o que repor, é preciso cruzar manualmente o saldo de cada produto com o nível de reposição, as vendas registradas e o fornecedor responsável.

### 2.2. Problema

Em uma loja virtual, quando um produto não tem estoque, a venda simplesmente não acontece — e o cliente não fica esperando na fila. A equipe tem dificuldade para:

- identificar rapidamente os produtos zerados ou abaixo do nível de reposição;
- avaliar se o estoque atual é suficiente em relação ao ritmo de vendas;
- priorizar os itens que mais geram receita;
- saber com qual fornecedor falar e por qual canal.

Sem essa visão, há risco de ruptura em produtos importantes, de compra desnecessária de itens descontinuados e de capital parado em estoque sem giro.

### 2.3. Solução proposta

Um dashboard web interativo, em **página única**, que mostra a posição atual do estoque, o ritmo de vendas efetivas no período selecionado e a prioridade de cada produto, terminando em uma tabela de compras exportável com o fornecedor e o contato de cada item.

### 2.4. Proposta de valor

Em uma única tela, a gestão responde: *o que está em risco, quanto vale o estoque, o que vende mais e o que precisa ser comprado de quem*.

## 3. Objetivos e resultados esperados

### 3.1. Objetivos

- **OBJ-1:** classificar cada produto por criticidade de estoque (ruptura, reposição urgente, alerta limítrofe, saudável ou descontinuado).
- **OBJ-2:** estimar por quanto tempo o estoque atual atende ao ritmo de vendas observado.
- **OBJ-3:** concentrar a atenção nos produtos que mais geram receita (curva ABC).
- **OBJ-4:** associar cada produto a repor ao seu fornecedor e e-mail de contato.
- **OBJ-5:** mostrar o capital imobilizado em estoque e o potencial de venda.

### 3.2. Indicadores de sucesso

Não há metas numéricas definidas pela gestão. O sucesso será medido pela capacidade do dashboard de responder às perguntas abaixo, levantadas na Aula 1, sem cálculo manual:

| Pergunta da gestão | Onde é respondida | Como medir |
| --- | --- | --- |
| Quais produtos estão abaixo do nível recomendado? | Card "Abaixo do ponto de reposição" e tabela de compras | Conferir a lista com o cálculo manual da SPEC (seção 13) |
| Quais estão zerados ou muito baixos? | Card "Produtos em ruptura" e status na tabela | Idem |
| Quais vendem mais e merecem atenção? | Dispersão (quadrante de prioridade) e curva ABC | Idem |
| Quais categorias concentram mais reposições? | Barras empilhadas categoria × status | Idem |
| Qual o valor do estoque a custo? | Card "Valor do estoque (custo)" | Idem |
| Quais produtos acompanhar com prioridade? | Tabela de compras ordenada por prioridade | Idem |
| Quais fornecedores estão associados à reposição? | Tabela de compras (fornecedor e e-mail) | Idem |

### 3.3. Critérios de sucesso

- Todos os indicadores reproduzem os valores de referência calculados manualmente (SPEC, seção 13).
- O dashboard executa localmente com os CSVs originais e exibe indicadores, filtros e visualizações.
- Situações sem dados mostram mensagens explicativas em vez de erros ou gráficos vazios.

## 4. Usuários e necessidades

### 4.1. Público-alvo

- **Gestão da loja:** acompanha a situação geral do estoque e o capital imobilizado.
- **Setor de compras:** decide o que repor e contata os fornecedores.

### 4.2. Necessidades dos usuários

- Como **gestora**, quero ver em segundos quantos produtos estão em ruptura ou abaixo do mínimo, para agir antes de perder vendas.
- Como **gestora**, quero saber quanto capital está parado em estoque, para avaliar o investimento.
- Como **compradora**, quero uma lista dos produtos a repor com o fornecedor e o e-mail, para emitir os pedidos de compra.
- Como **compradora**, quero que produtos descontinuados não sejam sugeridos para compra, para não comprar o que a loja deixou de vender.

### 4.3. Jornada principal

1. A usuária abre o dashboard e vê os cards com a situação geral do estoque.
2. Ajusta os filtros (categoria, fornecedor, status, curva ABC e período de vendas).
3. Analisa os gráficos para entender onde estão os problemas e o capital.
4. Consulta a tabela de compras, ordenada por prioridade, e exporta a lista em CSV.

## 5. Escopo do produto

### 5.1. Incluído no escopo

- Todos os indicadores definidos na Aula 1, reorganizados em página única.
- Filtros por categoria, fornecedor, status de estoque, curva ABC e período de vendas.
- Gráficos: barras empilhadas, treemap e dispersão.
- Tabela de compras ordenável e exportável em CSV.
- Paleta de cores própria, **sem vermelho**.

### 5.2. Fora do escopo

- Previsão de demanda ou sazonalidade (a base cobre apenas cerca de 5 meses).
- Ponto de reposição baseado em prazo de entrega (a base não tem lead time).
- Lote mínimo de compra por fornecedor (a base não tem MOQ).
- Escrita na base, emissão automática de pedidos de compra ou envio de e-mails.
- Análises de clientes: `customers.csv` não é necessário aos indicadores e contém dados pessoais, por isso não é carregado.
- Autenticação e múltiplos perfis de acesso.
- Hospedagem obrigatória na internet: a execução local atende à entrega. A publicação no Streamlit Community Cloud, para o portfólio, será feita depois da entrega (DP-003).

### 5.3. Premissas

- Os CSVs fornecidos na Aula 1 representam a posição atual do estoque e o histórico de pedidos disponível.
- `quantity_on_hand` é o saldo atual; não há movimentações históricas.
- `reorder_level` é o nível de referência para reposição definido pela empresa.

### 5.4. Restrições

- **Tecnologia:** Python, Streamlit, Pandas, Plotly e Pytest (escolha da autora, por ser publicável no portfólio).
- **Infraestrutura:** execução local em Windows.
- **Visual:** a cor vermelha é proibida, pois é reservada às correções do professor.
- **Dados:** os arquivos originais não podem ser alterados.
- **Processo:** repositório GitHub com branches e PRs, operado manualmente pela autora.

## 6. Requisitos funcionais

| ID | Requisito | Prioridade | Critério de aceitação |
| --- | --- | --- | --- |
| RF-001 | Carregar e validar `products`, `categories`, `suppliers`, `orders` e `order_items`. | Must | Com os CSVs originais, o dashboard abre sem erro. Se faltar um arquivo ou uma coluna obrigatória, a tela mostra qual está faltando. |
| RF-002 | Considerar como vendas efetivas apenas pedidos `shipped`, `pending` e `processing`. | Must | O pedido 17 (`cancelled`) não entra nas vendas: o Pruning Shears soma 1 unidade, e não 2. |
| RF-003 | Classificar cada produto em um status de estoque, com precedência definida. | Must | O Bird Feeder (descontinuado, 4 ≤ 6) aparece como **Descontinuado**; o Hanging Basket (0 unidades), como **Ruptura**. |
| RF-004 | Exibir os cards Valor do estoque (custo), Valor potencial de venda e Margem bruta média em estoque. | Must | Sem filtros: US\$ 4.763,00, US\$ 10.389,25 e 54,2%. |
| RF-005 | Exibir os cards Produtos em ruptura, Abaixo do ponto de reposição e Déficit total de peças, considerando apenas produtos ativos. | Must | Sem filtros: 1 produto, 5 produtos e 60 peças. |
| RF-006 | Calcular, por produto, a venda média diária e os dias de cobertura no período selecionado. | Must | Fiddle-Leaf Fig, período completo (152 dias): 5 unidades, cobertura de 425,6 dias. Produtos com estoque e sem vendas aparecem como "Sem giro". |
| RF-007 | Classificar os produtos na curva ABC pela receita efetiva do período. | Must | Sem filtros: 13 produtos A, 5 B, 4 C e 2 "Sem vendas". O Tulip Bulbs, que cruza o limite de 80%, fica na classe A. |
| RF-008 | Filtrar por categoria, fornecedor, status, curva ABC e período de vendas. | Must | O período altera apenas os indicadores de venda; os saldos de estoque não mudam. |
| RF-009 | Exibir barras horizontais empilhadas com o número de produtos por categoria e status. | Must | A soma das barras é igual ao número de produtos filtrados. |
| RF-010 | Exibir treemap do valor do estoque a custo por categoria e produto. | Must | A soma das áreas é igual ao card Valor do estoque (custo). |
| RF-011 | Exibir dispersão de vendas efetivas × dias de cobertura, com quadrante de prioridade. | Must | Os produtos com vendas acima da mediana e cobertura abaixo da mediana ficam destacados como prioridade. |
| RF-012 | Exibir a tabela de compras ordenada por prioridade, com fornecedor, e-mail e déficit mínimo, exportável em CSV. | Must | Os 5 produtos ativos abaixo do ponto aparecem com recomendação; o Bird Feeder aparece sem recomendação; fornecedores sem e-mail aparecem sinalizados. |
| RF-013 | Tratar situações sem dados. | Must | Filtros sem resultado ou período sem pedidos mostram uma mensagem explicativa, cards zerados ou "—" e nenhum erro. |
| RF-014 | Exibir as limitações da base no rodapé. | Should | O rodapé cita a ausência de lead time, de histórico de movimentações e de MOQ, além da janela curta de vendas. |
| RF-015 | Filtrar a tabela ao clicar em uma categoria ou em um ponto dos gráficos. | Could | O clique restringe a tabela aos produtos selecionados. Opcional nesta entrega; os filtros do topo já atendem à necessidade. |

## 7. Requisitos não funcionais

| ID | Categoria | Requisito | Critério de verificação |
| --- | --- | --- | --- |
| RNF-001 | Usabilidade | Paleta própria sem vermelho, textos em português, valores em US\$ com 2 casas decimais e percentuais com 1 casa. | Revisão visual e conferência da paleta em `config.py` e `.streamlit/config.toml`. |
| RNF-002 | Confiabilidade | Os dados originais nunca são alterados pelo código. | O código só lê os CSVs; nenhuma função grava em `data/raw/`. |
| RNF-003 | Privacidade | Dados pessoais de clientes não são carregados nem exibidos. | `customers.csv` não é lido pelo código. |
| RNF-004 | Manutenibilidade | As regras de cálculo ficam em funções puras, separadas da interface, e são cobertas por testes. | `pytest` executa os testes das regras da SPEC. |
| RNF-005 | Desempenho | Os dados são carregados uma vez por sessão (cache). | Uso de `st.cache_data` na carga. Não há meta numérica definida. |
| RNF-006 | Portabilidade | O dashboard executa localmente e pode ser publicado no Streamlit Community Cloud. | Instruções de execução validadas em `AGENTS.md`. |

## 8. Dados e integrações

- **Fontes de dados:** `products.csv`, `categories.csv`, `suppliers.csv`, `orders.csv` e `order_items.csv`, além do dicionário `garden_shop_dicionario_dados.xlsx`.
- **Não utilizado:** `customers.csv` (sem uso nos indicadores e com dados pessoais).
- **Entradas:** os CSVs em `data/raw/` (cópias fiéis dos originais).
- **Saídas:** a tela do dashboard e o CSV exportado da tabela de compras.
- **Integrações:** nenhuma.
- **Dados sensíveis:** os e-mails de fornecedores são contatos comerciais e aparecem na tabela de compras.
- **Divergência registrada:** o dicionário informa datas no formato `DD/MM/AAAA` e `discontinued` como `TRUE/FALSE`, mas os CSVs usam `AAAA-MM-DD` e `true/false`. O código aceita as duas formas (SPEC, seção 7).

## 9. Regras de negócio

As definições completas, com fórmulas e exemplos, estão na SPEC (seção 9).

- **RN-001 — Venda efetiva:** pedidos `cancelled` não compõem vendas. `shipped`, `pending` e `processing` contam como vendas efetivas, porque representam demanda real que já consumiu ou vai consumir o estoque. O pedido cancelado continua na base para auditoria.
- **RN-002 — Período × estoque atual:** o filtro de período altera apenas os indicadores de venda (venda média, cobertura e curva ABC). Os saldos e valores de estoque sempre representam a posição atual.
- **RN-003 — Status de estoque:** a primeira condição verdadeira define o status, nesta ordem: Descontinuado → Ruptura → Reposição urgente → Alerta limítrofe → Saudável.
- **RN-004 — Recomendação de compra:** só produtos ativos com déficit positivo recebem recomendação. A sugestão é o déficit mínimo para voltar ao `reorder_level`, e não o lote final de compra.
- **RN-005 — Descontinuados:** aparecem no painel para acompanhamento e entram no valor do estoque, mas nunca recebem recomendação e não entram nos cards de ruptura, abaixo do ponto e déficit.
- **RN-006 — Valor do estoque:** calculado por produto a partir da tabela de produtos, sem relacionar com os itens de pedidos, para não duplicar saldos.
- **RN-007 — Curva ABC:** pela receita efetiva do período. O produto que cruza o limite de 80% (ou 95%) pertence à classe superior. Produtos sem receita no período ficam como "Sem vendas". Esta regra revisa a da Aula 1 ("acumulado ≤ 80%"), que colocaria em C um produto responsável sozinho por toda a receita (DP-001).
- **RN-008 — Cobertura:** estoque atual dividido pela venda média diária. Estoque zerado = 0 dias; estoque positivo sem venda = "Sem giro".
- **RN-009 — Fornecedores:** fornecedores sem e-mail são sinalizados na tabela de compras ("Sem e-mail — buscar outro canal"). Um fornecedor sem produtos aparece no filtro, mas não gera linhas.

## 10. Fluxos e exceções

### 10.1. Fluxo principal

Abrir o dashboard → carregar e validar os CSVs → calcular a visão por produto → aplicar os filtros → exibir cards, gráficos e tabela → exportar a tabela de compras.

### 10.2. Fluxos alternativos

- **Período reduzido:** a venda média, a cobertura e a curva ABC são recalculadas para o período; o estoque não muda.
- **Fornecedor sem produtos (RootWorks Supply):** o filtro retorna o estado "sem resultados".
- **Somente descontinuados:** a tabela aparece sem nenhuma recomendação de compra.

### 10.3. Tratamento de erros

- **Arquivo ou coluna ausente:** mensagem com o nome do arquivo ou da coluna; o dashboard não é exibido.
- **Valor fora do domínio** (status desconhecido, estoque negativo, ID duplicado): mensagem de validação indicando o arquivo, o campo e o valor encontrado.
- **Item de pedido sem pedido ou produto correspondente:** é excluído das vendas e um aviso informa quantos itens foram ignorados.

## 11. Experiência e interface

- **Plataforma:** web (Streamlit), página única.
- **Organização (de cima para baixo):** cabeçalho → filtros → 6 cards → barras empilhadas e treemap lado a lado → dispersão → tabela de compras → rodapé com limitações.
- **Quadrante de prioridade:** as linhas de referência da dispersão ficam na mediana das vendas e na mediana da cobertura dos produtos exibidos, porque a gestão não definiu metas e a mediana se ajusta aos filtros (DP-002).
- **Paleta (sem vermelho):**

| Uso | Cor |
| --- | --- |
| Cabeçalho e cor principal | Ciano escuro `#003d48` |
| Fundo | Off-white `#F5F0E6` |
| Texto e rodapé | Navy `#0a1628` |
| Ruptura | Marrom terroso `#3d1f0f` |
| Reposição urgente | Marrom queimado `#8B5A2B` |
| Alerta limítrofe | Ocre `#C9A227` |
| Saudável | Ciano `#4F8A94` |
| Descontinuado | Cinza `#9AA0A6` |

- **Estados da interface:** carregamento, sucesso, sem resultados e erro de dados.
- **Compatibilidade:** navegadores atuais (Chrome, Edge e Firefox).

## 12. Riscos e dependências

| Risco ou dependência | Impacto | Mitigação |
| --- | --- | --- |
| Sem lead time dos fornecedores | Alto | Usar o `reorder_level` como linha de segurança e registrar a limitação. |
| Estoque sem histórico de movimentações | Médio | Calcular o consumo apenas pelos pedidos efetivos. |
| Janela curta (152 dias) e sazonalidade da jardinagem | Médio | Apresentar a cobertura como tendência recente e alertar no rodapé. |
| Volume de vendas pequeno (86 unidades), que gera coberturas muito longas | Médio | Usar a cobertura para comparar produtos entre si, não como previsão exata. |
| Fornecedores sem e-mail (RootWorks e Ironwood) | Médio | Sinalizar na tabela de compras. |
| Divergência entre o dicionário e os CSVs | Baixo | Aceitar os dois formatos e registrar na SPEC. |
| Compatibilidade do Streamlit com o Python 3.14 instalado | Baixo | Verificar na Fase 1; se houver problema, usar Python 3.12. |

## 13. Entregáveis

- Dashboard em Streamlit funcional, no repositório GitHub.
- `AGENTS.md`, `PRD.md` e `SPEC.md` preenchidos e no repositório.
- Testes automatizados das regras de cálculo.
- Print legível do dashboard em execução.

## 14. Critérios de conclusão do produto

O produto estará pronto quando:

- Os requisitos Must estiverem implementados.
- Os valores de referência da SPEC tiverem sido reproduzidos pelos testes.
- O dashboard tiver sido executado localmente e conferido visualmente.
- Os documentos refletirem o comportamento implementado.

## 15. Relação com os documentos técnicos

- **Especificação de referência:** [`SPEC.md`](SPEC.md)
- **Instruções gerais para agentes:** [`AGENTS.md`](AGENTS.md)
- **Instruções para Claude Code (opcional):** [`CLAUDE.md`](CLAUDE.md)

## 16. Decisões

| ID | Questão | Decisão | Responsável | Status |
| --- | --- | --- | --- | --- |
| DP-001 | Regra de fronteira da curva ABC: em qual classe fica o produto que cruza 80%? | Classe A, pela participação acumulada **anterior** ao produto. O Tulip Bulbs (78,8% → 82,4%) fica em A. | Ana Santos | Decidida em 2026-10-26 |
| DP-002 | Limites do quadrante de prioridade na dispersão. | Mediana das vendas e mediana da cobertura dos produtos exibidos. | Ana Santos | Decidida em 2026-10-26 |
| DP-003 | Publicar o dashboard no Streamlit Community Cloud para o portfólio? | Sim, depois da entrega. Não faz parte do escopo desta entrega. | Ana Santos | Decidida em 2026-10-26 |

## 17. Histórico de alterações

| Versão | Data | Alteração |
| --- | --- | --- |
| 1.0 | 2026-10-26 | Criação a partir da proposta da Aula 1 e do brainstorm da Aula 2. |
| 1.1 | 2026-10-26 | Decisões DP-001 (ABC: classe A para o produto que cruza o limite), DP-002 (medianas no quadrante) e DP-003 (publicação após a entrega). Status: Aprovado. |
