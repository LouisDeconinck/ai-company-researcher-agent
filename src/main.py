from apify import Actor
from apify_client import ApifyClient
import os
import asyncio
import json
from dotenv import load_dotenv
from pydantic_ai import Agent, Tool
from pydantic_ai.settings import ModelSettings
from pydantic_ai.models.gemini import GeminiModel
from typing import List, Dict, Any
from .models import CompanyInfo, BasicCompanyInfo, Deps
from .prompts import RESEARCH_AGENT_SYSTEM_PROMPT, BUSINESS_REPORT_AGENT_SYSTEM_PROMPT
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

business_report_agent = Agent(
    model,
    system_prompt=BUSINESS_REPORT_AGENT_SYSTEM_PROMPT,
)

def prepare_company_data_for_report(company_info: CompanyInfo) -> Dict[str, Any]:
    """Prepare a clean dictionary of company data for the report agent."""
    data = company_info.model_dump()
    
    # Convert nested models to dictionaries for better readability
    if "linkedin_data" in data and data["linkedin_data"]:
        data["linkedin_data"] = company_info.linkedin_data.model_dump()
    
    if "similarweb_data" in data and data["similarweb_data"]:
        data["similarweb_data"] = company_info.similarweb_data.model_dump()
    
    # Convert lists of models to lists of dictionaries
    if "trustpilot_data" in data and data["trustpilot_data"]:
        data["trustpilot_data"] = [review.model_dump() for review in company_info.trustpilot_data]
    
    if "google_maps_data" in data and data["google_maps_data"]:
        data["google_maps_data"] = [place.model_dump() for place in company_info.google_maps_data]
    
    if "key_employees" in data and data["key_employees"]:
        data["key_employees"] = [employee.model_dump() for employee in company_info.key_employees]
    
    if "latest_news" in data and data["latest_news"]:
        data["latest_news"] = [news.model_dump() for news in company_info.latest_news]
    
    return data

async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() 
        company_name = actor_input.get("company_name")
        
        await Actor.charge('init', 1)
        
        result = await research_agent.run(f'Research the company "{company_name}" and provide all required information', deps=Deps(client=client))
        
        usage = result.usage()
        if usage and usage.total_tokens > 0:
            await Actor.charge(event_name='llm-tokens', count=usage.total_tokens)

        # Convert social_media from string to dict if needed
        social_media = {}
        if result.data.social_media and isinstance(result.data.social_media, str):
            try:
                social_media = json.loads(result.data.social_media)
            except json.JSONDecodeError:
                social_media = {"social_media_raw": result.data.social_media}
        
        # Convert extra_data from string to dict if needed
        extra_data = {}
        if result.data.extra_data and isinstance(result.data.extra_data, str):
            try:
                extra_data = json.loads(result.data.extra_data)
            except json.JSONDecodeError:
                extra_data = {"extra_data_raw": result.data.extra_data}

        # Create a CompanyInfo object from the BasicCompanyInfo result
        company_info = CompanyInfo(
            company_name=result.data.company_name,
            website_url=result.data.website_url,
            short_description=result.data.short_description,
            
            # New fields
            industry=result.data.industry,
            business_model=result.data.business_model,
            target_market=result.data.target_market,
            products_services=result.data.products_services,
            founding_year=result.data.founding_year,
            funding_information=result.data.funding_information,
            estimated_revenue=result.data.estimated_revenue,
            key_employees=result.data.key_employees,
            employee_count=result.data.employee_count,
            headquarters_location=result.data.headquarters_location,
            competitors=result.data.competitors,
            market_position=result.data.market_position,
            social_media=result.data.social_media,
            
            # Traditional fields
            linkedin_url=result.data.linkedin_url,
            twitter_url=result.data.twitter_url,
            facebook_url=result.data.facebook_url,
            instagram_url=result.data.instagram_url,
            youtube_url=result.data.youtube_url,
            
            latest_news=result.data.latest_news,
            extra_data=result.data.extra_data
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
        
        # Generate the business report using the collected data
        Actor.log.info("Generating comprehensive business report...")
        company_data = prepare_company_data_for_report(company_info)
        
        report_prompt = f"""
        Generate a comprehensive business report for {company_name}.
        
        Use all the following company data to inform your analysis:
        
        ```json
        {json.dumps(company_data, indent=2, default=str)}
        ```
        
        Create a flexible report that adapts to the available information. Focus on providing meaningful 
        insights about the company based on the data collected. Use relevant business analysis frameworks 
        that make sense for this company and the available information.
        
        The report should be well-structured in markdown format with clear headings and subheadings.
        """
        
        report_result = await business_report_agent.run(report_prompt)
        
        usage = report_result.usage()
        if usage and usage.total_tokens > 0:
            await Actor.charge(event_name='llm-tokens', count=usage.total_tokens)
        
        # Extract the report content safely
        if isinstance(report_result.data, str):
            company_info.report = report_result.data
        elif hasattr(report_result.data, 'report'):
            company_info.report = report_result.data.report
        else:
            # Try to get the report as a dictionary attribute
            try:
                report_data = getattr(report_result.data, 'model_dump', lambda: {})()
                company_info.report = report_data.get('report', str(report_result.data))
            except Exception as e:
                Actor.log.warning(f"Could not extract report from result: {str(e)}")
                company_info.report = str(report_result.data)
        
        # Save the report to KV store
        try:
            default_store = await Actor.open_key_value_store()
            Actor.log.info("Saving business report to KV store...")
            await default_store.set_value(
                "report.md", 
                company_info.report,
                content_type="text/markdown"
            )
            Actor.log.info("Business report saved successfully")
        except Exception as e:
            Actor.log.error(f"Failed to save business report to KV store: {str(e)}")
        
        # Push complete data including the report to the default dataset
        await Actor.push_data(company_info.model_dump())
