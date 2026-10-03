#!/usr/bin/env bash
# transcrever-youtube.sh — Diretor de Aprendizado, Fase 1D: transcrição de aula do YouTube.
#
# RODA NO MAC (IP residencial). Na nuvem o YouTube exige login/PO Token para IP de datacenter:
# testado 27/09/2026 com yt-dlp 2026.08.19 — clientes default/mweb/tv/android_vr/ios = "Sign in to confirm
# you're not a bot"; web_safari passa mas descarta legendas sem PO Token; Jina Reader, youtubetranscript,
# Invidious e Piped também bloqueados. Por isso: missão na fila JARBAS → Mac executa.
#
# NA NUVEM: use assistir-video.py (Gemini lê o YouTube pelo lado do Google — funciona, medido 03/10/2026).
#
# Cascata por vídeo (para no primeiro que der texto):
#   1. legenda (manual ou automática) — clientes default, mweb, web_safari
#   2. mesma coisa com cookies do navegador logado (--cookies-from-browser), só leitura
#   3. áudio mono 16 kHz (mweb) → whisper local (grátis, sem API)
#
# Uso:
#   transcrever-youtube.sh <slug> <url|id|ytsearchN:consulta> [...]
#   NAVEGADOR=chrome|safari|firefox  (padrão chrome)   WHISPER_MODELO=small  (padrão)   IDIOMA=en
# Saída: ~/Claude/APRENDIZADO/<slug>/{transcricoes/*.txt, vtt/, audio/, RELATORIO.md}
# Nunca reprocessa: vídeo com .txt pronto é pulado.
set -uo pipefail
[ $# -ge 2 ] || { sed -n 2,20p "$0"; exit 2; }
SLUG="$1"; shift
BASE="${APRENDIZADO_DIR:-$HOME/Claude/APRENDIZADO}/$SLUG"
NAVEGADOR="${NAVEGADOR:-chrome}"; MODELO="${WHISPER_MODELO:-small}"; IDIOMA="${IDIOMA:-en}"
mkdir -p "$BASE"/{transcricoes,vtt,audio}
REL="$BASE/RELATORIO.md"; echo "# Transcrição — $SLUG — $(date '+%Y-%m-%d %H:%M')" > "$REL"
command -v yt-dlp >/dev/null || { echo "falta yt-dlp: brew install yt-dlp" | tee -a "$REL"; exit 3; }

vtt_para_txt() {  # remove cabeçalho, tempos, tags e linhas repetidas da legenda automática
  sed -e '/^WEBVTT/d' -e '/^Kind:/d' -e '/^Language:/d' -e '/-->/d' -e 's/<[^>]*>//g' -e '/^[[:space:]]*$/d' "$1" \
    | awk '!visto[$0]++' | tr '\n' ' ' | fold -s -w 120
}

ids=()
for alvo in "$@"; do
  case "$alvo" in
    ytsearch*|http*playlist*) while IFS= read -r i; do ids+=("$i"); done < <(yt-dlp --flat-playlist --print id "$alvo" 2>/dev/null) ;;
    http*) ids+=("$(yt-dlp --print id --skip-download --ignore-no-formats-error "$alvo" 2>/dev/null | head -1)") ;;
    *) ids+=("$alvo") ;;
  esac
done

ok=0; falha=0; total=${#ids[@]}; atual=0
echo "▶ $total vídeo(s) — progresso abaixo; relatório em $REL"
for id in "${ids[@]}"; do
  [ -n "$id" ] || continue
  atual=$((atual+1))
  url="https://www.youtube.com/watch?v=$id"
  titulo=$(yt-dlp --print title --skip-download --ignore-no-formats-error "$url" 2>/dev/null | head -1 | tr '/:' '--')
  nome="${titulo:-$id} [$id]"
  echo "[$atual/$total] $(date '+%H:%M') ${titulo:-$id}"
  [ -s "$BASE/transcricoes/$nome.txt" ] && { echo "- ✅ já existe: $nome" >> "$REL"; echo "      já existia"; ok=$((ok+1)); continue; }
  feito=""
  for tentativa in "default" "cookies" "mweb" "web_safari"; do   # 27/09: só "cookies" funcionou no Mac (9/9)
    args=(--skip-download --ignore-no-formats-error --write-sub --write-auto-sub --sub-lang "$IDIOMA.*,$IDIOMA" --sub-format vtt -o "$BASE/vtt/$id.%(ext)s")
    case "$tentativa" in
      default) ;;
      cookies) args+=(--cookies-from-browser "$NAVEGADOR") ;;
      *) args+=(--extractor-args "youtube:player_client=$tentativa") ;;
    esac
    yt-dlp -q "${args[@]}" "$url" >/dev/null 2>&1
    v=$(ls "$BASE"/vtt/"$id".*.vtt 2>/dev/null | head -1)
    if [ -n "$v" ]; then vtt_para_txt "$v" > "$BASE/transcricoes/$nome.txt"; feito="legenda ($tentativa)"; break; fi
  done
  [ -n "$feito" ] && echo "      ✅ $feito"
  if [ -z "$feito" ] && command -v whisper >/dev/null && command -v ffmpeg >/dev/null; then
    echo "      sem legenda → baixando áudio e transcrevendo com whisper (lento: até ~1 h por aula)"
    for extra in "--extractor-args youtube:player_client=mweb" "--cookies-from-browser $NAVEGADOR"; do
      # shellcheck disable=SC2086
      yt-dlp -q -f "bestaudio/18" $extra -x --audio-format mp3 --postprocessor-args "ffmpeg:-ac 1 -ar 16000" \
        -o "$BASE/audio/$id.%(ext)s" "$url" >/dev/null 2>&1 && break
    done
    if [ -s "$BASE/audio/$id.mp3" ]; then
      whisper "$BASE/audio/$id.mp3" --model "$MODELO" --language "$IDIOMA" --output_format txt \
        --output_dir "$BASE/transcricoes" --fp16 False >/dev/null 2>&1 \
        && mv "$BASE/transcricoes/$id.txt" "$BASE/transcricoes/$nome.txt" 2>/dev/null && feito="whisper ($MODELO)"
    fi
  fi
  if [ -n "$feito" ]; then
    [ "${feito#whisper}" != "$feito" ] && echo "      ✅ $feito"
    ok=$((ok+1)); echo "- ✅ $nome — $feito — $(wc -w < "$BASE/transcricoes/$nome.txt") palavras" >> "$REL"
  else
    echo "      ❌ falhou (sem legenda e sem áudio; ver $REL)"
    falha=$((falha+1)); echo "- ❌ $nome — sem legenda e sem áudio (tentar logar no YouTube no $NAVEGADOR)" >> "$REL"
  fi
done
echo -e "\n**$ok ok · $falha falha** — transcrições em $BASE/transcricoes" | tee -a "$REL"
[ "$falha" -eq 0 ]
