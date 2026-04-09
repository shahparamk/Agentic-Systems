import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from config.settings import SERPER_API_KEY


class SearchInput(BaseModel):
    query: str = Field(description="Search query to look up on the web")


class SerperSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = (
        "Searches the web for recent articles, trends, and discussions on a given topic. "
        "Use this to find relevant information for research and content creation."
    )
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {"q": query, "num": 5}

        try:
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            res.raise_for_status()
            data = res.json()

            results = []
            for item in data.get("organic", []):
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                results.append(f"Title: {title}\nSummary: {snippet}\nURL: {link}")

            if not results:
                return "No results found for this query."

            return "\n\n".join(results)

        except requests.exceptions.RequestException as e:
            return f"Search failed: {str(e)}"