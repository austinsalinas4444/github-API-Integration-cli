import os, time, json, sqlite3, requests, argparse
from dotenv import load_dotenv

# --- Auth / headers ---
load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit("Set GITHUB_TOKEN in your .env")

H = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "austin-github-integration/0.3"
}
RETRY = {429, 500, 502, 503, 504}

# --- Pagination helper ---
def next_link(resp):
    link = resp.headers.get("Link", "")
    for part in link.split(","):
        if 'rel="next"' in part:
            return part[part.find("<")+1:part.find(">")]
    return None

# --- Fetch all issues (with backoff + pagination) ---
def fetch_issues(owner, repo, since=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100"
    if since:
        url += f"&since={since}"
    out = []
    while url:
        for attempt in range(5):
            r = requests.get(url, headers=H, timeout=30)
            if r.status_code in RETRY:
                time.sleep(2 ** attempt)
                continue
            r.raise_for_status()
            break
        else:
            raise SystemExit(f"Failed after retries: {url}")

        # Keep only real issues (GitHub mixes PRs in this endpoint)
        page_items = [it for it in r.json() if "pull_request" not in it]
        out.extend(page_items)
        # Optional: progress
        # print(f"+{len(page_items)} (total: {len(out)}) from {owner}/{repo}")
        url = next_link(r)
    return out

# DB setup
def ensure_db():
    con = sqlite3.connect("data.db")
    con.execute("""
    CREATE TABLE IF NOT EXISTS issues(
      id INTEGER PRIMARY KEY,   -- GitHub issue id
      number INTEGER,           -- issue number
      title TEXT,
      state TEXT,
      created_at TEXT,
      updated_at TEXT,
      raw TEXT                  -- full JSON as a string
    )
    """)
    return con

def normalize(it):
    return (
        it["id"],
        it["number"],
        it.get("title",""),
        it.get("state",""),
        it.get("created_at"),
        it.get("updated_at"),
        json.dumps(it)
    )

def upsert_all(con, items):
    for it in items:
        con.execute("""
        INSERT INTO issues(id, number, title, state, created_at, updated_at, raw)
        VALUES(?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          number=excluded.number,
          title=excluded.title,
          state=excluded.state,
          created_at=excluded.created_at,
          updated_at=excluded.updated_at,
          raw=excluded.raw
        """, normalize(it))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--since", help="ISO like 2025-01-01T00:00:00Z")
    args = ap.parse_args()

    con = ensure_db()
    items = fetch_issues(args.owner, args.repo, args.since)
    upsert_all(con, items)
    con.commit(); con.close()
    print(f"Synced {len(items)} issues from {args.owner}/{args.repo}")

if __name__ == "__main__":
    main()

