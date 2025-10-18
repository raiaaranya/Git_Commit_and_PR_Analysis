from fastapi import FastAPI
from pydantic import BaseModel
import requests
import openai
from openai import OpenAI
from openai import OpenAIError
import os
from dotenv import load_dotenv
from sse_starlette.sse import EventSourceResponse

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

app = FastAPI()

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


def summarize_pr(title, body):
    prompt = f"Summarize this GitHub Pull Request:\nTitle: {title}\nBody: {body}\nSummary:"
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        print("OpenAI error:", str(e))
        return "Error generating summary"

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

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}