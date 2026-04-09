# Technical Report: ThoughtLeader AI
### Agentic LinkedIn & Tech Blog Content Pipeline
**IS 7200 — Building Agentic Systems | Northeastern University**
**Author: Param Shah | Date: April 2026**

---

## 1. System Overview

ThoughtLeader AI is a multi-agent content creation system built using **CrewAI** on Python. The system accepts a topic as input and autonomously produces a polished, LinkedIn-ready thought leadership post by orchestrating a pipeline of specialized agents, built-in tools, and a custom-built engagement scoring tool.

**Platform:** CrewAI (Python)
**Domain:** Content Creation — LinkedIn Thought Leadership
**LLM Backend:** Groq API (LLaMA 3.1 8B Instant)
**Search Backend:** Serper.dev API
**Memory:** Persistent JSON-based memory across runs

---

## 2. System Architecture

```
User Input (Topic)
       │
       ▼
┌─────────────────────────────────────────┐
│         Controller Agent                │
│   (Orchestrator — manages pipeline)     │
└──────────────┬──────────────────────────┘
               │ Sequential Process
       ┌───────▼────────┐
       │ Research Agent  │──► Web Search Tool (x3 queries)
       │                 │──► Content Summarizer Tool
       └───────┬─────────┘
               │ Research Brief
       ┌───────▼────────┐
       │  Writer Agent   │──► Drafts LinkedIn Post (150-250 words)
       └───────┬─────────┘
               │ Draft Post
       ┌───────▼────────┐
       │  Editor Agent   │──► LinkedIn Engagement Scorer (Custom)
       │                 │──► File Writer Tool
       └───────┬─────────┘
               │ Feedback Loop (rewrite if score < 70)
               ▼
       ┌───────────────────────────┐
       │  outputs/<topic>.md       │
       │  memory.json updated      │
       └───────────────────────────┘
```

**Execution Pattern:** Sequential (Research → Write → Edit → Score → Save)
**Feedback Loop:** If engagement score < 70, post is automatically rewritten and re-scored before saving.
**Memory:** Each run is stored in `memory.json` with topic, score, timestamp, and post preview.

---

## 3. Agent Roles and Responsibilities

### 3.1 Controller Agent
- **Role:** Content Pipeline Controller
- **Responsibility:** Orchestrates the full pipeline, delegates tasks to specialized agents, enforces quality standards, manages retries on failure
- **Configuration:** `allow_delegation=True`, `max_iter=3`
- **Decision Logic:** Uses sequential process — research informs writing, writing informs editing
- **Error Handling:** 3-attempt retry loop with progressive 30s/60s/90s waits on rate limit errors

### 3.2 Research Specialist Agent
- **Role:** Research Specialist
- **Responsibility:** Executes multiple web searches on the given topic, aggregates results, produces a structured research brief with key trends, statistics, talking points, and contrarian angles
- **Tools:** Web Search Tool (single tool to avoid LLM hallucinated multi-tool calls)
- **Prompting Strategy:** Backstory establishes domain expertise as a tech research analyst; task prompt enforces structured output format with explicit sections
- **Configuration:** `allow_delegation=False`, `max_iter=3`

### 3.3 LinkedIn Content Writer Agent
- **Role:** LinkedIn Content Writer
- **Responsibility:** Transforms the research brief into a compelling LinkedIn post with a strong hook (≤12 words), 150–250 word body, personal insight, call-to-action, and 3–5 hashtags
- **Tools:** None (pure generation task using context from Research Agent)
- **Prompting Strategy:** Backstory positions agent as a thought leadership ghostwriter; task prompt enforces specific structural requirements and tone guidelines
- **Configuration:** `allow_delegation=False`, `max_iter=3`

### 3.4 Content Editor & Optimizer Agent
- **Role:** Content Editor & Optimizer
- **Responsibility:** Reviews draft, scores it using the LinkedIn Engagement Scorer, saves the final output. Feedback loop in `main.py` handles automatic rewriting if score < 70
- **Tools:** LinkedIn Engagement Scorer (Custom), File Writer Tool
- **Prompting Strategy:** Backstory establishes data-driven editorial expertise; task prompt enforces specific scoring and revision workflow
- **Configuration:** `allow_delegation=False`, `max_iter=3`

---

## 4. Tool Integration and Functionality

### 4.1 Web Search Tool (Built-in)
- **File:** `tools/search_tool.py`
- **API:** Serper.dev (Google Search API wrapper)
- **Function:** Queries the web for recent articles, statistics, and discussions on the given topic
- **Parameters:** Returns top 5 organic results with title, snippet, and URL per query
- **Error Handling:** Try/catch with 10-second timeout; returns descriptive error string on failure
- **Configuration:** `SERPER_API_KEY` loaded from `.env` via `python-dotenv`

### 4.2 Content Summarizer Tool (Built-in)
- **File:** `tools/summarizer_tool.py`
- **Function:** Extracts key sentences from raw search results using keyword matching and sentence scoring
- **Parameters:** Accepts `text` (raw search output) and `topic` (for keyword context)
- **Output:** Structured research brief with up to 8 key insights
- **Error Handling:** Fallback to first sentence of each block if keyword matching yields fewer than 3 results
- **Note:** Runs directly in `main.py` after research task to guarantee execution regardless of LLM behavior

### 4.3 File Writer Tool (Built-in)
- **File:** `tools/file_writer_tool.py`
- **Function:** Saves the final post as a timestamped markdown file in the `outputs/` directory
- **Parameters:** Accepts `content` (post text) and `filename` (base name)
- **Output Format:** `outputs/<filename>_YYYYMMDD_HHMMSS.md`
- **Error Handling:** `os.makedirs` with `exist_ok=True`; returns success/failure string

### 4.4 LinkedIn Engagement Scorer — Custom Tool
- **File:** `tools/engagement_scorer.py`
- **Class:** `LinkedInEngagementScorer(BaseTool)`
- **Purpose:** Scores a LinkedIn post draft on four dimensions to provide actionable optimization feedback
- **Implementation:** Pure Python — no external API required
- **Input:** `post_text` (string) validated via Pydantic `EngagementScorerInput` schema
- **Output:** Formatted score report (string) with total score out of 100, per-dimension breakdown, and improvement tips

**Scoring Dimensions:**

| Dimension | Max Score | Method |
|---|---|---|
| Hook Strength | 25 | Checks for question mark, numbers, short line (≤12 words), first-person opening |
| Readability | 25 | Avg sentence length (≤15 words = full score), line break ratio (≥70% short lines) |
| Hashtag Usage | 25 | Regex count of `#word` patterns; optimal range 3–5 |
| Call-to-Action | 25 | Keyword matching against 15 common CTA phrases |

**Grade Thresholds:** Excellent (≥80), Good (≥60), Needs Work (<60)

**Limitations:** Rule-based heuristics; does not capture semantic quality. A well-written post with long sentences may score lower than a mediocre post with short sentences.

---

## 5. Orchestration System

### 5.1 Workflow Design
The system uses **sequential task execution** via CrewAI's `Process.sequential`. Each task passes its output as context to the next task:

```python
crew = Crew(
    agents=[controller, researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,
    manager_agent=controller,
    memory=False,
)
```

### 5.2 Feedback Loop
The core improvement mechanism — after scoring, if the post scores below 70, `main.py` calls `rewrite_post_for_score()` which:
1. Parses the score report to identify weak dimensions
2. Fixes the hook (converts to question format, shortens to ≤10 words)
3. Breaks long sentences and adds line breaks for readability
4. Appends a CTA if missing
5. Adds hashtags if count is below 3
6. Re-scores the improved draft and keeps whichever version scored higher

### 5.3 Persistent Memory System
After each run, a record is saved to `memory.json`:
```json
{
  "runs": [
    {
      "topic": "How AI is changing software engineering in 2025",
      "timestamp": "2026-04-09T02:06:53",
      "score": 72,
      "rewrote": false,
      "filename": "How_AI_is_changing_software_engineering_in_2025_linkedin_post",
      "post_preview": "AI is not replacing software engineers..."
    }
  ],
  "topic_scores": {
    "How AI is changing software engineering in 2025": {
      "best_score": 83,
      "runs": 3
    }
  },
  "total_runs": 3
}
```
This enables the system to reference past performance and inform future runs on the same topic.

### 5.4 Error Handling & Fallback Strategy
| Error Type | Handling Strategy |
|---|---|
| Groq rate limit (429) | 3 retries with 30s/60s/90s progressive waits |
| Empty pipeline output | Fallback to pre-written high-quality draft |
| Agent tool hallucination | Single tool per agent; summarizer runs directly in main.py |
| File save failure | os.makedirs with exist_ok=True; error returned as string |
| Missing API keys | Validation at startup in config/settings.py; raises ValueError |

### 5.5 Memory Management
Crew-level memory disabled (`memory=False`) due to free-tier OpenAI constraint. Context passed explicitly between tasks via `context=[previous_task]` parameter. Persistent state managed via `memory.json`.

---

## 6. Communication Protocol Between Agents

Agents communicate via CrewAI's task context system. Each task explicitly declares which prior task's output it depends on:

```python
writing_task = Task(
    description="...",
    agent=writer_agent,
    context=[research_task]   # research brief passed as input
)

editing_task = Task(
    description="...",
    agent=editor_agent,
    context=[writing_task]    # draft post passed as input
)
```

The Controller Agent manages the overall delegation order. No direct agent-to-agent messaging occurs — all communication flows through task context, ensuring clean separation of concerns.

---

## 7. Challenges and Solutions

| Challenge | Solution |
|---|---|
| Groq free tier rate limits (6,000 TPM) | Retry logic with progressive delays; reduced model from 70B to 8B |
| LLaMA 8B failing on multi-tool calls | Removed summarizer from agent tools; runs directly in main.py |
| CrewAI memory requiring OpenAI API | Set `memory=False`; added `OPENAI_API_KEY=dummy` to suppress warnings |
| Model calling non-existent tools | Simplified agent tool lists; single tool per agent |
| Output file not saving on editor failure | Forced file writer execution in main.py after crew.kickoff() |
| LLaMA 8B model deprecated | Switched from llama3-8b-8192 to llama-3.1-8b-instant |

---

## 8. System Performance

### 8.1 Test Run Results

| Run | Topic | Score | Feedback Loop | Status |
|---|---|---|---|---|
| 1 | AI in software engineering 2025 | 60/100 | Not triggered | Fallback draft used |
| 2 | AI in software engineering 2025 | 83/100 | Not triggered (score ≥ 70) | Full pipeline success |
| 3 | AI in software engineering 2025 | 75/100 | Not triggered (score ≥ 70) | Rate limit on edit, fallback to writer output |
| 4 | Why developers need prompt engineering | 72/100 | Not triggered (score ≥ 70) | Full pipeline success |

### 8.2 Average Engagement Score by Dimension

| Dimension | Max | Average | Notes |
|---|---|---|---|
| Hook Strength | 25 | 11/25 | Hooks present but often exceed 12 words |
| Readability | 25 | 18/25 | Sentence length slightly above optimal |
| Hashtag Usage | 25 | 25/25 | Consistently optimal across all runs |
| Call-to-Action | 25 | 23/25 | Strong CTAs in all runs |

### 8.3 Limitations
- **Rate Limits:** Groq free tier (6,000 TPM) caps throughput causing intermittent failures
- **Model Reliability:** LLaMA 3.1 8B occasionally hallucinates tool calls
- **Scorer Heuristics:** Rule-based scoring misses semantic quality signals
- **No Ground Truth:** Cannot validate whether higher scorer score = better real LinkedIn engagement

---

## 9. Future Improvements

1. Upgrade to Groq paid tier or Claude Haiku for more reliable tool use
2. Train engagement scorer on real LinkedIn post performance data (ML-based)
3. Add LinkedIn API integration for direct publishing
4. Implement parallel research execution for faster runs
5. Add A/B testing framework to compare post variants
6. Expand memory system to track topic performance trends over time
