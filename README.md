This Apify Actor is an AI-powered agent that performs comprehensive company research and generates detailed business reports. It leverages the Gemini 2.0 Flash model to research companies, collect data from multiple sources, and produce an in-depth business analysis report. The agent offers flexibility in both data collection and reporting, adapting its output to the available information.

## Features

- **Adaptive Company Research**: Uses AI to find and collate company information based on what's available
- **Multi-source Data Collection**: Gathers data from LinkedIn, Trustpilot, Similarweb, and Google Maps
- **Flexible Business Reports**: Generates tailored markdown reports that adapt to the available data
- **Comprehensive Analysis**: Applies relevant business frameworks based on the company and available information
- **Structured Data Output**: All collected data is available in structured JSON format

## Business Analysis Approaches

The report generation is adaptable and may include analysis frameworks such as:

1. **SWOT Analysis** (Strengths, Weaknesses, Opportunities, Threats)
2. **PESTLE Analysis** (Political, Economic, Social, Technological, Legal, Environmental factors)
3. **Porter's Five Forces** (Competitive Rivalry, Supplier Power, Buyer Power, Threat of Substitution, Threat of New Entry)
4. **Business Model Canvas Elements** (Value Propositions, Customer Segments, Key Resources, etc.)
5. **Competitor Analysis**
6. **Market Positioning**
7. **Digital Presence Evaluation** (based on social media profiles and web analytics)
8. **Customer Sentiment Analysis** (based on reviews if available)

The agent tailors its analysis to the available data and the specific company context, selecting the most relevant frameworks rather than forcing information into a rigid structure.

## Input

The Actor accepts a single input parameter:

```json
{
  "company_name": "Apify"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `company_name` | String | Name of the company to research |

## Output

The Actor produces two main outputs:

1. **Business Report**: A comprehensive markdown file stored in the Key-Value store with the key `report`
2. **Structured Data**: A JSON output in the default dataset containing all collected company information

### Example Output Structure

```json
{
  "company_name": "Apify",
  "website_url": "https://apify.com",
  "short_description": "...",
  "industry": "...",
  "business_model": "...",
  "target_market": "...",
  "products_services": [...],
  "founding_year": 2015,
  "funding_information": "...",
  "estimated_revenue": "...",
  "key_employees": [...],
  "employee_count": "...",
  "headquarters_location": "...",
  "competitors": [...],
  "market_position": "...",
  "social_media": {
    "linkedin": "https://www.linkedin.com/company/apify/",
    "twitter": "https://twitter.com/apify",
    "...": "..."
  },
  "latest_news": [...],
  "linkedin_data": {...},
  "trustpilot_data": [...],
  "similarweb_data": {...},
  "google_maps_data": [...],
  "extra_data": {...},
  "report": "# Comprehensive Business Report for Apify\n\n## Executive Summary\n..."
}
```

## Data Sources

The Actor collects information from the following data sources:

- **Google Search**: For basic company information
- **LinkedIn**: Company profile, employee count, specialties, industry
- **Trustpilot**: Customer reviews and ratings
- **Similarweb**: Website analytics, traffic sources, demographics
- **Google Maps**: Physical locations, customer reviews

## Implementation

The Actor is built using:

- **Python**: Core programming language
- **Apify SDK**: For Actor lifecycle management
- **Pydantic-AI**: For structured LLM agents and function calling
- **Gemini 2.0 Flash**: Google's LLM for AI-powered research and analysis

### Architecture

The Actor uses a multi-stage process:

1. **Research Phase**: An AI agent researches comprehensive company information using web searches
2. **Data Collection Phase**: Targeted data collection from external APIs (LinkedIn, Trustpilot, etc.)
3. **Report Generation Phase**: A second AI agent analyzes collected data and generates a tailored business report

## License

This project is licensed under the MIT License.
