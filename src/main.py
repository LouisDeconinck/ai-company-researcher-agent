from apify import Actor
from apify_client import ApifyClient
import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, Tool
from pydantic_ai.settings import ModelSettings
from pydantic_ai.models.gemini import GeminiModel
from typing import List
from .models import CompanyInfo, Deps
from .prompts import RESEARCH_AGENT_SYSTEM_PROMPT
from .tools import search_google

load_dotenv()

apify_api_key = os.getenv("APIFY_API_KEY")
client = ApifyClient(apify_api_key)

model = GeminiModel('gemini-2.0-flash', provider='google-gla')

research_agent = Agent(
    model,
    result_type=CompanyInfo,
    system_prompt = RESEARCH_AGENT_SYSTEM_PROMPT,
    deps_type=Deps,
    model_settings=ModelSettings(max_tokens=1024, temperature=0),
    tools=[
        Tool(search_google, takes_ctx=True)
    ]
)

async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() 
        company_name = actor_input.get("company_name", "Apify")
        
        result = await research_agent.run(f'Research the company "{company_name}" and provide all required information', deps=Deps(client=client))
        await Actor.push_data(result.data.model_dump())
