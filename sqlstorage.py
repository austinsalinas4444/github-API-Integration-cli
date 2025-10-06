import os, sqlite3, json, requests
from dotenv import load_dotenv

#load token
load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit("Set GITHUB_TOKEN in your .env")

#choose repo to select from (change here!)
OWNER,REPO = "pallets", "flask"

#call the API
url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "austin-github-integration/0.1"
}

params = {"state": "all", "per_page": 50}
r = requests.get(url, headers=headers, params=params, timeout = 30)
r.raise_for_status()

items = []
for issue in r.json():
    if "pull_request" not in issue:
        items.append(issue)

#create the sql database + table
con = sqlite3.connect("data.db")
con.execute ("""
CREATE TABLE IF NOT EXISTS issues(
             id INTEGER PRIMARY KEY,        -- GitHubs global issue id
             number INTEGER,                -- repo-local issue number
             title TEXT,
             state TEXT,
             created_at TEXT,
             updated_at TEXT,
             raw TEXT                       -- JSON as string for backup
          )     
""" )

#insert rows and ignore duplicates
for issue in items:
    con.execute("""
    INSERT OR IGNORE INTO issues(id, number, title, state, created_at, updated_at, raw)
    VALUES(?,?,?,?,?,?,?)         
""", (
    issue["id"],
    issue["number"],
    issue.get("title",""),
    issue.get("state",""),
    issue.get("created_at"),
    issue.get("updated_at"),
    json.dumps(issue)
))
    
con.commit()
con.close()

print(f"Saved {len(items)} issues from {OWNER}/{REPO} into data.db")

