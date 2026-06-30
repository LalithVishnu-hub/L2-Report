"""
Box API integration — upload L1/L2 HTML files and return direct file URLs.

First-time setup:
    python setup_box_auth.py

Requirements:
    pip install boxsdk

Environment variables (.env):
    BOX_CLIENT_ID       — App Client ID from developer.box.com
    BOX_CLIENT_SECRET   — App Client Secret from developer.box.com
    BOX_L1_ETE_FOLDER_ID  — Box folder ID for L1_ETE HTML pages
    BOX_L1_PVT_FOLDER_ID  — Box folder ID for L1_PVT HTML pages
    BOX_L2_HTML_FOLDER_ID — Box folder ID for L2 report HTML files
"""

import os
import json
import threading
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    from boxsdk import OAuth2, Client
    BOX_SDK_AVAILABLE = True
except ImportError:
    BOX_SDK_AVAILABLE = False

_PROJECT_ROOT = Path(__file__).parent.parent
_TOKEN_FILE = _PROJECT_ROOT / '.box_tokens.json'
_REDIRECT_URI = 'http://localhost:5556'
_REDIRECT_PORT = 5556


# ── Token persistence ────────────────────────────────────────────────────────

def _save_tokens(access_token, refresh_token):
    _TOKEN_FILE.write_text(
        json.dumps({'access_token': access_token, 'refresh_token': refresh_token}),
        encoding='utf-8'
    )


def _load_tokens():
    if _TOKEN_FILE.exists():
        try:
            return json.loads(_TOKEN_FILE.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


# ── OAuth2 first-time auth ────────────────────────────────────────────────────

class _CallbackHandler(BaseHTTPRequestHandler):
    """Minimal HTTP handler that captures the OAuth2 auth code."""
    captured_code = None

    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        _CallbackHandler.captured_code = params.get('code', [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            b'<h2 style="font-family:sans-serif;color:green">'
            b'Box authentication successful. You can close this tab.</h2>'
        )
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, *args):
        pass  # Suppress console noise


def setup_box_auth():
    """
    Run the one-time OAuth2 browser flow to authenticate with Box.
    Saves tokens to .box_tokens.json for future automated runs.
    """
    if not BOX_SDK_AVAILABLE:
        raise ImportError("boxsdk not installed. Run: pip install boxsdk")

    client_id = os.getenv('BOX_CLIENT_ID', '')
    client_secret = os.getenv('BOX_CLIENT_SECRET', '')
    if not client_id or not client_secret:
        raise ValueError(
            "BOX_CLIENT_ID and BOX_CLIENT_SECRET must be set in .env\n"
            "Get these from developer.box.com → Your App → Configuration"
        )

    oauth = OAuth2(client_id=client_id, client_secret=client_secret,
                   store_tokens=_save_tokens)
    auth_url, _ = oauth.get_authorization_url(_REDIRECT_URI)

    print(f"\n{'='*60}")
    print("BOX AUTHENTICATION — ONE-TIME SETUP")
    print(f"{'='*60}")
    print("Opening browser for Box login and authorization...")
    print(f"\nIf browser does not open, visit this URL manually:\n  {auth_url}\n")

    webbrowser.open(auth_url)

    server = HTTPServer(('localhost', _REDIRECT_PORT), _CallbackHandler)
    print(f"Waiting for redirect on http://localhost:{_REDIRECT_PORT} ...")
    server.serve_forever()

    code = _CallbackHandler.captured_code
    if not code:
        raise RuntimeError("Authentication failed — no auth code received.")

    oauth.authenticate(code)
    print(f"\n[OK] Box authentication successful!")
    print(f"[OK] Tokens saved to: {_TOKEN_FILE}\n")


# ── Client factory ────────────────────────────────────────────────────────────

def get_box_client():
    """
    Return an authenticated Box Client.
    Returns None if Box is not configured or tokens are missing
    (run setup_box_auth.py first).
    """
    if not BOX_SDK_AVAILABLE:
        return None

    client_id = os.getenv('BOX_CLIENT_ID', '').strip()
    client_secret = os.getenv('BOX_CLIENT_SECRET', '').strip()
    if not client_id or not client_secret:
        return None

    tokens = _load_tokens()
    if not tokens.get('access_token'):
        print("[WARN] Box tokens not found. Run: python setup_box_auth.py")
        return None

    oauth = OAuth2(
        client_id=client_id,
        client_secret=client_secret,
        access_token=tokens['access_token'],
        refresh_token=tokens.get('refresh_token'),
        store_tokens=_save_tokens
    )
    return Client(oauth)


# ── File operations ───────────────────────────────────────────────────────────

def upload_and_get_file_id(client, local_path: Path, folder_id: str):
    """
    Upload a file to a Box folder (or update it if it already exists).
    Returns the Box file ID string, or None on failure.
    """
    filename = local_path.name
    folder = client.folder(folder_id)

    # Check if a file with this name already exists in the folder
    try:
        for item in folder.get_items(limit=1000):
            if item.object_type == 'file' and item.name == filename:
                updated = item.update_contents(str(local_path))
                return updated.id
    except Exception as e:
        print(f"  [WARN] Box folder list failed ({filename}): {e}")

    # Upload as new file
    try:
        uploaded = folder.upload(str(local_path), filename)
        return uploaded.id
    except Exception as e:
        print(f"  [WARN] Box upload failed ({filename}): {e}")
        return None


def box_file_url(file_id: str) -> str:
    """Return the Box web URL for a given file ID."""
    return f"https://ibm.ent.box.com/file/{file_id}"


# ── Local sync.db lookup (no API required) ────────────────────────────────────

_BOX_SYNC_DB = Path(os.path.expandvars(
    r'%LOCALAPPDATA%\Box\Box\data\sync.db'
))


def get_box_file_id_from_local_db(filename: str) -> str | None:
    """
    Look up a Box file ID by filename from Box's local sync database.
    No API credentials required — reads Box Drive's local SQLite cache.
    Returns the box_id string, or None if not found.
    """
    import sqlite3, shutil, tempfile

    if not _BOX_SYNC_DB.exists():
        return None

    # Copy to temp — Box keeps the DB locked while running
    tmp = Path(tempfile.gettempdir()) / 'box_sync_lookup.db'
    try:
        shutil.copy2(_BOX_SYNC_DB, tmp)
    except Exception:
        return None

    try:
        conn = sqlite3.connect(str(tmp))
        row = conn.execute(
            "SELECT box_id FROM box_item WHERE name = ? AND item_type = 0",
            (filename,)
        ).fetchone()
        conn.close()
        return str(row[0]) if row else None
    except Exception:
        return None
