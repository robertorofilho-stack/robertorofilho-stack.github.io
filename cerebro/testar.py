#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
testar.py — bateria de testes do Cerebro.

Dois modos:

  --offline  (roda sem nenhuma chave, e o que rodou na entrega)
      Prova a logica: retry, fallback, calculo de custo, corte de legenda,
      montagem do payload multipart, leitura das pastas de AGENDAMENTOS.
      Usa um servidor HTTP falso — nao toca na internet.

  --online   (precisa das chaves no .env)
      1. Lista os perfis e as redes conectadas no Upload-Post
      2. Uma chamada real em cada modelo do OpenRouter
      3. Simula queda do OpenRouter e prova o fallback para o APIMart
      4. Mostra o custo total

Uso:
    python3 testar.py --offline
    python3 testar.py --online
    python3 testar.py --online --e2e video.mp4   # ponta a ponta, agenda em 10 min
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

VERDE, VERM, AMAR, FIM = "\033[92m", "\033[91m", "\033[93m", "\033[0m"

_passou = 0
_falhou = 0


def ok(msg: str) -> None:
    global _passou
    _passou += 1
    print(f"  {VERDE}PASSOU{FIM}  {msg}")


def falha(msg: str) -> None:
    global _falhou
    _falhou += 1
    print(f"  {VERM}FALHOU{FIM}  {msg}")


def checar(condicao: bool, msg: str) -> None:
    ok(msg) if condicao else falha(msg)


def titulo(t: str) -> None:
    print(f"\n{AMAR}=== {t} ==={FIM}")


class RespostaFalsa:
    """Imita requests.Response o suficiente para os testes."""

    def __init__(self, status: int, corpo: dict | None = None, texto: str = ""):
        self.status_code = status
        self._corpo = corpo
        self.text = texto or (json.dumps(corpo) if corpo else "")

    def json(self):
        if self._corpo is None:
            raise ValueError("sem json")
        return self._corpo


# ---------------------------------------------------------------------------
# Testes offline
# ---------------------------------------------------------------------------

def teste_corte_legenda() -> None:
    titulo("Corte de legenda por rede")
    from uploadpost_client import cortar_legenda, limite_de

    checar(limite_de("x") == 280, "limite do X e 280")
    checar(limite_de("tiktok") == 2200, "limite do TikTok e 2200")
    checar(limite_de("rede_inventada") == 2200, "rede desconhecida cai no padrao 2200")

    texto = "palavra " * 100  # 800 chars
    curto = cortar_legenda(texto, "x")
    checar(len(curto) <= 280, f"corte do X respeita 280 (deu {len(curto)})")
    checar(not curto[:-1].endswith(" "), "corte nao deixa espaco solto no fim")
    checar(cortar_legenda("curto", "x") == "curto", "texto curto passa intacto")
    checar(cortar_legenda("", "tiktok") == "", "texto vazio nao quebra")


def teste_datas() -> None:
    titulo("Interpretacao de data")
    from uploadpost_client import UploadPostClient, UploadPostError

    n = UploadPostClient._normalizar_data
    checar(n(None) is None, "None continua None")

    futuro = n(10)
    checar(futuro is not None and futuro.endswith("Z"), f"10 minutos vira ISO-8601 Z ({futuro})")
    dt = datetime.strptime(futuro, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    delta = (dt - datetime.now(timezone.utc)).total_seconds()
    checar(500 < delta < 700, f"10 minutos cai mesmo daqui a ~600s (deu {delta:.0f}s)")

    alvo = datetime.now(timezone.utc) + timedelta(hours=2)
    checar(n(alvo.isoformat()).endswith("Z"), "ISO-8601 com timezone e aceito")

    try:
        n("2020-01-01T00:00:00Z")
        falha("data no passado deveria dar erro")
    except UploadPostError:
        ok("data no passado e recusada")

    try:
        n("dia de sao nunca")
        falha("data invalida deveria dar erro")
    except UploadPostError:
        ok("data invalida e recusada")

    from agendar import interpretar_quando
    checar(interpretar_quando("+15") == 15, "'+15' vira 15 minutos")
    checar(interpretar_quando(30) == 30, "inteiro passa direto")
    amanha = interpretar_quando("amanha 11:00")
    checar(isinstance(amanha, str) and amanha.endswith("Z"), f"'amanha 11:00' vira ISO ({amanha})")


def teste_payload() -> None:
    titulo("Montagem do payload multipart")
    from uploadpost_client import UploadPostClient, TIKTOK_PADRAO

    campos = UploadPostClient._campos(
        {"user": "eu", "async_upload": True, "disable_comment": False, "titulo": None},
        ["tiktok", "instagram"],
    )
    chaves = [c[0] for c in campos]
    checar(chaves.count("platform[]") == 2, "duas redes viram dois platform[]")
    checar(("async_upload", "true") in campos, "booleano True vira 'true'")
    checar(("disable_comment", "false") in campos, "booleano False vira 'false'")
    checar("titulo" not in chaves, "campo None e omitido")

    checar(TIKTOK_PADRAO["privacy_level"] == "PUBLIC_TO_EVERYONE", "TikTok: publico")
    checar(TIKTOK_PADRAO["disable_comment"] is False, "TikTok: comentarios liberados")
    checar(TIKTOK_PADRAO["disable_duet"] is False, "TikTok: duet liberado")
    checar(TIKTOK_PADRAO["disable_stitch"] is False, "TikTok: stitch liberado")
    checar(TIKTOK_PADRAO["is_aigc"] is True, "TikTok: marcado como conteudo de IA")
    checar(TIKTOK_PADRAO["post_mode"] == "DIRECT_POST", "TikTok: publica direto, sem rascunho")


def teste_retry() -> None:
    titulo("Retry 3x do Upload-Post")
    import uploadpost_client as upc

    cliente = upc.UploadPostClient(api_key="chave_de_teste", usuario="teste", tentativas=3)

    # 500 tres vezes -> tenta 3 e desiste
    chamadas = []
    def sempre_500(*a, **k):
        chamadas.append(1)
        return RespostaFalsa(500, texto="erro interno")

    with mock.patch.object(cliente.sessao, "request", side_effect=sempre_500), \
         mock.patch("time.sleep"):
        try:
            cliente.validar_chave()
            falha("deveria falhar depois de 3 tentativas")
        except upc.UploadPostError:
            checar(len(chamadas) == 3, f"HTTP 500 tentou 3 vezes (tentou {len(chamadas)})")

    # 500, 500, 200 -> sucesso na terceira
    respostas = [RespostaFalsa(500, texto="x"), RespostaFalsa(500, texto="x"),
                 RespostaFalsa(200, {"email": "ok@teste"})]
    with mock.patch.object(cliente.sessao, "request", side_effect=respostas), \
         mock.patch("time.sleep"):
        r = cliente.validar_chave()
        checar(r.get("email") == "ok@teste", "recupera no terceiro try depois de dois 500")

    # 400 -> nao repete (erro de parametro nao melhora insistindo)
    chamadas.clear()
    def sempre_400(*a, **k):
        chamadas.append(1)
        return RespostaFalsa(400, texto="parametro invalido")

    with mock.patch.object(cliente.sessao, "request", side_effect=sempre_400), \
         mock.patch("time.sleep"):
        try:
            cliente.validar_chave()
            falha("400 deveria levantar erro")
        except upc.UploadPostError:
            checar(len(chamadas) == 1, f"HTTP 400 nao repete (tentou {len(chamadas)})")

    # 429 -> repete
    chamadas.clear()
    def sempre_429(*a, **k):
        chamadas.append(1)
        return RespostaFalsa(429, texto="rate limit")

    with mock.patch.object(cliente.sessao, "request", side_effect=sempre_429), \
         mock.patch("time.sleep"):
        try:
            cliente.validar_chave()
        except upc.UploadPostError:
            pass
        checar(len(chamadas) == 3, f"HTTP 429 repete 3x (tentou {len(chamadas)})")


def teste_log_publicacao() -> None:
    titulo("Log em logs/publicacao.log")
    import uploadpost_client as upc

    antes = upc.LOG_FILE.stat().st_size if upc.LOG_FILE.is_file() else 0
    cliente = upc.UploadPostClient(api_key="k", usuario="u", tentativas=1)
    with mock.patch.object(cliente.sessao, "request",
                           return_value=RespostaFalsa(200, {"ok": True})):
        cliente.validar_chave()
    for h in upc.logger.handlers:
        h.flush()
    depois = upc.LOG_FILE.stat().st_size if upc.LOG_FILE.is_file() else 0
    checar(upc.LOG_FILE.is_file(), f"arquivo existe: {upc.LOG_FILE}")
    checar(depois > antes, f"log cresceu ({antes} -> {depois} bytes)")

    # Confere que o resultado por rede aparece no log.
    upc.UploadPostClient._registrar_resultado(
        {"request_id": "req123",
         "results": {"tiktok": {"success": True, "post_url": "https://tiktok/x"},
                     "instagram": {"success": False, "error": "token expirado"}}},
        ["tiktok", "instagram"],
    )
    for h in upc.logger.handlers:
        h.flush()
    conteudo = upc.LOG_FILE.read_text(encoding="utf-8")
    checar("req123" in conteudo, "request_id vai para o log")
    checar("PUBLICADO" in conteudo, "sucesso por rede vai para o log")
    checar("token expirado" in conteudo, "erro por rede vai para o log")


def teste_custo() -> None:
    titulo("Calculo e registro de custo")
    import openrouter_client as orc

    # 1M entrada + 1M saida no Sonnet 5 = 2.00 + 10.00 = 12.00
    c = orc.calcular_custo("anthropic/claude-sonnet-5", 1_000_000, 1_000_000)
    checar(abs(c - 12.0) < 1e-9, f"Sonnet 5: 1M+1M = US$ 12.00 (deu {c})")

    c = orc.calcular_custo("google/gemini-3.8-flash", 1_000_000, 0)
    checar(abs(c - 0.75) < 1e-9, f"Gemini 3.8 Flash: 1M entrada = US$ 0.75 (deu {c})")

    c = orc.calcular_custo("openai/gpt-5-nano", 1_000_000, 1_000_000)
    checar(abs(c - 0.45) < 1e-9, f"gpt-5-nano: 1M+1M = US$ 0.45 (deu {c})")

    checar(orc.calcular_custo("modelo/inexistente", 1000, 1000) == 0.0,
           "modelo sem preco cadastrado devolve 0 em vez de inventar")

    # Registro em custos.jsonl
    antes = orc.resumo_custos()["chamadas"]
    r = orc.Resposta(texto="oi", modelo="anthropic/claude-sonnet-5", tarefa="roteiro",
                     provedor="openrouter", tokens_entrada=100, tokens_saida=50,
                     custo_usd=orc.calcular_custo("anthropic/claude-sonnet-5", 100, 50))
    orc.registrar_custo(r)
    resumo = orc.resumo_custos()
    checar(resumo["chamadas"] == antes + 1, "custos.jsonl ganhou uma linha")
    checar("roteiro" in resumo["por_tarefa"], "resumo separa por tarefa")
    checar(orc.LOG_CUSTOS.is_file(), f"arquivo existe: {orc.LOG_CUSTOS}")


def teste_uso_real_da_api() -> None:
    titulo("Custo vindo do proprio OpenRouter (usage.cost)")
    import openrouter_client as orc

    dados = {
        "model": "anthropic/claude-sonnet-5",
        "choices": [{"message": {"content": "OK"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "cost": 0.00042},
    }
    r = orc.OpenRouterClient._montar_resposta(dados, "anthropic/claude-sonnet-5", "roteiro", 1.0, 1)
    checar(r.custo_usd == 0.00042, "usa o custo real da API quando ele vem")
    checar(r.texto == "OK", "extrai o texto da resposta")
    checar(r.tokens_entrada == 10 and r.tokens_saida == 5, "extrai a contagem de tokens")

    # Sem 'cost' -> cai na tabela local
    dados["usage"].pop("cost")
    r2 = orc.OpenRouterClient._montar_resposta(dados, "anthropic/claude-sonnet-5", "roteiro", 1.0, 1)
    esperado = orc.calcular_custo("anthropic/claude-sonnet-5", 10, 5)
    checar(abs(r2.custo_usd - esperado) < 1e-12, "sem custo na API, calcula pela tabela")


def teste_fallback() -> None:
    titulo("Fallback OpenRouter -> APIMart")
    import openrouter_client as orc

    # apimart_client falso, instalado na memoria do Python.
    falso = type(sys)("apimart_client")
    falso.chat = lambda messages=None, **kw: {"text": "RESPOSTA DO APIMART"}
    sys.modules["apimart_client"] = falso

    cliente = orc.OpenRouterClient(api_key="chave_teste", tentativas=2)
    with mock.patch("time.sleep"):
        r = cliente.completar("teste", "trivial", _forcar_falha=True)
    checar(r.provedor == "apimart", f"caiu para o APIMart (provedor={r.provedor})")
    checar(r.caiu_para_fallback is True, "marca a resposta como fallback")
    checar("APIMART" in r.texto, f"texto veio do APIMart: {r.texto!r}")

    # Fallback tambem cobre HTTP 500 repetido, nao so falha de rede.
    with mock.patch.object(cliente.sessao, "post",
                           return_value=RespostaFalsa(500, texto="boom")), \
         mock.patch("time.sleep"):
        r2 = cliente.completar("teste", "trivial")
    checar(r2.provedor == "apimart", "HTTP 500 repetido tambem cai para o APIMart")

    # Sem chave nenhuma -> vai direto para o fallback, sem perder tempo
    sem_chave = orc.OpenRouterClient(api_key="", tentativas=3)
    r3 = sem_chave.completar("teste", "trivial")
    checar(r3.provedor == "apimart", "sem OPENROUTER_API_KEY vai direto ao fallback")

    # Fallback desligado -> erro explicito em vez de silencio
    duro = orc.OpenRouterClient(api_key="k", tentativas=1, usar_fallback=False)
    with mock.patch("time.sleep"):
        try:
            duro.completar("teste", "trivial", _forcar_falha=True)
            falha("com fallback desligado deveria levantar erro")
        except orc.OpenRouterError:
            ok("com fallback desligado, levanta erro explicito")

    # Descoberta de funcao: apimart que expoe outro nome
    outro = type(sys)("apimart_client")
    outro.gerar_texto = lambda prompt=None, **kw: "VIA GERAR_TEXTO"
    sys.modules["apimart_client"] = outro
    with mock.patch("time.sleep"):
        r4 = cliente.completar("teste", "trivial", _forcar_falha=True)
    checar("GERAR_TEXTO" in r4.texto, "acha a funcao do apimart mesmo com outro nome")

    del sys.modules["apimart_client"]


def teste_sucesso_openrouter() -> None:
    titulo("Caminho feliz do OpenRouter (HTTP mockado)")
    import openrouter_client as orc

    cliente = orc.OpenRouterClient(api_key="chave_teste")
    resposta = RespostaFalsa(200, {
        "model": "google/gemini-3.8-flash",
        "choices": [{"message": {"content": "Resposta da pesquisa."}}],
        "usage": {"prompt_tokens": 200, "completion_tokens": 100},
    })
    with mock.patch.object(cliente.sessao, "post", return_value=resposta) as post:
        r = cliente.completar("pesquise algo", "pesquisa")
    corpo = post.call_args.kwargs["json"]
    checar(corpo["model"] == "google/gemini-3.8-flash", "tarefa 'pesquisa' usa o Gemini Flash")
    checar(r.provedor == "openrouter", "nao caiu para o fallback sem precisar")
    checar(r.texto == "Resposta da pesquisa.", "texto extraido")
    esperado = 200 * 0.00000075 + 100 * 0.00000375
    checar(abs(r.custo_usd - esperado) < 1e-12, f"custo calculado: US$ {r.custo_usd:.8f}")


def teste_mapa_de_modelos() -> None:
    titulo("Modelos configurados")
    import openrouter_client as orc

    checar(orc.TAREFAS["pesquisa"].startswith("google/gemini"),
           f"pesquisa -> {orc.TAREFAS['pesquisa']}")
    checar("sonnet" in orc.TAREFAS["roteiro"], f"roteiro -> {orc.TAREFAS['roteiro']}")
    checar("sonnet" in orc.TAREFAS["legenda"], f"legenda -> {orc.TAREFAS['legenda']}")
    checar(orc.TAREFAS["trivial"].startswith("openai/"), f"trivial -> {orc.TAREFAS['trivial']}")
    for tarefa, modelo in orc.TAREFAS.items():
        checar(modelo in orc.PRECOS, f"preco cadastrado para {tarefa}: {modelo}")


def teste_agendamentos() -> None:
    titulo("Leitura das pastas de AGENDAMENTOS")
    import agendar as ag

    pasta = ag.PASTA_AGENDAMENTOS / "_teste_automatico"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "legenda.txt").write_text("Gancho forte aqui.\nCorpo da legenda.", encoding="utf-8")
    (pasta / "config.json").write_text(
        json.dumps({"redes": ["tiktok", "instagram", "x"], "adaptar": False}),
        encoding="utf-8")
    (pasta / "video.mp4").write_bytes(b"\x00" * 2048)

    post = ag.Post(pasta)
    checar(post.legenda_base.startswith("Gancho"), "leu legenda.txt")
    checar(post.redes == ["tiktok", "instagram", "x"], "leu as redes do config.json")
    checar(len(post.videos) == 1, "achou o video")
    checar(post.validar() == [], "post completo passa na validacao")
    checar(not post.ja_publicado, "post novo esta pendente")

    legendas, custo = ag.preparar_legendas(post, adaptar=False)
    checar(set(legendas) == {"tiktok", "instagram", "x"}, "gerou legenda para cada rede")
    checar(len(legendas["x"]) <= 280, f"legenda do X respeita 280 ({len(legendas['x'])})")
    checar(custo == 0.0, "sem adaptacao, custo zero")

    # Pasta incompleta e detectada
    vazia = ag.PASTA_AGENDAMENTOS / "_teste_incompleto"
    vazia.mkdir(parents=True, exist_ok=True)
    (vazia / "legenda.txt").write_text("so texto", encoding="utf-8")
    problemas = ag.Post(vazia).validar()
    checar(any("video" in p or "imagem" in p for p in problemas),
           f"pasta sem midia e sinalizada: {problemas}")

    # Marcador de publicado
    post.marcar_publicado({"request_id": "x"}, legendas, 0.0)
    checar(ag.Post(pasta).ja_publicado, "marcador .publicado.json impede republicar")

    import shutil
    shutil.rmtree(pasta, ignore_errors=True)
    shutil.rmtree(vazia, ignore_errors=True)


def teste_configurar_chaves() -> None:
    titulo("Gravacao de chave no .env sem apagar as outras")
    import configurar_chaves as cc
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        env = Path(tmp) / ".env"
        env.write_text(
            "# chaves do cerebro\n"
            "FAL_KEY=fal-abc123\n"
            "ELEVENLABS_API_KEY=el-xyz789\n"
            "HIGGSFIELD_API_KEY=hf-antigo\n",
            encoding="utf-8",
        )
        cc.definir(env, "UPLOAD_POST_API_KEY", "up-nova")
        cc.definir(env, "OPENROUTER_API_KEY", "sk-or-nova")
        texto = env.read_text(encoding="utf-8")

        checar("FAL_KEY=fal-abc123" in texto, "FAL_KEY intacta")
        checar("ELEVENLABS_API_KEY=el-xyz789" in texto, "ELEVENLABS_API_KEY intacta")
        checar("HIGGSFIELD_API_KEY=hf-antigo" in texto, "HIGGSFIELD_API_KEY preservada (nao apagar)")
        checar("# chaves do cerebro" in texto, "comentario preservado")
        checar("UPLOAD_POST_API_KEY=up-nova" in texto, "UPLOAD_POST_API_KEY adicionada")
        checar("OPENROUTER_API_KEY=sk-or-nova" in texto, "OPENROUTER_API_KEY adicionada")

        acao = cc.definir(env, "UPLOAD_POST_API_KEY", "up-atualizada")
        texto = env.read_text(encoding="utf-8")
        checar(acao == "atualizada", "regravar a mesma chave reporta 'atualizada'")
        checar(texto.count("UPLOAD_POST_API_KEY") == 1, "nao duplica a chave ao regravar")
        checar("up-atualizada" in texto and "up-nova" not in texto, "valor foi substituido")
        checar(env.with_suffix(".env.bak").is_file() or (Path(tmp) / ".env.bak").is_file(),
               "backup .env.bak foi criado")
        mascarada = cc.mascarar("chave-secreta-de-exemplo")
        checar("chave-secreta" not in mascarada and "..." in mascarada,
               f"chave e mascarada ao exibir ({mascarada})")


def rodar_offline() -> int:
    print(f"{AMAR}BATERIA OFFLINE — sem chaves, sem internet{FIM}")
    for fn in (teste_corte_legenda, teste_datas, teste_payload, teste_retry,
               teste_log_publicacao, teste_custo, teste_uso_real_da_api,
               teste_sucesso_openrouter, teste_fallback, teste_mapa_de_modelos,
               teste_agendamentos, teste_configurar_chaves):
        try:
            fn()
        except Exception as exc:
            import traceback
            falha(f"{fn.__name__} explodiu: {exc}")
            traceback.print_exc()

    print(f"\n{'='*60}")
    cor = VERDE if _falhou == 0 else VERM
    print(f"{cor}{_passou} passaram, {_falhou} falharam{FIM}")
    return 0 if _falhou == 0 else 1


# ---------------------------------------------------------------------------
# Testes online
# ---------------------------------------------------------------------------

def rodar_online(e2e: str | None = None) -> int:
    print(f"{AMAR}BATERIA ONLINE — usa as chaves do .env e gasta creditos{FIM}")
    custo_total = 0.0

    titulo("1. Upload-Post: perfis e redes conectadas")
    redes_faltando: dict[str, list[str]] = {}
    try:
        from uploadpost_client import UploadPostClient, REDES_PADRAO
        up = UploadPostClient()
        conta = up.validar_chave()
        ok(f"chave valida — {conta.get('email', conta)}")
        mapa = up.redes_conectadas()
        if not mapa:
            falha("nenhum perfil encontrado — crie um perfil em upload-post.com")
        for perfil, redes in mapa.items():
            print(f"    perfil '{perfil}': {', '.join(redes) if redes else '(nenhuma rede)'}")
            faltam = sorted(set(REDES_PADRAO) - set(redes))
            if faltam:
                redes_faltando[perfil] = faltam
                falha(f"perfil '{perfil}' NAO tem conectada: {', '.join(faltam)}")
            else:
                ok(f"perfil '{perfil}' tem todas as redes necessarias")
    except Exception as exc:
        falha(f"Upload-Post: {exc}")

    titulo("2. OpenRouter: uma chamada real em cada modelo")
    try:
        import openrouter_client as orc
        for tarefa, modelo in orc.TAREFAS.items():
            try:
                r = orc.cliente().completar(
                    "Responda apenas: OK", tarefa, max_tokens=20, temperatura=0)
                custo_total += r.custo_usd
                if r.provedor == "openrouter":
                    ok(f"{tarefa:<9} {modelo:<30} US$ {r.custo_usd:.6f}  {r.segundos:.1f}s")
                else:
                    falha(f"{tarefa:<9} {modelo} caiu para {r.provedor} (OpenRouter falhou)")
            except Exception as exc:
                falha(f"{tarefa} ({modelo}): {exc}")
    except Exception as exc:
        falha(f"OpenRouter: {exc}")

    titulo("3. Fallback: simulando queda do OpenRouter")
    try:
        import openrouter_client as orc
        r = orc.cliente().completar("Responda: OK", "trivial", _forcar_falha=True)
        if r.provedor == "apimart":
            ok(f"fallback funcionou — respondeu via APIMart ({r.modelo})")
        else:
            falha(f"esperava provedor 'apimart', veio '{r.provedor}'")
    except Exception as exc:
        falha(f"fallback nao funcionou: {exc}")

    if e2e:
        titulo("4. Ponta a ponta: pesquisa -> roteiro -> legenda -> agendamento")
        try:
            import openrouter_client as orc
            from uploadpost_client import UploadPostClient

            p = orc.pesquisar("Um fato curto e verdadeiro sobre dor no joelho em corredores.")
            custo_total += p.custo_usd
            ok(f"pesquisa: {p.texto[:80]}... (US$ {p.custo_usd:.6f})")

            s = orc.roteiro(f"Roteiro de 20 segundos, em portugues, sobre: {p.texto[:500]}")
            custo_total += s.custo_usd
            ok(f"roteiro: {s.texto[:80]}... (US$ {s.custo_usd:.6f})")

            c = orc.legenda(f"Legenda de Instagram para este roteiro: {s.texto[:500]}")
            custo_total += c.custo_usd
            ok(f"legenda: {c.texto[:80]}... (US$ {c.custo_usd:.6f})")

            up = UploadPostClient()
            r = up.publicar_video(e2e, c.texto, ["tiktok", "instagram"], quando=10)
            ok(f"agendado para daqui a 10 minutos: {json.dumps(r)[:200]}")
        except Exception as exc:
            falha(f"ponta a ponta: {exc}")

    print(f"\n{'='*60}")
    print(f"Custo desta bateria: US$ {custo_total:.6f}")
    try:
        import openrouter_client as orc
        print(f"Custo acumulado no custos.jsonl: US$ {orc.resumo_custos()['total_usd']:.6f}")
    except Exception:
        pass
    cor = VERDE if _falhou == 0 else VERM
    print(f"{cor}{_passou} passaram, {_falhou} falharam{FIM}")

    if redes_faltando:
        print(f"\n{AMAR}REDES QUE FALTA CONECTAR NO PAINEL upload-post.com:{FIM}")
        for perfil, faltam in redes_faltando.items():
            print(f"  perfil '{perfil}': {', '.join(faltam)}")
    return 0 if _falhou == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Testes do Cerebro.")
    ap.add_argument("--offline", action="store_true", help="Sem chaves, sem internet")
    ap.add_argument("--online", action="store_true", help="Usa as chaves reais")
    ap.add_argument("--e2e", metavar="VIDEO", help="Teste ponta a ponta com este video")
    args = ap.parse_args()

    if args.online or args.e2e:
        return rodar_online(args.e2e)
    return rodar_offline()


if __name__ == "__main__":
    sys.exit(main())
