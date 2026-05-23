import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def search_company(company):
    query = f'site:linkedin.com/in "{company}" engineer'

    params = {
        "q": query,
        "api_key": SERPAPI_KEY
    }

    r = requests.get(
        "https://serpapi.com/search.json",
        params=params
    )

    data = r.json()

    rows = []

    for item in data.get("organic_results", [])[:10]:
        rows.append({
            "company": company,
            "title": item.get("title"),
            "linkedin_url": item.get("link")
        })

    return rows


def run_pipeline(csv_file):
    df = pd.read_csv(csv_file)

    companies = df.iloc[:, 0].dropna().tolist()

    all_rows = []

    for company in companies:
        print(f"Searching: {company}")

        results = search_company(company)

        all_rows.extend(results)

    output_df = pd.DataFrame(all_rows)

    os.makedirs("output", exist_ok=True)

    output_path = "output/conference_leads.csv"

    output_df.to_csv(output_path, index=False)

    return output_path