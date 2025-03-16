from apify import Actor
from apify_client import ApifyClient
import os
import asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent, Tool
from pydantic_ai.settings import ModelSettings
from pydantic_ai.models.gemini import GeminiModel
from typing import List
from .models import CompanyInfo, BasicCompanyInfo, Deps
from .prompts import RESEARCH_AGENT_SYSTEM_PROMPT
from .tools import search_google, get_linkedin_company_profile, search_google_maps, get_trustpilot_reviews, get_similarweb_results

load_dotenv()

apify_api_key = os.getenv("APIFY_API_KEY")
client = ApifyClient(apify_api_key)

model = GeminiModel('gemini-2.0-flash', provider='google-gla')

research_agent = Agent(
    model,
    result_type=BasicCompanyInfo,
    system_prompt = RESEARCH_AGENT_SYSTEM_PROMPT,
    deps_type=Deps,
    model_settings=ModelSettings(temperature=0),
    tools=[
        Tool(search_google, takes_ctx=True)
    ],
    end_strategy='early'
)

async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() 
        company_name = actor_input.get("company_name")
        
        result = await research_agent.run(f'Research the company "{company_name}" and provide all required information', deps=Deps(client=client))
        
        # Create a CompanyInfo object from the BasicCompanyInfo result
        company_info = CompanyInfo(
            company_name=result.data.company_name,
            website_url=result.data.website_url,
            short_description=result.data.short_description,
            key_employees=result.data.key_employees,
            competitors=result.data.competitors,
            latest_news=result.data.latest_news,
            linkedin_url=result.data.linkedin_url,
            twitter_url=result.data.twitter_url,
            facebook_url=result.data.facebook_url,
            instagram_url=result.data.instagram_url,
            youtube_url=result.data.youtube_url
        )
        
        tasks = []
        
        if company_info.linkedin_url:
            tasks.append(get_linkedin_company_profile(client, company_info.linkedin_url))
        
        if company_info.website_url:
            tasks.append(get_trustpilot_reviews(client, company_info.website_url))
            tasks.append(get_similarweb_results(client, company_info.website_url))
        
        if tasks:
            results = await asyncio.gather(*tasks)
            
            # Assign results based on task index to avoid incorrect assignments
            result_index = 0
            
            if company_info.linkedin_url:
                company_info.linkedin_data = results[result_index]
                result_index += 1
            
            if company_info.website_url:
                company_info.trustpilot_data = results[result_index]
                result_index += 1
                company_info.similarweb_data = results[result_index]
        
            # Check if we have an address in linkedin_data or similarweb_data
            address = None
            if company_info.linkedin_data and company_info.linkedin_data.address:
                address = company_info.linkedin_data.address
            elif company_info.similarweb_data and company_info.similarweb_data.address:
                address = company_info.similarweb_data.address
                
            if address:
                # Include company name to improve search results
                maps_query = f"{company_name} {address}"
                company_info.google_maps_data = await search_google_maps(client, maps_query)
        
        await Actor.push_data(company_info.model_dump())
