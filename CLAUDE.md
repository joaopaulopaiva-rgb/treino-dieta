# Treino & Dieta — João Paulo

Contexto persistente. Qualquer sessão do Claude Code neste repositório deve ler este arquivo primeiro.

## 1. O que é

Sistema pessoal de acompanhamento de treinos (corrida + musculação) e dieta. Funciona por conversa: o JP diz o que comeu / treinou / pesou, o Claude registra no banco do painel (seção 4) e responde com o saldo do dia. Também deve dizer qual é o treino do dia e dar recomendações curtas (dieta ajustada ao treino, recuperação, preparação para a prova).

## 2. Perfil (ver `data/perfil.json`)

- 35 anos, homem, 183 cm, 87 kg (28/09/2026), trabalho sentado, treina normalmente às 17h, Natal-RN (fuso `America/Fortaleza`, UTC-3).
- Objetivo: **desempenho**, mantendo bom nível muscular e baixo percentual de gordura.
- **Prova-alvo: Meia Maratona PRF — 08/11/2026** (prova de corrida organizada pela PRF, **não** é TAF).
- Sem lesões, restrições ou condições médicas informadas.
- Macros base (definidos pelo JP): **Carb 232 g · Gordura 89 g · Proteína 232 g ≈ 2.657 kcal**.
- **Dias de longão e intervalado** (aprovado pelo JP em 28/09/2026): **Carb 300 g · Gordura 75 g · Proteína 232 g ≈ 2.803 kcal**. Marcados com `"meta": "intenso"` em `data/calendario.json`; valores em `config/metas.por_tipo.intenso` no banco do painel e em `data/perfil.json`.

## 3. Plano de treino

- Fonte original: `fontes/TREINO_JP.xlsx` (abas `UPPERLOWER` e `CORRIDA`).
- `data/musculacao.json`: os 4 treinos (T1 Upper, T2 Lower quadríceps, T3 Upper 2, T4 Lower posterior).
- `data/calendario.json`: plano dia a dia até a prova (corrida + qual treino de musculação). Dia ausente = descanso.
- Padrão semanal: seg = longão; ter = Lower; qua = intervalado + Upper; qui = Lower; sex = rodagem + Upper; sáb/dom = descanso.
- A planilha só diz "UPPER"/"LOWER"; mapeamento confirmado pelo JP: 1º lower da semana = T2, 1º upper = T1, 2º lower = T4, 2º upper = T3.
- 06/11 (sexta antes da prova): Upper 2 é **opcional** — pode ser descanso.
- `python3 scripts/hoje.py [AAAA-MM-DD]` mostra o plano do dia e o saldo de macros.

## 4. Registro diário — fica no banco do painel

**Fonte da verdade dos registros: o banco (`db`) do painel** — https://claude.ai/artifact/5AySTTsH6QVDPsTuCyGE3o
Ler/escrever com a ferramenta `ArtifactData` (url acima). O JP lança tanto pelo painel quanto pela conversa; os dois gravam no mesmo lugar. `data/registros/` no repositório não é usado.

- `config/metas` → `{"base": {...}, "por_tipo": {"intenso": {...}}}` — metas de macros. Ordem no painel: `meta` do próprio dia > meta do tipo do dia no calendário > base. Mudar só com aprovação do JP.
- `dias/<AAAA-MM-DD>` → um documento por dia:

```json
{
  "data": "2026-09-28",
  "meta": {"kcal": 2800, "carb_g": 300, "prot_g": 232, "gord_g": 75},   // opcional: só quando o dia tem meta ajustada
  "meta_nome": "Dia de longão",                                         // opcional: rótulo exibido no painel
  "peso_kg": 87.0,                       // pesagem da manhã; a data é o id do documento
  "peso_hora": "06:45",                   // hora local (Natal) em que foi salvo; vazio se lançado depois
  "peso_registrado_em": "2026-09-28T09:45:00Z",
  "refeicoes": [
    {"id": "m<base36>", "hora": "07:30", "nome": "Café da manhã", "descricao": "texto como o JP escreveu",
     "origem": "painel|claude", "pendente": false,
     "itens": [{"alimento": "Ovo inteiro cozido", "qtd": "2 un (100 g)", "kcal": 146, "carb_g": 1, "prot_g": 13, "gord_g": 10,
                "fibra_g": 0, "sodio_mg": 140, "tags": ["farinha refinada|ultraprocessado|açúcar adicionado|fritura|integral|fruta/verdura"]}]}
  ],
  "analise_alimentacao": {"nota": 6.4, "resumo": "...", "distribuicao": "...",
    "micronutrientes": [{"nome": "Fibra", "estimado": "9 g", "referencia": "30–38 g", "status": "baixo|ok|alto", "comentario": "..."}],
    "alertas": ["..."], "sugestoes": ["..."], "gerado_em": "ISO", "origem": "painel|claude"},
  "treino_feito": {"corrida": true, "musculacao": false, "obs": "texto livre",
    "exercicios_feitos": [1, 2, 3],   // ordem dos exercícios de musculação marcados; todos marcados => musculacao: true
    "resultado": {"fonte": "Zepp|Samsung Health|manual|Strava", "distancia_km": 12.04, "tempo": "1:10:12", "pace_medio": "5:50",
                  "fc_media": 156, "fc_max": 176, "calorias": 890, "salvo_em": "ISO",
                  "parciais": [{"n": 1, "dist_km": 1, "pace": "6:36", "fc": 138}]},   // parciais = km ou voltas/tiros
    "prints": [{"id": "<asset id 32 hex>", "enviado_em": "ISO"}],   // prints guardados no painel (assets)
    "print_pendente": true,                                          // print guardado e ainda não lido
    "analise": {"nota": 7.8, "confianca": "alta|média|baixa", "resumo": "...", "pontos_fortes": ["..."],
                "ajustes": ["..."], "proximo": "...", "gerado_em": "ISO", "origem": "painel|claude"}},
  "notas": ""
}
```

- Sempre ler o documento do dia antes de escrever e passar `if_version` (o painel pode ter gravado algo).
- `pendente: true` = o JP salvou só a descrição pelo painel; ao abrir uma conversa, procurar refeições pendentes, calcular os `itens` e gravar `pendente: false`.
- Estimar valores pela **tabela TACO** (e rótulo, quando o JP informar a marca). Quantidade não dita → medida caseira típica, avisando que foi estimado.
- Toda resposta de lançamento termina com: consumido / meta / falta (kcal, carbo, proteína, gordura).

### Painel
- Fonte: `painel/painel.template.html`; `python3 scripts/gerar_painel.py` gera `painel/index.html` embutindo `data/musculacao.json`, `data/calendario.json` e `data/perfil.json`.
- Mudou o plano ou o perfil → regenerar e republicar com a ferramenta `Artifact` passando `url` acima (nunca publicar sem `url`, senão cria outro painel).
- Capacidades: `db` (só o dono/editores escrevem), `sample` (Calcular macros, ler print quando a tela permite, análise do treino — usa o Claude da conta do JP) e `assets` (prints guardados). Ao republicar, repassar as três em `capabilities` ou omitir para manter.
- Compartilhamento: em 28/09 o painel estava como "qualquer pessoa com o link" (leitura). Só o JP escreve.

- **Prints pendentes (fazer ao abrir toda conversa):** procurar `treino_feito.print_pendente: true` nos dias recentes. Para cada print, baixar com `Artifact` `action: "read"`, `url` do painel e `path: <asset id>`; ler a imagem; gravar `treino_feito.resultado` (formato acima), `print_pendente: false` e uma `analise` (origem "claude") com os mesmos critérios do painel. Motivo: no navegador do celular o painel não consegue mandar imagem para o Claude (sample sem suporte a imagens nessa tela), então o print fica guardado e a leitura é feita na conversa.
- Análise/nota: botão "Analisar treino e dar nota" no painel (usa `sample`, só texto). Critérios, em ordem de peso: estrutura e distância cumpridas; ritmo de cada bloco dentro da faixa (rápido demais também é desvio); consistência e fim de treino; FC coerente; relato do atleta. Nota 0–10 com uma casa decimal.
- Treino: o card mostra **Previsto x Realizado** lado a lado. O JP pode enviar print do Samsung Health/Zepp (lido pelo `sample` com imagens) ou digitar. Cada parcial é marcada "no alvo / rápido / lento" (±3 s) contra o pace do bloco do plano (por km acumulado; tiros casados pela distância ±12%). Se ele mandar o print na conversa, extrair e gravar em `treino_feito.resultado` no mesmo formato.
- Musculação no painel: lista com checkbox por exercício (só nome + séries × reps; % de carga e descanso ficam fora da tela por pedido do JP, mas continuam em `data/musculacao.json`).
- Alimentação: horário de cada refeição é editável no painel (tocar no horário). Gráfico "Distribuição no dia" (kcal por refeição por hora, com faixa do treino às 17h) e avisos de concentração (≥45% das kcal numa refeição, ou todas no mesmo horário = provavelmente lançadas juntas). Botão "Analisar alimentação do dia" (sample) → `analise_alimentacao`: nota, distribuição, micronutrientes estimados (fibra, sódio, potássio, cálcio, ferro, magnésio, vit. C, ômega-3), alertas (farinha refinada, ultraprocessados etc.) e sugestões. Quando lançar refeição pela conversa, preencher também `fibra_g`, `sodio_mg` e `tags`.
- Peso: o painel tem a seção "Peso da manhã" no topo, com campo de data (padrão = hoje) — permite lançar um dia esquecido. Quando o JP disser o peso na conversa, gravar no dia certo com `peso_hora`.

## 5. Recomendações

- Curtas e práticas, ligadas ao treino do dia (pré/pós-treino, carbo em dia de volume, hidratação no calor de Natal).
- Base: diretrizes de nutrição esportiva (ACSM/IOC/ISSN). Pesquisar na web quando for algo específico.
- Sugestões de apoio, não substituem nutricionista/educador físico. **Nunca alterar a meta base sem o JP aprovar.**

## 6. Estilo

- Português, direto. Tratar por "você".
- Registros vão para o banco do painel (não precisam de commit). Mudanças de plano/código: commit + push (o ambiente é efêmero).

## 7. Strava (relógio Amazfit)

Caminho: Amazfit → app Zepp → Strava → `.github/workflows/strava.yml` (21:13 e 06:13 em Natal, + manual) → `scripts/strava_sync.py` → `data/atividades.json` (resumo, parciais por km, voltas/tiros, FC).
- Workflow criado com autorização do JP (28/09/2026). **Configuração ainda pendente** — enquanto os segredos não existirem, o workflow só registra "Strava ainda não configurado" e termina.
- Passos para o JP (guiar quando ele quiser fazer):
  1. Zepp: Perfil → Adicionar contas → Strava.
  2. strava.com/settings/api → criar app (Website: qualquer; Authorization Callback Domain: `localhost`). Anotar Client ID e Client Secret.
  3. Abrir `https://www.strava.com/oauth/authorize?client_id=<ID>&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=read,activity:read_all`, autorizar, e copiar o `code=` da URL (a página dá erro, é normal).
  4. GitHub → treino-dieta → Settings → Secrets and variables → Actions: `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`, `STRAVA_AUTH_CODE`.
  5. Actions → Sincronizar Strava → Run workflow (o código expira rápido: rodar logo após o passo 3).
- O refresh token fica em `data/.strava_token.enc` (criptografado com o client secret). Se der erro de autorização, refazer passos 3–5 apagando esse arquivo.
- Uso: ao conversar, ler `data/atividades.json` (dar `git pull`), comparar com o planejado em `data/calendario.json` e gravar em `treino_feito.resultado` (fonte "Strava") no banco do painel.
