import asyncio
import os
import sys
from dotenv import load_dotenv
from src.graph import CompliancePipeline


async def main():
    """Main entry point for the compliance evidence pipeline."""
    
    # Load environment variables
    load_dotenv()
    
    # Get Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment variables.")
        print("Please set up your .env file with your Gemini API key.")
        print("Copy .env.example to .env and add your API key.")
        sys.exit(1)
    
    # Get URL from command line arguments or prompt
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter the website URL to analyze: ").strip()
    
    if not url:
        print("Error: No URL provided.")
        sys.exit(1)
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Initialize and run pipeline
        pipeline = CompliancePipeline(api_key)
        result = await pipeline.run(url)
        
        # Display results
        print("\n" + "="*50)
        print("EXTRACTION RESULTS")
        print("="*50)
        
        if result.get("extracted_data"):
            data = result["extracted_data"]
            print(f"Company Name: {data.get('company_name', 'Not found')}")
            print(f"Contact Email: {data.get('contact_email', 'Not found')}")
            print(f"Phone Number: {data.get('phone_number', 'Not found')}")
            print(f"Address: {data.get('address', 'Not found')}")
            print(f"About Us: {data.get('about_us_text', 'Not found')[:200]}{'...' if len(data.get('about_us_text', '')) > 200 else ''}")
        else:
            print("No data was extracted successfully.")
        
        print(f"\nValidation Status: {'Success' if result.get('validated') else 'Failed'}")
        print(f"Retry Attempts: {result.get('retry_count', 0)}")
        
        if result.get("report"):
            print(f"\nReport saved to: reports/")
        
    except Exception as e:
        print(f"Pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
