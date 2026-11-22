#!/usr/bin/env python3
"""Esteira de notícias → vídeos explicados, para uma página de volume. Roda por agendamento (cron/systemd).

Uso:
  python3 esteira-noticias.py --config pagina.json [--quantos 5] [--so-escolher]

pagina.json (exemplo em esteira-exemplo.json):
  {"perfil": "@explicadodehoje", "publico": "geral", "voz": "pt-BR-AntonioNeural",
   "fontes": ["g1", "bbc_brasil", "guardian_mundo"], "pasta": "~/esteira/explicadodehoje",
   "publicar": {"via": "nenhum"}}          # ou {"via": "upload-post", "usuario": "...", "plataformas": ["instagram","tiktok"]}

O que faz a cada execução:
  1. lê os RSS das fontes e descarta o que já virou vídeo (estado.json na pasta);
  2. a IA escolhe as N notícias mais fortes para o público da página (relevância, impacto, curiosidade; sem duplicar o
     mesmo assunto de jornais diferentes; descarta crime com vítima identificável, tragédia com criança e boato);
  3. gera cada vídeo com noticia-em-video.py (traduz notícia estrangeira, cita a fonte na tela);
  4. salva em pasta/pendentes/AAAA-MM-DD/ o .mp4 + .txt (legenda com fonte e link);
  5. se "publicar.via" = "upload-post", agenda nos horários de "horarios" (padrão 9h,12h,15h,18h,21h) — senão fica
     esperando aprovação (padrão seguro).
Custo: ~US$ 0,20 por vídeo + ~US$ 0,01 da escolha.
"""
import argparse, datetime, json, os, re, subprocess, sys, urllib.request, html

FONTES = {
    "g1": "https://g1.globo.com/rss/g1/",
    "bbc_brasil": "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "guardian_mundo": "https://www.theguardian.com/world/rss",
    "bbc_mundo": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "agencia_brasil": "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml",
}
AQUI = os.path.dirname(os.path.abspath(__file__))
OR = "https://openrouter.ai/api/v1/chat/completions"


def rss(url, limite=40):
    x = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read() \
        .decode("utf-8", "ignore")
    itens = []
    for bloco in re.findall(r"(?s)<item[ >].*?</item>", x)[:limite]:
        def campo(n):
            m = re.search(rf"(?s)<{n}[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{n}>", bloco)
            return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else ""
        link = campo("link").split("?at_medium")[0]
        if link:
            itens.append({"titulo": campo("title"), "resumo": campo("description")[:240], "link": link})
    return itens


def escolher(candidatos, publico, n):
    lista = "\n".join(f"{i}. {c['titulo']} — {c['resumo']} [{c['fonte']}]" for i, c in enumerate(candidatos))
    pedido = (f"Você é editor de uma página de notícias em vídeo curto no Instagram/TikTok. Público: {publico}.\n"
              f"Escolha as {n} notícias com mais potencial de alcance e interesse real (impacto na vida das pessoas, "
              "curiosidade, assunto do dia). Regras: não repetir o mesmo assunto de jornais diferentes; misture Brasil e "
              "mundo; descarte crime com vítima comum identificável, tragédia envolvendo criança, boato, e notícia só "
              "de serviço local sem interesse geral. Devolva APENAS JSON: {\"escolhidas\": [índices em ordem de "
              "prioridade]}.\n\n" + lista)
    h = {"Content-Type": "application/json"}
    if os.environ.get("OPENROUTER_API_KEY"):
        h["Authorization"] = "Bearer " + os.environ["OPENROUTER_API_KEY"]
    r = json.load(urllib.request.urlopen(urllib.request.Request(OR, data=json.dumps({
        "model": "google/gemini-2.5-flash", "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": pedido}]}).encode(), headers=h), timeout=120))
    txt = re.sub(r"^```(json)?|```$", "", r["choices"][0]["message"]["content"].strip(), flags=re.M)
    idx = [int(i) for i in json.loads(txt)["escolhidas"] if str(i).isdigit() and int(i) < len(candidatos)]
    return [candidatos[i] for i in idx[:n]]


def publicar_upload_post(cfg, video, legenda, quando):
    """Agenda no Upload-Post (chave UPLOAD_POST_API_KEY no ambiente — nunca no arquivo)."""
    pub = cfg["publicar"]
    cmd = ["curl", "-sS", "-X", "POST", "https://api.upload-post.com/api/upload",
           "-H", "Authorization: Apikey " + os.environ["UPLOAD_POST_API_KEY"],
           "--form-string", "user=" + pub["usuario"], "--form-string", "title=" + legenda[:2000],
           "--form-string", "scheduled_date=" + quando.isoformat(), "-F", "video=@" + video]
    for p in pub.get("plataformas", ["instagram", "tiktok"]):
        cmd += ["--form-string", "platform[]=" + p]
    return subprocess.run(cmd, capture_output=True, text=True).stdout[:300]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True); ap.add_argument("--quantos", type=int, default=5)
    ap.add_argument("--so-escolher", action="store_true")
    a = ap.parse_args()
    cfg = json.load(open(os.path.expanduser(a.config)))
    pasta = os.path.expanduser(cfg["pasta"]); os.makedirs(pasta, exist_ok=True)
    est_arq = os.path.join(pasta, "estado.json")
    estado = json.load(open(est_arq)) if os.path.exists(est_arq) else {"feitos": []}
    candidatos = []
    for f in cfg.get("fontes", ["g1", "bbc_brasil", "guardian_mundo"]):
        try:
            for it in rss(FONTES.get(f, f)):
                if it["link"] not in estado["feitos"]:
                    it["fonte"] = f; candidatos.append(it)
        except Exception as e:
            print(f"fonte {f} falhou: {e}", file=sys.stderr)
    if not candidatos:
        sys.exit("nenhuma notícia nova")
    escolhidas = escolher(candidatos[:120], cfg.get("publico", "geral"), a.quantos)
    for c in escolhidas:
        print(f"• [{c['fonte']}] {c['titulo']}")
    if a.so_escolher:
        return
    hoje = datetime.date.today().isoformat()
    destino = os.path.join(pasta, "pendentes", hoje); os.makedirs(destino, exist_ok=True)
    horarios = cfg.get("horarios", ["09:00", "12:00", "15:00", "18:00", "21:00"])
    feitos = 0
    for i, c in enumerate(escolhidas):
        nome = re.sub(r"[^a-z0-9]+", "-", c["titulo"].lower())[:50].strip("-") or f"noticia-{i}"
        mp4 = os.path.join(destino, f"{i + 1:02d}-{nome}.mp4")
        r = subprocess.run([sys.executable, os.path.join(AQUI, "noticia-em-video.py"), c["link"], "--saida", mp4,
                            "--perfil", cfg["perfil"], "--publico", cfg.get("publico", "geral"),
                            "--voz", cfg.get("voz", "pt-BR-AntonioNeural")]
                           + (["--avatar", json.dumps(cfg["avatar"])] if cfg.get("avatar") else []),
                           capture_output=True, text=True)
        print(r.stdout.strip().splitlines()[-1] if r.returncode == 0 else f"ERRO {c['link']}: {r.stderr[-300:]}")
        if r.returncode:
            continue
        estado["feitos"].append(c["link"]); feitos += 1
        json.dump(estado, open(est_arq, "w"), ensure_ascii=False, indent=1)
        if cfg.get("publicar", {}).get("via") == "upload-post":
            hh, mm = map(int, horarios[i % len(horarios)].split(":"))
            quando = datetime.datetime.combine(datetime.date.today(), datetime.time(hh, mm))
            if quando < datetime.datetime.now():
                quando += datetime.timedelta(days=1)
            legenda = open(mp4[:-4] + ".txt").read()
            print("  agendado:", quando, publicar_upload_post(cfg, mp4, legenda, quando))
    estado["feitos"] = estado["feitos"][-2000:]
    json.dump(estado, open(est_arq, "w"), ensure_ascii=False, indent=1)
    print(f"{feitos}/{len(escolhidas)} vídeos em {destino}")


if __name__ == "__main__":
    main()
