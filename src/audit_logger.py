import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any
from .state import PipelineState


class AuditLogger:
    """Handles comprehensive audit logging for the pipeline."""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        os.makedirs(logs_dir, exist_ok=True)
        self.log_file = os.path.join(logs_dir, f"audit_{datetime.now().strftime('%Y%m%d')}.jsonl")
    
    def log_node_execution(self, node_name: str, state: PipelineState, status: str, error: str = None) -> None:
        """Log the execution of a pipeline node."""
        timestamp = datetime.now().isoformat()
        
        # Create input and output hashes for integrity checking
        input_hash = self._create_hash(str(state))
        output_hash = self._create_hash(str(state.get("extracted_data", "")))
        
        log_entry = {
            "timestamp": timestamp,
            "node": node_name,
            "status": status,
            "retry_count": state.get("retry_count", 0),
            "input_hash": input_hash,
            "output_hash": output_hash,
            "url": state.get("url", ""),
            "validated": state.get("validated", False)
        }
        
        if error:
            log_entry["error"] = error
        
        # Write to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"Audit log: {node_name} - {status}")
    
    def _create_hash(self, data: str) -> str:
        """Create SHA256 hash for data integrity."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]
    
    def get_pipeline_summary(self, state: PipelineState) -> Dict[str, Any]:
        """Get a summary of the pipeline execution."""
        return {
            "pipeline_completed": bool(state.get("report")),
            "validation_successful": state.get("validated", False),
            "retry_attempts": state.get("retry_count", 0),
            "fields_extracted": len([v for v in state.get("extracted_data", {}).values() if v]) if state.get("extracted_data") else 0,
            "url_processed": state.get("url", "")
        }
