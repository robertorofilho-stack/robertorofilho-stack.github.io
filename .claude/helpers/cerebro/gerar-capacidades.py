#!/usr/bin/env python3
"""GERAR CAPACIDADES — o índice único do que o Cérebro tem, gerado do que existe no disco (nunca escrito à mão).

Evolução do `gerar-inventario.py` do mestre (reusa REGRAS e FIXOS dele por AST — uma fonte de verdade para os domínios),
estendida para: diretores como registro de primeira classe, squads/commands, biblioteca de prompts, vários repositórios,
gatilhos extraídos das descrições ("Use quando…", frases entre aspas) e semeados pela 1ª coluna da ROUTER_RULES,
e um relatório de inconsistências (diretores por fonte, duplicatas, sem domínio, sem gatilho, ponteiros mortos).

Decisão de 13/10/2026 (organizacao-cerebro-diagnostico-e-proposta-13-10): contrato primeiro, sugestão depois.
Este arquivo é a peça 1 — o vocabulário fechado que a linha ROTA e o `rota-hook.mjs` conferem.

Uso:
  gerar-capacidades.py --raiz mestre=~/Claude/cerebro-backup --raiz satelite=~/robertorofilho-stack.github.io \
      --saida CAPACIDADES.json --relatorio RELATORIO-CAPACIDADES.md [--router caminho/ROUTER_RULES.md]
      [--regras caminho/gerar-inventario.py] [--estrito]
  --estrito: sai com 1 se houver diretor sem domínio, domínio sem diretor ou capacidade sem domínio (gate do `saude`;
             opt-in até a lista "cega" ser tratada — ligar sem limpar só deixa o CI vermelho para sempre).
Só biblioteca padrão. Determinístico (ordenado), para o JSON poder ser versionado.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import os
import re
import sys
import unicodedata

DOMINIOS_BASE = ["VENDER", "CONTEUDO", "MEDICO", "EMPRESA", "CONSTRUIR", "PENSAR", "CEREBRO"]
TITULOS = {
    "VENDER": "produto, oferta, copy, campanha, tráfego, checkout",
    "CONTEUDO": "roteiro, vídeo, imagem, voz, redes, marca",
    "MEDICO": "evidência, literatura, laudo, presença clínica",
    "EMPRESA": "financiamento, governo, jurídico, fiscal, dinheiro",
    "CONSTRUIR": "app, código, infra, deploy, segurança",
    "PENSAR": "estratégia, auditoria, verificação, pesquisa",
    "CEREBRO": "memória, contexto, manutenção, orquestração",
    "INEDITO": "pedido fora do mapa → Nível 1 (Arcanjo) com suposição declarada",
}
# Dono padrão de cada domínio quando FIXOS/regex não dizem. Diretor que existir no disco vence; o que não existir vira aviso.
DONOS_PADRAO = {
    "VENDER": ["diretor-de-vendas", "diretor-de-produtos", "diretor-de-produto"],
    "CONTEUDO": ["diretor-de-conteudo", "diretor-de-rede-social"],
    "MEDICO": ["diretor-medico", "diretor-de-identidade-digital"],
    "EMPRESA": ["diretor-de-financiamento"],
    "CONSTRUIR": ["diretor-whatsapp"],
    "PENSAR": ["diretor-arcanjo", "diretor-de-auditoria", "diretor-de-prompts"],
    "CEREBRO": ["diretor-aprendizado", "diretor-supremo"],
    "INEDITO": ["diretor-arcanjo"],
}
REGRAS_FALLBACK = [
    ("VENDER", r"vend|oferta|copy|campanha|tr[áa]fego|checkout|funil|an[úu]ncio|ads|lan[çc]amento|pre[çc]o|lead|cta|vsl|isca|headline|convers"),
    ("MEDICO", r"m[ée]dic|laudo|ortoped|cl[íi]nic|paciente|pubmed|cirurgi|sa[úu]de|scientific|literatura|evid[êe]ncia"),
    ("CONTEUDO", r"reels|carross|v[íi]deo|roteiro|conte[úu]do|storytell|youtube|instagram|tiktok|stories|post|imagem|voz|viral|social|seo"),
    ("EMPRESA", r"financiamento|investidor|licita|governo|cnpj|imposto|fiscal|jur[íi]dic|contrat|banco|cr[ée]dito|grant|cripto|quant"),
    ("CONSTRUIR", r"app|c[óo]digo|code|deploy|infra|servidor|docker|api|backend|frontend|python|sql|supabase|vercel|test|debug|arquitet|saas|site|web|mcp|hook"),
    ("PENSAR", r"arcanjo|auditor|auditar|verifica|revis|pesquis|research|decis|plan|estrat[ée]g|an[áa]lise|cr[íi]tic|adversar|council|nobel|eval"),
    ("CEREBRO", r"mem[óo]ria|memory|cerebro|c[ée]rebro|manuten|sync|sincroniz|painel|governan|skill|agente|orquestr|contexto|token|compact|aprend|config"),
]
RE_ASPAS = re.compile(r"[\"“”']([^\"“”']{3,80})[\"“”']")
RE_USE = re.compile(r"(?:Use(?: this skill)?(?: quando| em| para| se| when)|Ative em|Dispara em|Acione em|Quando pedirem)\s*[:\-]?\s*(.+?)(?:\.\s|\.$|$)", re.I)
RE_BOLD = re.compile(r"\*\*([^*]+)\*\*")


def slug(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def frontmatter(caminho):
    try:
        with open(caminho, encoding="utf-8", errors="ignore") as f:
            s = f.read(20000)
    except OSError:
        return {}
    m = re.match(r"^---\s*\n(.*?)\n---", s, re.S)
    if not m:
        return {}
    b = m.group(1)
    out = {}
    for campo in ("name", "description", "argument-hint", "dominio", "gatilhos"):
        mm = re.search(rf"^{campo}:\s*(.+?)(?=\n[a-zA-Z_-]+:|\Z)", b, re.S | re.M)
        if mm:
            out[campo] = " ".join(mm.group(1).split()).strip().strip("\"'")
    return out


def carregar_regras(caminho):
    """Lê REGRAS e FIXOS do gerar-inventario.py do mestre sem executá-lo (AST). Sem o arquivo: fallback mínimo."""
    if caminho and os.path.isfile(caminho):
        try:
            with open(caminho, encoding="utf-8") as f:
                arvore = ast.parse(f.read())
            regras, fixos = None, None
            for no in arvore.body:
                if isinstance(no, ast.Assign) and len(no.targets) == 1 and isinstance(no.targets[0], ast.Name):
                    if no.targets[0].id == "REGRAS":
                        regras = ast.literal_eval(no.value)
                    elif no.targets[0].id == "FIXOS":
                        fixos = ast.literal_eval(no.value)
            if regras and fixos is not None:
                return [(d, re.compile(rx)) for d, rx in regras], dict(fixos), caminho
        except (OSError, ValueError, SyntaxError):
            pass
    return [(d, re.compile(rx)) for d, rx in REGRAS_FALLBACK], {}, ""


def gatilhos_da_descricao(desc, nome=""):
    out = []
    for m in RE_USE.finditer(desc or ""):
        trecho = m.group(1)
        for parte in re.split(r"\s*(?:,|;| ou |/)\s*", trecho):
            parte = parte.strip(" .\"'“”")
            if 3 <= len(parte) <= 80:
                out.append(parte)
    for m in RE_ASPAS.finditer(desc or ""):
        out.append(m.group(1).strip())
    vistos, unicos = set(), []
    for g in out:
        k = slug(g)
        if k and k not in vistos and k != slug(nome):
            vistos.add(k)
            unicos.append(g)
    return unicos[:12]


def dominios_do_diretor(ident):
    return [d for d, donos in DONOS_PADRAO.items() if ident in donos and d != "INEDITO"]


def classifica(ident, desc, regras, fixos, fm_dominio=""):
    if fm_dominio:
        ds = [d.strip().upper() for d in re.split(r"[,\s]+", fm_dominio) if d.strip()]
        ds = [d for d in ds if d in DOMINIOS_BASE]
        if ds:
            return ds[:2]
    if ident in fixos:
        return list(fixos[ident])
    if ident.startswith("diretor") and dominios_do_diretor(ident):     # diretor: o mapa de donos vale mais que o regex
        return dominios_do_diretor(ident)[:2]
    t = (ident + " " + (desc or "")).lower()
    achou = [d for d, rx in regras if rx.search(t)]
    return achou[:2] if achou else ["OUTROS"]


def registro(ident, tipo, caminho, dono, fm, regras, fixos, como_invocar, extra=None):
    desc = (fm.get("description") or "")[:200]
    eh_diretor = ident.startswith("diretor")
    r = {
        "id": ident,
        "tipo": "diretor" if eh_diretor else tipo,
        "papel": tipo if eh_diretor else "",
        "nome": fm.get("name") or ident,
        "descricao": desc,
        "dominios": classifica(ident, desc, regras, fixos, fm.get("dominio", "")),
        "gatilhos": ([g.strip() for g in fm["gatilhos"].split(",") if g.strip()] if fm.get("gatilhos") else [])
                    + gatilhos_da_descricao(desc, ident),
        "como_invocar": como_invocar,
        "caminhos": [caminho],
        "dono": dono,
        "fontes": ["frontmatter"] if fm else ["disco"],
    }
    if extra:
        r.update(extra)
    return r


def varrer_raiz(nome, raiz, regras, fixos):
    """Descobre o layout da raiz (mestre: claude-config/…, agents/, prompts-arsenal/; satélite: .claude/…)."""
    raiz = os.path.abspath(os.path.expanduser(raiz))
    regs = []
    bases = []
    for b in ("claude-config", ".claude"):
        if os.path.isdir(os.path.join(raiz, b)):
            bases.append(os.path.join(raiz, b))
    for base in bases:
        rel = os.path.relpath(base, raiz)
        # skills
        sk = os.path.join(base, "skills")
        if os.path.isdir(sk):
            for d in sorted(os.listdir(sk)):
                p = os.path.join(sk, d, "SKILL.md")
                if os.path.isfile(p):
                    regs.append(registro(d, "skill", f"{rel}/skills/{d}/SKILL.md", nome, frontmatter(p), regras, fixos, f"/{d}"))
            # skills nativas sincronizadas (synced/<x>/SKILL.md)
            sync = os.path.join(sk, "synced")
            if os.path.isdir(sync):
                for d in sorted(os.listdir(sync)):
                    p = os.path.join(sync, d, "SKILL.md")
                    if os.path.isfile(p):
                        regs.append(registro(d, "skill", f"{rel}/skills/synced/{d}/SKILL.md", nome, frontmatter(p), regras, fixos, f"/{d}", {"origem": "synced"}))
        # subagentes
        for pasta in ("agents-user", "agents"):
            ag = os.path.join(base, pasta)
            if os.path.isdir(ag):
                for f in sorted(os.listdir(ag)):
                    if f.endswith(".md"):
                        ident = f[:-3]
                        regs.append(registro(ident, "subagente", f"{rel}/{pasta}/{f}", nome, frontmatter(os.path.join(ag, f)), regras, fixos,
                                             f"Agent(subagent_type={ident})"))
        # squads / commands
        cm = os.path.join(base, "commands")
        if os.path.isdir(cm):
            for d in sorted(os.listdir(cm)):
                pd = os.path.join(cm, d)
                if not os.path.isdir(pd):
                    continue
                personas = sorted(os.listdir(os.path.join(pd, "agents"))) if os.path.isdir(os.path.join(pd, "agents")) else []
                readme = next((os.path.join(pd, x) for x in ("README.md", f"{d}.md", "SKILL.md") if os.path.isfile(os.path.join(pd, x))), "")
                fm = frontmatter(readme) if readme else {}
                regs.append(registro(d, "squad", f"{rel}/commands/{d}/", nome, fm, regras, fixos, f"/{d}",
                                     {"personas": len([x for x in personas if x.endswith(".md")])}))
    # diretores-agente e pastas de agente do mestre (agents/<nome>/AGENT_CORE.md …)
    ag2 = os.path.join(raiz, "agents")
    if os.path.isdir(ag2):
        for d in sorted(os.listdir(ag2)):
            pd = os.path.join(ag2, d)
            if not os.path.isdir(pd):
                continue
            core = next((os.path.join(pd, x) for x in ("AGENT_CORE.md", "SKILL.md", "README.md", f"{d}.md") if os.path.isfile(os.path.join(pd, x))), "")
            fm = frontmatter(core) if core else {}
            regs.append(registro(d, "agente", f"agents/{d}/", nome, fm, regras, fixos, f"ler agents/{d}/AGENT_CORE.md e operar como {d}"))
    # biblioteca de prompts (uma entrada por pasta)
    pa = os.path.join(raiz, "prompts-arsenal")
    if os.path.isdir(pa):
        for d in sorted(os.listdir(pa)):
            pd = os.path.join(pa, d)
            if os.path.isdir(pd):
                n = sum(1 for _ in os.listdir(pd))
                regs.append(registro(f"prompts-{d}", "prompts", f"prompts-arsenal/{d}/", nome, {"description": f"biblioteca de prompts: {d} ({n} arquivos)"},
                                     regras, fixos, f"abrir prompts-arsenal/{d}/ e escolher o prompt", {"arquivos": n}))
    return regs


def fundir(regs):
    """Mesmo id em vários lugares → um registro com todos os caminhos (diretor em skill E agente, por exemplo)."""
    por_id = {}
    for r in regs:
        if r["id"] in por_id:
            a = por_id[r["id"]]
            a["caminhos"] += r["caminhos"]
            a["fontes"] = sorted(set(a["fontes"] + r["fontes"]))
            a["gatilhos"] = _unir(a["gatilhos"], r["gatilhos"])
            if not a["descricao"] and r["descricao"]:
                a["descricao"] = r["descricao"]
            if a["dominios"] == ["OUTROS"] and r["dominios"] != ["OUTROS"]:
                a["dominios"] = r["dominios"]
            if r["tipo"] == "diretor":
                a["tipo"] = "diretor"
            a["papel"] = "/".join(sorted(set(filter(None, [a.get("papel", ""), r.get("papel", "")]))))
            if a["dono"] != r["dono"]:
                a["dono"] = "mestre+satelite"
        else:
            por_id[r["id"]] = r
    return [por_id[k] for k in sorted(por_id)]


def _unir(a, b):
    vistos, out = set(), []
    for g in list(a) + list(b):
        k = slug(g)
        if k and k not in vistos:
            vistos.add(k)
            out.append(g)
    return out[:20]


def semear_router(regs, caminho_router):
    """1ª coluna da tabela de roteamento vira gatilho da capacidade em negrito na 2ª coluna. Devolve ponteiros mortos."""
    mortos = []
    if not caminho_router or not os.path.isfile(caminho_router):
        return mortos, 0
    with open(caminho_router, encoding="utf-8", errors="ignore") as f:
        linhas = f.read().split("\n")
    i = next((k for k, l in enumerate(linhas) if l.startswith("## ") and "roteamento" in l.lower()), -1)
    if i < 0:
        return mortos, 0
    tabela = []
    for l in linhas[i + 1:]:
        if l.startswith("## "):
            break
        if l.startswith("|"):
            tabela.append(l)
    por_slug = {}
    for r in regs:
        por_slug.setdefault(slug(r["id"]), r)
        por_slug.setdefault(slug(r["nome"]), r)
    semeados = 0
    for l in tabela[2:]:
        cols = [c.strip() for c in l.strip("|").split("|")]
        if len(cols) < 2:
            continue
        pedido = re.sub(r"[*`_]", "", cols[0]).strip()
        if not pedido or set(pedido) <= {"-"}:
            continue
        for alvo in RE_BOLD.findall(cols[1]):
            alvo = re.sub(r"^(skill|agente|agent|squad|command)\s+", "", alvo.strip(" `"), flags=re.I)
            alvo = re.sub(r"\s*\(.*\)$", "", alvo).strip(" `")
            s = slug(alvo)
            r = por_slug.get(s) or por_slug.get(s + "-squad") or por_slug.get(s.replace("-squad", ""))
            if not r:
                r = next((v for k, v in por_slug.items() if s and (k.startswith(s) or s.startswith(k)) and len(k) >= 5), None)
            if r:
                if slug(pedido) not in {slug(g) for g in r["gatilhos"]}:
                    r["gatilhos"].append(pedido[:100])
                    r["gatilhos"] = r["gatilhos"][:20]
                    semeados += 1
                if "router" not in r["fontes"]:
                    r["fontes"].append("router")
            else:
                mortos.append({"pedido": pedido[:80], "alvo": alvo})
    return mortos, semeados


def montar(raizes, caminho_regras, caminho_router):
    regras, fixos, origem_regras = carregar_regras(caminho_regras)
    regs = []
    for nome, raiz in raizes:
        regs += varrer_raiz(nome, raiz, regras, fixos)
    regs = fundir(regs)
    mortos, semeados = semear_router(regs, caminho_router)
    ids = {r["id"] for r in regs}
    diretores = [r for r in regs if r["tipo"] == "diretor"]
    dominios = {}
    for d in DOMINIOS_BASE + ["INEDITO"]:
        donos = [x["id"] for x in diretores if d in x["dominios"]]
        for cand in DONOS_PADRAO.get(d, []):
            if cand in ids and cand not in donos:
                donos.append(cand)
        dominios[d] = {"titulo": TITULOS[d], "diretores": donos}
    sem_dominio = [r["id"] for r in regs if r["dominios"] == ["OUTROS"]]
    cegas = [r["id"] for r in regs if not r["gatilhos"] and r["tipo"] in ("skill", "diretor", "squad", "agente")]
    diretores_sem_dominio = [r["id"] for r in diretores if r["dominios"] == ["OUTROS"]]
    dominios_sem_diretor = [d for d, v in dominios.items() if not v["diretores"]]
    # quase-duplicatas: ids iguais tirando 's' final ou 'de-'
    chave = {}
    for r in regs:
        k = re.sub(r"s$", "", r["id"].replace("-de-", "-"))
        chave.setdefault(k, []).append(r["id"])
    quase = sorted([v for v in chave.values() if len(v) > 1])
    por_tipo = {}
    for r in regs:
        por_tipo[r["tipo"]] = por_tipo.get(r["tipo"], 0) + 1
    por_dono = {}
    for r in regs:
        por_dono[r["dono"]] = por_dono.get(r["dono"], 0) + 1
    diretores_por_fonte = {}
    for r in diretores:
        for c in r["caminhos"]:
            fonte = c.split("/")[0] + "/" + (c.split("/")[1] if c.count("/") else "")
            diretores_por_fonte.setdefault(fonte, []).append(r["id"])
    return {
        "versao": 1,
        "gerado_em": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "raizes": [{"nome": n, "caminho": os.path.abspath(os.path.expanduser(p))} for n, p in raizes],
        "regras_de_dominio": origem_regras or "fallback interno",
        "router": caminho_router if caminho_router and os.path.isfile(caminho_router) else "",
        "dominios": dominios,
        "capacidades": regs,
        "contagens": {"total": len(regs), "por_tipo": dict(sorted(por_tipo.items())), "por_dono": dict(sorted(por_dono.items())),
                      "diretores": len(diretores), "sem_dominio": len(sem_dominio), "cegas": len(cegas),
                      "gatilhos_semeados_pelo_router": semeados, "ponteiros_mortos_router": len(mortos)},
        "inconsistencias": {"diretores_por_fonte": {k: sorted(v) for k, v in sorted(diretores_por_fonte.items())},
                            "quase_duplicatas": quase, "sem_dominio": sem_dominio, "cegas": cegas,
                            "diretores_sem_dominio": diretores_sem_dominio, "dominios_sem_diretor": dominios_sem_diretor,
                            "ponteiros_mortos_router": mortos},
    }


def vocabulario(dados):
    """≈ 0,3 KB que qualquer hook injeta: domínios → donos e a lista de diretores. Nunca a tabela inteira."""
    doms = " · ".join(f"{d}→{'/'.join(v['diretores'][:2]) or '?'}" for d, v in dados["dominios"].items())
    dirs = ", ".join(sorted(r["id"] for r in dados["capacidades"] if r["tipo"] == "diretor"))
    return ("ROTA: dominio=<" + "|".join(dados["dominios"].keys()) + "> | diretor=<id> | capacidades=<ids ou nenhuma, porque…> | nivel=<0-3>\n"
            f"Domínios→donos: {doms}\nDiretores: {dirs or 'nenhum neste repositório (use os do mestre)'}\n")


def relatorio_md(dados):
    c, inc = dados["contagens"], dados["inconsistencias"]
    L = [f"# Relatório de capacidades — {dados['gerado_em']}", "",
         f"Raízes: {', '.join(r['nome'] + ' (' + r['caminho'] + ')' for r in dados['raizes'])} · regras de domínio: `{dados['regras_de_dominio']}`"
         + (f" · router: `{dados['router']}`" if dados["router"] else " · router: nenhum"), "",
         "## Contagens", "",
         f"- Total: **{c['total']}** · por tipo: " + " · ".join(f"{k} {v}" for k, v in c["por_tipo"].items()),
         f"- Por repositório: " + " · ".join(f"{k} {v}" for k, v in c["por_dono"].items()),
         f"- Diretores: **{c['diretores']}** · sem domínio (OUTROS): **{c['sem_dominio']}** · sem gatilho (cegas): **{c['cegas']}**",
         f"- Gatilhos semeados pela ROUTER_RULES: {c['gatilhos_semeados_pelo_router']} · ponteiros mortos na ROUTER_RULES: {c['ponteiros_mortos_router']}",
         "", "## Domínios e donos", "", "| Domínio | Diretores donos |", "|---|---|"]
    for d, v in dados["dominios"].items():
        L.append(f"| {d} | {', '.join(v['diretores']) or '**nenhum**'} |")
    L += ["", "## Diretores por fonte (um diretor em dois lugares não é erro; o mesmo nome com dois papéis é)", ""]
    for fonte, ids in inc["diretores_por_fonte"].items():
        L.append(f"- `{fonte}`: {', '.join(ids)}")
    L += ["", "## Inconsistências", "",
          f"- Quase-duplicatas (mesmo nome tirando 's' ou 'de-'): {inc['quase_duplicatas'] or 'nenhuma'}",
          f"- Diretores sem domínio: {inc['diretores_sem_dominio'] or 'nenhum'}",
          f"- Domínios sem diretor: {inc['dominios_sem_diretor'] or 'nenhum'}",
          f"- Sem domínio (OUTROS), {len(inc['sem_dominio'])}: {', '.join(inc['sem_dominio'][:40])}{' …' if len(inc['sem_dominio']) > 40 else ''}",
          f"- Cegas (sem nenhum gatilho extraível), {len(inc['cegas'])}: {', '.join(inc['cegas'][:40])}{' …' if len(inc['cegas']) > 40 else ''}",
          "", "## Ponteiros mortos na ROUTER_RULES (negrito que não casa com nada no disco)", ""]
    for m in inc["ponteiros_mortos_router"][:30]:
        L.append(f"- \"{m['pedido']}\" → **{m['alvo']}**")
    if not inc["ponteiros_mortos_router"]:
        L.append("- nenhum")
    L += ["", "_Gerado por `gerar-capacidades.py`. Não editar à mão: a próxima geração sobrescreve._"]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Índice único de capacidades do Cérebro, gerado do disco.")
    ap.add_argument("--raiz", action="append", required=True, help="nome=caminho (repetível), ex.: mestre=~/Claude/cerebro-backup")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--relatorio")
    ap.add_argument("--regras", help="gerar-inventario.py do mestre (REGRAS/FIXOS por AST)")
    ap.add_argument("--router", help="ROUTER_RULES.md: 1ª coluna vira gatilho")
    ap.add_argument("--estrito", action="store_true")
    a = ap.parse_args(argv)
    raizes = []
    for item in a.raiz:
        nome, sep, caminho = item.partition("=")
        if not sep:
            nome, caminho = os.path.basename(os.path.abspath(os.path.expanduser(item))), item
        raizes.append((nome, caminho))
    regras = a.regras
    if not regras:
        for _, r in raizes:
            cand = os.path.join(os.path.expanduser(r), "claude-config", "helpers", "cerebro", "gerar-inventario.py")
            if os.path.isfile(cand):
                regras = cand
                break
    router = a.router
    if not router:
        for _, r in raizes:
            cand = os.path.join(os.path.expanduser(r), "cerebro-master-pacote", "governanca", "ROUTER_RULES.md")
            if os.path.isfile(cand):
                router = cand
                break
    dados = montar(raizes, regras, router)
    with open(a.saida, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
    with open(os.path.join(os.path.dirname(os.path.abspath(a.saida)), "VOCABULARIO-ROTA.txt"), "w", encoding="utf-8") as f:
        f.write(vocabulario(dados))
    if a.relatorio:
        with open(a.relatorio, "w", encoding="utf-8") as f:
            f.write(relatorio_md(dados))
    c = dados["contagens"]
    print(f"capacidades: {c['total']} ({', '.join(f'{k} {v}' for k, v in c['por_tipo'].items())}) · diretores {c['diretores']} · "
          f"sem domínio {c['sem_dominio']} · cegas {c['cegas']} · semeados {c['gatilhos_semeados_pelo_router']} · mortos {c['ponteiros_mortos_router']} → {a.saida}")
    inc = dados["inconsistencias"]
    if a.estrito and (inc["diretores_sem_dominio"] or inc["dominios_sem_diretor"] or inc["sem_dominio"]):
        print("✗ estrito: diretor sem domínio, domínio sem diretor ou capacidade sem domínio — veja o relatório", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
