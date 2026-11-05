"""Uso: python -m raio_x_enem <co_prova> <respostas> [--espanhol]

Exemplo: python -m raio_x_enem 1471 "ABCDE..." (45 letras, '.' = em branco)
Os códigos de prova estão em data/itens_2025.json.
"""
import argparse

from .provas import ESPANHOL, INGLES, carregar, corrigir


def main():
    ap = argparse.ArgumentParser(description="Calcula a nota TRI do ENEM 2025.")
    ap.add_argument("prova", help="código da prova (ver data/itens_2025.json)")
    ap.add_argument("respostas", help="45 letras na ordem do caderno; '.' = em branco")
    ap.add_argument("--espanhol", action="store_true", help="língua estrangeira espanhol (só Linguagens)")
    args = ap.parse_args()

    p = carregar()["provas"][args.prova]
    r = corrigir(args.prova, args.respostas, ESPANHOL if args.espanhol else INGLES)
    print(f"Prova {args.prova} ({p['area']}, caderno {p['cor'].lower()})")
    print(f"Acertos: {r.acertos} de {r.validos}")
    print(f"Theta: {r.theta:.3f} (dp {r.dp_theta:.3f})")
    print(f"Nota estimada: {r.nota:.1f}")
    print(f"Erros inesperados (chance de acerto >= 75%): {r.erros_inesperados or 'nenhum'}")
    print(f"Acertos improváveis (chance <= 35%): {r.acertos_improvaveis or 'nenhum'}")


if __name__ == "__main__":
    main()
