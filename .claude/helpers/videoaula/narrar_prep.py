#!/usr/bin/env python3
"""Gera o texto de narração de cada aula para o TTS (um arquivo por aula), com pausas entre trechos
e ajustes de pronúncia. Uso: narrar_prep.py aulas/*.json  → aulas/<id>.tts.txt"""
import json, re, sys, pathlib

SUBS = [
    (r"\bIAs\b", "inteligências artificiais"),
    (r"\bIA\b", "I.A."),
    (r"\bffmpeg\b", "éfe-éfe-ême-pég"),
    (r"\bLUFS\b", "lufs"),
    (r"\bfps\b", "quadros por segundo"),
    (r"\bJSON\b", "jeison"),
    (r"\bHTML\b", "agá-tê-ême-éle"),
    (r"\bCFM\b", "cê-éfe-ême"),
    (r"\bCREFITO\b", "crefito"),
    (r"\bCFO\b", "cê-éfe-ó"),
    (r"\bCFN\b", "cê-éfe-êne"),
    (r"\bCFP\b", "cê-éfe-pê"),
    (r"\bREF-02\b", "referência dois"),
    (r"\bB1\b", "bê um"), (r"\bB2\b", "bê dois"), (r"\bB3\b", "bê três"),
    (r"\bA2\b", "á dois"), (r"\bC1\b", "cê um"), (r"\bC2\b", "cê dois"),
]
PAUSA = ' <break time="1.2s" /> '

for p in sys.argv[1:]:
    a = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    falas = []
    for t in a["trechos"]:
        s = t["fala"]
        for rx, sub in SUBS:
            s = re.sub(rx, sub, s)
        falas.append(s.strip())
    txt = PAUSA.join(falas)
    out = pathlib.Path(p).with_suffix(".tts.txt")
    out.write_text(txt, encoding="utf-8")
    print(f"{a['id']}: {len(falas)} trechos, {len(txt)} caracteres → {out.name}")
