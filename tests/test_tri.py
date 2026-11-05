import json
import random
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from raio_x_enem import corrigir, eap, indice_guttman, itens_da_prova, prob_acerto
from raio_x_enem.provas import carregar

RAIZ = Path(__file__).resolve().parent.parent


def test_probabilidade_entre_chute_e_um():
    th = np.linspace(-6, 6, 50)
    p = prob_acerto(th, a=2.0, b=0.5, c=0.2)
    assert np.all(p >= 0.2) and np.all(p <= 1.0)
    assert np.all(np.diff(p) > 0)  # cresce com a proficiência


def test_no_ponto_b_probabilidade_e_media_entre_c_e_um():
    assert prob_acerto(0.5, a=2.0, b=0.5, c=0.2) == pytest.approx(0.6)


def test_mais_acertos_coerentes_aumentam_a_nota():
    a = np.full(10, 2.0); b = np.linspace(-2, 2, 10); c = np.full(10, 0.2)
    thetas = [eap(np.arange(10) < k, a, b, c)[0] for k in range(11)]
    assert all(t2 > t1 for t1, t2 in zip(thetas, thetas[1:]))


def test_mesmos_acertos_padrao_incoerente_tem_nota_menor():
    prova = "1471" if "1471" in carregar()["provas"] else next(iter(carregar()["provas"]))
    itens = [it for it in itens_da_prova(prova) if it["gabarito"]]
    ordem = sorted(range(len(itens)), key=lambda i: itens[i]["b"])
    k = 15

    def folha(acertar):
        letras = []
        for i, it in enumerate(itens_da_prova(prova)):
            if it["gabarito"] is None:
                letras.append(".")
            else:
                letras.append(it["gabarito"] if i in acertar else ("A" if it["gabarito"] != "A" else "B"))
        return "".join(letras)

    idx = [i for i, it in enumerate(itens_da_prova(prova)) if it["gabarito"]]
    faceis = {idx[j] for j in ordem[:k]}
    dificeis = {idx[j] for j in ordem[-k:]}
    rf, rd = corrigir(prova, folha(faceis)), corrigir(prova, folha(dificeis))
    assert rf.acertos == rd.acertos == k
    assert rf.nota > rd.nota + 50


def test_indice_guttman():
    b = [0, 1, 2, 3]
    assert indice_guttman([1, 1, 0, 0], b) == 0.0
    assert indice_guttman([0, 0, 1, 1], b) == 1.0
    assert indice_guttman([1, 1, 1, 1], b) == 0.0


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js não instalado")
def test_python_reproduz_o_motor_javascript_do_site():
    """O motor em Python precisa dar a mesma nota que a calculadora do site."""
    random.seed(42)
    casos = []
    for co_prova, p in carregar()["provas"].items():
        for lingua in ([0, 1] if p["area"] == "LC" else [0]):
            for _ in range(5):
                casos.append([co_prova, lingua, "".join(random.choice("ABCDE.") for _ in range(45))])

    script = r"""
const fs = require('fs');
const html = fs.readFileSync(process.argv[process.argv.length - 1], 'utf8');
const D = JSON.parse(html.match(/<script id="data" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const src = html.match(/function enemScore[\s\S]*?\n}\n/)[0];
eval(src);
const casos = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = casos.map(([k, l, r]) => enemScore(D.provas[k], D.provas[k].area, l, r, D.K).nota);
console.log(JSON.stringify(out));
"""
    res = subprocess.run(
        ["node", "-e", script, str(RAIZ / "web" / "index.html")],
        input=json.dumps(casos), capture_output=True, text=True, check=True,
    )
    notas_js = json.loads(res.stdout)
    notas_py = [corrigir(k, r, l).nota for k, l, r in casos]
    assert np.allclose(notas_py, notas_js, atol=1e-6)
