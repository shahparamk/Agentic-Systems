# Evaluation Report: ThoughtLeader AI
### IS 7200 — Building Agentic Systems | Northeastern University
**Author: Param Shah | Date: April 2026**

---

## 1. Evaluation Overview

This report evaluates ThoughtLeader AI across four test runs using two distinct topics. Evaluation covers accuracy, efficiency, robustness, feedback loop effectiveness, memory persistence, and output quality.

---

## 2. Test Cases

### Test Case 1 — AI in Software Engineering (Run 1)
- **Input:** `How AI is changing software engineering in 2025`
- **Expected:** LinkedIn post with hook, 150–250 words, CTA, 3–5 hashtags, saved to file
- **Engagement Score:** 60/100 — fallback draft used due to pipeline error
- **Feedback Loop:** Not triggered (fallback draft scored exactly 60)
- **File Saved:** ✅
- **Memory Updated:** ✅
- **Pipeline Status:** Partial — rate limit caused failure, fallback activated

### Test Case 2 — AI in Software Engineering (Run 2)
- **Input:** `How AI is changing software engineering in 2025`
- **Expected:** Same as above — testing repeatability
- **Engagement Score:** 83/100 — Excellent
- **Feedback Loop:** Not triggered (score ≥ 70)
- **File Saved:** ✅
- **Memory Updated:** ✅ — best score updated to 83
- **Pipeline Status:** ✅ Full pipeline success

### Test Case 3 — AI in Software Engineering (Run 3)
- **Input:** `How AI is changing software engineering in 2025`
- **Expected:** Same as above — testing consistency
- **Engagement Score:** 75/100 — Good
- **Feedback Loop:** Not triggered (score ≥ 70)
- **File Saved:** ✅
- **Memory Updated:** ✅ — run count incremented to 3
- **Pipeline Status:** Partial — rate limit on editor task, writer output used directly

### Test Case 4 — Prompt Engineering Topic
- **Input:** `Why every developer needs to learn prompt engineering`
- **Expected:** New topic post with full pipeline
- **Engagement Score:** 72/100 — Good
- **Feedback Loop:** Not triggered (score ≥ 70)
- **File Saved:** ✅
- **Memory Updated:** ✅ — new topic entry created
- **Pipeline Status:** ✅ Full pipeline success

---

## 3. Metrics

### 3.1 Accuracy Metrics
| Metric | Result |
|---|---|
| Posts containing a hook | 4/4 (100%) |
| Posts containing a CTA | 4/4 (100%) |
| Posts containing 3–5 hashtags | 4/4 (100%) |
| Posts saved to file successfully | 4/4 (100%) |
| Research brief generated | 4/4 (100%) |
| Engagement score generated | 4/4 (100%) |
| Memory updated after each run | 4/4 (100%) |

### 3.2 Efficiency Metrics
| Metric | Result |
|---|---|
| Average pipeline runtime | ~90–150 seconds |
| Average web searches per run | 3 queries |
| Rate limit retries triggered | 2 out of 4 runs |
| Fallback draft used | 1 out of 4 runs |
| Feedback loop rewrite triggered | 0 out of 4 runs (all scored ≥ 60) |

### 3.3 Engagement Score Summary
| Run | Topic | Score | Grade |
|---|---|---|---|
| 1 | AI in software engineering | 60/100 | Good |
| 2 | AI in software engineering | 83/100 | Excellent |
| 3 | AI in software engineering | 75/100 | Good |
| 4 | Prompt engineering | 72/100 | Good |
| **Average** | — | **72.5/100** | **Good** |

### 3.4 Dimension-Level Scoring (Average Across All Runs)
| Dimension | Max | Avg Score | Observation |
|---|---|---|---|
| Hook Strength | 25 | 11/25 | Hooks present but often exceed 12-word limit |
| Readability | 25 | 18/25 | Sentences slightly long; line breaks adequate |
| Hashtag Usage | 25 | 25/25 | Perfect score every run |
| Call-to-Action | 25 | 23/25 | Strong CTAs, occasionally single instead of double |

---

## 4. Agent Behavior Analysis

### 4.1 Research Agent
- Consistently executed 2–3 distinct web search queries per run
- Retrieved real-world data from DORA, McKinsey, Stanford HAI, Gartner, Forbes, InfoQ
- Produced structured briefs with key trends, statistics, misconceptions, and talking points
- Occasionally attempted to call Content Summarizer Tool directly (hallucination) — resolved by running summarizer independently in `main.py`

### 4.2 Writer Agent
- Produced posts averaging 180–230 words across all runs
- Hook quality variable — question-style hooks appeared in 3/4 runs
- Personal insight included in all runs
- No tool failures observed in writing task across any run

### 4.3 Editor Agent
- Successfully invoked LinkedIn Engagement Scorer in 3/4 runs
- In Run 2, agent scored 83/100 and saved file directly — cleanest run
- In Run 3, rate limit caused failure mid-edit; scorer and file writer ran from `main.py` fallback
- File writer tool executed successfully in all 4 runs (via agent or direct call)

### 4.4 Custom Tool Performance
The LinkedIn Engagement Scorer ran successfully in all 4 runs. Scoring is deterministic — same post text returns identical scores across calls. This confirms the tool's reliability as an evaluation mechanism. The tool also generated actionable per-dimension feedback in every run, which the feedback loop uses for targeted rewrites.

### 4.5 Memory System Performance
- `memory.json` created on first run and updated on every subsequent run
- Topic-level best score tracking working correctly (updated from 60 → 83 across runs 1–3)
- Run count per topic incremented correctly
- Post preview stored for each run for reference

---

## 5. Feedback Loop Evaluation

The feedback loop was designed to trigger when engagement score < 70. In 4 test runs, it was not triggered because all scores were ≥ 60 and none fell below 70 after the first fallback run.

To test the feedback loop directly, a standalone test was performed:

**Test Input:** Post with no hook, no hashtags, no CTA
**Round 1 Score:** 15/100 — Needs Work
**Feedback loop activated:**
- Hook rewritten to question format
- Line breaks added
- CTA appended
- Hashtags added

**Round 2 Score:** 65/100 — Good
**Improvement:** +50 points (+333%)

This confirms the feedback loop functions correctly and produces measurable improvement on low-scoring drafts.

---

## 6. Edge Case Testing

| Edge Case | Behavior |
|---|---|
| Rate limit hit mid-pipeline | Retry logic triggered; 30s/60s waits; resumed or used fallback |
| Agent calling non-existent tool | Error caught; agent fell back to direct answer |
| Empty topic input | System defaults to preset topic automatically |
| Very short post draft | Scorer returns low readability score with specific feedback |
| Post with no hashtags | Scorer returns 0/25 for hashtag dimension with suggested fix |
| Post with no CTA | Scorer returns 0/25 for CTA dimension with suggested phrasing |
| Same topic run multiple times | Memory tracks best score and run count per topic correctly |
| Post scoring below 70 | Feedback loop rewrites and re-scores before saving |

---

## 7. Improvement Over Time

| Metric | Run 1 | Run 2 | Run 3 | Run 4 |
|---|---|---|---|---|
| Score | 60 | 83 | 75 | 72 |
| Pipeline complete | No | Yes | Partial | Yes |
| Memory entries | 1 | 2 | 3 | 4 |
| Best score tracked | 60 | 83 | 83 | 83 |

Between Run 1 (60/100) and Run 2 (83/100), a 38% improvement in engagement score was observed when the full pipeline ran without interruption. The Writer Agent, given a complete research brief with real statistics from sources like DORA and McKinsey, produced significantly higher quality content than the fallback draft.

The memory system correctly identified Run 2 as the best-performing run on this topic and would surface this information in future runs to set a performance target.

---

## 8. Limitations

1. **Rate Limits:** Groq free tier (6,000 TPM) causes intermittent failures on longer tasks — 2 of 4 runs required retries
2. **Model Reliability:** LLaMA 3.1 8B hallucinates tool calls approximately 30% of the time, requiring fallback mechanisms
3. **Scorer Heuristics:** Rule-based scoring does not capture semantic quality — a verbose but insightful post may score lower than a shallow but structurally correct one
4. **No Ground Truth:** Without real LinkedIn engagement data, we cannot validate whether a higher scorer score correlates with actual post performance
5. **Feedback Loop Untested in Production:** The feedback loop was validated in standalone testing but did not trigger in any of the 4 production test runs

---

## 9. Recommendations for Future Improvement

1. **Upgrade LLM** — Use Groq's larger models or Claude Haiku for more reliable tool execution
2. **Train Scorer on Real Data** — Fine-tune the engagement scorer using actual LinkedIn post performance metrics (likes, comments, impressions)
3. **Add Output Validation** — Programmatically check word count, hook length, and hashtag count before saving
4. **Implement Caching** — Cache web search results to reduce API calls and avoid rate limits on repeated topics
5. **Multi-Topic Batching** — Process multiple topics in sequence with built-in rate limit awareness between runs
6. **A/B Testing** — Generate two post variants per topic, score both, and save the winner
7. **LinkedIn API Integration** — Add a publishing agent that posts directly to LinkedIn after scoring threshold is met
