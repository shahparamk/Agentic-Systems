import re
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class EngagementScorerInput(BaseModel):
    post_text: str = Field(description="The LinkedIn post or blog draft to score")


class LinkedInEngagementScorer(BaseTool):
    name: str = "LinkedIn Engagement Scorer"
    description: str = (
        "Scores a LinkedIn post or tech blog draft on four dimensions: "
        "hook strength, readability, hashtag usage, and call-to-action quality. "
        "Returns a total score out of 100 with per-dimension feedback."
    )
    args_schema: type[BaseModel] = EngagementScorerInput

    def _run(self, post_text: str) -> str:
        scores = {}
        feedback = {}

        # 1. Hook Strength (25pts)
        # Strong hooks: question, number, bold statement, "I", short punchy line
        first_line = post_text.strip().split("\n")[0]
        hook_score = 0
        hook_tips = []

        if "?" in first_line:
            hook_score += 10
        if any(char.isdigit() for char in first_line):
            hook_score += 8
        if len(first_line.split()) <= 12:
            hook_score += 7
        else:
            hook_tips.append("Shorten your opening line to under 12 words for more impact.")
        if first_line.startswith("I "):
            hook_score += 5
        if hook_score == 0:
            hook_tips.append("Start with a question, a bold stat, or a short punchy statement.")

        hook_score = min(hook_score, 25)
        scores["Hook Strength"] = hook_score
        feedback["Hook Strength"] = hook_tips if hook_tips else ["Strong hook!"]

        # 2. Readability (25pts)
        sentences = re.split(r'[.!?]', post_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_words = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        lines = post_text.split("\n")
        short_lines = sum(1 for l in lines if len(l.strip()) < 80 and len(l.strip()) > 0)
        line_ratio = short_lines / max(len(lines), 1)

        read_score = 0
        read_tips = []

        if avg_words <= 15:
            read_score += 15
        elif avg_words <= 20:
            read_score += 10
            read_tips.append("Try shorter sentences — aim for under 15 words on average.")
        else:
            read_score += 5
            read_tips.append("Sentences are too long. Break them up for LinkedIn readability.")

        if line_ratio >= 0.7:
            read_score += 10
        else:
            read_score += 5
            read_tips.append("Add more line breaks — white space improves LinkedIn engagement.")

        read_score = min(read_score, 25)
        scores["Readability"] = read_score
        feedback["Readability"] = read_tips if read_tips else ["Great readability!"]

        # 3. Hashtag Usage (25pts)
        hashtags = re.findall(r'#\w+', post_text)
        hash_count = len(hashtags)
        hash_score = 0
        hash_tips = []

        if 3 <= hash_count <= 5:
            hash_score = 25
        elif hash_count == 2:
            hash_score = 18
            hash_tips.append("Add 1–2 more relevant hashtags (ideal range: 3–5).")
        elif hash_count == 1:
            hash_score = 10
            hash_tips.append("Too few hashtags. Add 2–4 more relevant ones.")
        elif hash_count > 5:
            hash_score = 15
            hash_tips.append("Too many hashtags. Trim down to 3–5 for best reach.")
        else:
            hash_score = 0
            hash_tips.append("No hashtags found. Add 3–5 relevant hashtags.")

        scores["Hashtag Usage"] = hash_score
        feedback["Hashtag Usage"] = hash_tips if hash_tips else ["Hashtag usage is optimal!"]

        # 4. Call-to-Action (25pts)
        cta_phrases = [
            "comment", "share", "follow", "let me know", "what do you think",
            "drop", "thoughts", "tag", "repost", "dm me", "reach out",
            "subscribe", "click", "read more", "check out"
        ]
        post_lower = post_text.lower()
        matched_ctas = [p for p in cta_phrases if p in post_lower]
        cta_score = 0
        cta_tips = []

        if len(matched_ctas) >= 2:
            cta_score = 25
        elif len(matched_ctas) == 1:
            cta_score = 15
            cta_tips.append("Add a second CTA — e.g., 'Comment below' or 'Share with your network'.")
        else:
            cta_score = 0
            cta_tips.append("No call-to-action found. End with 'What do you think? Comment below.'")

        scores["Call-to-Action"] = cta_score
        feedback["Call-to-Action"] = cta_tips if cta_tips else ["Strong call-to-action!"]

        # Final report
        total = sum(scores.values())
        grade = "Excellent" if total >= 80 else "Good" if total >= 60 else "Needs Work"

        report = f"""
=== LinkedIn Engagement Score Report ===
Total Score: {total}/100 — {grade}

Breakdown:
  Hook Strength   : {scores['Hook Strength']}/25
  Readability     : {scores['Readability']}/25
  Hashtag Usage   : {scores['Hashtag Usage']}/25
  Call-to-Action  : {scores['Call-to-Action']}/25

Feedback:
  Hook       : {' | '.join(feedback['Hook Strength'])}
  Readability: {' | '.join(feedback['Readability'])}
  Hashtags   : {' | '.join(feedback['Hashtag Usage'])}
  CTA        : {' | '.join(feedback['Call-to-Action'])}
========================================
"""
        return report.strip()