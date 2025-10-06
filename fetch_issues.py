import os 
import requests
from dotenv import load_dotenv

#load token
load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise SystemExit("Set GITHUB_TOKEN in your .env")

#choose a repo -- change whenever you want
OWNER = "pallets"
REPO = "flask" #good public repo with active issues

#call the API (first page only)
url = f"https://api.github.com/repos/{OWNER}/{REPO}/issues"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "User-Agent": "austin-github-integration/0.1"
    }
params = {"state": "all", "per_page": 5} #small sample

r = requests.get(url, headers=headers, params=params, timeout=30)
r.raise_for_status() #crash early if HTTP error

items = r.json()

#Github returns PRs in the issues endpoint; filter those out
issues = [it for it in items if "pull_request" not in it]

print(f"Fetched {len(issues)} issues from {OWNER}/{REPO}")
for it in issues:
    print(f"#{it['number']} | {it.get('state')} | {it.get('title')[:80]}")