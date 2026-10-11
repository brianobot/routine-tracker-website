#!/usr/bin/env python3
"""Tiny local server for cambridge-scholarship-plan.html.

Serves that one HTML file plus a small JSON state API, so checkboxes and
notes get saved to a file on this machine (cambridge-scholarship-data.json,
next to this script) instead of one browser's local storage. Any device on
the same Wi-Fi/LAN that opens the printed network URL sees the same,
constantly up to date progress.

Run:
    python3 cambridge-scholarship-server.py

Then open the "On your network" URL it prints from any device on the same
network (your phone included). Opening the .html file directly by
double-clicking it still works too, as a single-device, offline fallback —
it just won't sync.

Stdlib only, nothing to install. Ctrl+C to stop.
"""
import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML_FILE = HERE / "cambridge-scholarship-plan.html"
DATA_FILE = HERE / "cambridge-scholarship-data.json"
PORT = 8765

_lock = threading.Lock()


def read_state():
    with _lock:
        if DATA_FILE.exists():
            try:
                return json.loads(DATA_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}
        return {}


def write_state(state):
    with _lock:
        DATA_FILE.write_text(json.dumps(state), encoding="utf-8")


class Handler(BaseHTTPRequestHandler):
    # Only ever serves the one HTML file above and the /api/state endpoint —
    # deliberately not a general static file server, so nothing else on this
    # machine is reachable from the network through it.

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self):
        if not HTML_FILE.exists():
            self.send_error(
                404,
                f"{HTML_FILE.name} not found next to this script",
            )
            return
        body = HTML_FILE.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html", "/" + HTML_FILE.name):
            self._send_html()
        elif self.path == "/api/state":
            self._send_json(read_state())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/state":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            state = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json({"ok": False, "error": "invalid json"}, 400)
            return
        write_state(state)
        self._send_json({"ok": True})

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet; errors still raise normally


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))  # no packet actually sent; just picks the LAN interface
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    ip = local_ip()
    print("Cambridge Scholarship plan server running.")
    print(f"  On this Mac:      http://localhost:{PORT}/")
    print(f"  On your network:  http://{ip}:{PORT}/   <- open this on your phone")
    print(f"  Data saved to:    {DATA_FILE}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
