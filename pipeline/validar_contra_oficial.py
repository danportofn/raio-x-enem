"""Compara a nota calculada pelo motor com a nota oficial do INEP.

Pré-requisito: baixar os Microdados do ENEM 2025 em
https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem
e apontar --resultados para o CSV de resultados (separador ';', encoding latin-1).

Uso:
    python pipeline/validar_contra_oficial.py --resultados caminho/RESULTADOS_2025.csv --amostra 8000

Saída: diferença média absoluta e a fração de candidatos reproduzidos a ±0,1 ponto, por área.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from raio_x_enem.provas import carregar, corrigir  # noqa: E402

AREAS = ["CN", "CH", "LC", "MT"]


def respostas_lc(texto: str) -> str:
    """No microdado, Linguagens traz as respostas das duas línguas; a não escolhida vem como '9'."""
    if len(texto) > 45:
        texto = texto[:10].replace("9", "") + texto[10:]
    return texto


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resultados", required=True, type=Path)
    ap.add_argument("--amostra", type=int, default=8000, help="candidatos por área")
    ap.add_argument("--semente", type=int, default=0)
    args = ap.parse_args()

    provas = carregar()["provas"]
    cols = ["TP_LINGUA"] + [f"{p}_{a}" for a in AREAS for p in ("CO_PROVA", "NU_NOTA", "TX_RESPOSTAS")]
    df = pd.read_csv(args.resultados, sep=";", encoding="latin-1", usecols=cols, dtype=str)

    for area in AREAS:
        d = df.dropna(subset=[f"CO_PROVA_{area}", f"NU_NOTA_{area}", f"TX_RESPOSTAS_{area}"])
        d = d[d[f"CO_PROVA_{area}"].isin(provas.keys())]
        d = d[d[f"NU_NOTA_{area}"].astype(float) > 0]
        d = d.sample(min(args.amostra, len(d)), random_state=args.semente)

        diffs = []
        for _, row in d.iterrows():
            resp = row[f"TX_RESPOSTAS_{area}"]
            lingua = int(row["TP_LINGUA"]) if area == "LC" else 0
            if area == "LC":
                resp = respostas_lc(resp)
            nota = corrigir(row[f"CO_PROVA_{area}"], resp, lingua).nota
            diffs.append(nota - float(row[f"NU_NOTA_{area}"]))

        diffs = np.abs(np.array(diffs))
        print(f"{area}: n={len(diffs)}  dif. média={diffs.mean():.3f}  "
              f"±0,1 ponto={np.mean(diffs <= 0.1):.1%}  máx={diffs.max():.2f}")


if __name__ == "__main__":
    main()
