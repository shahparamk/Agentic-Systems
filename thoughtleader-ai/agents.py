"""
agents.py — Agent Definitions for ThoughtLeader AI
====================================================
Defines all four agents in the pipeline:
- Controller Agent: orchestrates task delegation
- Research Specialist: gathers and synthesizes web information
- LinkedIn Content Writer: drafts the post from research
- Content Editor & Optimizer: scores and refines the final post
"""

from crewai import Agent
from config.settings import MODEL_NAME
from tools.search_tool import SerperSearchTool
from tools.summarizer_tool import ContentSummarizerTool
from tools.file_writer_tool import FileWriterTool
from tools.engagement_scorer import LinkedInEngagementScorer

# Instantiate tools — shared across agents
search_tool = SerperSearchTool()
summarizer_tool = ContentSummarizerTool()
file_writer_tool = FileWriterTool()
engagement_scorer = LinkedInEngagementScorer()


def get_controller_agent() -> Agent:
    """
    Controller Agent — Master orchestrator of the pipeline.
    Manages task delegation, enforces quality standards,
    and coordinates communication between specialized agents.
    Does not use tools directly — operates as a manager.
    """
    return Agent(
        role="Content Pipeline Controller",
        goal=(
            "Orchestrate the entire content creation pipeline. "
            "Delegate research, writing, and editing tasks to the right agents. "
            "Ensure the final output is high quality, well-scored, and saved."
        ),
        backstory=(
            "You are a senior content strategist with 10 years of experience managing "
            "editorial pipelines for top tech publications. You know how to coordinate "
            "teams, set clear briefs, and ensure every piece of content meets the bar "
            "before it goes live. You are decisive, organized, and quality-obsessed."
        ),
        llm=MODEL_NAME,
        verbose=True,
        allow_delegation=True,  # Can delegate to other agents
        max_iter=3,
    )


def get_research_agent() -> Agent:
    """
    Research Specialist Agent — Web research and insight synthesis.
    Runs multiple search queries and produces a structured research brief
    with key trends, statistics, talking points, and contrarian angles.
    Uses only the Web Search Tool to avoid multi-tool call failures on small LLMs.
    """
    return Agent(
        role="Research Specialist",
        goal=(
            "Search the web for the most relevant, recent, and insightful information "
            "on the given topic. Summarize findings into a clear research brief with "
            "key trends, stats, and talking points."
        ),
        backstory=(
            "You are a seasoned research analyst who has spent years gathering intelligence "
            "for top-tier tech journalists. You know how to cut through noise, identify "
            "what truly matters, and package insights into actionable briefs that writers "
            "can immediately use."
        ),
        llm=MODEL_NAME,
        tools=[search_tool],           # Single tool to prevent hallucinated tool calls
        verbose=True,
        allow_delegation=False,        # Focused specialist — no delegation
        max_iter=3,
    )


def get_writer_agent() -> Agent:
    """
    LinkedIn Content Writer Agent — Thought leadership post generation.
    Transforms the research brief into a compelling LinkedIn post with:
    strong hook, 150-250 words, personal insight, CTA, and hashtags.
    No tools needed — pure generation task from context.
    """
    return Agent(
        role="LinkedIn Content Writer",
        goal=(
            "Write a compelling, insightful LinkedIn post or tech blog article based on "
            "the research brief. The content must have a strong hook, clear structure, "
            "personal voice, and end with a call to action."
        ),
        backstory=(
            "You are a thought leadership writer who has ghostwritten viral LinkedIn posts "
            "for CTOs, VPs of Engineering, and AI researchers. You understand what makes "
            "tech professionals stop scrolling — bold openings, relatable stories, and "
            "clear takeaways. You write like a human, not a press release."
        ),
        llm=MODEL_NAME,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


def get_editor_agent() -> Agent:
    """
    Content Editor & Optimizer Agent — Quality assurance and finalization.
    Reviews the draft, scores it using the custom LinkedIn Engagement Scorer,
    and saves the final output. If score < 70, the feedback loop in main.py
    handles the rewrite automatically.
    """
    return Agent(
        role="Content Editor & Optimizer",
        goal=(
            "Review and refine the drafted content for tone, clarity, LinkedIn best practices, "
            "and engagement. Score it using the LinkedIn Engagement Scorer, incorporate feedback, "
            "and save the final polished version to a file."
        ),
        backstory=(
            "You are a meticulous editor who has optimized hundreds of LinkedIn posts for "
            "maximum reach and engagement. You know that white space matters, hooks win or lose "
            "in the first line, and every post needs a clear CTA. You use data to back your "
            "editorial decisions and never let mediocre content slide through."
        ),
        llm=MODEL_NAME,
        tools=[engagement_scorer, file_writer_tool],  # Custom tool + output tool
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )