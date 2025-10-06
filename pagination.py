import os, time, json, sqlite3, requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit("Set GITHUB_TOKEN in your .env")

OWNER, REPO = "pallets", "flask"

H = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "austin-github-integration/0.2"
}
RETRY = {429, 500, 502, 503, 504}

def next_link(resp):
    link = resp.headers.get("Link", "")
    for part in link.split(","):
        if 'rel="next"' in part:
            return part[part.find("<")+1:part.find(">")]
    return None

def fetch_all_issues(owner, repo, since = None):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100"
    if since:
        url += f"&since={since}"  #timestamps
    out = []
    while url:
        for attempt in range(5):
            r = requests.get(url, headers=H, timeout=30)
            if r.status_code in RETRY:
                time.sleep(2 ** attempt); continue
            r.raise_for_status(); break
        page_items = [item for item in r.json() if "pull_request" not in item]
        out.extend(page_items)
        url = next_link(r)
    return out

con = sqlite3.connect("data.db")
con.execute ("""
CREATE TABLE IF NOT EXISTS issues(
    id INTEGER PRIMARY KEY,
    number INTEGER,
    title TEXT,
    state TEXT,
    created_at TEXT,
    updated_at TEXT,
    raw TEXT              
)
""")
#upsert all pages
items = fetch_all_issues(OWNER, REPO)  
for issue in items:
    con.execute("""
    INSERT INTO issues(id, number, title, state, created_at, updated_at, raw)
    VALUES (?,?,?,?,?,?,?)  
    ON CONFLICT (id) DO UPDATE SET
    number=excluded.number,
    title=excluded.title,
    state=excluded.state,
    created_at=excluded.created_at,
    updated_at=excluded.updated_at,
    raw=excluded.raw             
""", (
    issue["id"], 
    issue["number"], 
    issue.get("title",""), 
    issue.get("state",""),
    issue.get("created_at"), 
    issue.get("updated_at"), 
    json.dumps(issue)
    ))

con.commit(); con.close()

print(f"Upserted {len(items)} issues from {OWNER}/{REPO}")            





        


                        
    
