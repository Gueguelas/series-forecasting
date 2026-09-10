# ADR-0002: Validação walk-forward obrigatória

**Status:** Aceita  
**Data:** 2026-09-10  
**Fonte:** `docs/instrucoes.pdf` seções 5.4 e 5.6

## Contexto

O enunciado exige validação walk-forward que simula o uso real: treinar só com histórico disponível, prever o horizonte, avançar o tempo e repetir. Todos os modelos devem usar as mesmas origens, horizonte e conjunto de teste.

## Decisão

1. Implementar walk-forward com:
   - Janela inicial de treinamento definida e documentada
   - Horizonte de previsão **h** fixo e igual para todos os modelos
   - Mesmas **datas de origem** para todas as combinações base × modelo
2. **Hiperparâmetros fixos** durante a avaliação final no período de teste (selecionados antes, sem usar o teste para tuning).
3. Registrar previsões, resíduos e tempo de execução por combinação.

## Parâmetros a definir (pendente)

| Parâmetro | Valor | ADR futura |
|-----------|-------|------------|
| Horizonte h | [DEFINIR] | ADR-0005 (sugerido) |
| Primeira origem | [DEFINIR] | ADR-0005 |
| Janela mínima de treino | [DEFINIR] | ADR-0005 |
| Período de teste | [DEFINIR] | ADR-0005 |

## Consequências

- Spec detalhada: [`specs/spec-validacao.md`](../specs/spec-validacao.md)
- Holt-Winters participa com mesmo calendário de origens (sem features externas)
