from typing import Dict, Any
from pydantic import ValidationError
from .llm_extractor import CompanyInfo
from .state import PipelineState


class Validator:
    """Validates extracted data using Pydantic schemas."""
    
    def validate_extraction(self, state: PipelineState) -> PipelineState:
        """Validate the extracted data."""
        extracted_data = state.get("extracted_data")
        
        if not extracted_data:
            state["validated"] = False
            print("No data to validate")
            return state
        
        try:
            # Validate using Pydantic
            company_info = CompanyInfo(**extracted_data)
            state["validated"] = True
            state["extracted_data"] = company_info.model_dump()
            print("Data validation successful")
            
        except ValidationError as e:
            state["validated"] = False
            print(f"Validation error: {str(e)}")
            
        except Exception as e:
            state["validated"] = False
            print(f"Unexpected validation error: {str(e)}")
        
        return state
    
    def should_retry(self, state: PipelineState) -> bool:
        """Determine if extraction should be retried."""
        return not state.get("validated", False) and state.get("retry_count", 0) < 1
