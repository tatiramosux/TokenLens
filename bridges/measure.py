"""Explicit, non-interactive measurement. No raw stream is persisted or printed."""
import argparse
import json
import shutil
import subprocess
import sys
import threading
import sqlite3
from pathlib import Path
from tokenlens.adapters import ADAPTERS
from tokenlens.contract import CATEGORIES, COMPLEXITIES, MODELS
from tokenlens.store import Store

DB = Path(__file__).resolve().parents[1]/".local"/"telemetry.sqlite3"

def collect(stream, adapter):
    # Bound memory and discard oversized lines without buffering their remainder.
    while True:
        raw = stream.readline(1024*1024+1)
        if not raw:
            break
        if len(raw) > 1024*1024:
            while raw and not raw.endswith(b"\n"):
                raw = stream.readline(65536)
            continue
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                yield from adapter.normalize(payload)
        except (ValueError, TypeError, KeyError, RecursionError):
            continue

def main():
    p = argparse.ArgumentParser(description="Mede uma execução não interativa; a resposta da IA é descartada, não é um substituto do terminal interativo.")
    p.add_argument("provider", choices=["codex", "claude_code"])
    p.add_argument("--category", choices=CATEGORIES, default="unknown")
    p.add_argument("--complexity", choices=COMPLEXITIES, default="unknown")
    p.add_argument("--model", choices=sorted(m for m in MODELS if m))
    p.add_argument("--db", type=Path, default=DB)
    p.add_argument("--smoke", action="store_true", help="Teste sintético curto, sem ferramentas; utiliza a autenticação da CLI.")
    p.add_argument("--timeout", type=int, default=120, help="Limite da execução em segundos.")
    args = p.parse_args()
    binary = shutil.which("codex" if args.provider == "codex" else "claude")
    if not binary:
        print("CLI não encontrada no PATH.", file=sys.stderr)
        return 2
    if args.provider == "codex":
        command = [binary, "exec", "--json", "--ephemeral", "--skip-git-repo-check", "--sandbox", "read-only", "-"]
        if args.smoke:
            command[2:2] = ["--ignore-user-config", "-c", "mcp_servers={}"]
    else:
        command = [binary, "-p", "--output-format", "stream-json", "--verbose", "--no-session-persistence", "--tools", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}']
        if args.smoke:
            command += ["--setting-sources", "", "--system-prompt", "Reply briefly. Do not use tools."]
    if args.model:
        command += ["--model", args.model]
    count = 0
    print("TokenLens: medindo; somente métricas serão exibidas.", file=sys.stderr)
    try:
        store = Store(args.db)
        with subprocess.Popen(command, stdin=subprocess.PIPE if args.smoke else None, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as proc:
            timer = threading.Timer(max(1, args.timeout), proc.kill)
            timer.daemon = True
            timer.start()
            if args.smoke:
                proc.stdin.write(b"Reply only OK. Do not read files or use tools.\n")
                proc.stdin.close()
            for event in collect(proc.stdout, ADAPTERS[args.provider]):
                event["task"] = {"category": args.category, "complexity": args.complexity, "classification_source": "manual" if (args.category, args.complexity) != ("unknown", "unknown") else "unknown"}
                # A requested model is not proof of the effective model: leave unknown on Codex.
                store.put(event)
                count += 1
            status = proc.wait()
            timer.cancel()
    except (OSError, KeyboardInterrupt, sqlite3.Error, ValueError):
        print("Execução interrompida ou indisponível; detalhes omitidos.", file=sys.stderr)
        return 2
    if count == 0:
        # Never manufacture a zero-token usage event when the source did not report usage.
        print("Nenhuma métrica recebida. Verifique login e conectividade diretamente na CLI.", file=sys.stderr)
    print(f"Medições salvas: {count}. Saída da CLI: {status}.")
    return status or (0 if count else 3)

if __name__ == "__main__":
    raise SystemExit(main())
