#!/usr/bin/env python3
"""
Download the most recent Meshy text-to-3D model (mallard) via the Meshy API.

Usage:
  export MESHY_API_KEY=your_key_here
  python scripts/download_meshy_model.py

The GLB will be saved to Assets/Prefabs/Species/Mallard/mallard.glb
"""

import os
import sys
import json
import ssl
import urllib.request
import urllib.error
from pathlib import Path

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

API_BASE = "https://api.meshy.ai/openapi/v2"
OUTPUT_DIR = Path(__file__).parent.parent / "Assets" / "Prefabs" / "Species" / "Mallard"


def get_api_key() -> str:
    key = os.environ.get("MESHY_API_KEY", "").strip()
    if not key:
        print("Error: MESHY_API_KEY environment variable not set.")
        print("  export MESHY_API_KEY=your_key_here")
        sys.exit(1)
    return key


def api_get(path: str, key: str) -> dict:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, context=SSL_CONTEXT) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} from {url}")
        print(f"Response body: {body[:500]}")
        raise


def download_file(url: str, dest: Path) -> None:
    print(f"  Downloading {url.split('?')[0]}")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, context=SSL_CONTEXT) as resp:
        dest.write_bytes(resp.read())


def main():
    key = get_api_key()

    print(f"Using API key: {key[:8]}... (length {len(key)})")
    print("Fetching your text-to-3D tasks...")
    data = api_get("/text-to-3d?page_num=1&page_size=20&sort_by=-created_at", key)

    tasks = data if isinstance(data, list) else data.get("result", [])
    if not tasks:
        print("No text-to-3D tasks found.")
        sys.exit(1)

    # Find the most recent succeeded task with a GLB URL
    target = None
    for task in tasks:
        if task.get("status") == "SUCCEEDED" and task.get("model_urls", {}).get("glb"):
            target = task
            break

    if not target:
        print("No completed tasks with a GLB found. Task statuses:")
        for t in tasks[:5]:
            print(f"  {t.get('id')} — {t.get('status')} — {t.get('prompt', '')[:60]}")
        sys.exit(1)

    print(f"\nFound model:")
    print(f"  ID     : {target['id']}")
    print(f"  Prompt : {target.get('prompt', '')[:80]}")
    print(f"  Status : {target['status']}")

    glb_url = target["model_urls"]["glb"]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "mallard.glb"

    print(f"\nSaving to: {out_path}")
    download_file(glb_url, out_path)

    size_kb = out_path.stat().st_size // 1024
    print(f"Done — {size_kb} KB written to {out_path}")

    # Also download textures if present
    texture_urls = target.get("texture_urls", [])
    if texture_urls:
        tex_dir = OUTPUT_DIR / "textures"
        tex_dir.mkdir(exist_ok=True)
        for i, tex in enumerate(texture_urls):
            for tex_type, tex_url in tex.items():
                if tex_url:
                    ext = tex_url.split(".")[-1].split("?")[0]
                    tex_path = tex_dir / f"mallard_{tex_type}_{i}.{ext}"
                    print(f"  Texture [{tex_type}]: {tex_path.name}")
                    download_file(tex_url, tex_path)

    print("\nNext step: open Unity and the asset will appear in Assets/Prefabs/Species/Mallard/")


if __name__ == "__main__":
    main()
