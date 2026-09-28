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
  "peso_kg": 87.0,
  "refeicoes": [
    {"id": "m<base36>", "hora": "07:30", "nome": "Café da manhã", "descricao": "texto como o JP escreveu",
     "origem": "painel|claude", "pendente": false,
     "itens": [{"alimento": "Ovo inteiro cozido", "qtd": "2 un (100 g)", "kcal": 146, "carb_g": 1, "prot_g": 13, "gord_g": 10}]}
  ],
  "treino_feito": {"corrida": true, "musculacao": false, "obs": "texto livre"},
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
- Capacidades: `db` (só o dono/editores escrevem) e `sample` (botão "Calcular macros" usa o Claude da própria conta do JP).

## 5. Recomendações

- Curtas e práticas, ligadas ao treino do dia (pré/pós-treino, carbo em dia de volume, hidratação no calor de Natal).
- Base: diretrizes de nutrição esportiva (ACSM/IOC/ISSN). Pesquisar na web quando for algo específico.
- Sugestões de apoio, não substituem nutricionista/educador físico. **Nunca alterar a meta base sem o JP aprovar.**

## 6. Estilo

- Português, direto. Tratar por "você".
- Registros vão para o banco do painel (não precisam de commit). Mudanças de plano/código: commit + push (o ambiente é efêmero).
