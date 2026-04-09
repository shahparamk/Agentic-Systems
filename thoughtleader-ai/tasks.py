"""
tasks.py — Task Definitions for ThoughtLeader AI
==================================================
Defines the three core tasks in the pipeline:
1. Research Task — web search and brief synthesis
2. Writing Task — LinkedIn post drafting
3. Editing Task — scoring, refinement, and file saving

Each task has explicit expected_output, agent assignment,
and context linkage to the previous task.
"""

from crewai import Task


def get_research_task(agent, topic: str) -> Task:
    """
    Research Task — assigned to the Research Specialist agent.
    Instructs the agent to run multiple web searches and produce
    a structured research brief covering trends, stats, and talking points.

    Args:
        agent: The Research Specialist agent instance
        topic: The LinkedIn post topic (string)

    Returns:
        CrewAI Task object
    """
    return Task(
        description=(
            f"Research the topic: '{topic}'\n\n"
            "Steps:\n"
            "1. Use the Web Search Tool to search for recent articles, trends, and insights on this topic.\n"
            "2. Run at least 2 different search queries to gather diverse perspectives.\n"
            "3. Distill your findings into a structured research brief.\n"
            "4. The brief must include: key trends, surprising stats, common misconceptions, "
            "and 3-5 strong talking points a thought leader could use.\n\n"
            "Output: A structured research brief ready for a writer to use."
        ),
        expected_output=(
            "A research brief with:\n"
            "- 3-5 key insights and trends\n"
            "- Relevant statistics or data points\n"
            "- Strong talking points for a LinkedIn post\n"
            "- Any contrarian or surprising angles worth exploring"
        ),
        agent=agent,
    )


def get_writing_task(agent, topic: str, research_task: Task) -> Task:
    """
    Writing Task — assigned to the LinkedIn Content Writer agent.
    Uses the research brief from the Research Specialist as context.
    Produces a 150-250 word LinkedIn post with hook, body, CTA, and hashtags.

    Args:
        agent: The LinkedIn Content Writer agent instance
        topic: The LinkedIn post topic (string)
        research_task: The preceding research task (for context linking)

    Returns:
        CrewAI Task object with context from research_task
    """
    return Task(
        description=(
            f"Write a LinkedIn thought leadership post on: '{topic}'\n\n"
            "Use the research brief from the Research Specialist as your foundation.\n\n"
            "Requirements:\n"
            "1. Start with a hook — a question, bold stat, or short punchy statement (max 12 words)\n"
            "2. Write 150-250 words total — concise but substantive\n"
            "3. Use short paragraphs and line breaks for LinkedIn readability\n"
            "4. Include a personal insight or opinion — not just facts\n"
            "5. End with a clear call-to-action (e.g., 'What do you think? Comment below.')\n"
            "6. Add 3-5 relevant hashtags at the end\n\n"
            "Tone: Professional but conversational. Write like a smart human, not a robot."
        ),
        expected_output=(
            "A complete LinkedIn post (150-250 words) with:\n"
            "- Strong opening hook (max 12 words)\n"
            "- Structured body with insights from the research brief\n"
            "- Personal opinion or takeaway\n"
            "- Call-to-action\n"
            "- 3-5 relevant hashtags"
        ),
        agent=agent,
        context=[research_task],    # Passes research brief as input context
    )


def get_editing_task(agent, topic: str, writing_task: Task) -> Task:
    """
    Editing Task — assigned to the Content Editor & Optimizer agent.
    Reviews the draft, scores it with the LinkedIn Engagement Scorer,
    and saves the final post. If score < 70, the feedback loop in
    main.py handles automatic rewriting and re-scoring.

    Args:
        agent: The Content Editor & Optimizer agent instance
        topic: The LinkedIn post topic (string)
        writing_task: The preceding writing task (for context linking)

    Returns:
        CrewAI Task object with context from writing_task
    """
    return Task(
        description=(
            f"Edit, score, and finalize the LinkedIn post on: '{topic}'\n\n"
            "Steps:\n"
            "1. Review the draft from the writer for tone, clarity, and structure.\n"
            "2. Use the LinkedIn Engagement Scorer tool to score the draft.\n"
            "3. If the score is below 70, revise the post to address the feedback.\n"
            "4. Re-score if you made significant changes.\n"
            "5. Use the File Writer Tool to save the final post with filename: "
            f"'{topic.replace(' ', '_')}_linkedin_post'\n\n"
            "Output: The final polished post + its engagement score report."
        ),
        expected_output=(
            "1. The final edited LinkedIn post (ready to publish)\n"
            "2. The engagement score report showing total score and per-dimension breakdown\n"
            "3. Confirmation that the file was saved successfully"
        ),
        agent=agent,
        context=[writing_task],     # Passes draft post as input context
    )