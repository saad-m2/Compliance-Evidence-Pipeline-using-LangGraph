import re
from bs4 import BeautifulSoup
from typing import Optional


class HTMLProcessor:
    """Preprocesses HTML to improve extraction accuracy."""
    
    @staticmethod
    def clean_html(html: str) -> str:
        """Clean and preprocess HTML for better extraction."""
        if not html:
            return ""
        
        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Remove common non-content elements
        for element in soup.find_all(['nav', 'header', 'footer', 'aside']):
            # Keep footer as it might contain contact info
            if element.name != 'footer':
                element.decompose()
        
        # Get clean text
        text = soup.get_text()
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_potential_emails(text: str) -> list:
        """Extract potential email addresses from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_potential_phones(text: str) -> list:
        """Extract potential phone numbers from text."""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # International
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\+49[-.\s]?\d{3,4}[-.\s]?\d{7,8}',  # German format
        ]
        
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return phones
    
    @staticmethod
    def extract_title(text: str) -> Optional[str]:
        """Extract potential company title from text."""
        # Look for common title patterns
        title_patterns = [
            r'(?:company|firma|unternehmen)[:\s]*([^\n]+)',  # German/English
            r'^(.{1,50})$',  # First line might be company name
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return None
