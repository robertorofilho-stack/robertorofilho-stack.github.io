#!/usr/bin/env python3
"""Extrai as âncoras literais de um transcript JSONL do Claude Code (usado pelo checkpoint.sh no PreCompact).

Saída em Markdown: primeiro pedido, últimos 3 pedidos, proibições ditas pelo operador e efeitos externos já
feitos. Nada é resumido nem parafraseado — só copiado. CMU 11-768 aulas 1–3 (fala): a compactação apaga o
"não apague" e faz o agente repetir ação externa ("five pull requests for the same functionality").
"""
import json
import re
import sys

PROIBE = re.compile(
    r"\b(nunca|jamais|proibid\w*|sem (pedir|autoriza\w*)|never|don'?t|do not|"
    r"n[ãa]o (pode|faça|faz|apague|apaga|delete|mexa|mexe|publique|publica|envie|envia|gaste|gasta|use|usa|"
    r"commite|mude|muda|toque|mande|manda|suba|sobe|rode|roda|compre|pague))\b", re.I)
EFEITO = re.compile(
    r"git push|gh pr |create_pull_request|merge_pull_request|push_files|create_or_update_file|send_message|"
    r"send_email|Gmail__(send|reply|forward|trash)|ads_create|ads_update|ads_activate|ads_boost|publish|deploy|"
    r"create_event|delete_event|vercel --prod|curl[^|\n]*-X ?(POST|PUT|PATCH|DELETE)|\brm -r|git reset --hard|"
    r"\bDROP |DELETE FROM", re.I)
RUIDO = ("<system-reminder", "[SYSTEM NOTIFICATION", "<task-notification", "<local-command", "<command-")


def extrair(caminho):
    pedidos, proibicoes, efeitos = [], [], []
    with open(caminho, encoding="utf-8", errors="replace") as f:
        for linha in f:
            try:
                j = json.loads(linha)
            except ValueError:
                continue
            c = (j.get("message") or {}).get("content")
            if j.get("type") == "user":
                if isinstance(c, list):   # resultado de ferramenta vem como lista; pedido humano vem como texto
                    c = " ".join(p.get("text", "") for p in c if isinstance(p, dict) and p.get("type") == "text")
                c = (c or "").strip()
                if not c or c.startswith(RUIDO):
                    continue
                pedidos.append(c)
                for frase in re.split(r"(?<=[.!?\n])\s+", c):
                    frase = frase.strip()
                    if PROIBE.search(frase) and frase[:300] not in proibicoes:
                        proibicoes.append(frase[:300])
            elif j.get("type") == "assistant" and isinstance(c, list):
                for p in c:
                    if isinstance(p, dict) and p.get("type") == "tool_use":
                        nome = p.get("name", "")
                        entrada = json.dumps(p.get("input", {}), ensure_ascii=False)
                        if EFEITO.search(nome + " " + entrada):
                            efeitos.append(f"{nome}: {entrada[:160]}")
    return pedidos, proibicoes, efeitos


def markdown(caminho):
    pedidos, proibicoes, efeitos = extrair(caminho)
    out = []
    cita = lambda t: "> " + t[:1500].replace("\n", "\n> ")  # noqa: E731
    if pedidos:
        out += ["### Primeiro pedido da sessão (literal — o objetivo original)", cita(pedidos[0]), ""]
        out += ["### Últimos pedidos do operador (literais)"]
        for p in pedidos[-3:]:
            out += [cita(p), ""]
    if proibicoes:
        out += ["### PROIBIÇÕES ditas pelo operador (literais — valem até ele revogar)"]
        out += ["- " + f.replace("\n", " ") for f in proibicoes[-15:]] + [""]
    if efeitos:
        out += ["### EFEITOS EXTERNOS JÁ FEITOS — NÃO REPETIR"]
        out += ["- " + e.replace("\n", " ") for e in efeitos[-20:]] + [""]
    out += [f"_Histórico completo em disco: {caminho}_", ""]
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(2)
    print(markdown(sys.argv[1]))
