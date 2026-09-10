#!/usr/bin/env bash
# Utilitários de JSON para os hooks — SEM dependência obrigatória de jq.
#
# macOS não traz jq. Se o hook quebrar por isso, o cérebro não carrega e a
# sessão segue "burra" em silêncio. Por isso a cadeia: jq → node → python3.
# Sem nenhum dos três, devolve '{}' e nunca derruba a sessão.
#
# Uso:  . "$(dirname "$0")/_json.sh"

# json_hook <evento> [<campo> <valor>]...   → imprime o JSON de saída do hook
json_hook() {
  local ev="$1"; shift
  if command -v jq >/dev/null 2>&1; then
    jq -n --arg e "$ev" \
      '$ARGS.positional as $p
       | {hookSpecificOutput: ({hookEventName: $e}
           + ([range(0; $p|length; 2)] | map({key: $p[.], value: $p[.+1]}) | from_entries))}' \
      --args "$@"
  elif command -v node >/dev/null 2>&1; then
    node -e '
      let a = process.argv.slice(1);
      if (a[0] === "--") a = a.slice(1);
      const o = { hookEventName: a[0] };
      for (let i = 1; i < a.length; i += 2) o[a[i]] = a[i + 1];
      console.log(JSON.stringify({ hookSpecificOutput: o }));' -- "$ev" "$@"
  elif command -v python3 >/dev/null 2>&1; then
    python3 -c '
import sys, json
a = sys.argv[1:]
o = {"hookEventName": a[0]}
for i in range(1, len(a), 2): o[a[i]] = a[i + 1]
print(json.dumps({"hookSpecificOutput": o}))' "$ev" "$@"
  else
    echo '{}'
  fi
}

# json_get_field <caminho.pontuado>  ← stdin (JSON do hook)  → imprime o valor
json_get_field() {
  local path="$1"
  if command -v jq >/dev/null 2>&1; then
    jq -r --arg p "$path" 'getpath($p | split(".")) // "" | tostring'
  elif command -v node >/dev/null 2>&1; then
    P="$path" node -e '
      let d = "";
      process.stdin.on("data", c => d += c).on("end", () => {
        try {
          const v = process.env.P.split(".").reduce((o, k) => (o ?? {})[k], JSON.parse(d));
          console.log(v == null ? "" : String(v));
        } catch { console.log(""); }
      });'
  elif command -v python3 >/dev/null 2>&1; then
    P="$path" python3 -c '
import sys, json, os
try:
    v = json.load(sys.stdin)
    for k in os.environ["P"].split("."): v = (v or {}).get(k)
    print("" if v is None else v)
except Exception: print("")'
  else
    cat >/dev/null; echo ""
  fi
}

# compatibilidade
json_get_command() { json_get_field tool_input.command; }
