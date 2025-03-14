from apify import Actor
import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Define Pydantic models for structured output
class Executive(BaseModel):
    name: str
    position: str

class NewsItem(BaseModel):
    title: str
    description: str
    url: str

class SocialMedia(BaseModel):
    platform: str
    handle: str

class CompanyInfo(BaseModel):
    company_name: str
    website_url: str
    hq_location: str
    year_founded: int
    industry: str
    short_description: str
    executives: List[Executive]
    employee_count: int
    social_media: List[SocialMedia]
    competitors: List[str]
    latest_news: List[NewsItem]
    job_listings_count: int

# Get API key from environment or pass directly
api_key = os.getenv("GEMINI_API_KEY")
model = GeminiModel('gemini-2.0-flash', provider='google-gla', api_key=api_key)
agent = Agent(
    model,
    result_type=CompanyInfo,
    system_prompt = '''You are a company research agent. Your task is to gather comprehensive information 
    about companies. Be thorough in your research and provide accurate details about the company
    including its operations, leadership, social presence, and recent developments.
    
    Always return a complete structured response with all the requested fields.
    If information for certain fields is not available, use reasonable estimates or indicate "Unknown".
    For social media handles, include major platforms like LinkedIn, Twitter, Facebook, etc.
    For competitors, list at least 3-5 major competitors if available.
    For latest news, find the most recent 3-5 news articles about the company.'''
)

async def main() -> None:
    async with Actor:
        # Get input asynchronously
        actor_input = await Actor.get_input() 
        
        # Extract company_name from input
        company_name = actor_input.get("company_name", "Apify")
        
        # Use async run instead of run_sync
        result = await agent.run(f'Research the company "{company_name}" and provide all required information')
        print(f"Researched information for {company_name}")
        
        # The result.data will already be a CompanyInfo object, no need for manual formatting
        await Actor.push_data(result.data.model_dump())
