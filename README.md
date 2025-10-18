# 🧠 GitHub PR Summarizer

A FastAPI microservice that fetches recent pull requests from any public GitHub repository and summarizes them using OpenAI's GPT-4. Built for demo, deployment, and interview readiness.

## 🚀 Features

- 🔍 Fetches latest PRs from any GitHub repo
- 🧠 Summarizes PR titles and bodies using GPT-4
- 🐳 Containerized with Docker for easy deployment
- 🔐 Secure token management via `.env` file
- 📄 Swagger UI available at `/docs`
- ✅ Health check endpoint at `/health`

## 📦 Tech Stack

- FastAPI
- Docker
- OpenAI SDK (v1.30+)
- GitHub REST API
- Python 3.10+

### 1. Clone the repo


git clone https://github.com/your-username/pr-summarizer.git
cd pr-summarizer


### 2. Create .env file

GITHUB_TOKEN=ghp_your_github_token_here
OPENAI_API_KEY=sk-your_openai_key_here

### 3. Build and run with Docker
docker build -t pr-summarizer .
docker run -p 8000:8000 --env-file .env pr-summarizer

### 🧪 Usage
POST /summarize
Fetch and summarize recent PRs from a GitHub repo.

Request:

json
{
  "repo": "microsoft/semantic-kernel",
  "count": 3
}
Response:

json
[
  {
    "title": "Add caching layer",
    "summary": "This PR introduces Redis caching to improve response times..."
  },
  ...
]

GET /health

Returns {"status": "ok"} if the app is running.

Swagger UI
Visit http://localhost:8000/docs for interactive API testing.

### 🌍 Deployment
You can deploy this app to Render, Azure App Service, or any container platform.

### 📄 License
This project is licensed under the GPL-3.0 License.

## 🙋‍♂️ Author

Built by G P Rai, a cloud engineer and DevOps specialist passionate about scalable AI solutions.







