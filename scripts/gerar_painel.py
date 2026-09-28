"""Gera painel/index.html a partir do template + plano (data/*.json).

Rodar sempre que o plano de treino ou o perfil mudar, e republicar o artifact.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def ler(nome):
    return json.loads((RAIZ / "data" / nome).read_text(encoding="utf-8"))


def main():
    plano = {"musculacao": ler("musculacao.json"), "calendario": ler("calendario.json")}
    html = (RAIZ / "painel" / "painel.template.html").read_text(encoding="utf-8")
    html = html.replace("__PLANO__", json.dumps(plano, ensure_ascii=False))
    html = html.replace("__PERFIL__", json.dumps(ler("perfil.json"), ensure_ascii=False))
    (RAIZ / "painel" / "index.html").write_text(html, encoding="utf-8")
    print("painel/index.html gerado")


if __name__ == "__main__":
    main()
