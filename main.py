#!/usr/bin/env python3
"""Serve a video with HTTP Range support and an HTML5 player."""
import argparse
import http.server
import os
import re
import tempfile
import threading
import urllib.request

PLAYER = """<!doctype html><html><head><meta charset="utf-8"><title>Stream</title>
<style>body{{margin:0;background:#0b0c10;color:#eee;font-family:system-ui,sans-serif;text-align:center}}
video{{width:min(96vw,900px);margin-top:4vh;background:#000;border-radius:8px}}</style></head>
<body><h1>Streaming Player</h1><video controls preload="metadata" src="/video"></video>
<p>HTTP Range requests keep seeking fast without downloading the whole file.</p></body></html>"""

class VideoHandler(http.server.BaseHTTPRequestHandler):
    file_path = None

    def _send(self, body: bytes, status=200, content_type="text/html; charset=utf-8", extra=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(PLAYER.encode()); return
        if self.path != "/video":
            self._send(b"not found", 404, "text/plain"); return
        size = os.path.getsize(self.file_path)
        range_header = self.headers.get("Range")
        if range_header:
            match = re.match(r"bytes=(\d*)-(\d*)", range_header)
            if not match:
                self._send(b"bad range", 416, "text/plain"); return
            start = int(match.group(1) or 0)
            end = int(match.group(2) or size - 1)
            end = min(end, size - 1)
            if start > end:
                self._send(b"bad range", 416, "text/plain"); return
            with open(self.file_path, "rb") as fh:
                fh.seek(start); chunk = fh.read(end - start + 1)
            self._send(chunk, 206, "video/mp4",
                       {"Content-Range": f"bytes {start}-{end}/{size}", "Accept-Ranges": "bytes"})
        else:
            with open(self.file_path, "rb") as fh:
                self._send(fh.read(), 200, "video/mp4", {"Accept-Ranges": "bytes"})

    def log_message(self, *args):
        pass

def demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "sample.mp4")
        with open(path, "wb") as fh:
            fh.write(b"\x00\x00\x00\x18ftypmp42" + bytes(range(256)) * 4000)
        handler = type("DemoHandler", (VideoHandler,), {"file_path": path})
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            with urllib.request.urlopen(base + "/") as response:
                page = response.read().decode()
            print("player page:", "<video" in page)
            request = urllib.request.Request(base + "/video", headers={"Range": "bytes=100-199"})
            with urllib.request.urlopen(request) as response:
                data = response.read()
                print("range status:", response.status, "| bytes:", len(data))
                print("content-range:", response.headers.get("Content-Range"))
            print("file size:", os.path.getsize(path))
        finally:
            server.shutdown(); server.server_close()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8003)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo or not args.file:
        demo(); return
    handler = type("BoundHandler", (VideoHandler,), {"file_path": args.file})
    server = http.server.ThreadingHTTPServer((args.host, args.port), handler)
    print(f"streaming {args.file} on http://{args.host}:{args.port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
