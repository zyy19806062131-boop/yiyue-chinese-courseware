#!/usr/bin/env python3
import base64
import hashlib
import hmac
import html
import json
import mimetypes
import os
import secrets
import shutil
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


ROOT = Path(__file__).resolve().parent
RULES_PATH = ROOT / "data" / "access_rules.json"
SESSION_SECRET = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin2026")
SESSION_COOKIE = "courseware_session"

DEFAULT_DATA_PATHS = (
    ROOT / "trainer_data.private.json",
    ROOT / "trainer_data.json",
)
CODES_PATH = Path(os.environ.get("ACCESS_CODES_PATH", ROOT / "access_codes.private.json"))

PUBLIC_HTML = {
    "/",
    "/index.html",
}
PUBLIC_PREFIXES = (
    "/assets/",
)


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


def password_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def safe_json_load(path, fallback):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return fallback


def read_rules():
    data = safe_json_load(RULES_PATH, {"lessons": []})
    lessons = []
    for item in data.get("lessons", []):
        path = normalize_lesson_path(item.get("path", ""))
        if not path:
            continue
        lessons.append(
            {
                "id": item.get("id") or path.replace("/", "-").replace(".html", ""),
                "title": item.get("title") or path,
                "path": path,
                "enabled": bool(item.get("enabled", True)),
                "password_hashes": [
                    value
                    for value in item.get("password_hashes", [])
                    if isinstance(value, str) and value
                ],
            }
        )
    return {"lessons": lessons}


def write_rules(rules):
    RULES_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = RULES_PATH.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(RULES_PATH)


def normalize_lesson_path(path):
    path = str(path or "").strip().lstrip("/")
    if not path.endswith(".html"):
        return ""
    if ".." in Path(path).parts:
        return ""
    return path


def discover_html_lessons():
    discovered = []
    for target in sorted(ROOT.rglob("*.html")):
        if ".git" in target.parts:
            continue
        rel = target.relative_to(ROOT).as_posix()
        request_path = "/" + rel
        if request_path in PUBLIC_HTML:
            continue
        title = rel
        try:
            head = target.read_text(encoding="utf-8", errors="ignore")[:4096]
            start = head.lower().find("<title>")
            end = head.lower().find("</title>")
            if 0 <= start < end:
                title = html.unescape(head[start + 7 : end]).strip() or rel
        except OSError:
            pass
        discovered.append({"id": rel.replace("/", "-").replace(".html", ""), "title": title, "path": rel})
    return discovered


def merged_rules():
    rules = read_rules()
    by_path = {lesson["path"]: lesson for lesson in rules["lessons"]}
    for item in discover_html_lessons():
        if item["path"] not in by_path:
            by_path[item["path"]] = {
                **item,
                "enabled": True,
                "password_hashes": [],
            }
    return {"lessons": list(by_path.values())}


def lesson_for_request(request_path):
    rel = request_path.lstrip("/")
    for lesson in merged_rules()["lessons"]:
        if lesson["path"] == rel:
            return lesson
    return None


def sign_session(payload):
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    body = base64.urlsafe_b64encode(raw).decode("ascii")
    sig = hmac.new(SESSION_SECRET.encode("utf-8"), body.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def parse_session(cookie_header):
    cookie = SimpleCookie(cookie_header or "")
    morsel = cookie.get(SESSION_COOKIE)
    if not morsel:
        return {}
    value = morsel.value
    if "." not in value:
        return {}
    body, sig = value.rsplit(".", 1)
    expected = hmac.new(SESSION_SECRET.encode("utf-8"), body.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return {}
    try:
        return json.loads(base64.urlsafe_b64decode(body.encode("ascii")).decode("utf-8"))
    except Exception:
        return {}


def session_cookie(payload):
    return f"{SESSION_COOKIE}={sign_session(payload)}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000"


def is_public_path(request_path):
    if request_path in PUBLIC_HTML:
        return True
    return any(request_path.startswith(prefix) for prefix in PUBLIC_PREFIXES)


def error_page(title, message):
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#f6f4ef;color:#1f2933;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
    main{{width:min(520px,calc(100% - 36px));background:#fff;border:1px solid #ddd7ca;border-radius:8px;padding:28px;box-shadow:0 18px 50px rgba(0,0,0,.08)}}
    h1{{font-size:28px;margin:0 0 12px}} p{{line-height:1.7;color:#59636f}} a{{color:#8b3dff;text-decoration:none;font-weight:700}}
  </style>
</head>
<body><main><h1>{html.escape(title)}</h1><p>{html.escape(message)}</p><p><a href="/">返回首页</a></p></main></body>
</html>"""


def lesson_login_page(lesson, error=""):
    title = lesson["title"]
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>访问课程 · {html.escape(title)}</title>
  <style>
    body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#f7f3ea;color:#1f2933;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
    main{{width:min(560px,calc(100% - 36px));background:#fff;border:1px solid #ded6c8;border-radius:8px;padding:30px;box-shadow:0 18px 60px rgba(64,54,38,.12)}}
    .eyebrow{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#8b6f47;font-weight:800}}
    h1{{font-size:28px;line-height:1.25;margin:10px 0 14px}} p{{line-height:1.7;color:#5b6570}}
    label{{display:block;font-weight:800;margin:22px 0 8px}} input{{box-sizing:border-box;width:100%;height:48px;border:1px solid #bfb7aa;border-radius:6px;padding:0 14px;font-size:18px}}
    button{{height:46px;margin-top:18px;border:0;border-radius:6px;background:#202124;color:#fff;font-weight:800;padding:0 18px;cursor:pointer}}
    .error{{margin-top:14px;color:#b42318;font-weight:700}} .row{{display:flex;gap:14px;align-items:center;justify-content:space-between;flex-wrap:wrap}}
    a{{color:#8b3dff;text-decoration:none;font-weight:700}}
  </style>
</head>
<body>
  <main>
    <div class="eyebrow">Courseware Access</div>
    <h1>{html.escape(title)}</h1>
    <p>请输入老师设置的访问密码。</p>
    <form method="post" action="/api/lesson-login">
      <input type="hidden" name="path" value="{html.escape(lesson["path"])}">
      <label for="password">访问密码</label>
      <input id="password" name="password" type="password" autocomplete="current-password" autofocus>
      <div class="row"><button type="submit">打开课件</button><a href="/">返回首页</a></div>
      {f'<div class="error">{html.escape(error)}</div>' if error else ''}
    </form>
  </main>
</body>
</html>"""


def admin_page():
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>课件访问后台</title>
  <style>
    :root{color-scheme:light}
    body{margin:0;background:#f6f7f9;color:#1f2933;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
    header{position:sticky;top:0;background:#fff;border-bottom:1px solid #d9dee7;padding:18px 28px;display:flex;align-items:center;justify-content:space-between;gap:18px}
    h1{font-size:24px;margin:0} h2{font-size:18px;margin:0 0 12px}
    main{max-width:1080px;margin:0 auto;padding:26px}
    .panel{background:#fff;border:1px solid #d9dee7;border-radius:8px;padding:20px;margin-bottom:18px}
    label{display:block;font-size:13px;font-weight:800;margin:14px 0 6px;color:#344054}
    input,textarea{box-sizing:border-box;width:100%;border:1px solid #b8c0cc;border-radius:6px;padding:10px 12px;font:inherit;background:#fff}
    textarea{min-height:76px;resize:vertical}
    button{height:40px;border:0;border-radius:6px;background:#202124;color:#fff;font-weight:800;padding:0 14px;cursor:pointer}
    button.secondary{background:#eef1f5;color:#1f2933}
    .grid{display:grid;grid-template-columns:1fr;gap:14px}
    .lesson{background:#fff;border:1px solid #d9dee7;border-radius:8px;padding:18px}
    .meta{color:#667085;font-size:13px;margin-bottom:8px;word-break:break-all}
    .row{display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
    .check{display:flex;align-items:center;gap:8px;font-weight:800}.check input{width:auto}
    .status{font-weight:800}.ok{color:#087443}.bad{color:#b42318}
    .hidden{display:none}
  </style>
</head>
<body>
  <header><h1>课件访问后台</h1><button class="secondary" id="refreshBtn">刷新</button></header>
  <main>
    <section class="panel" id="loginPanel">
      <h2>管理员登录</h2>
      <label for="adminPassword">管理员密码</label>
      <input id="adminPassword" type="password" autocomplete="current-password">
      <button id="loginBtn">登录</button>
      <p class="status bad" id="loginStatus"></p>
    </section>
    <section class="panel hidden" id="editorPanel">
      <div class="row">
        <div>
          <h2>课程密码</h2>
          <p class="meta">每行或逗号分隔一个访问密码。留空表示保留当前密码；输入新内容会替换这门课的旧密码。</p>
        </div>
        <button id="saveBtn">保存全部</button>
      </div>
      <p class="status" id="saveStatus"></p>
      <div class="grid" id="lessons"></div>
    </section>
  </main>
  <script>
    const loginPanel = document.getElementById('loginPanel');
    const editorPanel = document.getElementById('editorPanel');
    const lessonsEl = document.getElementById('lessons');
    const saveStatus = document.getElementById('saveStatus');

    async function api(path, options = {}) {
      const response = await fetch(path, {
        ...options,
        headers: {'Content-Type': 'application/json', ...(options.headers || {})}
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || '请求失败');
      return data;
    }

    async function loadRules() {
      const data = await api('/api/admin/rules');
      loginPanel.classList.add('hidden');
      editorPanel.classList.remove('hidden');
      lessonsEl.innerHTML = '';
      for (const lesson of data.lessons) {
        const card = document.createElement('div');
        card.className = 'lesson';
        card.dataset.path = lesson.path;
        card.innerHTML = `
          <div class="row">
            <h2></h2>
            <label class="check"><input type="checkbox" class="enabled"> 启用密码保护</label>
          </div>
          <div class="meta"></div>
          <label>显示名称</label>
          <input class="title">
          <label>替换访问密码</label>
          <textarea class="passwords" placeholder="留空保留当前 ${lesson.passwordCount} 个密码"></textarea>
        `;
        card.querySelector('h2').textContent = lesson.title;
        card.querySelector('.meta').textContent = `${lesson.path} · 当前 ${lesson.passwordCount} 个密码`;
        card.querySelector('.title').value = lesson.title;
        card.querySelector('.enabled').checked = lesson.enabled;
        lessonsEl.appendChild(card);
      }
    }

    document.getElementById('loginBtn').addEventListener('click', async () => {
      const password = document.getElementById('adminPassword').value;
      try {
        await api('/api/admin-login', {method: 'POST', body: JSON.stringify({password})});
        document.getElementById('loginStatus').textContent = '';
        await loadRules();
      } catch (error) {
        document.getElementById('loginStatus').textContent = error.message;
      }
    });

    document.getElementById('refreshBtn').addEventListener('click', () => loadRules().catch(() => {}));

    document.getElementById('saveBtn').addEventListener('click', async () => {
      const lessons = [...document.querySelectorAll('.lesson')].map(card => ({
        path: card.dataset.path,
        title: card.querySelector('.title').value.trim(),
        enabled: card.querySelector('.enabled').checked,
        passwords: card.querySelector('.passwords').value
      }));
      try {
        saveStatus.className = 'status';
        saveStatus.textContent = '保存中...';
        await api('/api/admin/rules', {method: 'POST', body: JSON.stringify({lessons})});
        saveStatus.className = 'status ok';
        saveStatus.textContent = '已保存';
        await loadRules();
      } catch (error) {
        saveStatus.className = 'status bad';
        saveStatus.textContent = error.message;
      }
    });

    loadRules().catch(() => {});
  </script>
</body>
</html>"""


class CoursewareHandler(BaseHTTPRequestHandler):
    server_version = "CoursewareServer/2.0"

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))

    def send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, status, body, extra_headers=None):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(encoded)

    def send_static(self, target, include_body=True):
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(target.stat().st_size))
        if target.suffix in {".html", ".js", ".css", ".json"}:
            self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if include_body:
            with target.open("rb") as f:
                shutil.copyfileobj(f, self.wfile, length=1024 * 1024)

    def read_body(self, limit=65536):
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > limit:
            raise ValueError("请求太大")
        raw = self.rfile.read(length)
        content_type = self.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.loads(raw.decode("utf-8") or "{}")
        parsed = parse_qs(raw.decode("utf-8"))
        return {key: values[-1] for key, values in parsed.items()}

    def current_session(self):
        return parse_session(self.headers.get("Cookie"))

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/login":
                self.handle_trainer_login()
            elif parsed.path == "/api/lesson-login":
                self.handle_lesson_login()
            elif parsed.path == "/api/admin-login":
                self.handle_admin_login()
            elif parsed.path == "/api/admin/rules":
                self.handle_admin_save()
            else:
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "接口不存在"})
        except ValueError as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
        except Exception as exc:
            self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": f"服务器错误: {exc}"})

    def handle_trainer_login(self):
        body = self.read_body(limit=4096)
        code = str(body.get("code", "")).strip()
        payload = build_payload(code)
        if not payload:
            self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "口令不对"})
            return
        self.send_json(HTTPStatus.OK, payload)

    def handle_lesson_login(self):
        body = self.read_body(limit=8192)
        path = normalize_lesson_path(body.get("path", ""))
        password = str(body.get("password", ""))
        lesson = lesson_for_request("/" + path)
        if not lesson:
            self.send_html(HTTPStatus.NOT_FOUND, error_page("没有找到课件", "这个课件路径不存在。"))
            return
        if not lesson.get("password_hashes"):
            self.send_html(HTTPStatus.FORBIDDEN, lesson_login_page(lesson, "这门课还没有设置访问密码。"))
            return
        if password_hash(password) not in lesson["password_hashes"]:
            self.send_html(HTTPStatus.UNAUTHORIZED, lesson_login_page(lesson, "访问密码不正确。"))
            return

        session = self.current_session()
        allowed = set(session.get("lessons", []))
        allowed.add(lesson["path"])
        session["lessons"] = sorted(allowed)
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", "/" + lesson["path"])
        self.send_header("Set-Cookie", session_cookie(session))
        self.send_header("Content-Length", "0")
        self.end_headers()

    def handle_admin_login(self):
        body = self.read_body(limit=4096)
        password = str(body.get("password", ""))
        if not hmac.compare_digest(password, ADMIN_PASSWORD):
            self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "管理员密码不正确"})
            return
        session = self.current_session()
        session["admin"] = True
        self.send_json(HTTPStatus.OK, {"ok": True}, {"Set-Cookie": session_cookie(session)})

    def require_admin(self):
        if self.current_session().get("admin") is True:
            return True
        self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "需要管理员登录"})
        return False

    def handle_admin_save(self):
        if not self.require_admin():
            return
        body = self.read_body(limit=262144)
        if not isinstance(body.get("lessons"), list) or not body["lessons"]:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": "没有收到课程规则"})
            return
        existing = {lesson["path"]: lesson for lesson in merged_rules()["lessons"]}
        lessons = []
        for item in body.get("lessons", []):
            path = normalize_lesson_path(item.get("path", ""))
            if not path:
                continue
            old = existing.get(path, {})
            raw_passwords = str(item.get("passwords", "")).replace(",", "\n").splitlines()
            cleaned_passwords = [value.strip() for value in raw_passwords if value.strip()]
            if cleaned_passwords:
                hashes = [password_hash(value) for value in cleaned_passwords]
            else:
                hashes = old.get("password_hashes", [])
            lessons.append(
                {
                    "id": old.get("id") or path.replace("/", "-").replace(".html", ""),
                    "title": str(item.get("title") or old.get("title") or path).strip(),
                    "path": path,
                    "enabled": bool(item.get("enabled", True)),
                    "password_hashes": hashes,
                }
            )
        write_rules({"lessons": lessons})
        self.send_json(HTTPStatus.OK, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)
        request_path = unquote(parsed.path)
        if request_path == "/healthz":
            self.send_json(HTTPStatus.OK, {"ok": True})
            return
        if request_path == "/admin":
            self.send_html(HTTPStatus.OK, admin_page())
            return
        if request_path == "/api/admin/rules":
            self.handle_admin_rules()
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

    def handle_admin_rules(self):
        if not self.require_admin():
            return
        payload = []
        for lesson in merged_rules()["lessons"]:
            payload.append(
                {
                    "id": lesson["id"],
                    "title": lesson["title"],
                    "path": lesson["path"],
                    "enabled": lesson["enabled"],
                    "passwordCount": len(lesson.get("password_hashes", [])),
                }
            )
        self.send_json(HTTPStatus.OK, {"lessons": payload})

    def serve_path(self, request_path, include_body=True):
        if request_path == "/":
            request_path = "/index.html"

        target = (ROOT / request_path.lstrip("/")).resolve()
        if (
            ROOT not in target.parents
            or not target.is_file()
            or target.name.endswith(".private.json")
            or ".private." in target.name
            or target.name == "access_rules.json"
        ):
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        if target.suffix == ".html" and not is_public_path(request_path):
            lesson = lesson_for_request(request_path)
            if not lesson:
                self.send_html(HTTPStatus.FORBIDDEN, error_page("课件未登记", "请先在管理员后台登记这门课。"))
                return
            if lesson.get("enabled", True):
                session = self.current_session()
                if lesson["path"] not in set(session.get("lessons", [])):
                    self.send_html(HTTPStatus.OK, lesson_login_page(lesson))
                    return

        self.send_static(target, include_body=include_body)


def main():
    port = int(os.environ.get("PORT", "8765"))
    host = os.environ.get("HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), CoursewareHandler)
    print(f"Courseware server running at http://{host}:{port}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
