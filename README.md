# Raio-X ENEM 2025

Reimplementação do cálculo de nota do ENEM pela **Teoria de Resposta ao Item (TRI)**, a partir dos microdados oficiais do INEP, e um site interativo com cinco análises da prova de 2025.

**[Abrir o site](https://raio-x-enem.vercel.app)** · Python + NumPy · JavaScript puro, sem dependências

## O que o projeto faz

| Seção | O que mostra |
|---|---|
| **Calculadora de nota TRI** | Nota estimada a partir do gabarito de qualquer caderno, com θ, percentil nacional e diagnóstico de coerência |
| **Coerência** | Por que o mesmo número de acertos gera notas até ~300 pontos diferentes |
| **Itens do topo** | Quais questões separam o 1% de cima, pela correlação ponto-bisserial dentro dos 10% melhores |
| **Redação** | Distribuição por competência e onde as redações 900–980 perdem pontos |
| **Posição no país** | Percentil nacional, por UF e por rede de ensino |

## Como a nota é calculada

O INEP usa o modelo logístico de 3 parâmetros. A probabilidade de um candidato com proficiência θ acertar o item *i* é

$$P_i(\theta) = c_i + \frac{1 - c_i}{1 + e^{-a_i(\theta - b_i)}}$$

onde *a* é a discriminação, *b* a dificuldade e *c* a chance de acerto ao acaso. Os três são publicados nos microdados.

A proficiência é estimada por **EAP** (*Expected A Posteriori*): a média da distribuição a posteriori de θ, com priori normal padrão, calculada por quadratura em 121 pontos no intervalo [−6, 6]. A nota final é uma transformação linear de θ com constantes próprias de cada área.

```python
from raio_x_enem import corrigir

r = corrigir("1471", "DBACE...")   # prova de Matemática, caderno azul; '.' = em branco
r.nota, r.acertos, r.erros_inesperados
```

Ou pela linha de comando:

```bash
python -m raio_x_enem 1471 "DBACEABCDE..."
```

## Validação

O motor foi comparado com a nota oficial de **8 mil candidatos reais**: diferença média de **0,03 ponto**, com 99% das notas reproduzidas a ±0,1. Para refazer a validação:

```bash
python pipeline/validar_contra_oficial.py --resultados RESULTADOS_2025.csv --amostra 8000
```

Os testes automatizados também garantem que o motor em Python e a calculadora do site dão exatamente a mesma nota:

```bash
pip install -r requirements.txt
pytest
```

## O que aprendi com os dados

- **Coerência pesa muito.** Em Matemática, quem acerta só as 29 questões mais fáceis tira cerca de 772; quem acerta só as 29 mais difíceis fica perto de 480.
- **Errar questão fácil custa caro no topo.** A TRI lê o erro como incoerência e reduz a nota mais do que o acerto de uma difícil compensa.
- **Na redação, a Competência 5 (proposta de intervenção) pesa embaixo e a Competência 1 (norma culta) trava em cima.**

## Estrutura

```
raio_x_enem/   motor TRI (3PL + EAP), coerência e correção de provas
data/          parâmetros a, b, c e gabaritos dos 16 cadernos de 2025
web/           site interativo (um único HTML)
pipeline/      validação contra as notas oficiais
tests/         testes, incluindo a equivalência Python × JavaScript
```

## Limitações

- A aplicação especial de Belém, Ananindeua e Marituba (COP30) não tem parâmetros de itens publicados e fica fora da calculadora.
- Desde 2024 os microdados de participantes não se ligam aos de resultados, então não há cruzamentos socioeconômicos.

## Fonte

INEP, [Microdados do ENEM 2025](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem) (arquivos de resultados e de itens da prova).
