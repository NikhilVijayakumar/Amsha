from crewai.tools import BaseTool
from duckduckgo_search import DDGS

class DuckDuckGoSearchTool(BaseTool):
    name: str = "DuckDuckGo Search Tool"
    description: str = "Performs a web search using DuckDuckGo and returns the top non-sponsored, non-ad results."

    def _run(self, query: str) -> str:
        with DDGS() as ddgs:
            raw_results = ddgs.text(query, max_results=10)

            # Filter out ads and sponsored results
            filtered_results = [
                result for result in raw_results
                if result.get('type') != 'ad' and not result.get('source', '').startswith('sponsored')
            ]

            if not filtered_results:
                return "No organic (non-sponsored) results found."

            top_results = filtered_results[:5]

            formatted_results = ""
            for idx, result in enumerate(top_results, start=1):
                title = result.get('title', 'No title')
                url = result.get('href', 'No URL')
                snippet = result.get('body', 'No snippet')
                formatted_results += f"{idx}. {title}\nURL: {url}\nSnippet: {snippet}\n\n"

            return formatted_results.strip()
