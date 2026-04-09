# ThoughtLeader AI
### Agentic LinkedIn & Tech Blog Content Pipeline
**IS 7200 — Building Agentic Systems | Northeastern University | Param Shah**

---

## Overview

ThoughtLeader AI is a multi-agent content creation system built with **CrewAI** that takes any topic as input and autonomously produces a polished, LinkedIn-ready thought leadership post. The system uses a Controller Agent to orchestrate three specialized agents — Research, Writer, and Editor — each powered by Groq's LLaMA 3.1 model. Every run is scored by a custom LinkedIn Engagement Scorer, and posts scoring below 70 are automatically rewritten. All runs are tracked in persistent JSON memory.

---

## System Architecture

```
User Input (Topic)
       │
       ▼
Controller Agent (Orchestrator)
       │
       ├──► Research Agent ──► Web Search Tool ──► Content Summarizer Tool
       │         │
       │         ▼ Research Brief
       ├──► Writer Agent ──► Drafts LinkedIn Post (150–250 words)
       │         │
       │         ▼ Draft Post
       └──► Editor Agent ──► LinkedIn Engagement Scorer (Custom)
                │                      │
                │              score < 70? → Rewrite → Re-score
                │
                └──► File Writer Tool ──► outputs/<topic>.md
                                     ──► memory.json updated
```

---

## Agents

| Agent | Role | Tools |
|---|---|---|
| Controller | Orchestrates pipeline, delegates tasks | None (manager) |
| Research Specialist | Web search, research brief synthesis | Web Search Tool, Summarizer |
| LinkedIn Content Writer | Drafts thought leadership post | None |
| Content Editor & Optimizer | Scores, rewrites if needed, saves output | Engagement Scorer, File Writer |

---

## Tools

### Built-in Tools
1. **Web Search Tool** (`tools/search_tool.py`) — Queries Serper.dev API for recent articles and trends
2. **Content Summarizer Tool** (`tools/summarizer_tool.py`) — Extracts key insights from raw search results
3. **File Writer Tool** (`tools/file_writer_tool.py`) — Saves final post as a timestamped markdown file

### Custom Tool
4. **LinkedIn Engagement Scorer** (`tools/engagement_scorer.py`) — Scores a post 0–100 across 4 dimensions:

| Dimension | Max | Method |
|---|---|---|
| Hook Strength | 25 | Question, numbers, short line (≤12 words), first-person |
| Readability | 25 | Avg sentence length, line break ratio |
| Hashtag Usage | 25 | Regex count — optimal range 3–5 |
| Call-to-Action | 25 | Keyword matching against 15 CTA phrases |

---

## Key Features

- **Multi-agent orchestration** — 4 agents with distinct roles coordinated by a Controller
- **Feedback loop** — posts scoring below 70 are automatically rewritten and re-scored
- **Persistent memory** — `memory.json` tracks all runs, scores, and best performance per topic
- **Retry logic** — 3-attempt retry with 30s/60s/90s waits on Groq rate limits
- **Fallback draft** — pre-written quality post used if pipeline fails completely
- **Free tier only** — runs entirely on Groq + Serper free tiers, no paid APIs required

---

## Project Structure

```
thoughtleader-ai/
│
├── main.py                   # Entry point — runs the full pipeline
├── agents.py                 # Agent definitions (Controller, Research, Writer, Editor)
├── tasks.py                  # Task definitions for each agent
├── tools/
│   ├── __init__.py
│   ├── search_tool.py        # Serper web search wrapper
│   ├── summarizer_tool.py    # Content summarization tool
│   ├── file_writer_tool.py   # Output file writer
│   └── engagement_scorer.py  # Custom LinkedIn Engagement Scorer
├── config/
│   └── settings.py           # API keys and model configuration
├── outputs/                  # Generated posts saved here (auto-created)
├── memory.json               # Persistent run history (auto-created)
├── .env                      # API keys (not committed to version control)
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- VSCode (recommended)
- Free API keys from [Groq](https://console.groq.com) and [Serper](https://serper.dev)

### Installation

```bash
# 1. Clone or download the project
cd thoughtleader-ai

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install crewai crewai-tools litellm python-dotenv requests

# 4. Create .env file in root folder with your API keys
GROQ_API_KEY=your_groq_key_here
SERPER_API_KEY=your_serper_key_here
OPENAI_API_KEY=dummy
```

### Running the System

```bash
python main.py
```

Enter any topic when prompted. Example topics:
- `How AI is changing software engineering in 2025`
- `Why every developer needs to learn prompt engineering`
- `The future of remote work in tech`

### What happens:
1. Research Agent searches the web (3 queries)
2. Content Summarizer extracts key insights
3. Writer Agent drafts a LinkedIn post
4. Engagement Scorer scores the draft (0–100)
5. If score < 70, post is rewritten and re-scored
6. Final post saved to `outputs/` folder
7. Run recorded in `memory.json`

---

## Dependencies

```
crewai
crewai-tools
litellm
python-dotenv
requests
```

Install all with:
```bash
pip install crewai crewai-tools litellm python-dotenv requests
```

---

## Free Tier API Setup

| Service | Free Tier | Sign Up |
|---|---|---|
| Groq | 6,000 TPM, LLaMA 3.1 8B Instant | console.groq.com |
| Serper | 2,500 searches/month | serper.dev |

---

## Example Output

**Input:** `How AI is changing software engineering in 2025`

**Generated post (saved to outputs/):**
```
Is AI making you a better software engineer, or just better at using AI?

As we enter 2025, 78% of organizations now use AI in their workflows
(Stanford HAI Index 2025).

Yet the DORA report reveals AI amplifies both strengths and weaknesses —
it's not a shortcut, it's a multiplier.

The engineers thriving right now treat AI as a thought partner.
Not just a code generator.

They use it to rubber-duck debug, draft architecture decisions,
and write tests faster.

The skill isn't prompting. It's knowing when to trust it and when to push back.

What's your biggest use of AI in your engineering workflow? Comment below.

#AI #SoftwareEngineering #TechLeadership #FutureOfWork #GenerativeAI
```

**Engagement Score:** 83/100 — Excellent

---

## Memory System

After each run, `memory.json` is updated:

```json
{
  "total_runs": 4,
  "topic_scores": {
    "How AI is changing software engineering in 2025": {
      "best_score": 83,
      "runs": 3
    }
  },
  "runs": [...]
}
```

On subsequent runs for the same topic, the system surfaces the previous best score as a performance target.

---

## Notes

- Built on **Groq's free tier** — no paid API required
- Rate limiting may cause retries between tasks (handled automatically with 30s/60s/90s waits)
- The custom LinkedIn Engagement Scorer runs entirely in Python with no external API calls
- All generated posts are saved with timestamps so no output is ever overwritten
