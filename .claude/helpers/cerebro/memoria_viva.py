#!/usr/bin/env python3
"""MEMÓRIA VIVA — recuperação, associação e consolidação sobre os arquivos de memória do Cérebro.

Versão real (testável, sem rede, só biblioteca padrão) das ideias de "memória agêntica" estudadas em
27/09/2026 (Stanford CS329A, CMU 11-768, DeepLearning.AI Agent Memory). Cada peça tem referência:

  camada             o que faz aqui                                   referência
  -----------------  -----------------------------------------------  ----------------------------------------
  semântica          os próprios arquivos .md (frontmatter + corpo)   memória como arquivo (MemGPT/Letta)
  recuperação        score = relevância + associação + recência       Generative Agents (Park et al., 2023)
                     + importância, cada termo normalizado em [0,1]
  associação         PageRank personalizado sobre o grafo de links    HippoRAG (Gutiérrez et al., 2024)
                     [[x]] e (x.md) + sinapses aprendidas
  hebbiano           sinapse w_ij ∈ [0,1] entre memórias usadas       regra de Hebb com saturação (tipo Oja):
                     JUNTAS numa missão: sucesso → w += η(1−w);       nunca explode, nunca fica negativa
                     fracasso → w ×= (1−η)
  confiança          média Beta (sucessos+1)/(usos+2) por memória     no lugar de "+0,05 por acesso"
  decaimento         W = importância · 0,5^(dias/meia-vida),          Ebbinghaus calculado NA LEITURA — o
                     calculado na leitura, nunca gravado              arquivo não é reescrito e nada é apagado
  episódica          episódio = tarefa + resultado + memórias +      Reflexion / ExpeL / LATS (reflexão verbal)
                     lição verbal (JSONL no estado)
  consolidação       lições parecidas (Jaccard) de ≥2 episódios      ExpeL: insight só com suporte repetido;
                     viram REGRA CANDIDATA — promoção exige revisão   o verificador é o gargalo (CS329A s03)

Lei da Monotonia: este helper NUNCA apaga nem reescreve memória. "frias" só lista candidatas a arquivar.

Uso:
  memoria_viva.py buscar "consulta" [--k 8] [--json] [--nomes]
  memoria_viva.py episodio --tarefa "..." --resultado ok|falha [--usadas a.md b.md] [--licao "..."]
  memoria_viva.py consolidar [--min 2] [--json]          regras candidatas a partir das lições repetidas
  memoria_viva.py frias [--limiar 0.2]                   candidatas a arquivo (nunca apaga)
  memoria_viva.py status
Opções globais: --mem DIR (repetível; padrão: mestre detectado + .claude/cerebro) · --estado ARQ · --meia-vida DIAS

Estado (sinapses, usos, episódios) fica AO LADO da primeira pasta de memória: se o mestre privado existe,
o estado mora nele — nome de memória privada nunca é gravado no repositório público.
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import unicodedata

# Pesos do CANAL DE TEXTO, calibrados em 27/09 no gabarito do MEMORY.md (170 consultas, grade 4×4×3):
# BM25 puro MRR 0,790 → estes 0,801, recall@5 igual (0,900). Associação forte no score PIORAVA (0,740):
# por isso ela virou canal separado — vagas extras (↔) que nunca desalojam acerto de texto.
PESOS = {"relevancia": 1.0, "associacao": 0.05, "recencia": 0.0, "importancia": 0.1}
VAGAS_ASSOCIACAO = 2
MEIA_VIDA_DIAS = 30.0
ETA = 0.2              # taxa hebbiana
BM25_K1, BM25_B = 1.2, 0.75
PPR_ALFA, PPR_ITER = 0.15, 30
STOP = set("""a o e é de da do das dos em no na nos nas um uma uns umas que para por com sem se ao aos à às
como mais mas ou ser foi são tem ter já não sim isso esta este essa esse está the and for with from that this
into are was were you your not but all can has have will ele ela eles elas seu sua seus suas nós vai via até
quando onde qual quais cada todo toda todos todas outro outra muito pouco sobre entre depois antes aqui ali
pode podes posso ver veja entao agora isso isto esse essa esses essas sim nao faz faca fazer vai vamos quero queria
preciso bom boa tudo obrigado obrigada valeu beleza mandar manda amigo amiga ok certo pronto favor por""".split())


# ---------------------------------------------------------------- texto
def normalizar(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def tokens(t):
    return [w for w in re.findall(r"[a-z0-9]{3,}", normalizar(t)) if w not in STOP]


RE_LINK = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]|\(([^()\s]+?\.md)\)")   # [[x]], [t](x.md), (x.md)
RE_DATA_ISO = re.compile(r"\b(20\d\d)-(\d\d)-(\d\d)")
RE_DATA_BR = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(20\d\d))?\b")


def frontmatter(txt):
    if not txt.startswith("---"):
        return {}, txt
    fim = txt.find("\n---", 3)
    if fim < 0:
        return {}, txt
    fm = {}
    for linha in txt[3:fim].splitlines():
        m = re.match(r"\s*([A-Za-z_]+):\s*(.*)$", linha)
        if m and m.group(2).strip():
            fm.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))
    return fm, txt[fim + 4:]


def _data_br(m, ano_ref):
    d, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3) or ano_ref.year)
    try:
        x = dt.date(ano, mes, d)
    except ValueError:
        return None
    if not m.group(3) and x > ano_ref:        # "27/12" sem ano, lido em setembro → ano anterior
        x = dt.date(ano - 1, mes, d) if not (mes == 2 and d == 29) else None
    return x


def data_de(fm, corpo, hoje=None):
    """modified do frontmatter > data mais recente no cabeçalho (ISO ou DD/MM[/AAAA]) > no corpo > None."""
    hoje = hoje or dt.date.today()
    for chave in ("modified", "updated", "date", "data"):
        m = RE_DATA_ISO.search(fm.get(chave, ""))
        if m:
            try:
                return dt.date(*map(int, m.groups()))
            except ValueError:
                pass
    for texto in (fm.get("description", ""), corpo[:20000]):
        datas = []
        for m in RE_DATA_ISO.finditer(texto):
            try:
                datas.append(dt.date(*map(int, m.groups())))
            except ValueError:
                pass
        for m in RE_DATA_BR.finditer(texto):
            x = _data_br(m, hoje)
            if x:
                datas.append(x)
        datas = [x for x in datas if x <= hoje]
        if datas:
            return max(datas)
    return None


def importancia_marcas(nome, fm, corpo):
    """Heurística declarada: lei/gotcha/feedback/decisão pesam mais; marcas 🔴 ⭐ LEI na descrição."""
    base = 0.5
    n = nome.lower()
    if re.match(r"(lei|gotcha|feedback|licao|decis)", n):
        base = 0.8
    desc = fm.get("description", "") + " " + corpo[:300]
    if re.search(r"🔴|⭐|\bLEI\b|INEGOCI|NUNCA|SEMPRE", desc):
        base = min(1.0, base + 0.15)
    return base


# ---------------------------------------------------------------- corpus
class Doc:
    __slots__ = ("id", "caminho", "nome", "desc", "tf", "tam", "links", "data", "marca")


def _cache_dir():
    base = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    return os.path.join(base, "memoria-viva")          # FORA dos repositórios: guarda tokens de memória privada


# ---------------------------------------------------------------- correção da consulta (27/09/2026)
# Palavra da consulta que não existe em NENHUMA memória (erro de digitação, flexão, corte) vira a palavra guardada mais
# próxima por distância de edição (corretor_lexico.py, SymSpell + Damerau-Levenshtein). Palavra que existe não é tocada:
# consulta limpa fica IDÊNTICA. Medido em 954 consultas perturbadas (3 sementes que nada viu): MRR +0,084
# [+0,069, +0,099], 0,3 ms/palavra. A "limpeza" pelo espaço de Hilbert (hilbert.py) também funcionava (+0,047) mas
# PERDEU para este corretor "burro" (−0,037, IC todo negativo) — o conselho de 4 IAs mandou comparar; comparado, fica o burro.
_CORRETOR = {}


def limpar_consulta(docs, consulta):
    toks = tokens(consulta)
    freq = {}
    for d in docs.values():
        for w, c in d.tf.items():
            freq[w] = freq.get(w, 0) + c
    fora = [w for w in toks if len(w) >= 4 and w not in freq]
    if not fora:
        return consulta
    try:
        import importlib.util
        chave = (len(freq), sum(freq.values()))
        if chave not in _CORRETOR:
            sp = importlib.util.spec_from_file_location("corretor_lexico", os.path.join(os.path.dirname(os.path.abspath(__file__)), "corretor_lexico.py"))
            cl = importlib.util.module_from_spec(sp)
            sp.loader.exec_module(cl)
            _CORRETOR.clear()
            _CORRETOR[chave] = cl.Corretor(freq)
        cor = _CORRETOR[chave]
    except Exception:
        return consulta
    return " ".join(cor.corrigir(w)[0] if w in fora else w for w in toks)


def _ler_doc(arq, p, hoje):
    with open(p, encoding="utf-8", errors="replace") as f:
        txt = f.read()
    fm, corpo = frontmatter(txt)
    nome = fm.get("name", arq[:-3])
    desc = fm.get("description", "")
    toks = tokens(nome + " " + desc) * 3 + tokens(corpo)   # cabeçalho pesa 3×
    tf = {}
    for w in toks:
        tf[w] = tf.get(w, 0) + 1
    links = set()
    for a, b in RE_LINK.findall(corpo):
        alvo = os.path.basename((a or b).strip())
        links.add(alvo if alvo.endswith(".md") else alvo + ".md")
    data = data_de(fm, corpo, hoje)
    return {"nome": nome, "desc": desc, "tf": tf, "tam": len(toks) or 1, "links": sorted(links),
            "data": data.isoformat() if data else None, "marca": importancia_marcas(arq, fm, corpo)}


def carregar(pastas, hoje=None, cache=True):
    """Lê as pastas de memória. Cache por (mtime, tamanho) de cada arquivo em ~/.cache/memoria-viva."""
    hoje = hoje or dt.date.today()
    cpath = None
    velho, novo_cache = {}, {}
    if cache:
        cpath = os.path.join(_cache_dir(), "corpus-%s.json" % hoje.isoformat()[:7])
        try:
            with open(cpath, encoding="utf-8") as f:
                velho = json.load(f)
        except (OSError, ValueError):
            velho = {}
    docs = {}
    for pasta in pastas:
        if not pasta or not os.path.isdir(pasta):
            continue
        for arq in sorted(os.listdir(pasta)):
            if not arq.endswith(".md") or arq.startswith("MEMORY") or arq in docs:   # índices (MEMORY*.md) não são memória: viram hub e poluem a associação
                continue                      # primeira pasta vence em nome repetido (mestre antes do satélite)
            p = os.path.join(pasta, arq)
            try:
                st = os.stat(p)
            except OSError:
                continue
            assin = "%s|%d|%d" % (p, int(st.st_mtime), st.st_size)
            reg = velho.get(assin)
            if reg is None:
                try:
                    reg = _ler_doc(arq, p, hoje)
                except OSError:
                    continue
            novo_cache[assin] = reg
            d = Doc()
            d.id, d.caminho = arq, p
            d.nome, d.desc, d.tf, d.tam = reg["nome"], reg["desc"], reg["tf"], reg["tam"]
            d.links = set(reg["links"])
            d.data = dt.date.fromisoformat(reg["data"]) if reg["data"] else None
            d.marca = reg["marca"]
            docs[arq] = d
    for d in docs.values():
        d.links = {l for l in d.links if l in docs and l != d.id}
    if cpath and novo_cache != velho:
        try:
            os.makedirs(os.path.dirname(cpath), mode=0o700, exist_ok=True)
            tmp = cpath + ".%d.tmp" % os.getpid()
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(novo_cache, f, ensure_ascii=False)
            os.chmod(tmp, 0o600)
            os.replace(tmp, cpath)
        except OSError:
            pass
    return docs


def bm25(docs, consulta):
    q = set(tokens(consulta))
    if not q or not docs:
        return {}
    n = len(docs)
    media = sum(d.tam for d in docs.values()) / n
    df = {w: sum(1 for d in docs.values() if w in d.tf) for w in q}
    out = {}
    for d in docs.values():
        s = 0.0
        for w in q:
            f = d.tf.get(w, 0)
            if not f:
                continue
            idf = math.log(1 + (n - df[w] + 0.5) / (df[w] + 0.5))
            s += idf * f * (BM25_K1 + 1) / (f + BM25_K1 * (1 - BM25_B + BM25_B * d.tam / media))
        if s > 0:
            out[d.id] = s
    return out


def grafo(docs, sinapses):
    """Arestas não-dirigidas: link explícito (peso 1) + sinapse aprendida (peso w)."""
    viz = {i: {} for i in docs}
    for d in docs.values():
        for l in d.links:
            viz[d.id][l] = viz[d.id].get(l, 0) + 1.0
            viz[l][d.id] = viz[l].get(d.id, 0) + 1.0
    for chave, w in sinapses.items():
        a, _, b = chave.partition("|")
        if a in viz and b in viz and w > 0:
            viz[a][b] = viz[a].get(b, 0) + w
            viz[b][a] = viz[b].get(a, 0) + w
    return viz


def pagerank(viz, semente=None, alfa=PPR_ALFA, it=PPR_ITER):
    nos = list(viz)
    if not nos:
        return {}
    if semente:
        tot = sum(semente.values())
        reinicio = {k: v / tot for k, v in semente.items()}
    else:
        reinicio = {k: 1 / len(nos) for k in nos}
    pr = dict(reinicio)
    saida = {k: sum(v.values()) for k, v in viz.items()}
    for _ in range(it):
        novo = {k: alfa * reinicio.get(k, 0.0) for k in nos}
        perdido = 0.0
        for k, massa in pr.items():
            if not massa:
                continue
            if saida[k] == 0:
                perdido += massa
                continue
            for j, w in viz[k].items():
                novo[j] += (1 - alfa) * massa * w / saida[k]
        if perdido:
            for k, v in reinicio.items():
                novo[k] += (1 - alfa) * perdido * v
        pr = novo
    return pr


def _norm(m):
    top = max(m.values(), default=0)
    return {k: v / top for k, v in m.items()} if top > 0 else {}


# ---------------------------------------------------------------- estado
def estado_padrao(pastas):
    for p in pastas:
        if p and os.path.isdir(p):
            return os.path.join(p, ".memoria-viva.json")
    return os.path.abspath(".memoria-viva.json")


def ler_estado(caminho):
    try:
        with open(caminho, encoding="utf-8") as f:
            e = json.load(f)
    except (OSError, ValueError):
        e = {}
    e.setdefault("versao", 1)
    e.setdefault("sinapses", {})
    e.setdefault("usos", {})         # id -> {"n": usos, "ok": sucessos, "ultimo": "AAAA-MM-DD"}
    e.setdefault("episodios", [])
    e.setdefault("consolidados", [])
    return e


def gravar_estado(caminho, e):
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(e, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, caminho)


def chave_sinapse(a, b):
    return "|".join(sorted((a, b)))


def hebb(estado, usadas, sucesso, hoje=None, eta=ETA):
    """Regra de Hebb saturada com VANTAGEM RELATIVA (CMU 11-768 aula 9; GRPO: Â = r − média do grupo).
    Linha de base = confiança média das memórias usadas ANTES do episódio. Sucesso esperado (memórias que
    sempre dão certo) quase não reforça; sucesso surpreendente reforça muito; fracasso enfraquece na medida
    da surpresa. w continua em [0, 1]. Retorna as sinapses tocadas."""
    usadas = sorted(set(usadas))
    hoje = (hoje or dt.date.today()).isoformat()
    base = sum(confianca(estado, u) for u in usadas) / len(usadas) if usadas else 0.5
    vantagem = (1.0 if sucesso else 0.0) - base
    for u in usadas:
        reg = estado["usos"].setdefault(u, {"n": 0, "ok": 0, "ultimo": hoje})
        reg["n"] += 1
        reg["ok"] += 1 if sucesso else 0
        reg["ultimo"] = hoje
    tocadas = {}
    for i, a in enumerate(usadas):
        for b in usadas[i + 1:]:
            k = chave_sinapse(a, b)
            w = estado["sinapses"].get(k, 0.0)
            w = w + eta * vantagem * (1 - w) if vantagem > 0 else w * (1 - eta * abs(vantagem))
            estado["sinapses"][k] = round(min(1.0, max(0.0, w)), 6)
            tocadas[k] = estado["sinapses"][k]
    return tocadas


def confianca(estado, i):
    u = estado["usos"].get(i)
    return (u["ok"] + 1) / (u["n"] + 2) if u else 0.5


def recencia(doc, estado, hoje, meia_vida):
    datas = [doc.data] if doc.data else []
    u = estado["usos"].get(doc.id)
    if u and u.get("ultimo"):
        try:
            datas.append(dt.date.fromisoformat(u["ultimo"]))
        except ValueError:
            pass
    if not datas:
        return 0.5
    dias = max(0, (hoje - max(datas)).days)
    return 0.5 ** (dias / meia_vida)


# ---------------------------------------------------------------- operações
# Piso de relevância (CMU 11-768 aula 4, fala: over-retrieval nº 1 = "não há nada relevante na memória").
# Calibrado em 27/09 com BM25 bruto do topo. Gabarito (frases longas): p5 = 10,35. Mas pergunta CURTA e real soma
# pouco: "previsão de caixa e CPA real" = 9,0 e "CPA real" = 6,6, contra "previsão do tempo" = 9,8 — BM25 não
# separa por SENTIDO. Perder a memória certa custa mais que injetar ponteiro de 1 linha → piso CONSERVADOR:
# 6 corta só o claramente vazio ("bom dia" 2,2 · "dois mais dois" 5,1); as palavras de conversa em STOP fazem o
# resto. Separar tema de verdade pede embeddings (divergência do conselho, 27/09) — medir antes de adotar.
PISO_RECALL = 6.0
PESO_CONTEXTO = 1.0   # AgentIR (CMU 11-768 aula 10): o raciocínio atual foi o sinal mais forte; peso igual ao da pergunta


def ultima_resposta(transcript, limite=1500):
    """Último texto do assistente num transcript JSONL do Claude Code (para buscar com o raciocínio atual)."""
    ultimo = ""
    try:
        with open(transcript, encoding="utf-8", errors="replace") as f:
            for linha in f:
                if '"assistant"' not in linha:
                    continue
                try:
                    j = json.loads(linha)
                except ValueError:
                    continue
                if j.get("type") != "assistant":
                    continue
                partes = (j.get("message") or {}).get("content") or []
                txt = " ".join(p.get("text", "") for p in partes if isinstance(p, dict) and p.get("type") == "text")
                if txt.strip():
                    ultimo = txt
    except OSError:
        return ""
    return ultimo[-limite:]


def buscar(docs, estado, consulta, k=8, hoje=None, meia_vida=MEIA_VIDA_DIAS, pesos=PESOS, vagas_assoc=VAGAS_ASSOCIACAO,
           contexto="", piso=0.0, limpar=True):
    """Dois canais: TEXTO (BM25 + desempate por importância/associação) ocupa o topo; ASSOCIAÇÃO (PageRank
    personalizado no grafo de links + sinapses) ganha até `vagas_assoc` vagas extras com o que não tem a palavra."""
    hoje = hoje or dt.date.today()
    consulta = limpar_consulta(docs, consulta) if limpar else consulta
    bruto = bm25(docs, consulta)
    if piso > 0:
        topo = max(bruto.values(), default=0.0)
        if contexto:
            topo = max(topo, max(bm25(docs, contexto).values(), default=0.0))
        if topo < piso:
            return []                            # nada relevante: injetar zero é melhor que injetar ruído
    rel = _norm(bruto)
    if contexto and rel:                      # contexto só reordena/amplia; sem acerto da pergunta, não inventa tema
        rc = _norm(bm25(docs, contexto))
        rel = _norm({i: rel.get(i, 0.0) + PESO_CONTEXTO * rc.get(i, 0.0) for i in set(rel) | set(rc)})
    if not rel:
        return []
    viz = grafo(docs, estado["sinapses"])
    sementes = dict(sorted(rel.items(), key=lambda x: -x[1])[:5])
    ppr = pagerank(viz, sementes)
    for s in sementes:                       # associação mede o que a semente PUXA, não a própria semente
        ppr[s] = 0.0
    assoc = _norm(ppr)
    glob = _norm(pagerank(viz))              # centralidade global entra na importância
    res = []

    def item(i, via):
        d = docs[i]
        imp = 0.5 * d.marca + 0.25 * glob.get(i, 0) + 0.25 * confianca(estado, i)
        partes = {
            "relevancia": rel.get(i, 0.0),
            "associacao": assoc.get(i, 0.0),
            "recencia": recencia(d, estado, hoje, meia_vida),
            "importancia": imp,
        }
        score = sum(pesos[c] * v for c, v in partes.items())
        return {"id": i, "nome": d.nome, "descricao": d.desc[:160], "score": round(score, 4),
                "partes": {c: round(v, 3) for c, v in partes.items()}, "via": via}

    texto = sorted((item(i, "texto") for i in rel), key=lambda r: (-r["score"], r["id"]))
    vizinhos = sorted((item(i, "associação") for i, v in assoc.items() if i not in rel and v >= 0.25),
                      key=lambda r: (-r["partes"]["associacao"], r["id"]))
    if vagas_assoc <= 0:
        return texto[:k]
    extra = min(vagas_assoc, len(vizinhos), max(0, k - 1))
    if len(texto) >= k - extra:
        return texto[:k - extra] + vizinhos[:extra]
    return (texto + vizinhos)[:k]            # poucos acertos de texto: vizinhos ocupam as vagas que sobraram


def frias(docs, estado, limiar=0.2, hoje=None, meia_vida=MEIA_VIDA_DIAS):
    hoje = hoje or dt.date.today()
    viz = grafo(docs, estado["sinapses"])
    grau = {i: len(v) for i, v in viz.items()}
    out = []
    for d in docs.values():
        w = (0.5 * d.marca + 0.5 * confianca(estado, d.id)) * recencia(d, estado, hoje, meia_vida)
        if w < limiar and grau.get(d.id, 0) == 0:
            out.append({"id": d.id, "peso": round(w, 3), "data": d.data.isoformat() if d.data else None})
    out.sort(key=lambda r: r["peso"])
    return out


def jaccard(a, b):
    a, b = set(tokens(a)), set(tokens(b))
    return len(a & b) / len(a | b) if a and b else 0.0


def consolidar(estado, minimo=2, limiar=0.4):
    """Agrupa lições parecidas; grupo com ≥ minimo episódios vira regra candidata. Não grava memória."""
    eps = [e for e in estado["episodios"] if e.get("licao")]
    grupos = []
    for e in eps:
        for g in grupos:
            if jaccard(e["licao"], g[0]["licao"]) >= limiar:
                g.append(e)
                break
        else:
            grupos.append([e])
    regras = []
    for g in grupos:
        if len(g) < minimo:
            continue
        ok = sum(1 for e in g if e["resultado"] == "ok")
        mems = {}
        for e in g:
            for u in e.get("usadas", []):
                mems[u] = mems.get(u, 0) + 1
        regras.append({
            "regra": max((e["licao"] for e in g), key=len),
            "suporte": len(g), "sucesso": round((ok + 1) / (len(g) + 2), 3),
            "episodios": [e["id"] for e in g],
            "memorias": sorted(mems, key=lambda m: -mems[m])[:5],
            "ja_consolidada": all(e["id"] in estado["consolidados"] for e in g),
        })
    regras.sort(key=lambda r: (-r["suporte"], -r["sucesso"]))
    return regras


def gabarito_do_indice(pasta):
    """MEMORY.md: cada linha '- ... [gancho](arquivo.md) — resumo' vira (consulta=gancho+resumo, alvo=arquivo).
    Os ganchos foram escritos à parte das memórias: servem de consultas com resposta conhecida."""
    try:
        with open(os.path.join(pasta, "MEMORY.md"), encoding="utf-8") as f:
            linhas = f.read().splitlines()
    except OSError:
        return []
    out = []
    for l in linhas:
        m = re.search(r"\[([^\]]{8,})\]\(([^)\s]+\.md)\)(.*)", l)
        if not m:
            continue
        consulta = re.sub(r"\(\d{1,2}/\d{1,2}(?:/\d{4})?\)", " ", m.group(1) + " " + m.group(3))
        consulta = re.sub(r"[*_`#>|\[\]]", " ", consulta)
        out.append((consulta.strip(), os.path.basename(m.group(2))))
    return out


def avaliar(docs, estado, gabarito, hoje=None, configs=None):
    """recall@1, recall@5 e MRR por configuração de pesos. BM25 puro é a linha de base."""
    configs = configs or {
        "bm25 puro": {"relevancia": 1.0, "associacao": 0.0, "recencia": 0.0, "importancia": 0.0},
        "bm25 + recência + importância": {"relevancia": 1.0, "associacao": 0.0, "recencia": 0.25, "importancia": 0.25},
        "pilha calibrada (canal de texto)": dict(PESOS),
        "associação forte no score (v0, rejeitada)": {"relevancia": 1.0, "associacao": 0.5, "recencia": 0.25, "importancia": 0.25},
    }
    casos = [(q, a) for q, a in gabarito if a in docs and tokens(q)]
    res = {}
    for nome, pesos in configs.items():
        r1 = r5 = rr = 0.0
        for q, alvo in casos:
            ids = [x["id"] for x in buscar(docs, estado, q, k=10, hoje=hoje, pesos=pesos, vagas_assoc=0)]
            if ids[:1] == [alvo]:
                r1 += 1
            if alvo in ids[:5]:
                r5 += 1
            if alvo in ids:
                rr += 1 / (ids.index(alvo) + 1)
        n = len(casos) or 1
        res[nome] = {"casos": len(casos), "recall@1": round(r1 / n, 3), "recall@5": round(r5 / n, 3), "mrr@10": round(rr / n, 3)}
    return res


PROMPT_LOBO_FRONTAL = """Você é o lobo frontal do sistema de consolidação de memória de um agente.
Entrada: episódios reais (tarefa, resultado ok/falha, fonte do resultado, lição verbal) que repetem a MESMA lição.
Tarefa: abstrair UMA regra operacional reutilizável. Responda só JSON:
{"regra": "imperativo, 1 frase, verificável",
 "quando_aplica": "gatilho concreto",
 "quando_nao_aplica": "o limite da regra — obrigatório",
 "contraexemplo": "um caso real ou plausível em que seguir a regra daria errado",
 "evitar": "o que os episódios de FALHA ensinam a não fazer (vazio se não houver falha)",
 "evidencia": ["ids dos episódios que sustentam"],
 "confianca": 0-1}
Regras: falha é tão informativa quanto sucesso — extraia dela a estratégia de evitar (ReasoningBank);
não invente fato fora dos episódios; se ok e falha se contradizem, diga isso em quando_nao_aplica e
baixe a confiança; sem saudação, sem log repetido, sem detalhe sintático."""


def abstrair_llm(regra, estado, chat):
    """Aplica o prompt do lobo frontal a UM grupo consolidado. `chat(sistema, usuario) -> texto` é injetável."""
    eps = {e["id"]: e for e in estado["episodios"]}
    linhas = [f"- {i}: tarefa={eps[i]['tarefa']!r} resultado={eps[i]['resultado']} fonte={eps[i].get('fonte', '?')} "
              f"lição={eps[i]['licao']!r}" for i in regra["episodios"] if i in eps]
    txt = chat(PROMPT_LOBO_FRONTAL, "EPISÓDIOS:\n" + "\n".join(linhas))
    m = re.search(r"\{.*\}", txt or "", re.S)
    try:
        j = json.loads(m.group(0)) if m else {}
    except ValueError:
        j = {}
    faltam = [c for c in ("regra", "quando_nao_aplica", "contraexemplo") if not str(j.get(c, "")).strip()]
    j["valida"] = not faltam and set(j.get("evidencia") or []) <= set(regra["episodios"]) and bool(j.get("evidencia"))
    j["faltam"] = faltam
    return j


def _chat_openrouter():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "conselho"))
    import conselho as cs  # noqa: E402
    cs.carregar_chaves()
    cs.detectar_proxy()
    if not os.environ.get("OPENROUTER_API_KEY"):
        raise SystemExit("memoria_viva: --llm precisa de OPENROUTER_API_KEY ou credencial no proxy")
    modelo = os.environ.get("MEMORIA_VIVA_MODELO") or next(m["id"] for m in cs.resolver(maximo=4)[0] if m["prov"] == "openrouter")

    def chat(sistema, usuario):
        st, d = cs.http(f"{cs.PROVEDORES['openrouter']['base']}/chat/completions",
                        {"model": modelo, "temperature": 0.2, "max_tokens": 1500, "reasoning": {"effort": "low"},
                         "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}]},
                        cs.cabecalhos("openrouter"))
        return (d.get("choices") or [{}])[0].get("message", {}).get("content", "") if st == 200 else ""
    return chat


# ---------------------------------------------------------------- CLI
def pastas_padrao():
    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    cands = [os.environ.get("CEREBRO_PRIVADO", ""), os.path.expanduser("~/Claude/cerebro-backup"),
             os.path.expanduser("~/cerebro-backup"), os.path.join(os.path.dirname(raiz), "cerebro-backup"),
             "/home/user/cerebro-backup"]
    out = []
    for c in cands:
        m = os.path.join(c, "claude-config", "memory") if c else ""
        if m and os.path.isdir(m):
            out.append(m)
            break
    sat = os.path.join(raiz, ".claude", "cerebro")
    if os.path.isdir(sat):
        out.append(sat)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="memoria_viva.py", description=__doc__.split("\n")[0])
    ap.add_argument("--mem", action="append")
    ap.add_argument("--estado")
    ap.add_argument("--meia-vida", type=float, default=MEIA_VIDA_DIAS)
    ap.add_argument("--hoje", help="AAAA-MM-DD (testes)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar"); b.add_argument("consulta"); b.add_argument("--k", type=int, default=8)
    b.add_argument("--json", action="store_true"); b.add_argument("--nomes", action="store_true")
    b.add_argument("--contexto", default="", help="raciocínio atual (AgentIR)")
    b.add_argument("--transcript", help="transcript JSONL: usa a última resposta do assistente como contexto")
    b.add_argument("--piso", type=float, default=0.0, help=f"relevância BM25 mínima do topo (recall usa {PISO_RECALL})")
    e = sub.add_parser("episodio"); e.add_argument("--tarefa", required=True)
    e.add_argument("--resultado", choices=["ok", "falha"], required=True)
    e.add_argument("--usadas", nargs="*", default=[]); e.add_argument("--licao", default="")
    e.add_argument("--forma", choices=["limpo", "recuperacao", "ruido"], default="limpo",
                   help="CMU 11-768 aula 8: limpo e recuperação ensinam; ruído é registrado mas não mexe em sinapse")
    e.add_argument("--fonte", choices=["humano", "metrica", "teste"], required=True,
                   help="de onde vem o ok/falha. Juiz LLM NÃO é fonte: deu 1,0 a resposta errada em 27/09")
    c = sub.add_parser("consolidar"); c.add_argument("--min", type=int, default=2); c.add_argument("--json", action="store_true")
    c.add_argument("--marcar", action="store_true", help="marca os episódios das regras listadas como consolidados")
    c.add_argument("--llm", action="store_true", help="abstrai cada regra com o prompt do lobo frontal (OpenRouter)")
    f = sub.add_parser("frias"); f.add_argument("--limiar", type=float, default=0.2)
    av = sub.add_parser("avaliar", help="recall@k no gabarito do MEMORY.md: pilha vs BM25 puro")
    av.add_argument("--json", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args(argv)

    pastas = a.mem or pastas_padrao()
    caminho = a.estado or estado_padrao(pastas)
    estado = ler_estado(caminho)
    hoje = dt.date.fromisoformat(a.hoje) if a.hoje else dt.date.today()

    if a.cmd == "episodio":
        docs = carregar(pastas, hoje)
        desconhecidas = [u for u in a.usadas if u not in docs and not u.startswith("skill:")]
        if desconhecidas:
            print("memoria_viva: memória inexistente: " + ", ".join(desconhecidas), file=sys.stderr)
            return 2
        ep = {"id": f"ep-{hoje.isoformat()}-{len(estado['episodios']) + 1:04d}", "data": hoje.isoformat(),
              "tarefa": a.tarefa[:500], "resultado": a.resultado, "usadas": sorted(set(a.usadas)),
              "licao": a.licao[:1000], "fonte": a.fonte, "forma": a.forma}
        estado["episodios"].append(ep)
        tocadas = {} if a.forma == "ruido" else hebb(estado, a.usadas, a.resultado == "ok", hoje)
        gravar_estado(caminho, estado)
        print(f"episódio {ep['id']} gravado · {len(tocadas)} sinapse(s) atualizada(s) · estado: {caminho}")
        return 0

    if a.cmd == "consolidar":
        regras = consolidar(estado, a.min)
        if a.llm and regras:
            chat = _chat_openrouter()
            for r in regras:
                r["abstracao"] = abstrair_llm(r, estado, chat)
        if a.marcar:
            for r in regras:
                estado["consolidados"] = sorted(set(estado["consolidados"]) | set(r["episodios"]))
            gravar_estado(caminho, estado)
        if a.json:
            print(json.dumps(regras, ensure_ascii=False, indent=1))
        elif not regras:
            print("nenhuma lição repetida ainda (precisa de ≥ %d episódios com lição parecida)" % a.min)
        else:
            for r in regras:
                flag = " (já consolidada)" if r["ja_consolidada"] else ""
                print(f"- [{r['suporte']}× · sucesso {r['sucesso']}]{flag} {r['regra']}\n  memórias: {', '.join(r['memorias'])}")
                ab = r.get("abstracao")
                if ab:
                    print(f"  regra abstraída{' ✅' if ab['valida'] else ' ❌ incompleta: ' + ', '.join(ab['faltam'] or ['evidência'])}: "
                          f"{ab.get('regra', '')}\n  não aplica: {ab.get('quando_nao_aplica', '')}\n  contraexemplo: {ab.get('contraexemplo', '')}")
            print("\nPromover = escrever/atualizar a memória com revisão (fundir-indice.py). Nada foi gravado.")
        return 0

    docs = carregar(pastas, hoje, cache=not os.environ.get("MEMORIA_VIVA_SEM_CACHE"))
    if a.cmd == "buscar":
        ctx = a.contexto or (ultima_resposta(a.transcript) if a.transcript else "")
        res = buscar(docs, estado, a.consulta, a.k, hoje, a.meia_vida, contexto=ctx, piso=a.piso)
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        elif a.nomes:
            for r in res:
                marca = "↔" if r["via"] == "associação" else "•"
                print(f"{marca} {r['id']} — {r['descricao'][:110]}")
        else:
            for r in res:
                p = r["partes"]
                print(f"{r['score']:.3f}  {r['id']:<50} rel {p['relevancia']:.2f} · assoc {p['associacao']:.2f} · "
                      f"rec {p['recencia']:.2f} · imp {p['importancia']:.2f}  [{r['via']}]")
        return 0 if res else 1

    if a.cmd == "frias":
        out = frias(docs, estado, a.limiar, hoje, a.meia_vida)
        for r in out:
            print(f"{r['peso']:.3f}  {r['id']}  ({r['data'] or 'sem data'})")
        print(f"\n{len(out)} candidata(s) a ARQUIVO (sem link, peso < {a.limiar}). Nada foi apagado — Lei da Monotonia.")
        return 0

    if a.cmd == "avaliar":
        gab = []
        for p in pastas:
            gab += gabarito_do_indice(p)
        if not gab:
            print("sem MEMORY.md com links nas pastas: nada a avaliar", file=sys.stderr)
            return 2
        res = avaliar(docs, estado, gab, hoje)
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        else:
            for nome, m in res.items():
                print(f"{nome:<32} casos {m['casos']:>4} · recall@1 {m['recall@1']:.3f} · recall@5 {m['recall@5']:.3f} · MRR {m['mrr@10']:.3f}")
        return 0

    if a.cmd == "status":
        links = sum(len(d.links) for d in docs.values())
        print(f"pastas: {', '.join(pastas) or '(nenhuma)'}\nmemórias: {len(docs)} · links: {links} · "
              f"sinapses aprendidas: {sum(1 for w in estado['sinapses'].values() if w > 0)} · "
              f"episódios: {len(estado['episodios'])} · estado: {caminho}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
