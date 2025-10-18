from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import openai
from openai import OpenAI
from openai import OpenAIError
import os
from dotenv import load_dotenv
from sse_starlette.sse import EventSourceResponse
import time

app = FastAPI()


from fastapi import Form

@app.get("/", response_class=HTMLResponse)
def landing_page():
    return """
    <html>
        <head>
            <title>GitHub PR Summarizer</title>
            <link rel="icon" href="https://cdn-icons-png.flaticon.com/512/1828/1828884.png">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 40px;
                    background-color: #f9f9f9;
                    color: #333;
                }
                h1 {
                    color: #2c3e50;
                    display: inline;
                }
                form {
                    background: #fff;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    max-width: 500px;
                }
                input, button {
                    width: 100%;
                    padding: 10px;
                    margin-top: 10px;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                }
                button {
                    background-color: #2c3e50;
                    color: white;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #34495e;
                }
                ul {
                    margin-top: 20px;
                }
                a {
                    color: #2980b9;
                    text-decoration: none;
                }
                footer {
                    margin-top: 40px;
                    font-size: 0.9em;
                    color: #888;
                }
            </style>
        </head>
        <body>
            <img src="https://cdn-icons-png.flaticon.com/512/1828/1828884.png" alt="Logo" width="50" style="vertical-align: middle; margin-right: 10px;">
            <h1>🧠 GitHub PR Summarizer</h1>
            <p>This FastAPI service summarizes pull requests using GPT-4.</p>
            <form method="post" action="/">
                <label>Repo (e.g. microsoft/semantic-kernel):</label>
                <input type="text" name="repo" required>
                <label>Count:</label>
                <input type="number" name="count" value="3" min="1">
                <button type="submit">Summarize PRs</button>
            </form>
            <ul>
                <li><a href="/docs">Swagger UI</a></li>
                <li><a href="/health">Health Check</a></li>
            </ul>
            <footer>
                Built by G P Rai • Powered by FastAPI + GPT-4 • <a href="https://github.com/raiaaranya" target="_blank">GitHub</a>
            </footer>
        </body>
    </html>
    """



@app.post("/", response_class=HTMLResponse)
def summarize_from_form(repo: str = Form(...), count: int = Form(...)):
    try:
        prs = fetch_pull_requests(repo, count)
        summaries = [
            f"<div style='margin-bottom:20px;'><strong>{pr['title']}</strong><br><p>{summarize_pr(pr.get('title', ''), pr.get('body', ''))}</p></div>"
            for pr in prs
        ]
        return f"""
        <html>
            <head><title>PR Summaries</title></head>
            <body style='font-family:Arial; margin:40px;'>
                <h1>🧠 Summarized PRs for {repo}</h1>
                {''.join(summaries)}
                <br><a href="/">🔙 Back</a>
            </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
            <body style='font-family:Arial; margin:40px;'>
                <h2>Error</h2>
                <pre>{str(e)}</pre>
                <br><a href="/">🔙 Back</a>
            </body>
        </html>
        """


load_dotenv()

# --- CONFIG ---
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
print("GitHub Token Loaded:", bool(GITHUB_TOKEN))
print("GitHub Token Length:", len(GITHUB_TOKEN))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
print("OpenAI API Key Loaded:", bool(OPENAI_API_KEY))
print("OpenAI API Key Length:", len(OPENAI_API_KEY))

client = OpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
)

# --- HEADERS ---
gh_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# --- MODELS ---
class PRRequest(BaseModel):
    repo: str
    count: int = 5

# --- FUNCTIONS ---
def fetch_pull_requests(repo, count):
    url = f"https://api.github.com/repos/{repo}/pulls?state=open&per_page={count}"
    response = requests.get(url, headers=gh_headers)
    print("GitHub response:", response.status_code, response.text)  # Add this line
    response.raise_for_status()
    return response.json()


def summarize_pr(title, body, max_retries=3, delay=2):
    prompt = f"Summarize this GitHub Pull Request:\nTitle: {title}\nBody: {body}\nSummary:"
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except OpenAIError as e:
            print(f"OpenAI error (attempt {attempt+1}):", str(e))
            time.sleep(delay)
    return "Error: Unable to generate summary after multiple attempts."

# --- ROUTE ---
@app.post("/summarize")
def summarize_prs(request: PRRequest):
    try:
        prs = fetch_pull_requests(request.repo, request.count)
        summaries = [
            {"title": pr["title"], "summary": summarize_pr(pr.get("title", ""), pr.get("body", ""))}
            for pr in prs
        ]
        return {"summaries": summaries}
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }



@app.get("/health")
def health_check():
    return {"status": "ok"}