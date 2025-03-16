from apify import Actor
from typing import List
from pydantic_ai import RunContext
from .models import Deps, LinkedInData, TrustpilotReview, SimilarwebData, GoogleMapsPlace, AdsSource, TopReferral, SocialNetwork, TopCountry, Competitor, TrafficSourcesData, AgeDistributionData, TopKeyword, GoogleMapsReview, AgeGroup
import re
from urllib.parse import urlparse

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
    try:
        # Sanitize the query to use as filename
        def sanitize_filename(text: str) -> str:
            # Replace spaces with underscores and remove/replace invalid filename characters
            invalid_chars = r'[\\/*?:"<>|\'"]'
            sanitized = re.sub(invalid_chars, "_", text)
            return sanitized.replace(" ", "_")
            
        kv_key = f"search_results_{sanitize_filename(query)}"
        
        # Use the proper method to get the key-value store
        default_store = await Actor.open_key_value_store()
        await default_store.set_value(kv_key, results)
    except Exception as e:
        Actor.log.warning(f"Failed to store search results: {str(e)}")
            
    Actor.log.info(f"Found {len(results)}/{max_results} search results for: {query}")
    await Actor.charge('tool_result', len(results))
    return results 

async def get_linkedin_company_profile(
    client,
    linkedin_company_url: str
) -> LinkedInData:
    """Get LinkedIn company profile.

    Args:
        client: The Apify client for making API calls.
        linkedin_company_url: The LinkedIn company URL. E.g. https://www.linkedin.com/company/apple/

    Returns:
        A LinkedInData object containing company details from LinkedIn.
    """
    Actor.log.info(f"Getting LinkedIn company profile for: {linkedin_company_url}")
    run_input = {
        "linkedinUrls": [linkedin_company_url]
    }

    try:
        run = client.actor("icypeas_official/linkedin-company-scraper").call(run_input=run_input, memory_mbytes=128)
        dataset = client.dataset(run["defaultDatasetId"]).list_items()

        if dataset.items and len(dataset.items) > 0:
            Actor.log.info(f"LinkedIn company profile retrieved for {linkedin_company_url}")
            item = dataset.items[0]['data'][0]['result']
            
            # Format address if it's a dictionary
            address = item.get("address")
            if isinstance(address, dict):
                address_parts = []
                if address.get("streetAddress"):
                    address_parts.append(address.get("streetAddress"))
                if address.get("addressLocality"):
                    address_parts.append(address.get("addressLocality"))
                if address.get("addressRegion"):
                    address_parts.append(address.get("addressRegion"))
                if address.get("postalCode"):
                    address_parts.append(address.get("postalCode"))
                if address.get("addressCountry"):
                    address_parts.append(address.get("addressCountry"))
                address = ", ".join([part for part in address_parts if part])
            
            # Create and return a LinkedInData model instance
            return LinkedInData(
                name=item.get("name"),
                description=item.get("description"),
                industry=item.get("industry"),
                employees=item.get("numberOfEmployees"),
                website=item.get("website"),
                specialties=[s["value"] for s in item.get("specialties", [])],
                address=address
            )
        await Actor.charge('tool_result', 1)
        return LinkedInData()

    except Exception as e:
        Actor.log.error(f"Error fetching LinkedIn company profile: {str(e)}")
        return LinkedInData() 
    
async def search_google_maps(
    client,
    query: str, 
) -> List[GoogleMapsPlace]:
    """Get Google Maps search results focused on company information.

    Args:
        client: The Apify client for making API calls.
        query: The search query for finding a company/business on Google Maps.
              Examples:
              - Company name: "Apify"
              - Company with location: "Microsoft Prague"
              - Office address: "1 Infinite Loop, Cupertino"

    Returns:
        A list of GoogleMapsPlace objects containing details about the location.
    """
    Actor.log.info(
        f"Searching Google Maps for: {query}")
    run_input = {
        "searchStringsArray": [query],
        "maxCrawledPlaces": 1,
        "maxReviews": 100,
        "language": "en",
    }

    try:
        run = client.actor("compass/crawler-google-places").call(run_input=run_input, memory_mbytes=1024)
        dataset = client.dataset(run["defaultDatasetId"]).list_items()

        results = []
        for item in dataset.items:
            Actor.log.info(f"Google Maps data retrieved for {query}")
            
            # Extract reviews with text
            reviews = []
            if "reviews" in item and isinstance(item["reviews"], list):
                for review in item["reviews"]:
                    # Only include reviews that have text
                    if review.get("text"):
                        reviews.append(GoogleMapsReview(
                            reviewerUrl=review.get("reviewerUrl"),
                            name=review.get("name"),
                            text=review.get("text"),
                            publishedAtDate=review.get("publishedAtDate"),
                            stars=review.get("stars")
                        ))
            
            # Create a GoogleMapsPlace model instance
            place = GoogleMapsPlace(
                title=item.get("title", ""),
                description=item.get("description", ""),
                categoryName=item.get("categoryName", ""),
                categories=item.get("categories", []),
                address=item.get("address", ""),
                street=item.get("street", ""),
                city=item.get("city", ""),
                postalCode=item.get("postalCode", ""),
                countryCode=item.get("countryCode", ""),
                website=item.get("website", ""),
                phone=item.get("phone", ""),
                totalScore=item.get("totalScore", 0),
                reviewsCount=item.get("reviewsCount", 0),
                reviews=reviews
            )
            results.append(place)

        await Actor.charge('tool_result', len(results))
        return results

    except Exception as e:
        Actor.log.error(f"Error fetching Google Maps results: {str(e)}")
        return [] 
    
async def get_trustpilot_reviews(
    client,
    company_domain: str,
) -> List[TrustpilotReview]:
    """Get reviews from Trustpilot for a website.

    Args:
        client: The Apify client for making API calls.
        company_domain: Domain name of the company (e.g., "apify.com")

    Returns:
        List of TrustpilotReview objects containing review details.
    """
    # Extract domain from URL if needed
    if company_domain.startswith(('http://', 'https://')):
        parsed_url = urlparse(company_domain)
        domain = parsed_url.netloc
        # Remove 'www.' if present
        domain = re.sub(r'^www\.', '', domain)
    else:
        domain = company_domain
    
    Actor.log.info(f"Getting Trustpilot reviews for company: {domain}")
    
    run_input = {
        "companyDomain": domain,
        "count": 100
    }
    
    try:
        run = client.actor("nikita-sviridenko/trustpilot-reviews-scraper").call(run_input=run_input, memory_mbytes=1024)
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        
        if dataset.items:
            Actor.log.info(f"{len(dataset.items)} Trustpilot reviews retrieved for {domain}")
            reviews = []
            for item in dataset.items:
                # Create a TrustpilotReview model instance
                review = TrustpilotReview(
                    reviewUrl=item.get("reviewUrl", ""),
                    authorName=item.get("authorName", ""),
                    datePublished=item.get("datePublished", ""),
                    reviewHeadline=item.get("reviewHeadline", ""),
                    reviewBody=item.get("reviewBody", ""),
                    reviewLanguage=item.get("reviewLanguage", ""),
                    ratingValue=item.get("ratingValue", 0),
                    verificationLevel=item.get("verificationLevel", ""),
                    numberOfReviews=item.get("numberOfReviews", 0),
                    consumerCountryCode=item.get("consumerCountryCode", ""),
                    experienceDate=item.get("experienceDate", ""),
                    likes=item.get("likes", 0)
                )
                reviews.append(review)
            await Actor.charge('tool_result', len(reviews))
            return reviews
        else:
            Actor.log.warning(f"No Trustpilot reviews retrieved for {domain}")
            return []
        
    except Exception as e:
        Actor.log.error(f"Error fetching Trustpilot reviews for {domain}: {str(e)}")
        return [] 
    
async def get_similarweb_results(
    client,
    website: str
) -> SimilarwebData:
    """Get analytics and company information from Similarweb for a website.

    Args:
        client: The Apify client for making API calls.
        website: Website domain to analyze (e.g., "google.com")
    
    Returns:
        A SimilarwebData object containing analytics and company information.
    """
    Actor.log.info(f"Getting Similarweb results for website: {website}")
    
    run_input = {
        "websites": [website]
    }
    
    try:
        run = client.actor("tri_angle/similarweb-scraper").call(run_input=run_input, memory_mbytes=1024)
        dataset = client.dataset(run["defaultDatasetId"]).list_items()
        
        if dataset.items and len(dataset.items) > 0:
            Actor.log.info(f"Similarweb data retrieved for {website}")
            data = dataset.items[0]
            
            # Create address string
            address = f"{data.get('companyHeadquarterCity', '')}, {data.get('companyHeadquarterStateCode', '')}, {data.get('companyHeadquarterCountryCode', '')}"
            
            # Process ad sources
            ad_sources = []
            for a in data.get("adsSources", []):
                if isinstance(a, dict) and a.get("domain"):
                    ad_sources.append(AdsSource(
                        domain=str(a.get("domain", "")),
                        visitsShare=float(a.get("visitsShare", 0))
                    ))
            
            # Process top referrals
            top_referrals = []
            for r in data.get("topReferrals", []):
                if isinstance(r, dict) and r.get("domain"):
                    top_referrals.append(TopReferral(
                        domain=str(r.get("domain", "")),
                        visitsShare=float(r.get("visitsShare", 0))
                    ))
            
            # Process social network distribution
            social_distribution = []
            for c in data.get("socialNetworkDistribution", []):
                if isinstance(c, dict):
                    social_distribution.append(SocialNetwork(
                        name=str(c.get("name", "")),
                        visitsShare=float(c.get("visitsShare", 0))
                    ))
            
            # Process top countries
            top_countries = []
            for c in data.get("topCountries", []):
                if isinstance(c, dict):
                    top_countries.append(TopCountry(
                        country=str(c.get("countryAlpha2Code", "")),
                        share=float(c.get("visitsShare", 0))
                    ))
            
            # Process competitors
            competitors = []
            for c in data.get("topSimilarityCompetitors", []):
                if isinstance(c, dict) and c.get("domain"):
                    competitors.append(Competitor(
                        domain=str(c.get("domain", "")),
                        visitsTotalCount=int(c.get("visitsTotalCount", 0))
                    ))
            
            # Process traffic sources from trafficSources object
            traffic_sources = TrafficSourcesData()
            traffic_sources_dict = data.get("trafficSources", {})
            if isinstance(traffic_sources_dict, dict):
                traffic_sources = TrafficSourcesData(
                    direct=traffic_sources_dict.get("directVisitsShare"),
                    referrals=traffic_sources_dict.get("referralVisitsShare"),
                    search=traffic_sources_dict.get("organicSearchVisitsShare"),
                    social=traffic_sources_dict.get("socialNetworksVisitsShare"),
                    mail=traffic_sources_dict.get("mailVisitsShare"),
                    paid=traffic_sources_dict.get("paidSearchVisitsShare")
                )
            
            # Process age distribution
            age_dist_groups = []
            age_distribution = AgeDistributionData()
            
            # Handle age distribution as an array of groups
            age_dist_array = data.get("ageDistribution", [])
            if isinstance(age_dist_array, list):
                for group in age_dist_array:
                    if isinstance(group, dict):
                        age_dist_groups.append(AgeGroup(
                            minAge=group.get("minAge"),
                            maxAge=group.get("maxAge"),
                            value=group.get("value")
                        ))
                        
                        # Also map to the original fields for backward compatibility
                        min_age = group.get("minAge")
                        max_age = group.get("maxAge")
                        if min_age == 18 and max_age == 24:
                            age_distribution.age18_24 = group.get("value")
                        elif min_age == 25 and max_age == 34:
                            age_distribution.age25_34 = group.get("value")
                        elif min_age == 35 and max_age == 44:
                            age_distribution.age35_44 = group.get("value")
                        elif min_age == 45 and max_age == 54:
                            age_distribution.age45_54 = group.get("value")
                        elif min_age == 55 and max_age == 64:
                            age_distribution.age55_64 = group.get("value")
                        elif min_age == 65:
                            age_distribution.age65_plus = group.get("value")
                
                # Add the groups to the age distribution
                age_distribution.groups = age_dist_groups
            
            # Process top keywords
            top_keywords = []
            keywords_data = data.get("topKeywords", [])
            if isinstance(keywords_data, list):
                for kw in keywords_data:
                    if isinstance(kw, dict) and kw.get("name"):
                        top_keywords.append(TopKeyword(
                            name=str(kw.get("name", "")),
                            estimatedSearches=int(kw.get("volume", 0)),
                            cpc=float(kw.get("cpc", 0.0))
                        ))
            
            # Handle avgVisitDuration - keep it as a string
            avg_visit_duration = data.get("avgVisitDuration")
            # If it's an integer in seconds, convert to time format
            if isinstance(avg_visit_duration, int):
                mins = avg_visit_duration // 60
                secs = avg_visit_duration % 60
                avg_visit_duration = f"00:{mins:02d}:{secs:02d}"
            
            # Keep traffic values as floats
            organic_traffic = data.get("organicTraffic")
            if not isinstance(organic_traffic, float):
                try:
                    organic_traffic = float(organic_traffic or 0)
                except (ValueError, TypeError):
                    organic_traffic = 0.0
                    
            paid_traffic = data.get("paidTraffic")
            if not isinstance(paid_traffic, float):
                try:
                    paid_traffic = float(paid_traffic or 0)
                except (ValueError, TypeError):
                    paid_traffic = 0.0
            
            # Process top interested websites (only domain properties)
            interested_websites = []
            top_interested = data.get("topInterestedWebsites", [])
            if isinstance(top_interested, list):
                for w in top_interested:
                    if isinstance(w, dict) and w.get("domain"):
                        interested_websites.append(str(w.get("domain", "")))
                    elif isinstance(w, str):
                        interested_websites.append(w)
            
            await Actor.charge('tool_result', 1)
            
            # Create and return a SimilarwebData model instance
            return SimilarwebData(
                name=data.get("name", ""),
                description=data.get("description", ""),
                globalRank=data.get("globalRank", 0),
                categoryId=data.get("categoryId", ""),
                companyYearFounded=data.get("companyYearFounded", 0),
                companyName=data.get("companyName", ""), 
                companyEmployeesMin=data.get("companyEmployeesMin", 0),
                companyEmployeesMax=data.get("companyEmployeesMax", 0),
                companyAnnualRevenueMin=data.get("companyAnnualRevenueMin", 0),
                companyHeadquarterCountryCode=data.get("companyHeadquarterCountryCode", ""),
                companyHeadquarterStateCode=data.get("companyHeadquarterStateCode", ""),
                companyHeadquarterCity=data.get("companyHeadquarterCity", ""),
                avgVisitDuration=avg_visit_duration,
                pagesPerVisit=data.get("pagesPerVisit", 0),
                bounceRate=data.get("bounceRate", 0),
                totalVisits=data.get("totalVisits", 0),
                trafficSources=traffic_sources,
                adsSources=ad_sources,
                topKeywords=top_keywords,
                organicTraffic=organic_traffic,
                paidTraffic=paid_traffic,
                topReferrals=top_referrals,
                socialNetworkDistribution=social_distribution,
                topCountries=top_countries,
                topSimilarityCompetitors=competitors,
                topInterestedWebsites=interested_websites,
                ageDistribution=age_distribution,
                maleDistribution=data.get("maleDistribution", 0),
                femaleDistribution=data.get("femaleDistribution", 0),
                address=address
            )
        else:
            Actor.log.warning(f"No Similarweb data retrieved for {website}")
            return SimilarwebData()
        
    except Exception as e:
        Actor.log.error(f"Error fetching Similarweb data for {website}: {str(e)}")
        return SimilarwebData() 