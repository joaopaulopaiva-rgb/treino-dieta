"""Mostra o plano do dia (corrida + musculação).

Os registros de refeições/peso ficam no banco do painel (ver CLAUDE.md, seção 4), não aqui.

Uso: python3 scripts/hoje.py [AAAA-MM-DD]
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
DIAS_SEMANA = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def carregar(nome):
    return json.loads((RAIZ / "data" / nome).read_text(encoding="utf-8"))


def main():
    dia = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.now(ZoneInfo("America/Fortaleza")).date()
    perfil = carregar("perfil.json")
    plano = carregar("calendario.json")["dias"].get(dia.isoformat(), {})
    mus = carregar("musculacao.json")

    prova = date.fromisoformat(perfil["prova_alvo"]["data"])
    print(f"{DIAS_SEMANA[dia.weekday()]}, {dia:%d/%m/%Y} — faltam {(prova - dia).days} dias para a {perfil['prova_alvo']['nome']}")

    if not plano or plano.get("descanso"):
        print("\nDescanso.")
    if "corrida" in plano:
        c = plano["corrida"]
        km = f" – {c['km']} km" if c["km"] else ""
        print(f"\nCORRIDA: {c['tipo']}{km}")
        for bloco in c["estrutura"]:
            print(f"  • {bloco}")
    if "musculacao" in plano:
        t = mus[plano["musculacao"]]
        print(f"\nMUSCULAÇÃO: {t['nome']}")
        for e in t["exercicios"]:
            print(f"  {e['ordem']}. {e['exercicio']} — {e['series']} x {e['reps']} @ {e['carga']} (desc. {e['descanso']})")
    if plano.get("obs"):
        print(f"\nObs.: {plano['obs']}")

if __name__ == "__main__":
    main()
