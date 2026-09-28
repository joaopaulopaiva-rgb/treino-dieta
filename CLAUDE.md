# Treino & Dieta — João Paulo

Contexto persistente. Qualquer sessão do Claude Code neste repositório deve ler este arquivo primeiro.

## 1. O que é

Sistema pessoal de acompanhamento de treinos (corrida + musculação) e dieta. Funciona por conversa: o JP diz o que comeu / treinou / pesou, o Claude registra nos arquivos de `data/`, faz commit/push e responde com o saldo do dia. Também deve dizer qual é o treino do dia e dar recomendações curtas (dieta ajustada ao treino, recuperação, preparação para a prova).

## 2. Perfil (ver `data/perfil.json`)

- 35 anos, homem, 183 cm, 87 kg (28/09/2026), trabalho sentado, treina normalmente às 17h, Natal-RN (fuso `America/Fortaleza`, UTC-3).
- Objetivo: **desempenho**, mantendo bom nível muscular e baixo percentual de gordura.
- **Prova-alvo: Meia Maratona PRF — 08/11/2026** (prova de corrida organizada pela PRF, **não** é TAF).
- Sem lesões, restrições ou condições médicas informadas.
- Macros base (definidos pelo JP): **Carb 232 g · Gordura 89 g · Proteína 232 g ≈ 2.657 kcal**.

## 3. Plano de treino

- Fonte original: `fontes/TREINO_JP.xlsx` (abas `UPPERLOWER` e `CORRIDA`).
- `data/musculacao.json`: os 4 treinos (T1 Upper, T2 Lower quadríceps, T3 Upper 2, T4 Lower posterior).
- `data/calendario.json`: plano dia a dia até a prova (corrida + qual treino de musculação). Dia ausente = descanso.
- Padrão semanal: seg = longão; ter = Lower; qua = intervalado + Upper; qui = Lower; sex = rodagem + Upper; sáb/dom = descanso.
- A planilha só diz "UPPER"/"LOWER"; mapeamento confirmado pelo JP: 1º lower da semana = T2, 1º upper = T1, 2º lower = T4, 2º upper = T3.
- 06/11 (sexta antes da prova): Upper 2 é **opcional** — pode ser descanso.
- `python3 scripts/hoje.py [AAAA-MM-DD]` mostra o plano do dia e o saldo de macros.

## 4. Registro diário

Um arquivo por dia em `data/registros/AAAA-MM-DD.json`:

```json
{
  "data": "2026-09-28",
  "meta": {"kcal": 2657, "carb_g": 232, "prot_g": 232, "gord_g": 89},
  "peso_kg": null,
  "refeicoes": [
    {"hora": "07:30", "nome": "Café da manhã", "descricao": "texto como o JP escreveu",
     "itens": [{"alimento": "Ovo inteiro cozido", "qtd": "2 un (100 g)", "kcal": 146, "carb_g": 1, "prot_g": 13, "gord_g": 10}]}
  ],
  "treino_feito": {"corrida": null, "musculacao": null, "obs": ""},
  "notas": ""
}
```

- `meta` do dia pode diferir da base (ex.: mais carbo em dia de longão) — registrar quando for ajustada.
- Estimar valores nutricionais pela **tabela TACO** (e rótulo, quando o JP informar a marca). Quando a quantidade não for dita, usar medida caseira típica e deixar claro na resposta que foi estimado.
- Toda resposta de lançamento termina com: consumido / meta / falta (kcal, carbo, proteína, gordura).

## 5. Recomendações

- Curtas e práticas, ligadas ao treino do dia (pré/pós-treino, carbo em dia de volume, hidratação no calor de Natal).
- Base: diretrizes de nutrição esportiva (ACSM/IOC/ISSN). Pesquisar na web quando for algo específico.
- Sugestões de apoio, não substituem nutricionista/educador físico. **Nunca alterar a meta base sem o JP aprovar.**

## 6. Estilo

- Português, direto. Tratar por "você".
- Commit + push a cada lançamento (o ambiente é efêmero: o que não foi pro GitHub se perde).
