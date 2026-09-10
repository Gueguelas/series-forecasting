# HANDOFF — Registro de sessões

Documento vivo para transferência de contexto entre integrantes e sessões de IA.  
**Atualizar ao encerrar trabalho relevante.** Commit apenas com autorização explícita.

---

## Sessão atual

_Status: Nenhuma sessão registrada._

### Objetivo
_[O que foi pedido e o que foi entregue nesta sessão]_

### Arquivos alterados
- _Nenhum_

### Decisões tomadas
- _Nenhuma_

### Validações executadas
- [ ] Features revisadas contra ADR-0003 (anti-leakage)
- [ ] Walk-forward com mesmas origens/horizonte (ADR-0002)
- [ ] MAE calculado apenas em previsões OOS
- [ ] Seeds e versões documentados

### Pendências / bloqueios
- [ ] Definir número do grupo e modelo de especialização
- [ ] Receber datasets e organizar em `data/base_01/` … `data/base_05/`
- [ ] Criar `notebooks/base_01.ipynb` … `base_05.ipynb` + `relatorio.ipynb`
- [ ] Fixar horizonte e protocolo walk-forward

### Próximo passo
_Ação concreta + responsável sugerido_

### Ações git
- **Commit:** não autorizado / autorizado por [nome] — _mensagem sugerida_
- **Push:** não autorizado

---

## Histórico de sessões

<!-- Copiar o bloco abaixo para cada sessão encerrada, mais recente no topo -->

<!--
## YYYY-MM-DD — [Título curto]

### Objetivo
...

### Arquivos alterados
- `path/arquivo` — resumo

### Decisões tomadas
- ...

### Validações executadas
- [x] ...

### Pendências
- ...

### Próximo passo
...

### Ações git
- Commit: não realizado (aguardando revisão)
-->

---

## Template rápido (copiar para nova sessão)

```markdown
## YYYY-MM-DD — [Título]

### Objetivo
[Pedido e entrega]

### Arquivos alterados
- `path` — [mudança]

### Decisões tomadas
- [Decisão → ADR-XXXX se estrutural]

### Validações executadas
- [ ] Anti-leakage
- [ ] Walk-forward
- [ ] MAE OOS
- [ ] Reprodutibilidade

### Pendências
- [ ] ...

### Próximo passo
[Responsável]: [ação]

### Ações git
- Commit: não autorizado
- Push: não autorizado
```
