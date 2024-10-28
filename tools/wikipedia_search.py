import wikipedia
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

from generators.LLM import LLM, LLMResponse

@dataclass
class WikipediaSearchResult:
    title: str
    content: str

class WikipediaResearcher:
    def __init__(self, llm: LLM) -> None:
        self.llm = llm

    def research(self, query: str, max_results: int = 3) -> Dict[str, any]:
        # Get research information through iterative searching
        research_response = self._perform_research(query, max_results)
        
        # Extract final information
        information = self._extract_tag(research_response.text, 'information')
        
        # Generate final answer using the LLM
        answer = self.llm.generate_text(
            system_prompt="You are a research assistant. Use the provided information to answer the question accurately and concisely.",
            prompt=f"Question: {query}\n\nResearch Information: {information}"
        )
        
        return {
            'answer': answer.text,
            'research_process': research_response.text,
            'cost': research_response.cost + answer.cost
        }

    def _perform_research(self, query: str, max_results: int) -> LLMResponse:
        system_prompt = """You are a research assistant with access to Wikipedia.
        Break down complex queries into simple searches.
        After each search, evaluate if you have enough information.
        Format your response with XML tags:
        - Use <scratchpad> for planning searches
        - Use <search_query> for each search
        - Use <search_quality> to evaluate results
        - Use <information> for final collected info
        """
        
        prompt = f"""Research this query: {query}
        
        You can search Wikipedia using <search_query>your search</search_query>.
        Keep queries short and focused.
        
        After each search, I'll provide results in <search_results> tags.
        Evaluate if you have enough information in <search_quality> tags.
        When done, summarize findings in <information> tags.
        """
        
        response = self.llm.generate_text(
            system_prompt=system_prompt,
            prompt=prompt
        )
        
        # Process any search queries
        while '<search_query>' in response.text and not '<information>' in response.text:
            search_query = self._extract_tag(response.text, 'search_query')
            search_results = self._search_wikipedia(search_query, max_results)
            
            # Continue research with results
            response = self.llm.generate_text(
                system_prompt=system_prompt,
                prompt=response.text + f"\n\n<search_results>{search_results}</search_results>"
            )
            
        return response

    def _search_wikipedia(self, query: str, max_results: int) -> str:
        """Performs Wikipedia search and formats results."""
        results: List[str] = wikipedia.search(query)
        search_results: List[WikipediaSearchResult] = []
        
        for result in results[:max_results]:
            try:
                page = wikipedia.page(result)
                search_results.append(WikipediaSearchResult(
                    title=page.title,
                    content=page.content
                ))
            except:
                continue
        
        # Format results
        formatted_results = []
        for i, result in enumerate(search_results, 1):
            formatted_results.append(
                f"Result {i}:\n"
                f"Title: {result.title}\n"
                f"Content: {result.content[:1000]}..."  # Truncate long content
            )
            
        return "\n\n".join(formatted_results)

    @staticmethod
    def _extract_tag(text: str, tag: str) -> str:
        """Extracts content between XML tags."""
        start_tag = f"<{tag}>"
        end_tag = f"</{tag}>"
        start = text.find(start_tag) + len(start_tag)
        end = text.find(end_tag)
        return text[start:end].strip() if start > -1 and end > -1 else ""

if __name__ == "__main__":
    from generators.LLM import Models, LLM
    
    # Example usage
    researcher = WikipediaResearcher(
        llm=LLM(model=Models.OpenAI.GPT4o)
    )
    
    result = researcher.research(
        query="El mito de Eco y Narciso"
    )
    
    print("Answer:", result['answer'])
    print("\nResearch Process:", result['research_process'])
    print("\nTotal Cost: $", result['cost'])
