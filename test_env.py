import os
from dotenv import load_dotenv

load_dotenv()
print("GITHUB_TOKEN is:", os.getenv("GITHUB_TOKEN")[:10] + "...")
