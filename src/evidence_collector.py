import os
import hashlib
from datetime import datetime
from typing import Dict, Any
from playwright.async_api import async_playwright
from .state import PipelineState


class EvidenceCollector:
    """Collects HTML evidence from websites using Playwright."""
    
    def __init__(self, evidence_dir: str = "evidence"):
        self.evidence_dir = evidence_dir
        os.makedirs(evidence_dir, exist_ok=True)
    
    async def collect_evidence(self, state: PipelineState) -> PipelineState:
        """Collect HTML evidence from the given URL."""
        url = state["url"]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate to URL and wait for network idle
                await page.goto(url, wait_until="networkidle")
                
                # Get HTML content
                html = await page.content()
                
                # Save HTML to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                html_filename = f"raw_{timestamp}.html"
                html_path = os.path.join(self.evidence_dir, html_filename)
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                
                # Update state
                state["html"] = html
                
                print(f"Evidence collected: {html_path}")
                
            except Exception as e:
                print(f"Error collecting evidence: {str(e)}")
                raise
            finally:
                await browser.close()
        
        return state
