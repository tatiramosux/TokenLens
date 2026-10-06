"""Loopback-only local dashboard. No outbound requests, analytics or CDN assets."""
import argparse
import json
import shutil
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from tokenlens.store import Store
from .demo import seed

ROOT = Path(__file__).resolve().parent
DB = ROOT.parent / ".local" / "telemetry.sqlite3"

def suggestions(events):
    result = []
    if not events:
        return ["Ainda não há medições neste filtro. Inicie uma CLI pelos comandos do guia local."]
    if any(e["task"]["category"] == "unknown" for e in events):
        result.append("Classifique as medições sem categoria para comparar tarefas semelhantes. Nenhum prompt é analisado.")
    if any(e["task"]["complexity"] == "low" and e["execution"]["reasoning_level"] in ("high", "xhigh", "max", "ultra") for e in events):
        result.append("Há tarefas declaradas simples com esforço alto. Experimente esforço menor em uma tarefa equivalente e compare qualidade e consumo; isto não prova desperdício.")
    if any(e["usage"]["total_tokens"] is None for e in events):
        result.append("Algumas medições não informam todos os tokens. Totais exibidos são parciais; não representam cobrança ou saldo da conta.")
    result.append("Adequação do modelo: evidência insuficiente. Tokens e duração, isoladamente, não demonstram qualidade nem complexidade.")
    return result

def filtered(store, query):
    events = store.events(query.get("mode", ["real"])[0] == "demo")
    days = query.get("days", ["7"])[0]
    if days in ("1", "7", "30"):
        threshold = datetime.now(timezone.utc)-timedelta(days=int(days))
        events = [e for e in events if datetime.fromisoformat(e["timestamp"]) >= threshold]
    for key, path in (("provider", None), ("model", "execution"), ("category", "task")):
        value = query.get(key, [""])[0]
        if value:
            target = None if key == "model" and value == "__unknown__" else value
            events = [e for e in events if (e[path][key] if path else e[key]) == target]
    return events

def model_options(store, query):
    # Facets depend only on dataset/provider, not the selected model, period or category.
    events = store.events(query.get("mode", ["real"])[0] == "demo")
    provider = query.get("provider", [""])[0]
    if provider:
        events = [e for e in events if e["provider"] == provider]
    values = {e["execution"]["model"] for e in events}
    return sorted(v for v in values if v is not None) + (["__unknown__"] if None in values else [])

def make_handler(store):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def allowed(self):
            host = self.headers.get("Host", "")
            expected = f"127.0.0.1:{self.server.server_port}"
            origin = self.headers.get("Origin")
            return host == expected and origin in (None, "http://" + expected) and self.headers.get("Sec-Fetch-Site") != "cross-site"

        def reply(self, code, data, mime="application/json; charset=utf-8"):
            raw = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self):
            if not self.allowed():
                return self.reply(403, {"error": "Origem não permitida."})
            route = urlsplit(self.path)
            if route.path == "/api/events":
                try:
                    query = parse_qs(route.query)
                    models = model_options(store, query)
                    selected = query.get("model", [""])[0]
                    if selected and selected not in models:
                        selected = ""
                        query.pop("model", None)
                    events = filtered(store, query)
                    return self.reply(200, {"events": events, "suggestions": suggestions(events), "models": models, "selected_model": selected})
                except Exception:
                    return self.reply(500, {"error": "Não foi possível ler as métricas."})
            if route.path == "/api/status":
                actual = store.events(False)
                return self.reply(200, {"providers": [{"provider": p, "installed": bool(shutil.which(cmd)), "last_event": next((e["timestamp"] for e in actual if e["provider"] == p), None), "integration": state} for p, cmd, state in (("codex", "codex", "Execução instrumentada"), ("claude_code", "claude", "Execução instrumentada / contexto interativo"), ("antigravity", "antigravity", "Integração automática pendente"))]})
            assets = {"/": ("index.html", "text/html; charset=utf-8"), "/app.js": ("app.js", "text/javascript; charset=utf-8"), "/style.css": ("style.css", "text/css; charset=utf-8"), "/favicon.svg": ("favicon.svg", "image/svg+xml"), "/chevron.svg": ("chevron.svg", "image/svg+xml")}
            assets.update({"/theme.css": ("theme.css", "text/css; charset=utf-8"), "/dropdown.js": ("dropdown.js", "text/javascript; charset=utf-8")})
            assets.update({"/timeline.js": ("timeline.js", "text/javascript; charset=utf-8"), "/chart.js": ("chart.js", "text/javascript; charset=utf-8")})
            if route.path in assets:
                name, mime = assets[route.path]
                return self.reply(200, (ROOT/"static"/name).read_bytes(), mime)
            return self.reply(404, {"error": "Não encontrado."})

        def do_POST(self):
            if not self.allowed():
                return self.reply(403, {"error": "Origem não permitida."})
            if self.path != "/api/label" or self.headers.get("Content-Type") != "application/json":
                return self.reply(404, {"error": "Não encontrado."})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 1024:
                    raise ValueError()
                data = json.loads(self.rfile.read(size))
                if set(data) != {"event_id", "category", "complexity"}:
                    raise ValueError()
                if not store.label(**data):
                    return self.reply(404, {"error": "Medição não encontrada."})
                return self.reply(200, {"ok": True})
            except Exception:
                return self.reply(400, {"error": "Classificação inválida; conteúdo omitido."})
    return Handler

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", type=Path, default=DB)
    args = parser.parse_args()
    store = Store(args.db)
    seed(store)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(store))
    print(f"TokenLens Lab: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
