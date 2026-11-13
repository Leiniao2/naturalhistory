#!/usr/bin/env python3
"""Natural History concept editor: a local web UI for the game's JSON data.

    python3 tools/concept-editor/server.py            # opens http://127.0.0.1:8765
    python3 tools/concept-editor/server.py --port 9000 --no-browser

Reads and writes Assets/Resources/Data/<dataset>.json. Every save first copies the previous
version to tools/concept-editor/backups/ (outside Assets/, so Unity never imports the backups).
Standard library only; listens on localhost only.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
import webbrowser
from datetime import datetime
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

EDITOR_DIR = Path(__file__).resolve().parent
PROJECT_DIR = EDITOR_DIR.parent.parent
DATA_DIR = PROJECT_DIR / "Assets" / "Resources" / "Data"
BACKUP_DIR = EDITOR_DIR / "backups"
STATIC_DIR = EDITOR_DIR / "web"

# Only these files can be read or written through the API
DATASETS = ["ages", "climate_history", "genes", "realms", "morphology", "ethology", "species", "factions"]
MAX_BACKUPS_PER_DATASET = 50


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, fmt, *args):
        if "/api/" in (args[0] if args else ""):
            sys.stderr.write("[editor] " + (fmt % args) + "\n")

    def end_headers(self):
        # Always serve fresh files while developing the editor itself
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    # ---------- API ----------

    def do_GET(self):
        if self.path == "/api/datasets":
            return self.send_json([{"name": n, "exists": (DATA_DIR / f"{n}.json").exists()} for n in DATASETS])
        if self.path.startswith("/api/data/"):
            name = self.dataset_name()
            if name is None:
                return
            path = DATA_DIR / f"{name}.json"
            if not path.exists():
                return self.send_error_json(HTTPStatus.NOT_FOUND, f"{name}.json does not exist yet")
            try:
                return self.send_json(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError as e:
                return self.send_error_json(HTTPStatus.UNPROCESSABLE_ENTITY, f"{name}.json is not valid JSON: {e}")
        return super().do_GET()

    def do_PUT(self):
        if not self.path.startswith("/api/data/"):
            return self.send_error_json(HTTPStatus.NOT_FOUND, "Unknown endpoint")
        name = self.dataset_name()
        if name is None:
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, json.JSONDecodeError) as e:
            return self.send_error_json(HTTPStatus.BAD_REQUEST, f"Body is not valid JSON: {e}")
        if not isinstance(body, dict):
            return self.send_error_json(HTTPStatus.BAD_REQUEST, "Top level must be a JSON object")

        path = DATA_DIR / f"{name}.json"
        backup = backup_file(path, name)
        write_atomic(path, json.dumps(body, indent=2, ensure_ascii=False) + "\n")
        return self.send_json({"saved": f"Assets/Resources/Data/{name}.json",
                               "backup": os.path.relpath(backup, PROJECT_DIR) if backup else None})

    # ---------- helpers ----------

    def dataset_name(self):
        name = self.path[len("/api/data/"):].split("?")[0]
        if name not in DATASETS:
            self.send_error_json(HTTPStatus.NOT_FOUND, f"Unknown dataset '{name}'")
            return None
        return name

    def send_json(self, obj, status=HTTPStatus.OK):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_error_json(self, status, message):
        self.send_json({"error": message}, status)


def backup_file(path: Path, name: str):
    if not path.exists():
        return None
    BACKUP_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = BACKUP_DIR / f"{name}-{stamp}.json"
    shutil.copy2(path, target)
    # Keep only the newest backups per dataset
    old = sorted(BACKUP_DIR.glob(f"{name}-*.json"))[:-MAX_BACKUPS_PER_DATASET]
    for f in old:
        f.unlink(missing_ok=True)
    return target


def write_atomic(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.stem}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not DATA_DIR.is_dir():
        sys.exit(f"Data folder not found: {DATA_DIR}")

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Natural History concept editor → {url}")
    print(f"Editing {DATA_DIR.relative_to(PROJECT_DIR)}  (Ctrl+C to stop)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
