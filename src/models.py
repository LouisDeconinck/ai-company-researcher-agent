from typing import List, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass
from apify_client import ApifyClient


@dataclass  
class Deps:
    client: ApifyClient

# Define Pydantic models for structured output
class Employee(BaseModel):
    name: str = Field(..., description="Full name of the company employee")
    position: str = Field(..., description="Job title or role of the employee in the company")

class NewsItem(BaseModel):
    title: str = Field(..., description="Headline or title of the news article")
    description: str = Field(..., description="Brief summary or excerpt of the news content")
    url: str = Field(..., description="Web link to the full news article")

class CompanyInfo(BaseModel):
    company_name: str = Field(..., description="Official name of the company")
    website_url: str = Field(..., description="URL of the company's official website")
    hq_location: str = Field(..., description="City, country or full address of company headquarters")
    year_founded: int = Field(..., description="Year when the company was established")
    industry: str = Field(..., description="Primary business sector or industry of operation")
    short_description: str = Field(..., description="Brief overview of the company's business and mission")
    key_employees: List[Employee] = Field(default_factory=list, description="List of key company leaders and their positions")
    competitors: List[str] = Field(default_factory=list, description="Names of major competing companies in the same industry")
    latest_news: List[NewsItem] = Field(default_factory=list, description="Recent news articles or press releases about the company")
    linkedin_url: str = Field(..., description="URL of the company's LinkedIn profile")
    twitter_url: str = Field(..., description="URL of the company's Twitter profile")
    facebook_url: str = Field(..., description="URL of the company's Facebook profile")
    instagram_url: str = Field(..., description="URL of the company's Instagram profile")
    youtube_url: str = Field(..., description="URL of the company's YouTube channel")
