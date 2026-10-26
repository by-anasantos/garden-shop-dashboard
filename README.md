# Garden Shop — Dashboard de Estoque e Reposição

Dashboard funcional para a equipe de gestão da Garden Shop acompanhar a
posição atual do estoque e apoiar decisões de reposição. Usa os CSVs da
base Garden Shop (products, categories, suppliers, orders, order_items,
customers) sem alterar os dados originais.

## O que o dashboard mostra
- Indicadores: produtos abaixo do nível de reposição, estoque zerado e
  valor do estoque a custo (quantity_on_hand × cost)
- Vendas efetivas por produto no período (pedidos `cancelled` excluídos)
- Filtros por categoria e fornecedor
- Tabela de produtos que exigem atenção, com o fornecedor associado

## Regras principais
- Pedidos `cancelled` não contam como venda; tratamento de `pending`,
  `processing` e `shipped` definido no PRD
- Produtos descontinuados não recebem recomendação automática de reposição
- Estoque = posição atual; vendas = período selecionado
- Agregações feitas antes dos joins para não duplicar saldos

## Documentação
- [PRD.md](PRD.md) — problema, escopo, requisitos e critérios de aceitação
- [SPEC.md](SPEC.md) — dados, fórmulas, regras e exemplos esperados
- [AGENTS.md](AGENTS.md) — instruções para o agente, instalação, execução e testes
