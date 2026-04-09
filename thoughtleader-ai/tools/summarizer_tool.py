from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import re


class SummarizerInput(BaseModel):
    text: str = Field(description="Raw text content to summarize into a research brief")
    topic: str = Field(description="The main topic for context")


class ContentSummarizerTool(BaseTool):
    name: str = "Content Summarizer Tool"
    description: str = (
        "Summarizes raw search results or long text into a concise research brief. "
        "Extracts key insights, trends, and talking points relevant to the topic."
    )
    args_schema: type[BaseModel] = SummarizerInput

    def _run(self, text: str, topic: str) -> str:
        # Split into chunks by double newline or result blocks
        blocks = [b.strip() for b in re.split(r'\n{2,}', text) if b.strip()]

        # Extract sentences that contain meaningful content
        insights = []
        keywords = topic.lower().split()

        for block in blocks:
            sentences = re.split(r'(?<=[.!?])\s+', block)
            for sentence in sentences:
                s_lower = sentence.lower()
                if any(kw in s_lower for kw in keywords):
                    cleaned = sentence.strip()
                    if len(cleaned) > 30 and cleaned not in insights:
                        insights.append(cleaned)

        # Fallback: just take first sentence of each block
        if len(insights) < 3:
            for block in blocks:
                first = block.split(".")[0].strip()
                if len(first) > 30 and first not in insights:
                    insights.append(first)

        insights = insights[:8]  # cap at 8 insights

        brief = f"=== Research Brief: {topic} ===\n\n"
        brief += "Key Insights & Talking Points:\n"
        for i, insight in enumerate(insights, 1):
            brief += f"{i}. {insight}\n"
        brief += f"\nTotal sources summarized: {text.count('URL:')}"

        return brief