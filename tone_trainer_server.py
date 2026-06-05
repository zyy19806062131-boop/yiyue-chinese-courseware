#!/usr/bin/env python3
import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_PATHS = (
    ROOT / "trainer_data.private.json",
    ROOT / "trainer_data.json",
)
CODES_PATH = Path(os.environ.get("ACCESS_CODES_PATH", ROOT / "access_codes.private.json"))


def default_data_path():
    configured = os.environ.get("TRAINER_DATA_PATH")
    if configured:
        return Path(configured)

    for path in DEFAULT_DATA_PATHS:
        if path.exists():
            return path

    return DEFAULT_DATA_PATHS[-1]


def load_json(path, env_key):
    raw = os.environ.get(env_key)
    if raw:
        return json.loads(raw)

    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def build_payload(code):
    data = load_json(default_data_path(), "TRAINER_DATA_JSON")
    access_codes = load_json(CODES_PATH, "ACCESS_CODES_JSON")
    profile = access_codes.get(code)
    if not profile:
        return None

    allowed = profile.get("decks")
    all_decks = data.get("decks", [])
    if allowed == "all":
        decks = all_decks
    else:
        allowed_set = set(allowed or [])
        decks = [deck for deck in all_decks if deck.get("id") in allowed_set]

    allowed_sentence_ids = {
        sentence.get("id")
        for deck in decks
        for sentence in deck.get("sents", [])
        if sentence.get("id")
    }
    audio = {
        sentence_id: voices
        for sentence_id, voices in data.get("audio", {}).items()
        if sentence_id in allowed_sentence_ids
    }

    return {
        "label": profile.get("label", "ACCESS GRANTED"),
        "decks": decks,
        "audio": audio,
    }


class ToneTrainerHandler(BaseHTTPRequestHandler):
    server_version = "ToneTrainer/1.0"

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_static(self, target, include_body=True):
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if target.suffix in {".html", ".js", ".css"}:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/login":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "接口不存在"})
            return

        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 4096:
            self.send_json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "请求太大"})
            return

        try:
            raw = self.rfile.read(length).decode("utf-8")
            body = json.loads(raw or "{}")
        except Exception:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "请求格式不对"})
            return

        code = str(body.get("code", "")).strip()
        payload = build_payload(code)
        if not payload:
            self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "口令不对"})
            return

        self.send_json(HTTPStatus.OK, payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        request_path = unquote(parsed.path)
        if request_path == "/healthz":
            self.send_json(HTTPStatus.OK, {"ok": True})
            return

        self.serve_path(request_path)

    def do_HEAD(self):
        parsed = urlparse(self.path)
        request_path = unquote(parsed.path)
        if request_path == "/healthz":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        self.serve_path(request_path, include_body=False)

    def serve_path(self, request_path, include_body=True):
        if request_path == "/":
            request_path = "/tone_trainer.html"

        target = (ROOT / request_path.lstrip("/")).resolve()
        if (
            ROOT not in target.parents
            or not target.is_file()
            or target.name.endswith(".private.json")
            or ".private." in target.name
        ):
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        self.send_static(target, include_body=include_body)


def main():
    port = int(os.environ.get("PORT", "8765"))
    host = os.environ.get("HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), ToneTrainerHandler)
    print(f"Tone trainer backend running at http://{host}:{port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
