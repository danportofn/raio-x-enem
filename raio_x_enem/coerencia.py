"""Medidas de coerência do padrão de respostas.

A TRI espera que quem acerta itens difíceis também acerte os fáceis. Quando isso
não acontece, a nota cai, porque o modelo atribui parte dos acertos ao chute.
"""
from __future__ import annotations

import numpy as np

from .tri import prob_acerto


def indice_guttman(acertos, b) -> float:
    """Proporção de pares (fácil, difícil) em que o candidato errou o fácil e acertou o difícil.

    0 = padrão perfeitamente coerente (escalograma de Guttman); valores altos = incoerente.
    Considera só pares com um acerto e um erro, que são os únicos informativos.
    """
    acertos = np.asarray(acertos, dtype=bool)
    b = np.asarray(b, dtype=float)
    ordem = np.argsort(b)
    x = acertos[ordem]
    k = int(x.sum())
    n = len(x)
    if k in (0, n):
        return 0.0
    # Para cada acerto, conta quantos itens mais fáceis (à esquerda) foram errados.
    erros_acumulados = np.cumsum(~x)
    inversoes = int(erros_acumulados[x].sum())
    return inversoes / (k * (n - k))


def respostas_inesperadas(theta, acertos, a, b, c, posicoes, lim_erro=0.75, lim_acerto=0.35):
    """Lista erros em itens que o candidato deveria acertar e acertos improváveis para o nível dele."""
    p = prob_acerto(theta, np.asarray(a), np.asarray(b), np.asarray(c))
    acertos = np.asarray(acertos, dtype=bool)
    erros = [pos for pos, ok, pi in zip(posicoes, acertos, p) if not ok and pi >= lim_erro]
    sorte = [pos for pos, ok, pi in zip(posicoes, acertos, p) if ok and pi <= lim_acerto]
    return erros, sorte
