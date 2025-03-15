from typing import List, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass
from apify_client import ApifyClient


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
