# Autonomous Coding Agent

A GitHub Actions workflow that runs on a nightly cron schedule, reads `agent-brief.md`, uses the **Gemini 2.0 Flash** API (free tier) to plan and write code, commits iteratively, waits for CI, self-critiques, and opens a Pull Request when the code passes review.

Everything runs inside GitHub's free Actions minutes (2,000 min/month on free accounts).

---

## One-time setup

### 1. Fork or clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2. Get a free Gemini API key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **Create API key**.
3. Copy the key — you'll need it in the next step.

### 3. Add secrets to GitHub

Go to your repo on GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

| Secret name      | Value                              | Where to get it |
|------------------|------------------------------------|-----------------|
| `GEMINI_API_KEY` | Your Gemini API key                | [aistudio.google.com](https://aistudio.google.com/app/apikey) |

> **`GITHUB_TOKEN`** is provided automatically by GitHub Actions — you do **not** need to add it manually.

### 4. Enable Actions write permissions

Go to **Settings** → **Actions** → **General** → **Workflow permissions** → select **Read and write permissions** → **Save**.

---

## Writing agent-brief.md

Edit `agent-brief.md` in the repo root. Describe what you want built. Be specific:

```markdown
# Agent Brief

## What to build
A REST API endpoint `POST /summarize` that accepts `{"text": "..."}` and
returns `{"summary": "..."}` using a simple extractive summarizer.

## Location
- `api/summarize.py`
- `api/tests/test_summarize.py`

## Constraints
- Python standard library only
- Tests must use pytest
```

The agent reads this file every run, so you can update it between runs to
iterate on the requirements.

---

## Triggering the agent

### Automatic (nightly)

The workflow runs automatically at **11 pm UTC** every day via cron.

### Manual

1. Go to the **Actions** tab in your GitHub repo.
2. Click **Autonomous Coding Agent** in the left sidebar.
3. Click **Run workflow** → **Run workflow**.

---

## Monitoring a run

1. Go to **Actions** → **Autonomous Coding Agent**.
2. Click the most recent run.
3. Expand the **Run agent** step to watch logs in real time.

The agent logs each iteration, CI poll, and critique score as it runs.

---

## How the agent works

```
Read agent-brief.md
        │
        ▼
  Gemini: plan          (list of files to create/modify)
        │
        ▼
┌─── iteration loop (max 8) ──────────────────────────────┐
│                                                          │
│  Gemini: generate code  ──► write files ──► git commit  │
│                                    │                     │
│           ┌────────────────────────┘                     │
│           ▼                                              │
│    wait for GitHub CI                                    │
│    (poll every 60 s, timeout 20 min)                     │
│           │                                              │
│    CI pass?  ──No──► pass logs back to Gemini ──────►   │
│           │                                              │
│    ┌── critique loop (max 3) ──────────────┐            │
│    │  Gemini: score 1-10                   │            │
│    │  score ≥ 8  ──► open PR  ──► done     │            │
│    │  score < 8  ──► fix issues ──► repeat │            │
│    └───────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
         (if max iterations hit, open PR with caveat)
```

---

## Limitations

- **Gemini free tier rate limits**: 15 RPM, 1,500 req/day, 1M tokens/min. Each
  agent run makes roughly 10–30 API calls. You should stay well within limits
  for one nightly run.
- **GitHub Actions free tier**: 2,000 minutes/month. A typical run takes
  5–15 minutes. Running nightly uses ~150–450 min/month.
- **No persistent memory**: The agent starts fresh each run. If you want it to
  build on prior work, commit the files it generates before the next run.
- **Context window**: Very large repos may exceed Gemini's context. The agent
  limits file reads to 200 KB of source files.

---

## Swapping Gemini for Claude

1. Edit `agent/llm.py` — replace the `google-generativeai` SDK calls with
   the `anthropic` SDK.
2. Change the model to `claude-haiku-4-5-20251001` (free via API credits) or
   another Claude model.
3. Add an `ANTHROPIC_API_KEY` secret in GitHub repo settings.
4. Update `agent/requirements.txt`: replace `google-generativeai` with
   `anthropic`.

---

## Project structure

```
.github/
  workflows/
    agent.yml          # cron workflow — triggers agent.py
agent/
  agent.py             # main loop: plan → code → CI → critique → PR
  github_utils.py      # git/gh CLI operations
  llm.py               # Gemini API wrapper
  prompts.py           # all system/user prompt templates
  state.py             # in-run state (written to /tmp)
  requirements.txt     # Python dependencies
agent-brief.md         # YOU edit this to describe what to build
README.md              # this file
```
