# GitHub API Integration CLI 

A lightweight Python command-line tool that connects to the GitHub REST API, fetches repository issues (with pagination), and stores them in a local SQLite database for quick pulls.

This project handles pagination and structures JSON data in a relational database.

---

## Features

- Fetches issues from any public GitHub repository :) 
- Handles pagination & retry logic
- Stores data locally in data.db
- Simple CLI interface
- Excludes pull requests from issue results  

---

## Example 

```bash
# Activate virtual env
source .venv/bin/activate

# Run CLI
python github_cli.py --owner pallets --repo flask

# Output
Synced 2697 issues from pallets/flask
```

## Setup

**Clone this repository**
   ```bash
   git clone https://github.com/austinsalinas4444/github-API-Integration-cli.git
   cd github-API-Integration-cli
```
Create virtual envrionment
 ```bash
python3 -m venv .venv
source .venv/bin/activate
```
