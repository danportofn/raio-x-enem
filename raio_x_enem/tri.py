"""Motor TRI do ENEM: modelo logístico de 3 parâmetros (3PL) com estimativa EAP.

O INEP estima a proficiência de cada candidato assim:

* Probabilidade de acerto no item i, dado o traço latente theta:
      P_i(theta) = c_i + (1 - c_i) / (1 + exp(-a_i * (theta - b_i)))
  a = discriminação, b = dificuldade, c = acerto ao acaso (chute).
  Os parâmetros publicados nos microdados já estão na métrica sem a constante D = 1,7.

* Estimativa EAP (Expected A Posteriori): theta é a média da distribuição a
  posteriori, com priori normal padrão N(0, 1). A integral é aproximada por
  quadratura em uma grade de pontos igualmente espaçados.

* Nota na escala do ENEM: transformação linear  nota = media + escala * theta,
  com constantes próprias de cada área e de cada edição.
"""
from __future__ import annotations

import numpy as np

GRADE_PADRAO = np.linspace(-6.0, 6.0, 121)


def prob_acerto(theta, a, b, c):
    """Probabilidade de acerto no modelo 3PL. Aceita escalares ou arrays (broadcast)."""
    theta = np.asarray(theta, dtype=float)
    return c + (1.0 - c) / (1.0 + np.exp(-a * (theta - b)))


def log_verossimilhanca(acertos, a, b, c, grade=GRADE_PADRAO):
    """Log-verossimilhança do padrão de respostas em cada ponto da grade.

    acertos: array booleano (n_itens,). a, b, c: arrays (n_itens,).
    Retorna array (n_pontos,).
    """
    acertos = np.asarray(acertos, dtype=bool)
    p = prob_acerto(grade[:, None], np.asarray(a), np.asarray(b), np.asarray(c))
    return np.where(acertos[None, :], np.log(p), np.log1p(-p)).sum(axis=1)


def eap(acertos, a, b, c, grade=GRADE_PADRAO):
    """Estima theta (EAP) e o desvio-padrão a posteriori.

    Usa a priori N(0,1). A subtração do máximo antes da exponencial evita underflow.
    """
    log_post = log_verossimilhanca(acertos, a, b, c, grade) - 0.5 * grade**2
    w = np.exp(log_post - log_post.max())
    w /= w.sum()
    theta = float((w * grade).sum())
    dp = float(np.sqrt((w * (grade - theta) ** 2).sum()))
    return theta, dp


def theta_para_nota(theta: float, escala: float, media: float) -> float:
    """Converte theta para a escala de notas da área (ex.: Matemática 2025)."""
    return media + escala * theta
