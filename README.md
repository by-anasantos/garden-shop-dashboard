# Garden Shop — Dashboard de Estoque e Reposição

**Autora:** Ana Santos

🌿 **Dashboard online:** https://garden-shop-dashboard-cnddk2u89vfajvgsmsadkz.streamlit.app/

Dashboard em Streamlit que mostra, em uma única página, a situação do estoque da Garden Shop (loja virtual de jardinagem): o que está em risco, quanto vale o estoque, o que vende mais e o que precisa ser comprado de qual fornecedor.

- **Cards:** valor do estoque a custo, valor potencial de venda, margem bruta, produtos em ruptura, abaixo do ponto de reposição e déficit de peças.
- **Gráficos:** produtos por categoria e status, treemap do capital em estoque e quadrante de prioridade (vendas × dias de cobertura).
- **Tabela de compras:** ordenada por prioridade, com fornecedor, e-mail e sugestão mínima de compra, exportável em CSV.
- **Filtros:** período de vendas, categoria, fornecedor, status e curva ABC.

## Como executar localmente (Windows, PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest                    # 81 testes
python -m streamlit run app.py      # abre em http://localhost:8501
```

## Documentação

| Documento | Conteúdo |
| --- | --- |
| [`PRD.md`](PRD.md) | Problema, usuários, escopo, requisitos e regras de negócio |
| [`SPEC.md`](SPEC.md) | Fórmulas, contratos de dados, exemplos com resultado esperado e testes |
| [`AGENTS.md`](AGENTS.md) | Como agentes de IA trabalham no repositório; comandos verificados |
| [`CLAUDE.md`](CLAUDE.md) | Orientações específicas para o Claude Code |

## Dados

`data/raw/` contém cópias fiéis de cinco CSVs da Garden Shop (products, categories, suppliers, orders e order_items), com pedidos de 15/01/2024 a 14/06/2024. O `customers.csv` não é usado nem versionado, porque contém dados pessoais e não entra nos indicadores.

**Limitações da base:** sem prazo de entrega dos fornecedores, sem histórico de movimentações do estoque, sem lote mínimo de compra e com uma janela curta de vendas.

**Stack:** Python · Streamlit · Pandas · Plotly · Pytest
