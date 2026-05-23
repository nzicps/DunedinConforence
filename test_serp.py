import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("SERPAPI_KEY")

params = {
    "q": "site:linkedin.com/in google engineer",
    "api_key": key
}

r = requests.get("https://serpapi.com/search.json", params=params)

data = r.json()

for item in data.get("organic_results", [])[:3]:
    print(item["title"])
    print(item["link"])
    print("---")