"""Puxa as atividades do Strava (Amazfit -> Zepp -> Strava) para data/atividades.json.

Roda no GitHub Actions (.github/workflows/strava.yml). Segredos do repositório:
  STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET  — do app criado em strava.com/settings/api
  STRAVA_AUTH_CODE                         — só na primeira vez (código de autorização)

O refresh token do Strava muda com o tempo, então fica salvo no próprio repositório,
criptografado com o client secret (data/.strava_token.enc).
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TOKEN_ENC = RAIZ / "data" / ".strava_token.enc"
SAIDA = RAIZ / "data" / "atividades.json"
INICIO = "2026-09-21"  # uma semana antes do início do ciclo


def cripto(dados: bytes, decifrar: bool) -> bytes:
    args = ["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-a", "-A", "-pass", "env:STRAVA_CLIENT_SECRET"]
    if decifrar:
        args.append("-d")
    return subprocess.run(args, input=dados, capture_output=True, check=True).stdout


def post(url, campos):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(campos).encode(), method="POST")
    return pedir(req)


def get(url, token):
    return pedir(urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"}))


def pedir(req, tentativas=4):
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code < 500 and e.code != 429:
                sys.exit(f"Strava recusou ({e.code}): {e.read().decode()[:300]}")
        except urllib.error.URLError:
            pass
        time.sleep(2 ** (i + 1))
    sys.exit(f"Strava não respondeu: {req.full_url}")


def obter_token():
    cid, segredo = os.environ["STRAVA_CLIENT_ID"], os.environ["STRAVA_CLIENT_SECRET"]
    base = {"client_id": cid, "client_secret": segredo}
    if TOKEN_ENC.exists():
        refresh = cripto(TOKEN_ENC.read_bytes(), decifrar=True).decode().strip()
        r = post("https://www.strava.com/oauth/token", {**base, "grant_type": "refresh_token", "refresh_token": refresh})
    else:
        codigo = os.environ.get("STRAVA_AUTH_CODE", "").strip()
        if not codigo:
            sys.exit("Sem token salvo e sem STRAVA_AUTH_CODE — veja a configuração no CLAUDE.md, seção 7.")
        r = post("https://www.strava.com/oauth/token", {**base, "grant_type": "authorization_code", "code": codigo})
        if "activity:read" not in r.get("scope", "activity:read"):
            sys.exit("A autorização não incluiu leitura de atividades. Refaça o link de autorização.")
    TOKEN_ENC.write_bytes(cripto(r["refresh_token"].encode(), decifrar=False))
    return r["access_token"]


def pace(seg_por_km):
    if not seg_por_km:
        return None
    s = round(seg_por_km)
    return f"{s // 60}:{s % 60:02d}"


def resumir(a):
    km = a.get("distance", 0) / 1000
    mov = a.get("moving_time", 0)
    res = {
        "id": a["id"],
        "data": a["start_date_local"][:10],
        "hora": a["start_date_local"][11:16],
        "tipo": a.get("sport_type") or a.get("type"),
        "nome": a.get("name"),
        "distancia_km": round(km, 2),
        "tempo_mov_s": mov,
        "pace_medio": pace(mov / km) if km else None,
        "fc_media": a.get("average_heartrate"),
        "fc_max": a.get("max_heartrate"),
        "elevacao_m": a.get("total_elevation_gain"),
        "calorias": a.get("calories"),
    }
    if a.get("splits_metric"):
        res["parciais_km"] = [
            {"km": s["split"], "pace": pace(s["moving_time"] / (s["distance"] / 1000)) if s.get("distance") else None,
             "fc": s.get("average_heartrate")}
            for s in a["splits_metric"]
        ]
    if a.get("laps") and len(a["laps"]) > 1:
        res["voltas"] = [
            {"n": l.get("lap_index"), "dist_m": round(l.get("distance", 0)), "tempo_s": l.get("moving_time"),
             "pace": pace(l["moving_time"] / (l["distance"] / 1000)) if l.get("distance") else None,
             "fc": l.get("average_heartrate")}
            for l in a["laps"]
        ]
    return res


def main():
    token = obter_token()
    atual = json.loads(SAIDA.read_text(encoding="utf-8")) if SAIDA.exists() else {"atividades": {}}
    ativs = atual["atividades"]
    desde = max([INICIO] + [a["data"] for a in ativs.values()])
    depois = int(time.mktime(time.strptime(desde, "%Y-%m-%d"))) - 3 * 86400
    novos = 0
    pagina = 1
    while True:
        lista = get(f"https://www.strava.com/api/v3/athlete/activities?after={depois}&per_page=50&page={pagina}", token)
        if not lista:
            break
        for a in lista:
            detalhe = get(f"https://www.strava.com/api/v3/activities/{a['id']}", token)
            ativs[str(a["id"])] = resumir(detalhe)
            novos += 1
        pagina += 1
    atual["atualizado_em"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    SAIDA.write_text(json.dumps(atual, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{novos} atividade(s) lidas; {len(ativs)} no total.")


if __name__ == "__main__":
    main()
