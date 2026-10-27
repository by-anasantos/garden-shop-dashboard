# AGENTS.md — Instruções para agentes de IA

> **Projeto:** Garden Shop — Dashboard de Estoque e Reposição · **Autora:** Ana Santos · **Atualizado em:** 2026-10-27
>
> **Repositório:** https://github.com/by-anasantos/garden-shop-dashboard
>
> **Dashboard online:** https://garden-shop-dashboard-cnddk2u89vfajvgsmsadkz.streamlit.app/

## 1. Objetivo

Este documento define como agentes de IA devem analisar, planejar, implementar, testar e documentar alterações neste repositório. O agente trabalha **como par da autora**: propõe, explica e implementa, mas as decisões de negócio e as operações de Git e GitHub são dela.

## 2. Documentos a consultar

Antes de qualquer tarefa, leia nesta ordem:

1. **`AGENTS.md`** (este arquivo): como trabalhar no repositório.
2. **[`PRD.md`](PRD.md):** problema, usuários, escopo, requisitos RF/RNF e regras de negócio em linguagem de produto.
3. **[`SPEC.md`](SPEC.md):** fonte de verdade do comportamento: fórmulas, contratos, exemplos com resultado esperado e casos de teste.
4. **[`CLAUDE.md`](CLAUDE.md):** apenas se estiver usando o Claude Code.

As regras de negócio **não** são repetidas aqui. Consulte a SPEC (seções 6 e 9) para evitar cópias divergentes.

### Resolução de conflitos

- A SPEC prevalece sobre o código. Se o código divergir, corrija o código ou proponha a mudança na SPEC (seção 17 da SPEC). Nunca altere o comportamento em silêncio.
- Se o PRD e a SPEC divergirem, aponte o conflito à autora antes de implementar.
- Não invente regras, metas, campos ou aprovações. Decisões em aberto ficam nas pendências (PRD, seção 16; SPEC, seção 18).
- Restrições explícitas (dados somente leitura, **sem vermelho**, Git manual) prevalecem sobre a conveniência.

## 3. Abordagem de implementação: SDD (Spec-Driven Development)

A autora escolheu o **SDD**. A SPEC orienta o planejamento, a implementação e a validação, e é revisada sempre que o entendimento muda.

### 3.1. Ciclo de cada parte da entrega

| Etapa | O que o agente faz | Evidência exigida antes de seguir |
| --- | --- | --- |
| 1. Specify | Identifica os REQ/RN/TEST da SPEC afetados. Se faltar uma regra ou um exemplo, propõe a alteração na SPEC e aguarda a aprovação da autora. | Lista dos requisitos afetados; SPEC atualizada, se necessário. |
| 2. Plan | Diz quais arquivos vai criar ou alterar e em qual fase/branch (SPEC, seção 12). | Plano curto apresentado à autora. |
| 3. Testes das regras | Para regras de cálculo e de carga, escreve primeiro os testes a partir dos exemplos da SPEC (seção 13) e confirma que falham pelo motivo esperado. | Saída do `pytest` com as falhas esperadas. |
| 4. Implement | Implementa o mínimo necessário para satisfazer os requisitos. | Código revisável, sem funcionalidades extras. |
| 5. Verify | Roda o `pytest` completo; para a interface, executa o app e segue o roteiro TEST-030. | Saída real do `pytest`; descrição do que foi conferido na tela. |
| 6. Update | Atualiza a SPEC (status, histórico e pendências), o PRD (se o escopo mudou) e a tabela de comandos verificados. | Diff dos documentos. |

> Escrever os testes das regras antes do código é uma exigência do exercício (`lista_02.docx`). Dentro do SDD, esses testes são a forma executável dos critérios de aceitação da SPEC. Não se trata de TDD aplicado a todo o projeto.

**Como foi aplicado nesta entrega:** em cada fase, os testes foram escritos a partir da SPEC, executados contra um esqueleto vazio (todos falhando com `NotImplementedError` ou por módulo inexistente) e só depois o código foi implementado. Descobertas durante a implementação viraram versões da SPEC (1.2 a 1.6), por exemplo: o `st.error` do Streamlit é vermelho, então as mensagens usam uma caixa própria.

### 3.2. Quando revisar a SPEC

- Uma descoberta nos dados muda uma regra ou um resultado esperado.
- Um requisito se mostra ambíguo ou impossível de implementar como descrito.
- A autora decide uma pendência (DP/SPEC-OPEN).

Nesses casos: altere a SPEC, incremente a versão no histórico, ajuste os testes e só então altere o código.

## 4. Estrutura do repositório

```
garden-shop-dashboard/
├── app.py                    # Interface Streamlit (layout apenas, sem fórmulas)
├── requirements.txt
├── .streamlit/config.toml    # Tema (paleta sem vermelho)
├── data/raw/                 # Cópias fiéis de 5 CSVs — SOMENTE LEITURA (sem customers.csv)
├── src/garden_shop/
│   ├── config.py             # Caminhos, constantes de negócio, paleta
│   ├── loader.py             # Leitura e validação dos CSVs
│   ├── metrics.py            # Regras de cálculo (funções puras)
│   ├── filters.py            # Filtros de dimensão
│   ├── charts.py             # Figuras Plotly
│   └── formatting.py         # Formatação de US$, %, dias
├── tests/                    # Pytest (recorte de referência em conftest.py)
└── README.md · PRD.md · SPEC.md · AGENTS.md · CLAUDE.md
```

**Fora do repositório** (no `.gitignore` ou só na pasta de trabalho da autora): `.venv/`, a pasta `Garden Shop/` com os CSVs originais da Aula 1 (inclui `customers.csv`), o dicionário de dados, os templates dos documentos e o material da aula.

Responsabilidades: SPEC, seção 5.2. Regra principal: **fórmulas ficam somente em `metrics.py`** e constantes de negócio, somente em `config.py`.

## 5. Ambiente e comandos

### 5.1. Padrões do projeto

- **Linguagem:** Python 3.14 (verificado com 3.14.3 no Windows).
- **Dependências:** `pip` + `requirements.txt` em um ambiente virtual `.venv` na raiz.
- **Bibliotecas:** `streamlit`, `pandas`, `plotly`, `pytest`. O NumPy é usado em `metrics.py` e chega como dependência do Pandas. Não adicione outras sem justificar à autora.
- **Código:** nomes em inglês nas funções e variáveis; textos da interface em português; type hints nas funções públicas; docstrings curtas.
- **Lint/formatação:** nenhuma ferramenta adotada nesta entrega.
- **Imports:** `app.py` e os testes importam de `src/garden_shop` (o caminho é configurado em `tests/conftest.py` e no início do `app.py`).

### 5.2. Comandos de referência (PowerShell, na raiz do projeto)

| Finalidade | Comando | Status |
| --- | --- | --- |
| Criar o ambiente virtual | `python -m venv .venv` | ✅ Verificado em 2026-10-27 |
| Ativar o ambiente (a cada PowerShell novo) | `.\.venv\Scripts\Activate.ps1` | ✅ Verificado em 2026-10-27 |
| Instalar as dependências | `python -m pip install -r requirements.txt` | ✅ Verificado em 2026-10-27 (Python 3.14.3) |
| Rodar todos os testes | `python -m pytest` | ✅ Verificado em 2026-10-27 — 81 passed |
| Rodar os testes de um módulo | `python -m pytest tests/test_metrics.py -v` | ✅ Verificado em 2026-10-27 |
| Executar o dashboard | `python -m streamlit run app.py` | ✅ Verificado em 2026-10-27 — abre em `http://localhost:8501` |
| Usar outra pasta de dados | `$env:GARDEN_SHOP_DATA_DIR="C:\caminho\dados"; python -m streamlit run app.py` | ⏳ Não verificado na máquina da autora (coberto por `config.data_dir()`) |

**Problemas conhecidos:**

- `No module named pytest` ou `streamlit`: o ambiente não foi ativado (a linha do PowerShell precisa começar com `(.venv)`).
- "A execução de scripts foi desabilitada" ao ativar: rode `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` uma vez.
- Na primeira execução, o Streamlit pode pedir um e-mail no terminal: aperte Enter para pular.

**Regra:** só marque ✅ Verificado depois de executar o comando e conferir a saída real, registrando a data. Nunca afirme que um comando ou teste passou sem tê-lo executado.

## 6. Git e GitHub: operação manual pela autora

A autora opera o Git e o GitHub **manualmente, pelo GitHub Desktop** (o Git de linha de comando não está instalado na máquina). O agente:

- **não executa** operações de Git nem cria PRs ou repositórios;
- **pode sugerir**, ao final de cada parte, o nome da branch, a lista de arquivos, a mensagem de commit e o texto do PR;
- **não reescreve o histórico** nem descarta alterações locais da autora.

**Fluxo no GitHub Desktop:** `main` → **Fetch/Pull origin** → **New branch** → copiar os arquivos → conferir a lista em *Changes* → **Commit** → **Publish branch** → **Create Pull Request** → revisar o diff e **Merge** no site → voltar ao `main` e dar **Pull**. Nunca fazer commit direto no `main`.

### 6.1. Branches e PRs

| Fase | Branch | PR | Conteúdo |
| --- | --- | --- | --- |
| 0 | — | — | PRD, SPEC e AGENTS enviados direto ao `main` pelo site, antes de o GitHub Desktop ser instalado |
| 1 | `feat/carga-dados` | #1 | Estrutura, `requirements.txt`, `.gitignore`, `data/raw/`, `config.py`, `loader.py`, testes de carga |
| 2 | `feat/regras-calculo` | #2 | `metrics.py`, `filters.py`, testes das regras |
| 3 | `feat/dashboard` | #3 | Tema, `formatting.py`, `charts.py`, `app.py`, testes da interface |
| 4 | `docs/fechamento` | #4 | Documentos alinhados ao código, comandos verificados, `README.md`, `CLAUDE.md` |
| 5 | `docs/publicacao` | #5 | Link do dashboard publicado |

**Publicação:** o Streamlit Community Cloud republica o app automaticamente a cada merge no `main`. Por isso, nada entra no `main` sem passar pelos testes.

### 6.2. Revisão antes de cada PR

- [ ] Os requisitos da SPEC afetados estão listados na descrição do PR.
- [ ] O `pytest` foi executado e a saída foi conferida.
- [ ] Nenhum arquivo em `data/raw/` foi alterado.
- [ ] A SPEC e o PRD refletem o que foi implementado.
- [ ] Não há vermelho em cores novas (o `tests/test_palette.py` confere a paleta).

### 6.3. `.gitignore`

`.venv/`, `__pycache__/`, `.pytest_cache/`, `*.pyc`, `~$*` (temporários do Office), `lista_0*.docx`, `*.pptx`, `*.pdf`, `Garden Shop/` e `garden_shop_dicionario_dados.xlsx`.

## 7. Limites e cuidados com os dados

- **Somente leitura:** o código nunca grava em `data/raw/`. Os CSVs são cópias fiéis dos originais da Aula 1; para restaurá-los, descarte a alteração no GitHub Desktop.
- **Somente o necessário:** use apenas as tabelas e os campos listados na SPEC (seção 7.1). **Não leia `customers.csv`** (dados pessoais sem uso nos indicadores); ele não está no repositório.
- **Nada de dados inventados:** não crie linhas, não corrija valores e não preencha ausências nos CSVs. Dados de teste ficam só nas fixtures de `tests/`, sempre em pastas temporárias.
- **Duplicação:** agregue as vendas por produto antes de juntar com produtos (SPEC, RN-006). Toda função que junta tabelas deve preservar uma linha por produto.
- **Período × estoque:** o filtro de período nunca altera saldos ou valores de estoque (SPEC, RN-002).
- **Divergências encontradas** nos dados ou no dicionário: registre na SPEC (seção 7.1) e avise a autora; não "corrija" o dado.
- **Cores:** use apenas a paleta da SPEC (seção 11.3). **Vermelho é proibido**, inclusive o `st.error` do Streamlit.
- **Segredos:** o projeto não usa credenciais; não adicione nenhuma.

## 8. Regras de desenvolvimento

- Implemente somente o que a SPEC pede; ideias novas viram sugestão para a autora, não código.
- Prefira alterações pequenas, uma fase por vez.
- Trate os erros de carga com `DataValidationError` e mensagem clara; não esconda exceções com `except` genérico.
- Valide as entradas na fronteira (o loader); as funções de `metrics.py` assumem dados já validados.
- Não altere configurações não relacionadas à tarefa nem instale pacotes globalmente.

## 9. Critérios de qualidade

Uma parte está pronta quando:

- atende aos REQ da SPEC e aos exemplos com resultado esperado;
- os testes pertinentes foram executados e passaram (saída real conferida);
- trata as situações sem dados (SPEC, REQ-010);
- não altera os dados originais;
- os documentos estão coerentes com o código.

## 10. Protocolo para dúvidas e bloqueios

Pergunte à autora quando:

- uma regra da SPEC estiver incompleta ou em conflito com os dados;
- a tarefa exigir mudança de escopo ou nova dependência;
- houver duas soluções com efeitos diferentes nos indicadores.

Para dúvidas pequenas e de baixo risco (ex.: o texto de um rótulo), adote a opção mais simples, coerente com a SPEC, e registre a decisão no resumo da entrega.

## 11. Formato de entrega de cada parte

1. **Resumo:** o que foi feito e quais REQ/TEST cobre.
2. **Arquivos:** criados e alterados.
3. **Decisões:** escolhas técnicas e mudanças na SPEC.
4. **Testes:** comandos executados e resultado real.
5. **Pendências:** o que falta, os riscos e o que não foi verificado.
6. **Git (sugestão):** branch, commit e texto do PR para a autora executar.

## 12. Princípio geral

Priorize a correção dos indicadores, a aderência à SPEC e a preservação dos dados. Um dashboard bonito com um número errado não atende ao objetivo.
