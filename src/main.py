from apify import Actor
from apify_client import ApifyClient
import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from pydantic import BaseModel, Field
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# Load environment variables from .env file
load_dotenv()

apify_api_key = os.getenv("APIFY_API_KEY")
client = ApifyClient(apify_api_key)

@dataclass
class Deps:
    client: ApifyClient

# Define Pydantic models for structured output
class Executive(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the company executive")
    position: Optional[str] = Field(None, description="Job title or role of the executive in the company")

class NewsItem(BaseModel):
    title: Optional[str] = Field(None, description="Headline or title of the news article")
    description: Optional[str] = Field(None, description="Brief summary or excerpt of the news content")
    url: Optional[str] = Field(None, description="Web link to the full news article")

class SocialMedia(BaseModel):
    platform: Optional[str] = Field(None, description="Name of the social media platform (e.g., LinkedIn, Twitter)")
    handle: Optional[str] = Field(None, description="Username or account name on the platform")
    url: Optional[str] = Field(None, description="Full URL to the company's profile on the platform")

class CompanyInfo(BaseModel):
    company_name: Optional[str] = Field(None, description="Official name of the company")
    website_url: Optional[str] = Field(None, description="URL of the company's official website")
    hq_location: Optional[str] = Field(None, description="City, country or full address of company headquarters")
    year_founded: Optional[int] = Field(None, description="Year when the company was established")
    industry: Optional[str] = Field(None, description="Primary business sector or industry of operation")
    short_description: Optional[str] = Field(None, description="Brief overview of the company's business and mission")
    executives: Optional[List[Executive]] = Field(default_factory=list, description="List of key company leaders and their positions")
    employee_count: Optional[int] = Field(None, description="Approximate number of employees working at the company")
    social_media: Optional[List[SocialMedia]] = Field(default_factory=list, description="Company's presence on various social media platforms")
    competitors: Optional[List[str]] = Field(default_factory=list, description="Names of major competing companies in the same industry")
    latest_news: Optional[List[NewsItem]] = Field(default_factory=list, description="Recent news articles or press releases about the company")
    job_listings_count: Optional[int] = Field(None, description="Number of open job positions currently advertised")

# Get API key from environment or pass directly
gemini_api_key = os.getenv("GEMINI_API_KEY")
model = GeminiModel('gemini-2.0-flash', provider='google-gla', api_key=gemini_api_key)
research_agent = Agent(
    model,
    result_type=CompanyInfo,
    system_prompt = '''You are a company research agent. Your task is to gather comprehensive information 
    about companies. Be thorough in your research and provide accurate details about the company
    including its operations, leadership, social presence, and recent developments.
    
    Always return a complete structured response with all the requested fields.
    If information for a field is not available, return null for that field.
    For lists like social_media, executives, competitors, or latest_news, return an empty list if no information is found.
    If you can't find any useful information about the company at all, return null for all fields except company_name.
    For social media handles, include major platforms like LinkedIn, Twitter, Facebook, etc. if available.
    For competitors, list major competitors if available.
    For latest news, find recent news articles about the company if available.''',
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
