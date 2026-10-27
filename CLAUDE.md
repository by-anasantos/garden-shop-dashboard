# CLAUDE.md — Instruções para Claude Code

> **Status:** referência opcional. O exercício não exige este arquivo; ele existe para uso futuro e não exige configurar a ferramenta.

## 1. Leitura obrigatória

Antes de alterar qualquer arquivo, leia:

1. [`AGENTS.md`](AGENTS.md): regras comuns a todos os agentes, incluindo a **abordagem SDD**, os comandos verificados, os limites com os dados e o **Git manual pela autora (GitHub Desktop)**.
2. [`PRD.md`](PRD.md): problema, escopo e requisitos.
3. [`SPEC.md`](SPEC.md): fonte de verdade do comportamento, dos exemplos e dos testes.

Este arquivo não repete essas regras. Em caso de dúvida, o `AGENTS.md` e a `SPEC.md` prevalecem.

## 2. Orientações específicas para o Claude Code

- **Modo de planejamento:** em tarefas que tocam mais de um módulo, apresente o plano (REQs afetados, arquivos, testes) antes de editar, conforme a etapa *Plan* do AGENTS.md (seção 3.1).
- **Comandos:** use somente os da tabela do AGENTS.md (seção 5.2). Não execute comandos Git que alterem o repositório; sugira a branch, o commit e o texto do PR à autora.
- **Ferramentas e integrações:** não presuma que existam MCPs, skills ou hooks configurados neste projeto. Hoje não há nenhum.
- **Subagentes:** não são necessários para o tamanho deste projeto.
- **Edições:** mantenha as fórmulas em `src/garden_shop/metrics.py`, as constantes em `config.py` e não edite `data/raw/`.

## 3. Relatório final

Use o formato do AGENTS.md (seção 11).
