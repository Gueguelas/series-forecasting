# HANDOFF — Guia e template

Handoffs **não ficam mais neste arquivo**. Cada sessão gera um arquivo em:

```
context/handoff/handoff_{resumo_da_sessao}.md
```

## Como funciona

1. Integrante pede: *"crie o handoff"* (ou similar).
2. Agente cria `context/handoff/handoff_{resumo}.md` com o conteúdo da sessão.
3. Atualiza o índice em [`handoff/README.md`](handoff/README.md).

## Nomenclatura do arquivo

| Regra | ✅ Correto | ❌ Errado |
|-------|-----------|----------|
| Prefixo `handoff_` | `handoff_eda_base_01.md` | `eda_base_01.md` |
| `snake_case`, minúsculas | `handoff_elastic_net_tuning.md` | `handoff_ElasticNet.md` |
| Resumo curto da sessão | `handoff_persistencia_artifacts.md` | `handoff_sessao.md` |
| Sem acentos | `handoff_validacao_walk_forward.md` | `handoff_validação.md` |

## Template

Copiar de [`handoff/_template.md`](handoff/_template.md) ou usar o bloco abaixo:

```markdown
# Handoff — [Título da sessão]

**Data:** YYYY-MM-DD
**Grupo:** 3 — Elastic Net

## Objetivo
[Pedido e entrega]

## Arquivos alterados
- `path` — [mudança]

## Decisões tomadas
- [Decisão → ADR-XXXX se estrutural]

## Validações executadas
- [ ] Anti-leakage (ADR-0003)
- [ ] Walk-forward (ADR-0002)
- [ ] MAE OOS (ADR-0001)
- [ ] Nomenclatura data/artifacts (ADR-0005)

## Pendências / bloqueios
- [ ] ...

## Próximo passo
**[Responsável]:** [ação]

## Ações git
- **Commit:** não autorizado
- **Push:** não autorizado
```

## Handoffs registrados

Ver índice completo em [`handoff/README.md`](handoff/README.md).
