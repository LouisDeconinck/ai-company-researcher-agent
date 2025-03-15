from apify import Actor
from apify_client import ApifyClient
import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from typing import List
from .models import CompanyInfo, Deps
from .prompts import RESEARCH_AGENT_SYSTEM_PROMPT

# Load environment variables from .env file
load_dotenv()

apify_api_key = os.getenv("APIFY_API_KEY")
client = ApifyClient(apify_api_key)

model = GeminiModel('gemini-2.0-flash', provider='google-gla', api_key=gemini_api_key)
research_agent = Agent(
    model,
    result_type=CompanyInfo,
    system_prompt = RESEARCH_AGENT_SYSTEM_PROMPT,
    deps_type=Deps
)

@research_agent.tool
async def search_google(ctx: RunContext[Deps], query: str) -> List[str]:
    """Search Google for the given query and return the results as a list of strings.
    
    Args:
        ctx: The run context containing dependencies
        query: The query to search for
        
    Returns:
        A list of strings containing the search results
    """
    Actor.log.info(f"Searching Google for {query}")
    run_input = {
        "query": query,
        "maxResults": 10,
        "outputFormats": ["markdown"],
        "scrapingTool": "raw-http",
    }
    run = ctx.deps.client.actor("apify/rag-web-browser").call(run_input=run_input)
    
    # Get the raw items from ListPage and convert to list of strings
    list_page = ctx.deps.client.dataset(run["defaultDatasetId"]).list_items()
    results = []
    
    for item in list_page.items:
        if not isinstance(item, dict):
            continue
            
        # Create a formatted result with the most useful information
        formatted_result = ""
        
        # Add title and URL if available
        if "searchResult" in item and isinstance(item["searchResult"], dict):
            if "title" in item["searchResult"]:
                formatted_result += f"# {item['searchResult']['title']}\n\n"
            if "url" in item["searchResult"]:
                formatted_result += f"URL: {item['searchResult']['url']}\n\n"
            if "description" in item["searchResult"]:
                formatted_result += f"Description: {item['searchResult']['description']}\n\n"
        
        # Add metadata if available
        if "metadata" in item and isinstance(item["metadata"], dict):
            if "author" in item["metadata"] and item["metadata"]["author"]:
                formatted_result += f"Author: {item['metadata']['author']}\n"
        
        # Add the markdown content (most useful part) if available
        if "markdown" in item and item["markdown"]:
            # Limit markdown to a reasonable length to avoid overwhelming the model
            markdown_content = item["markdown"]
            if len(markdown_content) > 5000:  # Limit to ~5000 chars
                markdown_content = markdown_content[:5000] + "...[content truncated]"
            
            formatted_result += f"Content:\n{markdown_content}\n"
        
        if formatted_result:
            results.append(formatted_result)
            
    Actor.log.info(f"Found {len(results)} formatted search results")
    return results

async def main() -> None:
    async with Actor:
        # Get input asynchronously
        actor_input = await Actor.get_input() 
        
        # Extract company_name from input
        company_name = actor_input.get("company_name", "Apify")
        
        # Use async run instead of run_sync
        result = await research_agent.run(f'Research the company "{company_name}" and provide all required information', deps=Deps(client=client))
        print(f"Researched information for {company_name}")
        
        # The result.data will already be a CompanyInfo object, no need for manual formatting
        await Actor.push_data(result.data.model_dump())
