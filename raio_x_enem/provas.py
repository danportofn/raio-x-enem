"""Carrega os parâmetros dos itens e corrige uma folha de respostas."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import numpy as np

from .coerencia import respostas_inesperadas
from .tri import eap, theta_para_nota

DADOS = Path(__file__).resolve().parent.parent / "data"
INGLES, ESPANHOL, AMBAS = 0, 1, -1


@lru_cache(maxsize=None)
def carregar(ano: int = 2025) -> dict:
    with open(DADOS / f"itens_{ano}.json", encoding="utf-8") as f:
        return json.load(f)


def itens_da_prova(co_prova: str, lingua: int = INGLES, ano: int = 2025) -> list[dict]:
    """Itens na ordem do caderno. Em Linguagens, as 5 primeiras dependem da língua estrangeira."""
    prova = carregar(ano)["provas"][str(co_prova)]
    return [it for it in prova["itens"] if it["lingua"] in (AMBAS, lingua)]


@dataclass
class Resultado:
    area: str
    acertos: int
    validos: int
    theta: float
    dp_theta: float
    nota: float
    erros_inesperados: list[int] = field(default_factory=list)
    acertos_improvaveis: list[int] = field(default_factory=list)


def corrigir(co_prova: str, respostas: str, lingua: int = INGLES, ano: int = 2025) -> Resultado:
    """Corrige uma prova e devolve a nota TRI estimada.

    respostas: 45 letras na ordem do caderno; '.' ou ' ' = em branco (conta como erro).
    Itens anulados (sem gabarito) ficam fora do cálculo, como no ENEM.
    """
    base = carregar(ano)
    area = base["provas"][str(co_prova)]["area"]
    itens = itens_da_prova(co_prova, lingua, ano)
    respostas = respostas.upper().ljust(len(itens), ".")

    validos = [(it, r) for it, r in zip(itens, respostas) if it["gabarito"] is not None]
    acertos = np.array([r == it["gabarito"] for it, r in validos])
    a, b, c = (np.array([it[k] for it, _ in validos]) for k in "abc")

    theta, dp = eap(acertos, a, b, c)
    conv = base["conversao"][area]
    posicoes = [it["posicao"] for it, _ in validos]
    inesperados, improvaveis = respostas_inesperadas(theta, acertos, a, b, c, posicoes)

    return Resultado(
        area=area,
        acertos=int(acertos.sum()),
        validos=len(validos),
        theta=theta,
        dp_theta=dp,
        nota=theta_para_nota(theta, conv["escala"], conv["media"]),
        erros_inesperados=inesperados,
        acertos_improvaveis=improvaveis,
    )
