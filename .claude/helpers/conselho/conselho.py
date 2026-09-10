#!/usr/bin/env python3
"""CONSELHO — segunda opinião de outros motores (GPT, Grok, Gemini, DeepSeek…), em paralelo, por API.

A missão estratégica gera uma tese. O mesmo prompt ADVERSARIAL vai para 3–4 modelos de laboratórios
diferentes; cada um devolve as razões mais fortes contra a tese. Modelos de origens diferentes têm
pontos cegos diferentes — é isso que compra a segunda opinião. A síntese é do Claude (skill /conselho).

Uso:
  conselho.py --status                       quais chaves/motores estão prontos (exit 2 = nenhum)
  conselho.py --listar                       modelos disponíveis por provedor (rede)
  conselho.py --tese "..." [--contexto "..."] [--modo contra|livre] [--max 4] [--saida x.md] [--json]
  conselho.py --arquivo tese.md              tese lida de arquivo (stdin com "-")
  --modelo prov:id  (repetível) força modelos; ou env CONSELHO_MODELOS="openrouter:openai/gpt-5,gemini:gemini-2.5-pro"

Chaves (só leitura, nunca gravadas, nunca impressas): variáveis de ambiente OPENROUTER_API_KEY (uma chave,
todos os modelos — recomendado), OPENAI_API_KEY, XAI_API_KEY, GEMINI_API_KEY, DEEPSEEK_API_KEY.
Sem variável, tenta arquivos .env FORA do repositório: $CONSELHO_ENV, ~/.config/cerebro/conselho.env,
iCloud CEREBRO-CHAVES-BACKUP/conselho.env (convenção do Cérebro mestre).

Modo "credencial no proxy" (Claude Code na web, planos Pro/Max): a chave fica em API credentials do
ambiente e o proxy da Anthropic a injeta nas requisições para o host; o helper detecta isso sozinho
(sonda autenticada responde 200 sem chave) e então NÃO envia Authorization — o proxy envia.

Só biblioteca padrão. Todos os provedores falam o formato OpenAI (chat/completions); o Gemini pelo
endpoint compatível. Custo: calculado do preço por token quando o provedor informa (OpenRouter).
"""
import concurrent.futures as cf
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

PROVEDORES = {
    "openrouter": {
        "base": "https://openrouter.ai/api/v1",
        "chave": "OPENROUTER_API_KEY",
        "sonda": "/auth/key",  # exige auth: 200 sem enviarmos chave = o proxy da nuvem injetou a credencial
        "familias": {"openai": r"^openai/gpt-", "xai": r"^x-ai/grok-", "google": r"^google/gemini-", "deepseek": r"^deepseek/deepseek-"},
    },
    "openai": {"base": "https://api.openai.com/v1", "chave": "OPENAI_API_KEY", "familias": {"openai": r"^gpt-"}},
    "xai": {"base": "https://api.x.ai/v1", "chave": "XAI_API_KEY", "familias": {"xai": r"^grok-"}},
    "gemini": {
        "base": "https://generativelanguage.googleapis.com/v1beta/openai",
        "chave": "GEMINI_API_KEY",
        "familias": {"google": r"^(models/)?gemini-"},
    },
    "deepseek": {"base": "https://api.deepseek.com/v1", "chave": "DEEPSEEK_API_KEY", "familias": {"deepseek": r"^deepseek-"}},
}
ORDEM_FAMILIAS = ["openai", "xai", "google", "deepseek"]
# variantes especializadas ou instáveis: só entram se não houver outra opção na família
ESPECIALIZADOS = ("codex", "image", "audio", "tts", "search", "vision", "embed", "realtime", "live",
                  "nano", "mini", "lite", "fast", "distill", "-exp", "preview", ":free", ":batch", "instruct",
                  "online", "beta", "oss", "build", "multi-agent")
TETO_USD = float(os.environ.get("CONSELHO_TETO_USD", "0.25"))  # custo máximo estimado por opinião
TOKENS_ESTIMATIVA = (3000, 1200)  # entrada, saída — para estimar custo antes de chamar
TIMEOUT = 120
MAX_TOKENS = 1400

PROMPT_CONTRA = (
    "Você é um crítico rigoroso, cético e bem informado. Sua tarefa NÃO é confirmar: é encontrar as razões mais "
    "fortes pelas quais a tese abaixo está errada, incompleta ou arriscada. Responda em português do Brasil, "
    "sem elogios e sem preâmbulo, em no máximo 500 palavras, exatamente neste formato:\n"
    "1. OBJEÇÕES — as 5 mais fortes, da mais grave para a menos, cada uma com o dado, número ou mecanismo que a sustenta.\n"
    "2. PREMISSAS OCULTAS — o que precisaria ser verdade para a tese funcionar e ainda não foi provado.\n"
    "3. TESTE DE 7 DIAS — o experimento mais barato que invalidaria a tese.\n"
    "4. CONCORRENTE — o que um concorrente competente faria contra isso.\n"
    "5. VEREDITO — uma linha: SEGUIR, AJUSTAR ou MATAR, com o porquê."
)
PROMPT_LIVRE = (
    "Você é um consultor sênior direto e prático. Responda em português do Brasil, sem preâmbulo, com ideias "
    "concretas e o raciocínio por trás, em no máximo 500 palavras."
)


# ---------------------------------------------------------------- chaves
def _carregar_dotenv(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            for l in f:
                l = l.strip()
                if not l or l.startswith("#") or "=" not in l:
                    continue
                k, v = l.split("=", 1)
                k = k.strip().removeprefix("export ").strip()
                v = v.strip().strip('"').strip("'")
                if k and v and k not in os.environ:
                    os.environ[k] = v
    except OSError:
        pass


def carregar_chaves():
    home = os.path.expanduser("~")
    for p in (
        os.environ.get("CONSELHO_ENV"),
        os.path.join(home, ".config", "cerebro", "conselho.env"),
        os.path.join(home, "Library", "Mobile Documents", "com~apple~CloudDocs", "CEREBRO-CHAVES-BACKUP", "conselho.env"),
    ):
        if p and os.path.isfile(p):
            _carregar_dotenv(p)


PROXY = "proxy"  # valor-sentinela: credencial injetada pelo proxy da nuvem, não pelo helper


def chaves_presentes():
    return {p: os.environ.get(cfg["chave"], "").strip() for p, cfg in PROVEDORES.items() if os.environ.get(cfg["chave"], "").strip()}


def _sondar(prov):
    st, _ = http(f"{PROVEDORES[prov]['base']}{PROVEDORES[prov].get('sonda', '/models')}", timeout=8)
    return prov, st == 200


def detectar_proxy():
    """Sem nenhuma chave no ambiente: pergunta a cada provedor, SEM Authorization, se já estamos autenticados.
    200 = o proxy da nuvem injetou a credencial → marca o provedor como disponível via proxy."""
    if chaves_presentes() or os.environ.get("CONSELHO_SEM_SONDA"):
        return []
    achados = []
    with cf.ThreadPoolExecutor(max_workers=len(PROVEDORES)) as ex:
        for prov, ok in ex.map(_sondar, list(PROVEDORES)):
            if ok:
                os.environ[PROVEDORES[prov]["chave"]] = PROXY
                achados.append(prov)
    return achados


def mascarar(txt):
    for v in chaves_presentes().values():
        if v and v != PROXY and len(v) > 6:
            txt = txt.replace(v, v[:4] + "…" + v[-2:])
    return txt


# ---------------------------------------------------------------- HTTP (substituível nos testes)
def _http(url, dados=None, cabecalhos=None, timeout=TIMEOUT):
    corpo = json.dumps(dados).encode("utf-8") if dados is not None else None
    req = urllib.request.Request(url, data=corpo, headers=cabecalhos or {}, method="POST" if corpo else "GET")
    req.add_header("User-Agent", "cerebro-conselho/1.0")
    if corpo:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def http(url, dados=None, cabecalhos=None, timeout=TIMEOUT):
    """Uma tentativa extra em 429/5xx. Erros HTTP viram (status, {"error": ...}) — nunca exceção com chave."""
    ultimo = None
    for tentativa in (1, 2):
        try:
            return _http(url, dados, cabecalhos, timeout)
        except urllib.error.HTTPError as e:
            try:
                det = json.loads(e.read().decode("utf-8"))
            except Exception:
                det = {"error": str(e)}
            ultimo = (e.code, det)
            if e.code == 429 or e.code >= 500:
                time.sleep(3 * tentativa)
                continue
            return ultimo
        except Exception as e:  # rede, timeout, TLS
            ultimo = (0, {"error": mascarar(str(e))})
            time.sleep(2 * tentativa)
    return ultimo


def cabecalhos(prov):
    chave = os.environ[PROVEDORES[prov]["chave"]]
    h = {} if chave == PROXY else {"Authorization": f"Bearer {chave}"}  # no modo proxy, quem assina é o proxy
    if prov == "openrouter":
        h["HTTP-Referer"] = "https://github.com/robertorofilho-stack/robertorofilho-stack.github.io"
        h["X-Title"] = "Cerebro Conselho"
    return h


# ---------------------------------------------------------------- modelos
def _versao(id_):
    """Número logo após o nome da família: gpt-6-astra → 6, deepseek-v4.1-flash → 4.1, gpt-oss-120b → 0."""
    m = re.search(r"(?:gpt|grok|gemini|deepseek)-?v?(\d+(?:\.\d+)?)", id_.split("/")[-1])
    return float(m.group(1)) if m else 0.0


def custo_estimado(m):
    if m.get("preco_in") is None:
        return None
    return TOKENS_ESTIMATIVA[0] * (m["preco_in"] or 0) + TOKENS_ESTIMATIVA[1] * (m["preco_out"] or 0)


def listar_modelos(prov):
    st, d = http(f"{PROVEDORES[prov]['base']}/models", cabecalhos=cabecalhos(prov))
    if st != 200 or not isinstance(d, dict):
        return [], d
    out = []
    for m in d.get("data", []):
        mid = m.get("id") or m.get("name") or ""
        mid = mid.removeprefix("models/")
        preco = m.get("pricing") or {}
        out.append({
            "id": mid,
            "created": m.get("created") or 0,
            "preco_in": float(preco.get("prompt") or 0) if preco else None,
            "preco_out": float(preco.get("completion") or 0) if preco else None,
        })
    return out, None


def escolher(modelos, padrao):
    """Mais novo da família; variantes especializadas só se não houver outra."""
    fam = [m for m in modelos if re.search(padrao, m["id"])]
    if not fam:
        return None
    gerais = [m for m in fam if not any(x in m["id"].lower() for x in ESPECIALIZADOS)]
    cand = gerais or fam
    cand.sort(key=lambda m: (_versao(m["id"]), m["created"] or 0), reverse=True)
    dentro = [m for m in cand if custo_estimado(m) is None or custo_estimado(m) <= TETO_USD]
    if dentro:
        return dentro[0]
    return min(cand, key=lambda m: custo_estimado(m) or 0)  # todos acima do teto: o mais barato


def resolver(forcados=None, maximo=4):
    """Devolve lista de {prov, id, preco_in, preco_out, familia}. Diretos vencem o OpenRouter na mesma família."""
    forcados = forcados or [x for x in os.environ.get("CONSELHO_MODELOS", "").split(",") if x.strip()]
    presentes = chaves_presentes()
    if forcados:
        out = []
        for f in forcados:
            prov, _, mid = f.strip().partition(":")
            if prov in presentes and mid:
                out.append({"prov": prov, "id": mid, "preco_in": None, "preco_out": None, "familia": prov})
        return out[:maximo], {}
    escolhidos, erros = {}, {}
    for prov in ["openai", "xai", "gemini", "deepseek", "openrouter"]:  # diretos primeiro
        if prov not in presentes:
            continue
        modelos, erro = listar_modelos(prov)
        if erro:
            erros[prov] = erro
            continue
        for familia, padrao in PROVEDORES[prov]["familias"].items():
            if familia in escolhidos:
                continue
            m = escolher(modelos, padrao)
            if m:
                escolhidos[familia] = {"prov": prov, "familia": familia, **m}
    ordem = sorted(escolhidos.values(), key=lambda m: ORDEM_FAMILIAS.index(m["familia"]) if m["familia"] in ORDEM_FAMILIAS else 9)
    return ordem[:maximo], erros


# ---------------------------------------------------------------- consulta
def consultar(m, tese, contexto="", modo="contra"):
    sistema = PROMPT_CONTRA if modo == "contra" else PROMPT_LIVRE
    usuario = f"TESE:\n{tese}" + (f"\n\nCONTEXTO:\n{contexto}" if contexto else "")
    dados = {
        "model": m["id"],
        "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}],
        "temperature": 0.4,
        "max_tokens": MAX_TOKENS,
    }
    if m["prov"] == "openrouter":
        dados["usage"] = {"include": True}
    t0 = time.time()
    st, d = http(f"{PROVEDORES[m['prov']]['base']}/chat/completions", dados, cabecalhos(m["prov"]))
    dt = time.time() - t0
    r = {"prov": m["prov"], "familia": m.get("familia", m["prov"]), "modelo": m["id"], "segundos": round(dt, 1)}
    if st != 200 or not isinstance(d, dict) or not d.get("choices"):
        err = d.get("error") if isinstance(d, dict) else d
        if isinstance(err, dict):
            err = err.get("message") or json.dumps(err)[:200]
        r.update({"ok": False, "erro": mascarar(f"HTTP {st}: {err}")})
        return r
    uso = d.get("usage") or {}
    ent, sai = int(uso.get("prompt_tokens") or 0), int(uso.get("completion_tokens") or 0)
    custo = uso.get("cost")
    if custo is None and m.get("preco_in") is not None:
        custo = ent * (m["preco_in"] or 0) + sai * (m["preco_out"] or 0)
    r.update({
        "ok": True,
        "texto": (d["choices"][0].get("message") or {}).get("content", "").strip(),
        "tokens_in": ent, "tokens_out": sai,
        "custo_usd": round(float(custo), 4) if custo is not None else None,
    })
    return r


def rodar(tese, contexto="", modo="contra", maximo=4, forcados=None):
    modelos, erros = resolver(forcados, maximo)
    if not modelos:
        return [], erros
    with cf.ThreadPoolExecutor(max_workers=max(1, len(modelos))) as ex:
        res = list(ex.map(lambda m: consultar(m, tese, contexto, modo), modelos))
    return res, erros


def markdown(tese, res, erros, modo):
    linhas = [f"# Conselho — {time.strftime('%Y-%m-%d %H:%M')} · modo {modo}", "", f"**Tese:** {tese.strip()}", ""]
    for r in res:
        if r["ok"]:
            custo = f"US$ {r['custo_usd']:.4f}" if r.get("custo_usd") is not None else "custo n/d"
            linhas += [f"## {r['familia']} · `{r['modelo']}` · {r['segundos']} s · {r['tokens_in']}→{r['tokens_out']} tokens · {custo}", "", r["texto"], ""]
    falhas = [r for r in res if not r["ok"]]
    if falhas or erros:
        linhas += ["## Falhas", ""]
        linhas += [f"- {r['familia']} `{r['modelo']}`: {r['erro']}" for r in falhas]
        linhas += [f"- {p}: {mascarar(json.dumps(e)[:200])}" for p, e in erros.items()]
        linhas.append("")
    ok = [r for r in res if r["ok"]]
    total = sum(r["custo_usd"] or 0 for r in ok)
    linhas += ["## Resumo", "", "| Motor | Modelo | Tempo | Tokens | Custo |", "|---|---|---|---|---|"]
    for r in res:
        if r["ok"]:
            c = f"{r['custo_usd']:.4f}" if r.get("custo_usd") is not None else "n/d"
            linhas.append(f"| {r['familia']} | `{r['modelo']}` | {r['segundos']} s | {r['tokens_in']}+{r['tokens_out']} | {c} |")
        else:
            linhas.append(f"| {r['familia']} | `{r['modelo']}` | — | — | falhou |")
    linhas.append(f"\n**{len(ok)}/{len(res)} motores responderam · custo total conhecido US$ {total:.4f}**")
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------- CLI
def main(argv):
    carregar_chaves()
    detectar_proxy()
    a = {"tese": None, "arquivo": None, "contexto": "", "modo": "contra", "max": 4, "saida": None,
         "json": False, "status": False, "listar": False, "quieto": False, "modelos": []}
    it = iter(argv)
    for x in it:
        if x == "--tese": a["tese"] = next(it, None)
        elif x == "--arquivo": a["arquivo"] = next(it, None)
        elif x == "--contexto": a["contexto"] = next(it, "") or ""
        elif x == "--modo": a["modo"] = next(it, "contra")
        elif x == "--max": a["max"] = int(next(it, "4"))
        elif x == "--saida": a["saida"] = next(it, None)
        elif x == "--modelo": a["modelos"].append(next(it, ""))
        elif x == "--json": a["json"] = True
        elif x == "--status": a["status"] = True
        elif x == "--listar": a["listar"] = True
        elif x == "--quieto": a["quieto"] = True
        else:
            print(f"conselho: opção desconhecida {x}", file=sys.stderr); return 64

    presentes = chaves_presentes()
    if a["status"]:
        if not presentes:
            if not a["quieto"]:
                print("conselho: nenhuma chave — na web: API credential do ambiente (host openrouter.ai) ou "
                      "variável OPENROUTER_API_KEY; no Mac: ~/.config/cerebro/conselho.env. "
                      "Alternativas diretas: OPENAI_API_KEY / XAI_API_KEY / GEMINI_API_KEY / DEEPSEEK_API_KEY.")
            return 2
        print("conselho: motores prontos → " + ", ".join(
            f"{p} (credencial no proxy da nuvem)" if v == PROXY else p for p, v in sorted(presentes.items())))
        return 0
    if a["listar"]:
        if not presentes:
            print("conselho: nenhuma chave"); return 2
        for prov in presentes:
            modelos, erro = listar_modelos(prov)
            print(f"## {prov}: {len(modelos)} modelos" + (f" · erro: {mascarar(json.dumps(erro)[:160])}" if erro else ""))
            for fam, padrao in PROVEDORES[prov]["familias"].items():
                m = escolher(modelos, padrao)
                print(f"  {fam:<9} → {m['id'] if m else '(nenhum)'}")
        return 0

    tese = a["tese"]
    if a["arquivo"]:
        tese = sys.stdin.read() if a["arquivo"] == "-" else open(a["arquivo"], encoding="utf-8").read()
    if not tese or not tese.strip():
        print("uso: conselho.py --tese \"...\" | --arquivo tese.md | --status | --listar", file=sys.stderr); return 64
    if not presentes:
        print("conselho: nenhuma chave — sem segunda opinião. Use /adversarial como substituto.", file=sys.stderr); return 2

    res, erros = rodar(tese, a["contexto"], a["modo"], a["max"], a["modelos"] or None)
    if not res:
        print("conselho: nenhum modelo resolvido — " + mascarar(json.dumps(erros)[:300]), file=sys.stderr); return 3
    saida = json.dumps({"tese": tese, "respostas": res, "erros": erros}, ensure_ascii=False, indent=2) if a["json"] else markdown(tese, res, erros, a["modo"])
    if a["saida"]:
        with open(a["saida"], "w", encoding="utf-8") as f:
            f.write(saida)
        print(f"conselho: gravado em {a['saida']} · {sum(1 for r in res if r['ok'])}/{len(res)} responderam")
    else:
        print(saida)
    return 0 if any(r["ok"] for r in res) else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
