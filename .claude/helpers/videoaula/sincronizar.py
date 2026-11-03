#!/usr/bin/env python3
"""Monta a linha do tempo de uma aula (cenas com ini/dur) a partir da narração.
Uso: sincronizar.py aulas/p1-aula1.json [narracao.mp3] > aulas/p1-aula1.sync.json
Sem áudio: durações provisórias por tamanho do texto (para pré-visualizar).
Com áudio: detecta as pausas (<break 1.2s> entre trechos) com ffmpeg silencedetect.
"""
import json, re, subprocess, sys, pathlib

ABERTURA = 2.6   # cartão de título antes da narração
CAUDA = 1.2      # respiro no fim

def duracao_audio(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip()
    return float(out)

def silencios(p, ruido="-35dB", minimo=0.7):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", f"silencedetect=noise={ruido}:d={minimo}", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", txt)]
    fim = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", txt)]
    pares = list(zip(ini, fim))
    return [(a, b) for a, b in pares if b - a >= minimo]

def main():
    aula = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    audio = sys.argv[2] if len(sys.argv) > 2 else None
    trechos = aula["trechos"]
    n = len(trechos)
    if audio:
        total_audio = duracao_audio(audio)
        sil = silencios(audio)
        # ignora silêncio inicial/final; escolhe as n-1 pausas mais longas entre as internas
        internas = [(a, b) for a, b in sil if a > 0.3 and b < total_audio - 0.3]
        internas.sort(key=lambda ab: ab[1] - ab[0], reverse=True)
        escolhidas = sorted(internas[: n - 1], key=lambda ab: ab[0])
        if len(escolhidas) != n - 1:
            print(f"AVISO: {len(escolhidas)} pausas para {n} trechos; completando proporcionalmente", file=sys.stderr)
        limites = [(a + b) / 2 for a, b in escolhidas]
        if len(limites) < n - 1:  # completa por proporção de caracteres
            tam = [len(t["fala"]) for t in trechos]
            acc, tot = 0, sum(tam)
            prop = []
            for x in tam[:-1]:
                acc += x
                prop.append(total_audio * acc / tot)
            limites = sorted(set(limites + prop))[: n - 1]
        pontos = [0.0] + limites + [total_audio]
        durs = [pontos[i + 1] - pontos[i] for i in range(n)]
        modo = "audio"
    else:
        durs = [max(3.5, len(t["fala"]) / 14.5 + 0.9) for t in trechos]
        total_audio = sum(durs)
        modo = "provisorio"
    cenas = [{"tipo": "titulo", "titulo": aula["titulo"], "sub": aula["sub"], "selo": aula["selo"], "numero": str(aula["numero"]).zfill(2), "ini": 0.0, "dur": ABERTURA}]
    t = ABERTURA
    for tr, d in zip(trechos, durs):
        c = dict(tr["cena"]); c["ini"] = round(t, 3); c["dur"] = round(d, 3); c["tiles"] = tr.get("tiles", [])
        cenas.append(c); t += d
    cenas[-1]["dur"] = round(cenas[-1]["dur"] + CAUDA, 3)
    total = round(ABERTURA + total_audio + CAUDA, 3)
    out = {"id": aula["id"], "rotulo": aula["rotulo"], "titulo": aula["titulo"], "total": total, "abertura": ABERTURA, "modo": modo, "cenas": cenas}
    print(json.dumps(out, ensure_ascii=False))
    print(f"{aula['id']}: {n} trechos, modo {modo}, total {total:.1f}s", file=sys.stderr)

if __name__ == "__main__":
    main()
