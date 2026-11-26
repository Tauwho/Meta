"""Threads API account connection: OAuth token exchange, refresh, whoami.

Tokens and the app secret live only in .env; nothing here prints them.

    meta auth A      # browser login -> long-lived token in .env
    meta whoami A
    meta refresh A   # run every <60 days (token must be >24h old)
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from dotenv import dotenv_values, set_key

from . import config

GRAPH = "https://graph.threads.net"
REDIRECT = "https://localhost/"
SCOPES = "threads_basic,threads_content_publish,threads_manage_replies,threads_read_replies,threads_manage_insights,threads_delete,threads_keyword_search,threads_location_tagging"


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
        sys.exit(f"No THREADS_{slot}_TOKEN in .env. Run: meta auth {slot}")
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


def _user(slot):
    uid = _env().get(f"THREADS_{slot}_USER_ID")
    if not uid:
        sys.exit(f"No THREADS_{slot}_USER_ID in .env. Run: meta auth {slot}")
    return uid


def publish_text(slot, text, reply_to=None, image_url=None, link=None, topic_tag="", poll=None,
                 quote_post_id="", location_id=""):
    """Create + publish one text or image post (or a reply). `link` adds a link-preview card
    (the article's own thumbnail and headline) to a text post; `topic_tag` files the post under a
    Threads topic feed; `poll` (2-4 options) adds a poll to a text post. Returns the published media id."""
    tok, uid = _token(slot), _user(slot)
    data = {"media_type": "IMAGE" if image_url else "TEXT", "text": text, "access_token": tok}
    if image_url:
        data["image_url"] = image_url
    if link and not image_url:
        data["link_attachment"] = link
    if topic_tag:
        data["topic_tag"] = topic_tag
    if poll and not image_url:
        data["poll_attachment"] = json.dumps(dict(zip(("option_a", "option_b", "option_c", "option_d"), poll)),
                                             ensure_ascii=False)
    if quote_post_id:
        data["quote_post_id"] = quote_post_id
    if location_id:
        data["location_id"] = location_id
    if reply_to:
        data["reply_to_id"] = reply_to
    container = _call(f"{GRAPH}/v1.0/{uid}/threads", data)
    # Publishing before the container is FINISHED fails with "requested resource does not exist".
    for _ in range(12):
        status = _call(f"{GRAPH}/v1.0/{container['id']}?" + urllib.parse.urlencode(
            {"fields": "status,error_message", "access_token": tok}))
        if status.get("status") == "FINISHED":
            break
        if status.get("status") in ("ERROR", "EXPIRED"):
            sys.exit(f"Threads container {status.get('status')}: {status.get('error_message', '')}")
        time.sleep(5)
    else:
        sys.exit("Threads container not ready after 60s")
    # Meta sometimes 404s a FINISHED container for a few seconds ("requested resource does not exist");
    # that error means nothing was published, so retrying cannot double-post.
    for attempt in range(4):
        try:
            return _call(f"{GRAPH}/v1.0/{uid}/threads_publish",
                         {"creation_id": container["id"], "access_token": tok})["id"]
        except SystemExit as e:
            if "does not exist" not in str(e) or attempt == 3:
                raise
            time.sleep(10)


def search(slot, q, limit=10):
    """Top public posts for a keyword from the last 24h. Until Meta approves threads_keyword_search
    this returns only the account's own posts, which callers drop, so quoting stays dormant."""
    res = _call(f"{GRAPH}/v1.0/keyword_search?" + urllib.parse.urlencode({
        "q": q, "search_type": "TOP", "since": int(time.time()) - 86400, "limit": limit,
        "fields": "id,text,username,permalink,timestamp", "access_token": _token(slot)}))
    return res.get("data", [])


def location_id(slot, name):
    """Threads location id for a place name, or "". Until Meta approves threads_location_tagging the
    search only knows "Menlo Park", so a result whose name does not match `name` is ignored."""
    res = _call(f"{GRAPH}/v1.0/location_search?" + urllib.parse.urlencode(
        {"q": name, "fields": "id,name", "access_token": _token(slot)}))
    want = name.split(",")[0].strip().casefold()
    return next((loc["id"] for loc in res.get("data", []) if want in loc.get("name", "").casefold()), "")


def delete(slot, media_id):
    """Permanently delete one of the account's posts or replies (needs threads_delete)."""
    req = urllib.request.Request(f"{GRAPH}/v1.0/{media_id}?" + urllib.parse.urlencode(
        {"access_token": _token(slot)}), method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r).get("success", False)
    except urllib.error.HTTPError as e:
        msg = json.loads(e.read() or b"{}").get("error", {}).get("message", str(e))
        sys.exit(f"Threads API error: {msg}")


def permalink(slot, media_id):
    return _call(f"{GRAPH}/v1.0/{media_id}?" + urllib.parse.urlencode(
        {"fields": "permalink", "access_token": _token(slot)})).get("permalink", "")


def recent(slot, limit=5):
    """The account's latest posts: check this before retrying a failed publish, to never double-post."""
    r = _call(f"{GRAPH}/v1.0/me/threads?" + urllib.parse.urlencode(
        {"fields": "id,text,timestamp,permalink", "limit": limit, "access_token": _token(slot)}))
    for t in r.get("data", []):
        print(t["timestamp"], t["id"], t.get("permalink", ""), " ".join((t.get("text") or "").split())[:60])


METRICS = "views,likes,replies,reposts,quotes,shares"


def insights(slot, media_id):
    r = _call(f"{GRAPH}/v1.0/{media_id}/insights?" + urllib.parse.urlencode(
        {"metric": METRICS, "access_token": _token(slot)}))
    out = {}
    for m in r.get("data", []):
        v = m.get("total_value", {}).get("value")
        if v is None and m.get("values"):
            v = m["values"][0].get("value")
        out[m["name"]] = v or 0
    return out
