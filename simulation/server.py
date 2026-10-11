"""Minimal authenticated HTTP gateway for the IgnisPyro simulation server.

No fire spread calculation is performed here. Keep behind TLS reverse proxy and
private network; set IGNISPYRO_SIM_TOKEN before starting.
"""
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .contract import ContractError, validate_weather

MAX_BODY = 65536

class Handler(BaseHTTPRequestHandler):
    def respond(self, code, body):
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path == "/health":
            return self.respond(200, {"status": "ok", "service": "ignispyro-simulation-gateway", "engine": "not_configured"})
        self.respond(404, {"error": "not_found"})

    def do_POST(self):
        if self.path != "/api/v1/weather/validate":
            return self.respond(404, {"error": "not_found"})
        token = os.environ.get("IGNISPYRO_SIM_TOKEN", "")
        auth = self.headers.get("Authorization", "")
        if not token or not hmac.compare_digest(auth, "Bearer " + token):
            return self.respond(401, {"error": "unauthorized"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return self.respond(400, {"error": "invalid_length"})
        if not 0 < size <= MAX_BODY:
            return self.respond(413, {"error": "invalid_body_size"})
        try:
            body = json.loads(self.rfile.read(size))
            normalized = validate_weather(body)
        except (ValueError, UnicodeDecodeError, ContractError) as exc:
            return self.respond(422, {"error": str(exc)})
        return self.respond(200, {"valid": True, "data": normalized, "simulation_started": False})

def main():
    if not os.environ.get("IGNISPYRO_SIM_TOKEN"):
        raise SystemExit("IGNISPYRO_SIM_TOKEN must be set")
    host = os.environ.get("IGNISPYRO_SIM_HOST", "127.0.0.1")
    port = int(os.environ.get("IGNISPYRO_SIM_PORT", "8102"))
    ThreadingHTTPServer((host, port), Handler).serve_forever()

if __name__ == "__main__":
    main()
