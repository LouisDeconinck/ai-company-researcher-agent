from apify import Actor
import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel

# Load environment variables from .env file
load_dotenv()

# Get API key from environment or pass directly
api_key = os.getenv("GEMINI_API_KEY")
model = GeminiModel('gemini-2.0-flash', provider='google-gla', api_key=api_key)
agent = Agent(
    model,
    system_prompt = 'Be concise, reply with one sentence.'
)

async def main() -> None:
    async with Actor:
        # Get input asynchronously
        actor_input = await Actor.get_input() 
        
        # Extract company_name from input
        company_name = actor_input.get("company_name", "Apify")
        
        # Use async run instead of run_sync
        result = await agent.run(f'What does the company "{company_name}" do?')  
        print(result)
        
        # Create a proper JSON object for the output
        output_data = {
            "company_name": company_name,
            "description": result.data
        }
        
        # Push the formatted data
        await Actor.push_data(output_data)
