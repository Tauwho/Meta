"""Threads API account connection: OAuth token exchange, refresh, whoami.

Tokens and the app secret live only in .env; nothing here prints them.

    python -m medium_engine.threads auth A      # browser login -> long-lived token in .env
    python -m medium_engine.threads whoami A
    python -m medium_engine.threads refresh A   # run every <60 days (token must be >24h old)
"""
import json
import sys
import urllib.parse
import urllib.request

from dotenv import dotenv_values, set_key

from . import config

GRAPH = "https://graph.threads.net"
REDIRECT = "https://localhost/"
SCOPES = "threads_basic,threads_content_publish,threads_manage_replies,threads_read_replies,threads_manage_insights"


def _env_path():
    return config.root() / ".env"


def _env():
    return dotenv_values(_env_path())


def _call(url, data=None):
    body = urllib.parse.urlencode(data).encode() if data else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=body), timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # Meta error bodies never echo the secret back; show message only
        msg = json.loads(e.read() or b"{}").get("error", {}).get("message", str(e))
        sys.exit(f"Threads API error: {msg}")


def code_from_redirect(url):
    """Pull the auth code out of the pasted redirect URL; Meta appends '#_'."""
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url.strip()).query)
    if "code" not in q:
        sys.exit("No code= in that URL. Paste the full address bar after the redirect.")
    return q["code"][0].removesuffix("#_")


def auth(slot):
    env = _env()
    app_id, secret = env.get("THREADS_APP_ID"), env.get("THREADS_APP_SECRET")
    if not app_id or not secret:
        sys.exit("Set THREADS_APP_ID and THREADS_APP_SECRET in .env first.")
    url = f"https://threads.net/oauth/authorize?" + urllib.parse.urlencode(
        {"client_id": app_id, "redirect_uri": REDIRECT, "scope": SCOPES, "response_type": "code"})
    print(f"1. Open this while logged into Threads account {slot}:\n\n{url}\n")
    print("2. Approve. The browser lands on a localhost page that does not load; that is expected.")
    code = code_from_redirect(input("3. Paste that page's full URL here: "))
    short = _call(f"{GRAPH}/oauth/access_token", {
        "client_id": app_id, "client_secret": secret, "grant_type": "authorization_code",
        "redirect_uri": REDIRECT, "code": code})
    long = _call(f"{GRAPH}/access_token?" + urllib.parse.urlencode({
        "grant_type": "th_exchange_token", "client_secret": secret, "access_token": short["access_token"]}))
    set_key(_env_path(), f"THREADS_{slot}_USER_ID", str(short["user_id"]))
    set_key(_env_path(), f"THREADS_{slot}_TOKEN", long["access_token"])
    print(f"Saved THREADS_{slot}_USER_ID and THREADS_{slot}_TOKEN to .env "
          f"(valid ~{long.get('expires_in', 0) // 86400} days).")
    whoami(slot)


def _token(slot):
    tok = _env().get(f"THREADS_{slot}_TOKEN")
    if not tok:
        sys.exit(f"No THREADS_{slot}_TOKEN in .env. Run: python -m medium_engine.threads auth {slot}")
    return tok


def whoami(slot):
    me = _call(f"{GRAPH}/v1.0/me?" + urllib.parse.urlencode(
        {"fields": "id,username", "access_token": _token(slot)}))
    print(f"Account {slot}: @{me['username']} (id {me['id']})")


def refresh(slot):
    r = _call(f"{GRAPH}/refresh_access_token?" + urllib.parse.urlencode(
        {"grant_type": "th_refresh_token", "access_token": _token(slot)}))
    set_key(_env_path(), f"THREADS_{slot}_TOKEN", r["access_token"])
    print(f"Refreshed THREADS_{slot}_TOKEN (valid ~{r.get('expires_in', 0) // 86400} days).")


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmds = {"auth": auth, "whoami": whoami, "refresh": refresh}
    if len(argv) != 2 or argv[0] not in cmds or argv[1].upper() not in ("A", "B"):
        sys.exit("usage: python -m medium_engine.threads {auth|whoami|refresh} {A|B}")
    cmds[argv[0]](argv[1].upper())


if __name__ == "__main__":
    main()
