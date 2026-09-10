#!/usr/bin/env bash
# Testa os hooks simulando máquinas sem jq, sem node e sem nada.
# Usado pelo bootstrap (--teste) e pelo workflow de saúde semanal.
set -uo pipefail
cd "$(dirname "$0")"
export CLAUDE_PROJECT_DIR="$(cd ../.. && pwd)"
FALHAS=0

echo "── sintaxe ──"
for h in *.sh; do bash -n "$h" && echo "  ✓ $h" || { echo "  ✗ $h"; FALHAS=$((FALHAS+1)); }; done

PY=$(command -v python3 || true); NODE=$(command -v node || true)
if [ -z "$PY" ]; then echo "python3 ausente: só sintaxe verificada."; exit $FALHAS; fi

T=$(mktemp -d)
cat > "$T/v.py" <<'PYEOF'
import sys, json
esp = sys.argv[1]; raw = sys.stdin.read().strip()
def r(ok, m): print(("  ✓ " if ok else "  ✗ ") + m); sys.exit(0 if ok else 1)
if raw == "": r(esp in ("vazio",), "vazio (permitido)")
try: h = json.loads(raw).get("hookSpecificOutput", {})
except Exception as e: r(False, f"JSON inválido: {e}")
if esp == "ctx":   r(len(h.get("additionalContext","")) > 1000, f"ctx {len(h.get('additionalContext',''))} chars")
if esp == "deny":  r(h.get("permissionDecision") == "deny", f"deny: {h.get('permissionDecisionReason','')[:36]}")
if esp == "nulo":  r(h == {}, "{} (degradação silenciosa)")
if esp == "json":  r(True, "JSON válido")
if esp == "recall": r("additionalContext" in h and "MEMÓRIA" in h["additionalContext"], f"recall {len(h.get('additionalContext',''))} chars")
PYEOF
montar() { rm -rf "$T/bin"; mkdir -p "$T/bin"
  for d in /usr/bin /bin; do for f in "$d"/*; do n=$(basename "$f")
    case " $1 " in *" $n "*) continue;; esac; ln -sf "$f" "$T/bin/$n" 2>/dev/null; done; done
  case " $1 " in *" node "*) ;; *) [ -n "$NODE" ] && ln -sf "$NODE" "$T/bin/node";; esac
  case " $1 " in *" python3 "*) ;; *) ln -sf "$PY" "$T/bin/python3";; esac; }
c() { "$@" || FALHAS=$((FALHAS+1)); }
P="rm -rf"; F="--for""ce"
RM="{\"tool_input\":{\"command\":\"$P /\"}}"; FP="{\"tool_input\":{\"command\":\"git push $F origin main\"}}"
OK='{"tool_input":{"command":"ls"}}'; PR='{"prompt":"lançar infoproduto sobre joelho com pix e anuncio"}'

for cen in "jq" "jq node"; do
  montar "$cen"; echo "── sem: $cen ──"
  c sh -c "PATH='$T/bin' bash ./carregar-cerebro.sh | '$PY' '$T/v.py' ctx"
  c sh -c "echo '$RM' | PATH='$T/bin' bash ./guarda.sh | '$PY' '$T/v.py' deny"
  c sh -c "echo '$FP' | PATH='$T/bin' bash ./guarda.sh | '$PY' '$T/v.py' deny"
  c sh -c "echo '$OK' | PATH='$T/bin' bash ./guarda.sh | '$PY' '$T/v.py' vazio"
  c sh -c "echo '$PR' | PATH='$T/bin' bash ./recall.sh | '$PY' '$T/v.py' recall"
  c sh -c "PATH='$T/bin' bash ./lembrar-memoria.sh | '$PY' '$T/v.py' json"
done
montar "jq node python3"; echo "── sem nada ──"
c sh -c "PATH='$T/bin' bash ./carregar-cerebro.sh | '$PY' '$T/v.py' nulo"
c sh -c "echo '$RM' | PATH='$T/bin' bash ./guarda.sh | '$PY' '$T/v.py' vazio"
c sh -c "echo '$PR' | PATH='$T/bin' bash ./recall.sh | '$PY' '$T/v.py' nulo"
rm -rf "$T"
echo "FALHAS: $FALHAS"; exit $FALHAS
