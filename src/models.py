from typing import List, Optional, Dict, Any
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

# Models for external data sources
class LinkedInData(BaseModel):
    name: Optional[str] = Field(None, description="Company name from LinkedIn")
    description: Optional[str] = Field(None, description="Company description from LinkedIn")
    industry: Optional[str] = Field(None, description="Industry type from LinkedIn")
    employees: Optional[int] = Field(None, description="Number of employees")
    website: Optional[str] = Field(None, description="Company website")
    specialties: List[str] = Field(default_factory=list, description="Company specialties")
    address: Optional[str] = Field(None, description="Company address")

class TrustpilotReview(BaseModel):
    reviewUrl: Optional[str] = Field(None, description="Review URL")
    authorName: Optional[str] = Field(None, description="Author name")
    datePublished: Optional[str] = Field(None, description="Date published")
    reviewHeadline: Optional[str] = Field(None, description="Review headline")
    reviewBody: Optional[str] = Field(None, description="Review text content")
    reviewLanguage: Optional[str] = Field(None, description="Review language")
    ratingValue: Optional[int] = Field(None, description="Rating value (1-5)")
    verificationLevel: Optional[str] = Field(None, description="Verification level")
    numberOfReviews: Optional[int] = Field(None, description="Number of reviews by author")
    consumerCountryCode: Optional[str] = Field(None, description="Country code of reviewer")
    experienceDate: Optional[str] = Field(None, description="Date of experience")
    likes: Optional[int] = Field(None, description="Number of likes")

# Specific models for Similarweb data components
class AdsSource(BaseModel):
    domain: str = Field("", description="Ad source domain")
    visitsShare: float = Field(0.0, description="Share of visits from this source")

class TopReferral(BaseModel):
    domain: str = Field("", description="Referral domain")
    visitsShare: float = Field(0.0, description="Share of visits from this referral")

class SocialNetwork(BaseModel):
    name: str = Field("", description="Social network name")
    visitsShare: float = Field(0.0, description="Share of visits from this network")

class TopCountry(BaseModel):
    country: str = Field("", description="Country code")
    share: float = Field(0.0, description="Share of traffic from this country")

class Competitor(BaseModel):
    domain: str = Field("", description="Competitor domain")
    visitsTotalCount: int = Field(0, description="Total visits to competitor")

class GoogleMapsReview(BaseModel):
    reviewerUrl: Optional[str] = Field(None, description="URL of the reviewer's profile")
    name: Optional[str] = Field(None, description="Name of the reviewer")
    text: Optional[str] = Field(None, description="Text content of the review")
    publishedAtDate: Optional[str] = Field(None, description="Date when the review was published")
    stars: Optional[int] = Field(None, description="Rating stars (1-5)")

class GoogleMapsPlace(BaseModel):
    title: Optional[str] = Field(None, description="Business name")
    description: Optional[str] = Field(None, description="Business description") 
    categoryName: Optional[str] = Field(None, description="Primary business category")
    categories: List[str] = Field(default_factory=list, description="Business categories")
    address: Optional[str] = Field(None, description="Full address")
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City name")
    postalCode: Optional[str] = Field(None, description="Postal/ZIP code")
    countryCode: Optional[str] = Field(None, description="Country code")
    website: Optional[str] = Field(None, description="Business website")
    phone: Optional[str] = Field(None, description="Phone number")
    totalScore: Optional[float] = Field(None, description="Average rating (0-5)")
    reviewsCount: Optional[int] = Field(None, description="Total number of reviews")
    reviews: List[GoogleMapsReview] = Field(default_factory=list, description="List of reviews with text content")

class TrafficSourcesData(BaseModel):
    direct: Optional[float] = Field(None, description="Direct traffic percentage")
    referrals: Optional[float] = Field(None, description="Referrals traffic percentage")
    search: Optional[float] = Field(None, description="Search traffic percentage")
    social: Optional[float] = Field(None, description="Social traffic percentage")
    mail: Optional[float] = Field(None, description="Mail traffic percentage")
    paid: Optional[float] = Field(None, description="Paid traffic percentage")

class AgeGroup(BaseModel):
    minAge: Optional[int] = Field(None, description="Minimum age in the range")
    maxAge: Optional[int] = Field(None, description="Maximum age in the range")
    value: Optional[float] = Field(None, description="Percentage of users in this age range")

class AgeDistributionData(BaseModel):
    age18_24: Optional[float] = Field(None, description="18-24 age group percentage")
    age25_34: Optional[float] = Field(None, description="25-34 age group percentage")
    age35_44: Optional[float] = Field(None, description="35-44 age group percentage")
    age45_54: Optional[float] = Field(None, description="45-54 age group percentage")
    age55_64: Optional[float] = Field(None, description="55-64 age group percentage")
    age65_plus: Optional[float] = Field(None, description="65+ age group percentage")
    groups: List[AgeGroup] = Field(default_factory=list, description="Age distribution by groups")

class TopKeyword(BaseModel):
    name: str = Field("", description="Keyword name")
    estimatedSearches: int = Field(0, description="Estimated number of searches")
    cpc: float = Field(0.0, description="Cost per click")

class SimilarwebData(BaseModel):
    name: Optional[str] = Field(None, description="Company name")
    description: Optional[str] = Field(None, description="Company description")
    globalRank: Optional[int] = Field(None, description="Global traffic rank")
    categoryId: Optional[str] = Field(None, description="Industry category")
    companyYearFounded: Optional[int] = Field(None, description="Year founded")
    companyName: Optional[str] = Field(None, description="Legal company name")
    companyEmployeesMin: Optional[int] = Field(None, description="Minimum employee count")
    companyEmployeesMax: Optional[int] = Field(None, description="Maximum employee count")
    companyAnnualRevenueMin: Optional[int] = Field(None, description="Minimum annual revenue")
    companyHeadquarterCountryCode: Optional[str] = Field(None, description="HQ country code")
    companyHeadquarterStateCode: Optional[str] = Field(None, description="HQ state code")
    companyHeadquarterCity: Optional[str] = Field(None, description="HQ city")
    avgVisitDuration: Optional[str] = Field(None, description="Average visit duration") 
    pagesPerVisit: Optional[float] = Field(None, description="Pages per visit")
    bounceRate: Optional[float] = Field(None, description="Bounce rate percentage")
    totalVisits: Optional[int] = Field(None, description="Total visits")
    trafficSources: TrafficSourcesData = Field(default_factory=TrafficSourcesData, description="Traffic sources")
    adsSources: List[AdsSource] = Field(default_factory=list, description="Advertising sources")
    topKeywords: List[TopKeyword] = Field(default_factory=list, description="Top keywords")
    organicTraffic: Optional[float] = Field(None, description="Organic traffic")
    paidTraffic: Optional[float] = Field(None, description="Paid traffic")
    topReferrals: List[TopReferral] = Field(default_factory=list, description="Top referral sites")
    socialNetworkDistribution: List[SocialNetwork] = Field(default_factory=list, description="Social network distribution")
    topCountries: List[TopCountry] = Field(default_factory=list, description="Top countries by traffic")
    topSimilarityCompetitors: List[Competitor] = Field(default_factory=list, description="Top competitors")
    topInterestedWebsites: List[str] = Field(default_factory=list, description="Top interested websites")
    ageDistribution: AgeDistributionData = Field(default_factory=AgeDistributionData, description="Age distribution")
    maleDistribution: Optional[float] = Field(None, description="Male audience percentage")
    femaleDistribution: Optional[float] = Field(None, description="Female audience percentage")
    address: Optional[str] = Field(None, description="Company address")

class CompanyInfo(BaseModel):
    # Core company information
    company_name: str = Field(..., description="Official name of the company")
    website_url: str = Field(..., description="URL of the company's official website")
    short_description: str = Field(..., description="Brief overview of the company's business and mission")
    
    # Business details
    industry: str = Field(..., description="Industry or sector the company operates in")
    business_model: str = Field(..., description="Description of how the company generates revenue")
    target_market: str = Field(..., description="Description of the company's target audience or customer base")
    products_services: List[str] = Field(default_factory=list, description="Main products or services offered by the company")
    
    # Financial information
    founding_year: int = Field(..., description="Year the company was founded")
    funding_information: str = Field(..., description="Details about funding rounds, investors, or financial status")
    estimated_revenue: str = Field(..., description="Estimated annual revenue range or specific figures if available")
    
    # People and organization
    key_employees: List[Employee] = Field(default_factory=list, description="List of key company leaders and their positions")
    employee_count: str = Field(..., description="Approximate number of employees at the company")
    
    # Competitive landscape
    competitors: List[str] = Field(default_factory=list, description="Names of major competing companies in the same industry")
    market_position: str = Field(..., description="Description of the company's position in its market")
    
    # Social media URLs
    linkedin_url: str = Field("", description="URL of the company's LinkedIn profile")
    twitter_url: str = Field("", description="URL of the company's Twitter profile")
    facebook_url: str = Field("", description="URL of the company's Facebook profile")
    instagram_url: str = Field("", description="URL of the company's Instagram profile")
    youtube_url: str = Field("", description="URL of the company's YouTube channel")
    github_url: str = Field("", description="URL of the company's GitHub profile")
    discord_url: str = Field("", description="URL of the company's Discord server")
    
    # News and updates
    latest_news: List[NewsItem] = Field(default_factory=list, description="Recent news articles or press releases about the company")
    
    # Additional data fields from external sources with specific models
    linkedin_data: LinkedInData = Field(default_factory=LinkedInData, description="Data retrieved from LinkedIn company profile")
    trustpilot_data: List[TrustpilotReview] = Field(default_factory=list, description="Reviews retrieved from Trustpilot")
    similarweb_data: SimilarwebData = Field(default_factory=SimilarwebData, description="Analytics data retrieved from Similarweb")
    google_maps_data: List[GoogleMapsPlace] = Field(default_factory=list, description="Location data retrieved from Google Maps")
    
    # Additional flexible data
    extra_data: str = Field(..., description="Additional relevant data that doesn't fit into predefined categories")
    
    # Business report field
    report: Optional[str] = Field(None, description="Comprehensive business report in markdown format")

class BasicCompanyInfo(BaseModel):
    """Basic company information model without external API data fields.
    This is used as the output type for the research agent."""
    # Core company information
    company_name: str = Field(..., description="Official name of the company")
    website_url: str = Field(..., description="URL of the company's official website")
    short_description: str = Field(..., description="Brief overview of the company's business and mission")
    
    # Business details
    industry: str = Field(..., description="Industry or sector the company operates in")
    business_model: str = Field(..., description="Description of how the company generates revenue")
    target_market: str = Field(..., description="Description of the company's target audience or customer base")
    products_services: List[str] = Field(default_factory=list, description="Main products or services offered by the company")
    
    # Financial information
    founding_year: int = Field(..., description="Year the company was founded")
    funding_information: str = Field(..., description="Details about funding rounds, investors, or financial status")
    estimated_revenue: str = Field(..., description="Estimated annual revenue range or specific figures if available")
    
    # People and organization
    key_employees: List[Employee] = Field(default_factory=list, description="List of key company leaders and their positions")
    employee_count: str = Field(..., description="Approximate number of employees at the company")
    
    # Competitive landscape
    competitors: List[str] = Field(default_factory=list, description="Names of major competing companies in the same industry")
    market_position: str = Field(..., description="Description of the company's position in its market")
    
    # Social media URLs
    linkedin_url: str = Field("", description="URL of the company's LinkedIn profile")
    twitter_url: str = Field("", description="URL of the company's Twitter profile")
    facebook_url: str = Field("", description="URL of the company's Facebook profile")
    instagram_url: str = Field("", description="URL of the company's Instagram profile")
    youtube_url: str = Field("", description="URL of the company's YouTube channel")
    github_url: str = Field("", description="URL of the company's GitHub profile")
    discord_url: str = Field("", description="URL of the company's Discord server")
    
    # News and updates
    latest_news: List[NewsItem] = Field(default_factory=list, description="Recent news articles or press releases about the company")
    
    # Additional flexible data
    extra_data: str = Field(..., description="Additional relevant data that doesn't fit into predefined categories")
