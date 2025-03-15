from apify import Actor
from typing import List
from pydantic_ai import RunContext
from .models import Deps

async def search_google(ctx: RunContext[Deps], query: str, max_results: int = 1) -> List[str]:
    """Search Google for the given query and return the results as a list of strings.
    
    Args:
        ctx: The run context containing dependencies
        query: The query to search for
        max_results: The maximum number of results to return
        
    Returns:
        A list of strings containing the search results
    """
    Actor.log.info(f"Searching Google for: {query} ({max_results} results)")
    run_input = {
        "query": query,
        "maxResults": max_results,
        "outputFormats": ["markdown"],
    }
    run = ctx.deps.client.actor("apify/rag-web-browser").call(run_input=run_input, memory_mbytes=1024)
    
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
        
        # Add the markdown content (most useful part) if available
        if "markdown" in item and item["markdown"]:
            markdown_content = item["markdown"]
            
            formatted_result += f"Content:\n{markdown_content}\n"
        
        if formatted_result:
            results.append(formatted_result)
            
    # Store search results in the default KV store
    sanitized_query = query.replace(" ", "_").replace("\"", "").replace("'", "")
    kv_key = f"search_results_{sanitized_query}"
    default_store = await Actor.open_key_value_store()
    await default_store.set_value(kv_key, results)
            
    Actor.log.info(f"Found {len(results)}/{max_results} search results for: {query}")
    return results 