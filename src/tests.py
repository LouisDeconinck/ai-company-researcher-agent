import unittest
import asyncio
import json
import os
from dotenv import load_dotenv
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai import Agent
from models import CompanyInfo, Employee, NewsItem, LinkedInData, SimilarwebData
from prompts import BUSINESS_REPORT_AGENT_SYSTEM_PROMPT
from pydantic import BaseModel, Field
from typing import Optional

# Load environment variables from .env file
load_dotenv()

# Define BusinessReport class that matches what the agent returns
class BusinessReport(BaseModel):
    """Business report model for storing the generated report text."""
    report: str = Field(..., description="Comprehensive business report in markdown format")

class TestBusinessReportAgent(unittest.TestCase):
    """Tests for the business report agent functionality."""

    def setUp(self):
        """Set up test environment."""
        # Initialize the model and agent
        self.model = GeminiModel('gemini-2.0-flash', provider='google-gla')
        self.business_report_agent = Agent(
            self.model,
            system_prompt=BUSINESS_REPORT_AGENT_SYSTEM_PROMPT,
            result_type=BusinessReport,
        )
        
        # Create a mock company info object for testing
        self.mock_company_info = CompanyInfo(
            company_name="Test Company Inc.",
            website_url="https://www.testcompany.com",
            short_description="A fictional company created for testing purposes. They specialize in software testing tools and services.",
            linkedin_url="https://www.linkedin.com/company/test-company",
            twitter_url="https://twitter.com/testcompany",
            facebook_url="https://www.facebook.com/testcompany",
            instagram_url="https://www.instagram.com/testcompany",
            youtube_url="https://www.youtube.com/testcompany",
            key_employees=[
                Employee(name="Jane Smith", position="CEO", linkedin_url="https://www.linkedin.com/in/janesmith"),
                Employee(name="John Doe", position="CTO", linkedin_url="https://www.linkedin.com/in/johndoe")
            ],
            competitors=["CompetitorA", "CompetitorB", "CompetitorC"],
            latest_news=[
                NewsItem(
                    title="Test Company Launches New Product", 
                    url="https://www.technews.com/test-company-launches", 
                    description="Test Company announced the launch of their innovative new testing platform that promises to revolutionize software QA processes."
                )
            ]
        )
        
        # Add some mock data for LinkedIn
        self.mock_company_info.linkedin_data = LinkedInData(
            description="Test Company is a leading provider of software testing solutions.",
            followers=5000,
            employeeCount=250,
            founded=2010,
            industry="Information Technology & Services",
            specialties=["Software Testing", "Quality Assurance", "DevOps"],
            headquarters="San Francisco, CA",
            website="https://www.testcompany.com",
            address="123 Test Street, San Francisco, CA 94105, USA"
        )
        
        # Add some mock data for Similarweb
        self.mock_company_info.similarweb_data = SimilarwebData(
            name="Test Company Inc.",
            description="Software testing solutions provider",
            globalRank=50000,
            categoryId="Software",
            companyYearFounded=2010,
            companyEmployeesMin=200,
            companyEmployeesMax=300,
            totalVisits=150000,
            bounceRate=45.5,
            pagesPerVisit=3.2,
            avgVisitDuration="00:02:30"
        )

    def prepare_company_data_for_report(self, company_info: CompanyInfo):
        """Prepare company data for the report agent."""
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
    
    async def test_business_report_generation(self):
        """Test if the business report agent can generate a report from company data."""
        # Prepare the test data
        company_data = self.prepare_company_data_for_report(self.mock_company_info)
        company_name = self.mock_company_info.company_name
        
        # Create the prompt for the business report agent
        report_prompt = f"""
        Generate a comprehensive business report for {company_name}.
        
        Use all the following company data to inform your analysis:
        
        ```json
        {json.dumps(company_data, indent=2, default=str)}
        ```
        
        Remember to include SWOT, PESTLE, Porter's Five Forces, Business Model Canvas, 
        competitor analysis, market positioning, digital presence evaluation, and customer sentiment analysis.
        """
        
        # Run the business report agent
        report_result = await self.business_report_agent.run(report_prompt)
        
        # Assertions to verify the report
        self.assertIsNotNone(report_result)
        self.assertIsNotNone(report_result.data)
        self.assertIsNotNone(report_result.data.report)
        
        # Check if the report contains expected sections
        report_text = report_result.data.report
        
        # Check if the report mentions the company name
        self.assertIn(company_name, report_text)
        
        print("\nTest passed! The business report agent successfully generated a report with expected sections.")
        print(f"Report length: {len(report_text)} characters")
        
        # Optional: print a snippet of the report for manual inspection
        print("\nReport snippet (first 500 characters):")
        print(report_text[:500] + "...")


def run_async_test(test_func):
    """Helper function to run async test methods."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_func())


if __name__ == "__main__":
    # Run the test directly
    test_instance = TestBusinessReportAgent()
    test_instance.setUp()
    try:
        run_async_test(test_instance.test_business_report_generation)
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {str(e)}")