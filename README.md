# Compliance Evidence Pipeline using LangGraph

Study proeject to work with LangGraph and Playwright.

## How It Works

1. **Evidence Collection**: Playwright captures HTML content from websites
2. **AI Extraction**: Gemini API processes HTML to extract company information  
3. **Data Validation**: Pydantic validates extracted data with retry logic
4. **Report Generation**: Creates structured reports with findings
5. **Audit Logging**: Logs every step for compliance requirements


## Setup
Make an env file and set it up with the gemini api key
```bash
pip install -r requirements.txt
playwright install
Run with: python main.py <url> 
