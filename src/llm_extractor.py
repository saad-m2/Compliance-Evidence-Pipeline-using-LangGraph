import os
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import google.genai as genai
from .state import PipelineState
from .html_processor import HTMLProcessor


class CompanyInfo(BaseModel):
    """Pydantic schema for company information extraction."""
    company_name: Optional[str] = Field(None, description="The name of the company")
    contact_email: Optional[str] = Field(None, description="Contact email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Physical address")
    about_us_text: Optional[str] = Field(None, description="About us or company description text")


class LLMExtractor:
    """Extracts structured company information using Gemini API."""
    
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
    
    def extract_company_info(self, state: PipelineState) -> PipelineState:
        """Extract company information from HTML using Gemini."""
        html = state["html"]
        
        if not html:
            raise ValueError("No HTML content available for extraction")
        
        # Preprocess HTML to improve extraction
        cleaned_html = HTMLProcessor.clean_html(html)
        
        # Extract potential data for context
        potential_emails = HTMLProcessor.extract_potential_emails(cleaned_html)
        potential_phones = HTMLProcessor.extract_potential_phones(cleaned_html)
        
        # Create enhanced extraction prompt
        prompt = self._create_extraction_prompt(cleaned_html, potential_emails, potential_phones)
        
        try:
            # Generate response from Gemini
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            response_text = response.text
            
            # Parse the JSON response
            try:
                # Try to extract JSON from the response
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    extracted_data = json.loads(json_str)
                else:
                    # If no JSON found, create empty structure
                    extracted_data = {}
                
                # Validate with Pydantic
                company_info = CompanyInfo(**extracted_data)
                state["extracted_data"] = company_info.model_dump()
                state["validated"] = True
                
                print("Company information extracted successfully")
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                state["validated"] = False
                state["extracted_data"] = None
                
            except Exception as e:
                print(f"Validation error: {str(e)}")
                state["validated"] = False
                state["extracted_data"] = None
                
        except Exception as e:
            print(f"LLM extraction error: {str(e)}")
            state["extracted_data"] = None
            state["validated"] = False
        
        return state
    
    def _create_extraction_prompt(self, html: str, potential_emails: list = None, potential_phones: list = None) -> str:
        """Create the extraction prompt for Gemini."""
        # Truncate HTML if too long
        max_length = 50000  # Adjust based on model limits
        if len(html) > max_length:
            html = html[:max_length] + "..."
        
        # Add context about found patterns
        context = ""
        if potential_emails:
            context += f"\nFound potential emails: {', '.join(potential_emails[:3])}"  # Limit to first 3
        if potential_phones:
            context += f"\nFound potential phones: {', '.join(potential_phones[:3])}"  # Limit to first 3
        
        prompt = f"""
Extract the following company information from the HTML content and return ONLY a valid JSON object.

IMPORTANT: The content may be in English OR German. Handle both languages appropriately.

Extract these fields:
1. company_name: The official name of the company (look for logos, headers, titles, footer text)
2. contact_email: Contact email address (look for email patterns like *@*.*, mailto: links, "Kontakt" sections)
3. phone_number: Phone number (look for phone patterns, "Tel:", "Telefon:", international formats)
4. address: Physical address or location information (look for address patterns, street names, cities)
5. about_us_text: Any about us, company description, mission statement, or service descriptions (in original language)

EXTRACTION TIPS:
- Check headers, footers, navigation menus, and contact sections
- Look for both English and German terms:
  * Contact: "Contact", "Kontakt", "Reach us", "Kontaktieren Sie uns"
  * About: "About", "About us", "Über uns", "Wir sind"
  * Email: look for mailto: links, @ symbols, email addresses
  * Legal: "Impressum" (German legal notice), "Datenschutz" (privacy policy)
- Company names often appear in: <title>, <h1>, logos, footer copyright
- For German content, preserve German text in about_us_text
- Pay attention to the context information below

CONTEXT INFORMATION:
{context}

HTML Content:
{html}

Return ONLY a JSON object with these exact keys. If a field is not found, use null for that field.

Example format:
{{
    "company_name": "LeadLane",
    "contact_email": "os@leadlane.de", 
    "phone_number": "+49-123-456789",
    "address": "Street Name, City, Germany",
    "about_us_text": "German or English description here..."
}}
"""
        return prompt
    
    def extract_with_retry(self, state: PipelineState) -> PipelineState:
        """Extract with retry logic using corrective prompt."""
        if state["retry_count"] >= 1:
            print("Maximum retry attempts reached")
            return state
        
        print(f"Retrying extraction (attempt {state['retry_count'] + 1})")
        
        # Use a more specific prompt for retry
        html = state["html"]
        
        # Preprocess HTML for retry
        cleaned_html = HTMLProcessor.clean_html(html)
        prompt = self._create_retry_prompt(cleaned_html)
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            response_text = response.text
            
            # Parse the JSON response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                extracted_data = json.loads(json_str)
                
                # Validate with Pydantic
                company_info = CompanyInfo(**extracted_data)
                state["extracted_data"] = company_info.model_dump()
                state["validated"] = True
                
                print("Retry extraction successful")
                
            else:
                state["validated"] = False
                state["extracted_data"] = None
                
        except Exception as e:
            print(f"Retry extraction failed: {str(e)}")
            state["validated"] = False
            state["extracted_data"] = None
        
        state["retry_count"] += 1
        return state
    
    def _create_retry_prompt(self, html: str) -> str:
        """Create a more specific prompt for retry attempts."""
        prompt = f"""
The previous extraction failed. Please try again with this HTML content and be very careful to return ONLY valid JSON.

CRITICAL: This content may be in GERMAN or English. Look for both languages.

Search specifically for:
- Company name (usually in header, title, footer, or about section)
- Email addresses (patterns like contact@, info@, support@, mailto: links)
- Phone numbers (patterns like (xxx) xxx-xxxx, +x-xxx-xxx-xxxx, Tel:, Telefon:)
- Address information (street, city, state, zip patterns, German addresses)
- About us/description text (paragraphs describing the company, in original language)

GERMAN-SPECIFIC SEARCH TERMS:
- "Kontakt" = Contact
- "Über uns" = About us  
- "Impressum" = Legal notice/imprint
- "Datenschutz" = Privacy policy
- "Sprechen Sie uns an" = Contact us
- "Wir freuen uns" = We look forward to

HTML Content:
{html}

Return ONLY a valid JSON object. No explanations, no markdown formatting, just the JSON.
"""
        return prompt
