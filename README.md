# Séries Temporais — Modelagem e Forecasting

Projeto acadêmico para comparação de modelos de séries temporais com variáveis externas, incluindo especificações, decisões arquiteturais e artefatos de execução.

**Visão Rápida**
- **Descrição:** Repositório com dados, notebooks, artefatos e documentação para experimentos de forecasting.
- **Fonte de verdade (context):** A pasta [context/README.md](context/README.md) contém a governança, ordem de leitura e onde agentes e colaboradores devem buscar especificações; trate-a como referência primária tanto para humanos quanto para agentes.

**Como Começar**
- **Pré-requisitos:** Python 3.8+ e bibliotecas listadas nos notebooks (use um ambiente virtual).
- **Abrir notebooks:** Veja [notebooks/README.md](notebooks/README.md) para orientações e execução interativa.
- **Dados:** Os dados ficam em [data/README.md](data/README.md); siga as instruções para preparação/ingestão antes de rodar experimentos.

**Estrutura do Repositório**
- **context/**: Documentação de produto, SDD, regras, ADRs, handoffs e instruções para agentes — fonte de verdade para decisões e especificações. Veja [context/README.md](context/README.md).
- **notebooks/**: Jupyter notebooks com análises e pipelines experimentais.
- **data/**: Dados brutos e scripts de ingestão/transformação (ver [data/README.md](data/README.md)).
- **artifacts/**: Resultados, modelos e relatórios gerados (ver [artifacts/README.md](artifacts/README.md)).

**Documentos-chave**
- [context/PRD.md](context/PRD.md) — requisitos e entregáveis.
- [context/SDD.md](context/SDD.md) — visão técnica e mapa do sistema.
- [context/RULES.md](context/RULES.md) — regras de trabalho e reprodutibilidade.
- [context/AGENTS.md](context/AGENTS.md) — instruções específicas para agentes de IA que interajam com o repositório.

**Contribuindo**
- Siga as regras definidas em [context/RULES.md](context/RULES.md). Para mudanças de decisão, crie uma ADR em [context/adr/](context/adr/).

**Handoff e Contato**
- Use [context/HANDOFF.md](context/HANDOFF.md) e os templates em [context/handoff/](context/handoff/) para transferir trabalho entre colaboradores.

---
Gerado automaticamente: resumo do repositório e indicação clara da pasta `context/` como fonte de verdade para agentes e humanos.
