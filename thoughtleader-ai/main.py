"""
ThoughtLeader AI — Main Pipeline
=================================
Entry point for the multi-agent LinkedIn content creation system.
Orchestrates the full pipeline: Research → Write → Edit → Score → Save.

Features:
- Sequential multi-agent execution via CrewAI
- Automatic retry on rate limit errors
- Feedback loop: rewrites post if engagement score < 70
- Persistent JSON memory: tracks topics, scores, and outputs across runs
- Fallback draft if pipeline fails
"""

import time
import os
import json
import re
from datetime import datetime
from crewai import Crew, Process
from agents import (
    get_controller_agent,
    get_research_agent,
    get_writer_agent,
    get_editor_agent,
)
from tasks import get_research_task, get_writing_task, get_editing_task
from tools.engagement_scorer import LinkedInEngagementScorer
from tools.file_writer_tool import FileWriterTool
from tools.summarizer_tool import ContentSummarizerTool

# Disable CrewAI telemetry
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["CREWAI_STORAGE_DIR"] = "./crewai_storage"

# Memory file path — persists across runs
MEMORY_FILE = "memory.json"


def load_memory() -> dict:
    """Load persistent memory from JSON file.
    Memory stores past topics, scores, and generated posts.
    Returns empty structure if file doesn't exist."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"runs": [], "topic_scores": {}, "total_runs": 0}


def save_memory(memory: dict):
    """Persist memory to JSON file after each run."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def extract_score(report: str) -> int:
    """Extract numeric total score from engagement score report string."""
    match = re.search(r"Total Score:\s*(\d+)/100", report)
    return int(match.group(1)) if match else 0


def rewrite_post_for_score(draft: str, score_report: str, topic: str) -> str:
    """
    Feedback loop: if score < 70, rewrite the post to address feedback.
    Parses the score report for weak dimensions and rewrites accordingly.
    This is the core improvement mechanism — agents learn from scorer feedback.
    """
    print("\n⚡ Score below 70 — activating feedback loop rewrite...")

    # Parse which dimensions scored low
    hook_low = "Hook" in score_report and ("0/25" in score_report.split("Hook")[1][:50]
                                            or "Shorten" in score_report)
    read_low = "Readability" in score_report and "shorter" in score_report.lower()
    cta_low = "Call-to-Action" in score_report and "Add" in score_report.split("Call-to-Action")[1][:100]
    hash_low = "hashtag" in score_report.lower() and ("few" in score_report.lower()
                                                       or "No hashtags" in score_report)

    lines = draft.strip().split("\n")
    improved_lines = []

    # Fix hook — make first line a question if it's not already
    first_line = lines[0].strip() if lines else ""
    if hook_low:
        if "?" not in first_line:
            # Convert statement to question format
            improved_lines.append(f"Is this the most important skill in tech right now?")
        else:
            # Shorten the hook
            words = first_line.split()
            improved_lines.append(" ".join(words[:10]) + "?")
    else:
        improved_lines.append(first_line)

    # Add blank line after hook for readability
    improved_lines.append("")

    # Process body — shorten long sentences, add line breaks
    for line in lines[1:]:
        if read_low and len(line.split()) > 20:
            # Split long lines at natural break points
            words = line.split()
            mid = len(words) // 2
            improved_lines.append(" ".join(words[:mid]))
            improved_lines.append(" ".join(words[mid:]))
        else:
            improved_lines.append(line)

    rewritten = "\n".join(improved_lines)

    # Fix CTA — append if missing
    if cta_low and "comment" not in rewritten.lower() and "share" not in rewritten.lower():
        rewritten += "\n\nWhat do you think? Comment below and share with your network."

    # Fix hashtags — append if missing or insufficient
    existing_hashtags = re.findall(r"#\w+", rewritten)
    if hash_low or len(existing_hashtags) < 3:
        topic_words = [w.capitalize() for w in topic.split()[:3]]
        extra_tags = " ".join([f"#{w}" for w in topic_words])
        rewritten += f"\n\n{extra_tags} #AI #ThoughtLeadership"

    return rewritten


def run_pipeline(topic: str):
    """
    Main pipeline function.
    1. Loads persistent memory
    2. Runs CrewAI multi-agent pipeline
    3. Summarizes research output
    4. Scores the generated post
    5. Applies feedback loop rewrite if score < 70
    6. Saves output to file and updates memory
    """
    print(f"\n{'='*50}")
    print(f"  ThoughtLeader AI — Starting Pipeline")
    print(f"  Topic: {topic}")
    print(f"{'='*50}\n")

    # Load persistent memory
    memory = load_memory()
    print(f"📚 Memory loaded — {memory['total_runs']} previous runs found.")

    # Check if we've run this topic before
    if topic in memory["topic_scores"]:
        prev = memory["topic_scores"][topic]
        print(f"💡 Previous run on this topic scored {prev['best_score']}/100. Aiming higher.\n")

    # Initialize agents
    controller = get_controller_agent()
    researcher = get_research_agent()
    writer = get_writer_agent()
    editor = get_editor_agent()

    # Initialize tasks
    research_task = get_research_task(researcher, topic)
    writing_task = get_writing_task(writer, topic, research_task)
    editing_task = get_editing_task(editor, topic, writing_task)

    # Assemble crew with memory disabled (handled via JSON memory instead)
    crew = Crew(
        agents=[controller, researcher, writer, editor],
        tasks=[research_task, writing_task, editing_task],
        process=Process.sequential,
        verbose=True,
        manager_agent=controller,
        memory=False,
    )

    # Run pipeline with retry on rate limit
    result = None
    for attempt in range(3):
        try:
            result = crew.kickoff()
            break
        except Exception as e:
            err = str(e)
            if "rate_limit" in err.lower() or "429" in err:
                wait = 30 * (attempt + 1)
                print(f"\n⏳ Rate limit hit. Waiting {wait}s before retry {attempt+1}/3...\n")
                time.sleep(wait)
            else:
                print(f"\n❌ Pipeline error: {err}")
                break

    # Run summarizer directly on research output
    research_raw = research_task.output.raw if research_task.output else ""
    if research_raw:
        print("\n--- Running Content Summarizer ---")
        summarizer = ContentSummarizerTool()
        brief = summarizer._run(text=research_raw, topic=topic)
        print(brief)

    # Extract written post — prefer writer output, fallback to preset
    draft = ""
    if writing_task.output and writing_task.output.raw:
        draft = writing_task.output.raw
    elif result:
        draft = str(result)

    if not draft:
        draft = (
            f"Is this the most important skill in tech right now?\n\n"
            f"AI is not replacing software engineers — it's replacing those who don't use AI.\n\n"
            f"In 2025, 90% of engineering teams use AI coding tools (up from 61% last year).\n\n"
            f"Yet most developers still treat AI as an autocomplete tool.\n\n"
            f"The engineers thriving right now treat AI as a thought partner — not just a code generator.\n\n"
            f"They use it to rubber-duck debug, draft architecture decisions, and write tests faster.\n\n"
            f"The skill isn't prompting. It's knowing when to trust it and when to push back.\n\n"
            f"What's your biggest use of AI in your engineering workflow? Comment below.\n\n"
            f"#AI #SoftwareEngineering #TechLeadership #FutureOfWork #GenerativeAI"
        )
        print("\n⚠️  Using fallback post draft.\n")

    # === FEEDBACK LOOP ===
    # Score the draft — if below 70, rewrite and re-score
    print("\n--- Running LinkedIn Engagement Scorer (Round 1) ---")
    scorer = LinkedInEngagementScorer()
    score_report = scorer._run(draft)
    print(score_report)

    score = extract_score(score_report)
    final_draft = draft
    final_report = score_report
    rewrote = False

    if score < 70:
        # Apply feedback loop rewrite
        improved_draft = rewrite_post_for_score(draft, score_report, topic)
        print("\n--- Re-scoring after feedback loop rewrite ---")
        improved_report = scorer._run(improved_draft)
        print(improved_report)

        improved_score = extract_score(improved_report)

        # Use whichever version scored higher
        if improved_score >= score:
            print(f"\n✅ Feedback loop improved score: {score} → {improved_score}")
            final_draft = improved_draft
            final_report = improved_report
            score = improved_score
            rewrote = True
        else:
            print(f"\n⚠️  Rewrite did not improve score ({improved_score} vs {score}). Keeping original.")

    # Save final post to file
    print("\n--- Saving Final Post to File ---")
    file_writer = FileWriterTool()
    filename = topic.replace(" ", "_")[:50] + "_linkedin_post"
    save_result = file_writer._run(content=final_draft, filename=filename)
    print(save_result)

    # === UPDATE PERSISTENT MEMORY ===
    run_record = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "score": score,
        "rewrote": rewrote,
        "filename": filename,
        "post_preview": final_draft[:100] + "...",
    }
    memory["runs"].append(run_record)
    memory["total_runs"] += 1

    # Track best score per topic
    if topic not in memory["topic_scores"]:
        memory["topic_scores"][topic] = {"best_score": score, "runs": 1}
    else:
        memory["topic_scores"][topic]["runs"] += 1
        if score > memory["topic_scores"][topic]["best_score"]:
            memory["topic_scores"][topic]["best_score"] = score

    save_memory(memory)
    print(f"\n💾 Memory updated — run #{memory['total_runs']} saved to {MEMORY_FILE}")

    print(f"\n{'='*50}")
    print(f"  Pipeline Complete! Final Score: {score}/100")
    print(f"{'='*50}\n")
    return final_draft


if __name__ == "__main__":
    topic = input("Enter a topic for your LinkedIn post: ").strip()
    if not topic:
        topic = "How AI is changing software engineering in 2025"
    run_pipeline(topic)