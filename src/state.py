from typing import TypedDict, Optional, Dict, Any


class PipelineState(TypedDict):
    """State object for the compliance evidence pipeline."""
    url: str
    html: Optional[str]
    extracted_data: Optional[Dict[str, Any]]
    validated: bool
    retry_count: int
    report: Optional[str]
