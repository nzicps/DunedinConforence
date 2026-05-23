import os
import shutil
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from docx import Document

# import your pipeline (must exist in your project)
from api_pipeline import run_pipeline

app = FastAPI(title="Org LinkedIn Enrichment API")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# -----------------------------
# Helpers
# -----------------------------
def read_docx(file_path):
    doc = Document(file_path)
    items = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            items.append(text)

    return items


def save_list_to_csv(items, path):
    df = pd.DataFrame(items, columns=["company"])
    df.to_csv(path, index=False)


# -----------------------------
# UI HOME PAGE
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Org Upload Tool</title>
        </head>
        <body style="font-family: Arial; max-width: 700px; margin: 50px auto;">

            <h2>🚀 Organisation LinkedIn Search Tool</h2>

            <p>Upload a CSV or Word document (.docx) with company names.</p>

            <form action="/upload" enctype="multipart/form-data" method="post">

                <input name="file" type="file" accept=".csv,.docx" required>

                <br><br>

                <button type="submit" style="
                    padding:10px 20px;
                    background:#4CAF50;
                    color:white;
                    border:none;
                    cursor:pointer;
                ">
                    Upload & Run
                </button>

            </form>

        </body>
    </html>
    """


# -----------------------------
# Upload Endpoint
# -----------------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # -----------------------------
    # Parse file
    # -----------------------------
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file_path)
        orgs = df.iloc[:, 0].dropna().tolist()

    elif file.filename.endswith(".docx"):
        orgs = read_docx(file_path)

    else:
        return {"error": "Only CSV or DOCX supported"}

    # -----------------------------
    # Save temp CSV for pipeline
    # -----------------------------
    temp_csv = os.path.join(UPLOAD_DIR, "temp.csv")
    save_list_to_csv(orgs, temp_csv)

    # -----------------------------
    # Run your scraper pipeline
    # -----------------------------
    output_file = run_pipeline(temp_csv)

    # -----------------------------
    # Result page
    # -----------------------------
    return HTMLResponse(f"""
    <html>
        <body style="font-family: Arial; max-width: 700px; margin: 50px auto;">

            <h2>✅ Done!</h2>

            <p><b>Companies processed:</b> {len(orgs)}</p>

            <p><b>Output file:</b> {output_file}</p>

            <a href="/download"
               style="padding:10px 20px; background:#2196F3; color:white; text-decoration:none;">
               Download Results
            </a>

        </body>
    </html>
    """)


# -----------------------------
# Download Endpoint
# -----------------------------
@app.get("/download")
def download():
    files = os.listdir(OUTPUT_DIR)

    if not files:
        return {"error": "No output file found"}

    latest = max([os.path.join(OUTPUT_DIR, f) for f in files], key=os.path.getctime)

    return FileResponse(latest, filename="results.xlsx")