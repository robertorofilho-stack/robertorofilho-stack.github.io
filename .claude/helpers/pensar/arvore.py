#!/usr/bin/env python3
"""ÁRVORE — busca em árvore de pensamentos (MCTS/PUCT + reflexão verbal) para problemas difíceis e verificáveis.

Versão corrigida e testável do "LLM-MCTS" estudado em 27/09/2026 (LATS, Zhou et al. 2023, arXiv 2310.04406;
AlphaZero/PUCT; Reflexion; Stanford CS329A s05; CMU 11-768 "Tree Search"). O que foi consertado no pseudocódigo
original que circulou:

  1. prior = exp(logprob da SEQUÊNCIA inteira) ≈ 0 para qualquer frase → o termo de exploração morria.
     Aqui o prior é a nota do propositor NORMALIZADA entre os irmãos (soma 1).
  2. U = c·P·√N_pai/(1+n) com N_pai = 0 na primeira descida → exploração zero. Aqui √(N_pai+1).
  3. Avaliava o nó PAI depois de expandir; aqui avalia o filho novo (o que de fato foi gerado).
  4. Sem teto de chamadas nem de dólar → loop pago infinito. Aqui: --max-chamadas e --teto-usd (duros).
  5. Sem memória de erro → a reflexão verbal do nó ruim entra no prompt dos próximos (o "gradiente semântico").
  6. "Entropia controlada" real: estagnou por N iterações → sobe a temperatura e pede abordagem de outro domínio.
  7. Verificador programático (quando existe) VENCE o LLM-juiz — o gargalo é verificar, não gerar (CS329A s03).

Uso:
  arvore.py --problema "..." [--iter 12] [--k 3] [--prof 4] [--max-chamadas 40] [--teto-usd 0.30] [--saida x.md]
  arvore.py --jogo24 "4 7 8 8"        demonstração com verificador exato (benchmark clássico do Tree-of-Thoughts)
  arvore.py --simulado                 sem rede (testes)
Não use para ação irreversível (pagar, enviar, publicar): a árvore EXPLORA, e explorar ação irreversível é executá-la.
"""
import argparse
import itertools
import json
import math
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- nó e política
class No:
    __slots__ = ("passo", "pai", "filhos", "n", "w", "prior", "valor", "critica", "terminal", "prof", "vazias")

    def __init__(self, passo="", pai=None, prior=1.0):
        self.passo, self.pai, self.prior = passo, pai, prior
        self.filhos, self.n, self.w = [], 0, 0.0
        self.valor, self.critica, self.terminal = None, "", False
        self.vazias = 0
        self.prof = (pai.prof + 1) if pai else 0

    @property
    def q(self):
        return self.w / self.n if self.n else 0.0

    def caminho(self):
        no, out = self, []
        while no and no.pai:
            out.append(no.passo)
            no = no.pai
        return out[::-1]


def puct(pai, filho, c=1.4):
    return filho.q + c * filho.prior * math.sqrt(pai.n + 1) / (1 + filho.n)


def normalizar_priors(notas):
    notas = [max(0.0, float(x)) for x in notas]
    tot = sum(notas)
    return [x / tot for x in notas] if tot > 0 else [1 / len(notas)] * len(notas)


# ---------------------------------------------------------------- motores
class Orcamento(Exception):
    pass


class Motor:
    """Interface: propor(problema, caminho, k, temperatura, reflexoes, diverso) -> [(passo, nota, final)]
                  avaliar(problema, caminho) -> (valor ∈ [0,1], critica)
                  verificar(problema, caminho) -> valor ∈ [0,1] | None (None = sem verificador exato)"""
    chamadas = 0
    custo = 0.0
    tem_verificador = False

    def verificar(self, problema, caminho):
        return None


class Simulado(Motor):
    """Problema de brinquedo determinístico: montar a palavra-alvo letra a letra. Serve aos testes."""

    tem_verificador = True

    def __init__(self, alvo="LUCRO", ruido=None):
        self.alvo, self.ruido = alvo, ruido or "XYZW"
        self.prompts = []

    def propor(self, problema, caminho, k, temperatura, reflexoes, diverso):
        self.chamadas += 1
        self.prompts.append({"reflexoes": list(reflexoes), "temperatura": temperatura, "diverso": diverso})
        i = len(caminho)
        certo = self.alvo[i] if i < len(self.alvo) else "."
        erradas = [c for c in self.ruido if c != certo][: k - 1]
        final = i + 1 >= len(self.alvo)
        # o propositor "prefere" uma errada — a busca tem de corrigir isso pelo valor, não pelo prior
        return [(erradas[0], 0.6, final)] + [(certo, 0.3, final)] + [(e, 0.1, final) for e in erradas[1:]]

    def avaliar(self, problema, caminho):
        self.chamadas += 1
        acertos = 0
        for a, b in zip(caminho, self.alvo):
            if a != b:
                break
            acertos += 1
        v = acertos / len(self.alvo)
        return v, ("" if v == len(caminho) / len(self.alvo) else f"a letra {len(caminho)} está errada")

    def verificar(self, problema, caminho):
        return 1.0 if "".join(caminho) == self.alvo else (0.0 if len(caminho) >= len(self.alvo) else None)


class Jogo24:
    """Verificador EXATO do Game of 24 (Yao et al., Tree of Thoughts, 2023). Passo = uma operação 'a op b = c'."""

    def __init__(self, numeros):
        self.inicio = [float(x) for x in numeros]

    def restantes(self, caminho):
        nums = list(self.inicio)
        for passo in caminho:
            passo = re.sub(r"(\d),(\d)", r"\1.\2", passo)
            m = re.fullmatch(r"\s*(-?[\d.]+)\s*([-+*/x×÷])\s*(-?[\d.]+)\s*=\s*(-?[\d.]+)\s*\.?\s*", passo)
            if not m:
                return None
            a, op, b = float(m.group(1)), m.group(2), float(m.group(3))
            real = {"+": a + b, "-": a - b, "*": a * b, "x": a * b, "×": a * b,
                    "/": a / b if b else None, "÷": a / b if b else None}[op]
            if real is None or abs(real - float(m.group(4))) > 1e-2:
                return None
            for x in (a, b):
                ach = next((i for i, y in enumerate(nums) if abs(y - x) < 1e-2), None)
                if ach is None:
                    return None
                nums.pop(ach)
            nums.append(real)
        return nums

    def valor(self, caminho):
        r = self.restantes(caminho)
        if r is None:
            return 0.0
        if len(r) == 1:
            return 1.0 if abs(r[0] - 24) < 1e-6 else 0.0
        return None if self.solucivel(r) else 0.0     # poda exata: o que sobrou não chega a 24

    def solucivel(self, nums):
        if len(nums) == 1:
            return abs(nums[0] - 24) < 1e-6
        for i, j in itertools.permutations(range(len(nums)), 2):
            resto = [nums[t] for t in range(len(nums)) if t not in (i, j)]
            a, b = nums[i], nums[j]
            for c in (a + b, a - b, a * b) + ((a / b,) if b else ()):
                if self.solucivel(resto + [c]):
                    return True
        return False


class OpenRouter(Motor):
    """LLM real pelo transporte do conselho (chave do cofre ou credencial injetada pelo proxy da nuvem)."""

    def __init__(self, modelo=None, max_chamadas=40, teto_usd=0.30, verificador=None, formato_passo=""):
        sys.path.insert(0, os.path.join(AQUI, "..", "conselho"))
        import conselho as cs  # noqa: E402
        self.cs = cs
        cs.carregar_chaves()
        cs.detectar_proxy()
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise SystemExit("arvore: sem OPENROUTER_API_KEY nem credencial no proxy (ver conselho.py --status)")
        self.modelo = modelo or os.environ.get("ARVORE_MODELO") or self._escolher()
        self.max_chamadas, self.teto_usd = max_chamadas, teto_usd
        self.verificador = verificador
        self.tem_verificador = verificador is not None
        self.formato_passo = formato_passo

    def _escolher(self):
        ms, _ = self.cs.resolver(maximo=4)
        ms = [m for m in ms if m["prov"] == "openrouter"]
        if not ms:
            raise SystemExit("arvore: nenhum modelo OpenRouter disponível")
        return ms[0]["id"]

    def _chat(self, sistema, usuario, temperatura):
        if self.chamadas >= self.max_chamadas or self.custo >= self.teto_usd:
            raise Orcamento(f"orçamento atingido: {self.chamadas} chamadas, US$ {self.custo:.4f}")
        self.chamadas += 1
        dados = {"model": self.modelo, "temperature": temperatura, "max_tokens": 1500, "usage": {"include": True},
                 "reasoning": {"effort": "low"},
                 "messages": [{"role": "system", "content": sistema}, {"role": "user", "content": usuario}]}
        st, d = self.cs.http(f"{self.cs.PROVEDORES['openrouter']['base']}/chat/completions", dados,
                             self.cs.cabecalhos("openrouter"))
        if st != 200 or not d.get("choices"):
            raise RuntimeError(self.cs.mascarar(f"HTTP {st}: {json.dumps(d)[:300]}"))
        self.custo += float((d.get("usage") or {}).get("cost") or 0)
        return (d["choices"][0].get("message") or {}).get("content", "")

    @staticmethod
    def _json(txt):
        m = re.search(r"\{.*\}", txt, re.S)
        try:
            return json.loads(m.group(0)) if m else {}
        except ValueError:
            return {}

    def propor(self, problema, caminho, k, temperatura, reflexoes, diverso):
        sistema = ("Você propõe o PRÓXIMO passo de raciocínio para resolver um problema. Responda só JSON: "
                   '{"passos":[{"passo":"...","nota":0-1,"final":true|false}]} com passos DIFERENTES entre si. '
                   "nota = sua chance estimada de o passo levar à solução. final=true se o passo encerra a resposta.")
        u = f"PROBLEMA:\n{problema}\n\nPASSOS JÁ DADOS:\n" + ("\n".join(f"{i+1}. {p}" for i, p in enumerate(caminho)) or "(nenhum)")
        u += f"\n\nProponha {k} próximos passos alternativos, UM passo cada (não resolva tudo de uma vez)."
        if self.formato_passo:
            u += f"\nFORMATO OBRIGATÓRIO de cada passo: {self.formato_passo}"
        if reflexoes:
            u += "\n\nERROS JÁ COMETIDOS EM OUTROS RAMOS (não repita):\n" + "\n".join(f"- {r}" for r in reflexoes[-6:])
        if diverso:
            u += "\n\nA busca ESTAGNOU: proponha ao menos um passo de abordagem radicalmente diferente, vinda de outro domínio."
        passos = self._json(self._chat(sistema, u, temperatura)).get("passos") or []
        out = []
        for p in passos[:k]:
            if isinstance(p, dict) and str(p.get("passo", "")).strip():
                try:
                    nota = float(p.get("nota", 0.5))
                except (TypeError, ValueError):
                    nota = 0.5
                out.append((str(p["passo"]).strip()[:600], nota, bool(p.get("final"))))
        return out

    def avaliar(self, problema, caminho):
        sistema = ("Você é um verificador severo. Avalie se a sequência de passos está CORRETA e leva à solução. "
                   'Responda só JSON: {"valor":0-1,"critica":"o erro principal, em 1 frase, ou vazio"}')
        u = f"PROBLEMA:\n{problema}\n\nPASSOS:\n" + "\n".join(f"{i+1}. {p}" for i, p in enumerate(caminho))
        j = self._json(self._chat(sistema, u, 0.0))
        try:
            v = min(1.0, max(0.0, float(j.get("valor", 0))))
        except (TypeError, ValueError):
            v = 0.0
        return v, str(j.get("critica", ""))[:300]

    def verificar(self, problema, caminho):
        return self.verificador(caminho) if self.verificador else None


# ---------------------------------------------------------------- busca
def _todos(raiz):
    pilha, out = [raiz], []
    while pilha:
        n = pilha.pop()
        out.append(n)
        pilha.extend(n.filhos)
    return out


def buscar(motor, problema, iteracoes=12, k=3, prof_max=4, c=1.4, paciencia=3, t0=0.7, log=None):
    raiz = No()
    reflexoes, temperatura, melhor_v, sem_melhora = [], t0, -1.0, 0
    motor_tem_verificador = bool(getattr(motor, "tem_verificador", False))
    melhor_folha = None
    parou = ""
    exatos = set()

    def avaliar(no):
        v = motor.verificar(problema, no.caminho())          # verificador exato > juiz LLM
        if v is None:
            v, critica = motor.avaliar(problema, no.caminho())
            if v >= 1.0 and motor_tem_verificador:
                v = 0.99                                      # juiz não fecha o que o verificador ainda não fechou
        else:
            exatos.add(id(no))
            critica = "" if v >= 1 else "verificador exato reprovou este caminho"
            if v <= 0:
                no.terminal = True                           # caminho inválido: não expandir
        no.valor, no.critica = v, critica
        if v < 0.3 and critica:
            reflexoes.append(f"{' → '.join(no.caminho())[:200]}: {critica}")
        return v

    for it in range(iteracoes):
        no = raiz
        while not no.terminal:                               # 1. seleção (PUCT) só entre filhos VIVOS
            vivos = [f for f in no.filhos if not (f.terminal and f.valor is not None and f.valor <= 0)]
            if not vivos:
                break                                        # sem filho vivo: alarga este nó (novas propostas)
            no = max(vivos, key=lambda f: puct(no, f, c))
        v = no.valor if no.valor is not None else 0.0
        if not no.terminal and no.prof < prof_max:           # 2. expansão + 3. avaliação de TODOS os filhos (LATS)
            diverso = sem_melhora >= paciencia
            try:
                props = motor.propor(problema, no.caminho(), k, temperatura, reflexoes, diverso)
                vistos, unicas = {f.passo for f in no.filhos}, []
                for passo, nota, final in props:
                    if passo not in vistos:
                        vistos.add(passo)
                        unicas.append((passo, nota, final))
                novos = []
                for (passo, _, final), p in zip(unicas, normalizar_priors([x[1] for x in unicas]) if unicas else []):
                    f = No(passo, no, p)
                    # com verificador exato, o fim é dele (o propositor marca "final" em passo parcial)
                    f.terminal = f.prof >= prof_max or (final and not motor_tem_verificador)
                    no.filhos.append(f)
                    novos.append(f)
                for f in novos:
                    f.n, f.w = 1, avaliar(f)
            except Orcamento as e:
                parou = str(e)
                for f in list(no.filhos):                    # filho criado e não avaliado sai da árvore
                    if f.valor is None:
                        no.filhos.remove(f)
                break
            if novos:
                v = max(f.valor for f in novos)
            else:
                no.vazias += 1                               # resposta vazia/ilegível: tenta de novo, 2× seguidas = folha
                if no.vazias >= 2 and not any(f for f in no.filhos if not f.terminal):
                    no.terminal = True
                v = 0.0
        no_bp = no
        while no_bp:                                         # 4. retropropagação
            no_bp.n += 1
            no_bp.w += v
            no_bp = no_bp.pai
        if v > melhor_v + 1e-9:
            melhor_v, sem_melhora = v, 0
            temperatura = t0
        else:
            sem_melhora += 1
            if sem_melhora >= paciencia:
                temperatura = min(1.2, temperatura + 0.3)
        if log:
            log(f"iter {it+1}: valor {v:.2f} · melhor {melhor_v:.2f} · temp {temperatura:.1f} · chamadas {motor.chamadas}")
        if melhor_v >= 1.0:
            fechou = [n for n in _todos(raiz) if n.valor is not None and n.valor >= 1.0]
            if any(id(n) in exatos for n in fechou):
                parou = "solução verificada (verificador exato)"
                break
            if not motor_tem_verificador:
                parou = "aprovada pelo juiz LLM — NÃO verificada"
                break
    todas = [n for n in _todos(raiz) if n.valor is not None and n.pai]
    if todas:
        melhor_folha = max(todas, key=lambda n: (n.valor, n.prof, n.n))
    robusto, no = [], raiz                                    # caminho mais visitado (estável, estilo AlphaZero)
    while no.filhos:
        no = max(no.filhos, key=lambda f: (f.n, f.q))
        robusto.append(no.passo)
    verificada = bool(melhor_folha and id(melhor_folha) in exatos and melhor_folha.valor >= 1.0)
    return {"verificada": verificada, "melhor": melhor_folha.caminho() if melhor_folha else [], "valor": melhor_folha.valor if melhor_folha else 0.0,
            "mais_visitado": robusto, "reflexoes": reflexoes, "chamadas": motor.chamadas,
            "custo_usd": round(motor.custo, 4), "nos": len(todas), "parou": parou or "iterações esgotadas", "raiz": raiz}


def relatorio(problema, r, modelo=""):
    L = [f"# Árvore de pensamento\n\n**Problema:** {problema}\n",
         f"**Resultado:** valor {r['valor']:.2f} · {r['nos']} nós avaliados · {r['chamadas']} chamadas · "
         f"US$ {r['custo_usd']:.4f}{' · ' + modelo if modelo else ''} · parada: {r['parou']}\n",
         "## Melhor caminho\n"] + [f"{i+1}. {p}" for i, p in enumerate(r["melhor"])]
    if r["mais_visitado"] != r["melhor"]:
        L += ["\n## Caminho mais visitado (robusto)\n"] + [f"{i+1}. {p}" for i, p in enumerate(r["mais_visitado"])]
    if r["reflexoes"]:
        L += ["\n## Reflexões (erros que a busca aprendeu a evitar)\n"] + [f"- {x}" for x in r["reflexoes"]]
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="arvore.py", description=__doc__.split("\n")[0])
    ap.add_argument("--problema")
    ap.add_argument("--jogo24")
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--iter", type=int, default=12)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--prof", type=int, default=4)
    ap.add_argument("--max-chamadas", type=int, default=40)
    ap.add_argument("--teto-usd", type=float, default=0.30)
    ap.add_argument("--modelo")
    ap.add_argument("--saida")
    ap.add_argument("--quieto", action="store_true")
    a = ap.parse_args(argv)
    log = None if a.quieto else (lambda s: print(s, file=sys.stderr))
    if a.simulado:
        motor, problema, rotulo = Simulado(), "montar a palavra-alvo", "simulado"
    elif a.jogo24:
        nums = a.jogo24.split()
        j = Jogo24(nums)
        problema = (f"Game of 24: usando CADA um dos números {', '.join(nums)} exatamente uma vez e + - * /, chegar a 24. "
                    "Cada passo combina DOIS números restantes no formato 'a op b = c' (ex.: '8 / 4 = 2'). "
                    "O último passo deve dar 24.")
        motor = OpenRouter(a.modelo, a.max_chamadas, a.teto_usd, verificador=j.valor,
                           formato_passo="SÓ a conta 'a op b = c' com números (ex.: '8 / 4 = 2'), sem nenhuma palavra.")
        rotulo = motor.modelo
        a.prof = max(a.prof, len(nums) - 1)
    elif a.problema:
        motor = OpenRouter(a.modelo, a.max_chamadas, a.teto_usd)
        problema, rotulo = a.problema, motor.modelo
    else:
        ap.error("informe --problema, --jogo24 ou --simulado")
    r = buscar(motor, problema, a.iter, a.k, a.prof, log=log)
    md = relatorio(problema, r, rotulo)
    if a.saida:
        with open(a.saida, "w", encoding="utf-8") as f:
            f.write(md)
    print(md)
    return 0 if r["verificada"] or not a.jogo24 else 3


if __name__ == "__main__":
    sys.exit(main())
