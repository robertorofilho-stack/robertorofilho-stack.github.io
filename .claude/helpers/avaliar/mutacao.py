#!/usr/bin/env python3
"""MUTAÇÃO — mede se os testes pegam defeito de verdade (CMU 11-768 aula 6: "teste ruim é o maior problema").

Troca um operador por vez no arquivo-alvo (< por <=, and por or, True por False, +1 por -1…), roda a suíte e
confere se ela QUEBRA. Mutante que sobrevive = trecho que nenhum teste vigia. O arquivo original é restaurado
sempre (try/finally + cópia .mutacao-bak). Só biblioteca padrão.

Uso:
  mutacao.py alvo.py teste.py [--max 25] [--minimo 0.6]
Saída: placar (mortos/total) e a lista dos sobreviventes com linha. Sai com 1 se o placar < --minimo.
"""
import os
import re
import shutil
import subprocess
import sys

TROCAS = [(r" <= ", " < "), (r" >= ", " > "), (r" < ", " <= "), (r" > ", " >= "), (r" == ", " != "),
          (r" != ", " == "), (r" and ", " or "), (r" or ", " and "), (r"\bTrue\b", "False"), (r"\bFalse\b", "True"),
          (r" \+ 1\b", " - 1"), (r" - 1\b", " + 1"), (r"\bmax\(", "min("), (r"\bmin\(", "max(")]


def sitios(linhas):
    out = []
    dentro = False                                     # dentro de texto de várias linhas (docstring, listas em texto)
    for n, l in enumerate(linhas):
        aspas = l.count('"""') + l.count("'''")
        if dentro or aspas:
            if aspas % 2 == 1:
                dentro = not dentro
            continue
        codigo = l.split("#", 1)[0]
        if not codigo.strip() or codigo.lstrip().startswith(("import", "from", "def ", "class ", "print(", '"""', "'")):
            continue
        if '"' in codigo and codigo.count('"') >= 2 and re.search(r'"[^"]*(<|>|==| and | or )[^"]*"', codigo):
            continue                                   # operador dentro de texto: mutar não testa lógica
        for padrao, troca in TROCAS:
            for m in re.finditer(padrao, codigo):
                out.append((n, m.start(), m.end(), troca))
    return out


def rodar(teste, timeout=120):
    # Sem bytecode: "==" → "!=" não muda o tamanho do arquivo e a restauração cai no mesmo segundo; o .pyc do
    # MUTANTE seria reaproveitado depois (bug real, 27/09 — o frias passou a devolver 1 fora da mutação).
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run([sys.executable, "-B", teste], capture_output=True, text=True, timeout=timeout, env=env)
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        return False                                   # travou = o teste percebeu (mutante morto)


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if len(a) < 2:
        print(__doc__)
        return 2
    alvo, teste = a[0], a[1]
    maximo = int(a[a.index("--max") + 1]) if "--max" in a else 25
    minimo = float(a[a.index("--minimo") + 1]) if "--minimo" in a else 0.6
    if not rodar(teste):
        print("a suíte já falha SEM mutação — conserte antes de medir", file=sys.stderr)
        return 2
    with open(alvo, encoding="utf-8") as f:
        original = f.read()
    linhas = original.splitlines(keepends=True)
    todos = sitios(linhas)
    passo = max(1, len(todos) // maximo)
    escolhidos = todos[::passo][:maximo]              # amostra determinística espalhada pelo arquivo
    bak = alvo + ".mutacao-bak"
    shutil.copy2(alvo, bak)
    mortos, sobreviventes = 0, []
    try:
        for n, i, j, troca in escolhidos:
            nova = list(linhas)
            nova[n] = linhas[n][:i] + troca + linhas[n][j:]
            with open(alvo, "w", encoding="utf-8") as f:
                f.write("".join(nova))
            if rodar(teste):
                sobreviventes.append((n + 1, linhas[n].strip()[:90], troca.strip()))
            else:
                mortos += 1
    finally:
        with open(alvo, "w", encoding="utf-8") as f:
            f.write(original)
        os.remove(bak)
        cache = os.path.join(os.path.dirname(os.path.abspath(alvo)), "__pycache__")
        base = os.path.splitext(os.path.basename(alvo))[0] + "."
        for n in (os.listdir(cache) if os.path.isdir(cache) else []):
            if n.startswith(base):
                os.remove(os.path.join(cache, n))   # nenhum bytecode de mutante sobrevive
    total = len(escolhidos)
    placar = mortos / total if total else 1.0
    print(f"mutação {os.path.basename(alvo)}: {mortos}/{total} mutantes mortos ({placar:.0%}) · {len(todos)} sítios no arquivo")
    for ln, txt, troca in sobreviventes:
        try:
            print(f"  sobreviveu L{ln}: {txt}   (trocado por '{troca}')")
        except BrokenPipeError:
            break
    return 0 if placar >= minimo else 1


if __name__ == "__main__":
    sys.exit(main())
