# 🐟 TinyFish Job & Internship Scraper AI

> Built for **"AI That Clicks."**, the **TinyFish × Team Technojam** workshop at Galgotias University.

An Agentic AI job and internship scraper powered by **TinyFish**. It crawls live openings from company careers pages and modern job portals, matches them precisely against your desired target profile (role, location, seniority, tech stack), keeps results continuously fresh, and tracks your job applications.

---

## ✨ Features

- **Autonomous Agentic Web Scraping**: Powered by TinyFish Web Agents (`tinyfish.TinyFish`) to navigate, browse, scroll, and extract structured jobs from dynamic JavaScript career portals (Greenhouse, Lever, Ashby, Workday, etc.).
- **Live Event Streaming (SSE)**: Watch the TinyFish agent navigate, inspect the DOM, and extract openings in real-time right inside the integrated terminal drawer.
- **Intelligent Multi-Factor Matching**:
  - 🎯 **Role & Title Matching**: Semantic synonym matching (e.g., SDE = Software Engineer = Full Stack Developer).
  - 🎓 **Seniority Detection**: Filters Internship, Entry-Level / New Grad, Mid-Level, and Senior.
  - 📍 **Location & Work Mode**: Remote, Hybrid, or On-site matching (e.g. India, Bengaluru, Delhi NCR, SF, Worldwide).
  - ⚡ **Skills Extraction**: Automatically extracts tech stack keywords (Python, React, TypeScript, Docker, PyTorch, etc.) and computes compatibility scores (0–100%).
- **Freshness Engine & Deduplication**:
  - Automatically indexes new postings, timestamps updates, and prunes stale postings.
  - Background scheduler automatically keeps your job feed fresh.
- **Modern Glassmorphic Web Dashboard**:
  - Filter by Role, Seniority, Work Mode, Min Match Score, and Application Status.
  - 1-Click Apply links, bookmarking, and built-in Kanban status tracker (`Not Applied`, `Applied`, `Interviewing`, `Offer`, `Rejected`).
  - Target Career Portals Manager: Add custom company career URLs with 1 click.
  - Export matched listings to CSV and JSON.
- **Full Terminal CLI**:
  - Run scrapes and view colored job tables directly in your terminal via `python cli.py`.

---

## 🚀 Quickstart

### 1. Run the Web Dashboard
```bash
python cli.py serve
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### 2. Run via Command Line
```bash
# Crawl portals and display matched roles
python cli.py scrape

# List jobs currently in your local database
python cli.py list --min-score 50

# View configured career portals
python cli.py portals

# View overall stats
python cli.py stats
```

---

## 🔑 TinyFish API Key Setup

1. Get your API key from [agent.tinyfish.ai/api-keys](https://agent.tinyfish.ai/api-keys).
2. Configure it in either of two ways:
   - **Via Web UI**: Click the TinyFish status badge in the top navigation bar, paste your key, test connection, and click Save.
   - **Via `.env` file**:
     ```env
     TINYFISH_API_KEY=tf_your_api_key_here
     ```

> **Note**: Even before entering your API key, the tool functions out-of-the-box with live public feeds (Greenhouse boards, RemoteOK live API) and high-fidelity browser agent simulations. Once you add your key, the full TinyFish Cloud Agent browser worker is automatically activated.

---

## 🏗️ Architecture

```
e:\jobhunt-ai/
├── app/
│   ├── config.py             # Environment settings & dynamic key loading
│   ├── db.py                 # SQLite database & WAL schema (jobs, profiles, portals, logs)
│   ├── matcher.py            # AI scoring engine (role, location, seniority, skills)
│   ├── tinyfish_client.py    # TinyFish Web Agent & Search SDK integration
│   ├── scraper.py            # Crawling orchestrator & live feeds (Greenhouse, RemoteOK, TinyFish)
│   ├── scheduler.py          # Freshness background engine
│   ├── static/
│   │   ├── style.css         # Modern dark glassmorphic styling
│   │   └── app.js            # Real-time SSE streaming, filtering, and modal handlers
│   └── templates/
│       └── index.html        # Interactive dashboard
├── cli.py                    # Terminal CLI with rich formatting
├── main.py                   # FastAPI server entrypoint
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```
