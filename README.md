# Compliance Evidence Pipeline using LangGraph

A production-style AI pipeline that extracts structured company information from websites using LangGraph orchestration, Playwright for evidence collection, and Gemini API for LLM processing.

## Features

- **Web Evidence Collection**: Uses Playwright to capture HTML content with network idle waiting
- **AI-Powered Extraction**: Leverages Gemini API for structured data extraction
- **Validation & Retry Logic**: Pydantic validation with automatic retry on failures
- **Audit Logging**: Comprehensive logging for compliance requirements
- **Structured Reports**: Clean, formatted reports with extracted information

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

### 4. Set Up Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

## Usage

### Command Line

Run the pipeline with a URL:
```bash
python main.py https://example.com
```

Or run without arguments and enter URL when prompted:
```bash
python main.py
```

### Interactive Mode

The pipeline will:
1. Collect HTML evidence from the website
2. Extract company information using Gemini AI
3. Validate the extracted data
4. Generate a structured report
5. Log all steps for audit purposes

## Extracted Information

The pipeline extracts the following company information:
- Company Name
- Contact Email
- Phone Number
- Address
- About Us / Description Text

## Output Structure

```
Compliance-Evidence-Pipeline-using-LangGraph/
├── evidence/          # HTML evidence files
├── reports/           # Generated reports
├── logs/             # Audit logs
└── venv/             # Virtual environment
```

## Example Output

```
Company Information Report
==========================

Generated: 2024-02-11 21:12:34
Source URL: https://example.com

EXTRACTED INFORMATION
---------------------

Company Name: Example Corporation
Contact Email: contact@example.com
Phone Number: +1-555-123-4567
Address: 123 Main St, City, State 12345
About Us: We are a leading technology company specializing in...

EVIDENCE FILES
--------------

HTML Evidence: evidence/raw_20240211_211234.html

EXTRACTION STATUS
-----------------

Validation Status: ✓ Validated
Fields Extracted: 5/5
```

## Architecture

The pipeline uses LangGraph for orchestration with the following flow:

```
[Start] → [Collect HTML Evidence] → [Extract Company Info] → [Validate] → [Generate Report] → [Log] → [End]
                                      ↺ (if invalid and retry_count < 1)
```

## Dependencies

- `langgraph`: Graph-based orchestration
- `google-generativeai`: Gemini API client
- `pydantic`: Data validation
- `playwright`: Web automation and evidence collection
- `python-dotenv`: Environment variable management

## Error Handling

- Automatic retry on extraction failures (max 1 retry)
- Comprehensive error logging
- Graceful handling of network issues
- Validation error reporting

## Audit Trail

All pipeline executions are logged with:
- Timestamps
- Node execution status
- Input/output hashes for integrity
- Error details (if any)
- Retry attempts

Logs are stored in `logs/audit_YYYYMMDD.jsonl` format.

## License

This project is for educational and demonstration purposes.
