import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_azure_openai():
    # Get environment variables
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    model = os.getenv("AZURE_OPENAI_MODEL", "gpt-35-turbo")

    # Print configuration
    print("\nAzure OpenAI Configuration:")
    print(f"Endpoint: {endpoint}")
    print(f"API Version: {api_version}")
    print(f"Model: {model}")
    print(f"API Key length: {len(api_key) if api_key else 0}")

    if not all([api_key, endpoint, model]):
        print("\nError: Missing one or more environment variables.")
        return False

    try:
        # Initialize client
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=f"{endpoint}openai/deployments/{model}", 
            default_query={"api-version": api_version},
        )

        # Test simple completion
        print("\nTesting API with a simple prompt...")
        response = await client.chat.completions.create(
            model=model, 
            messages=[{"role": "user", "content": "Say hello!"}],
            max_tokens=10,
        )

        print("\nSuccess! Response:")
        print(response.choices[0].message.content)
        return True

    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_azure_openai())
