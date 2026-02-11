from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import PipelineState
from .evidence_collector import EvidenceCollector
from .llm_extractor import LLMExtractor
from .validator import Validator
from .report_generator import ReportGenerator
from .audit_logger import AuditLogger


class CompliancePipeline:
    """Main pipeline orchestrator using LangGraph."""
    
    def __init__(self, gemini_api_key: str):
        self.evidence_collector = EvidenceCollector()
        self.llm_extractor = LLMExtractor(gemini_api_key)
        self.validator = Validator()
        self.report_generator = ReportGenerator()
        self.audit_logger = AuditLogger()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph pipeline."""
        workflow = StateGraph(PipelineState)
        
        # Add nodes
        workflow.add_node("collect_evidence", self._collect_evidence_node)
        workflow.add_node("extract_data", self._extract_data_node)
        workflow.add_node("validate_data", self._validate_data_node)
        workflow.add_node("retry_extraction", self._retry_extraction_node)
        workflow.add_node("generate_report", self._generate_report_node)
        workflow.add_node("log_completion", self._log_completion_node)
        
        # Set entry point
        workflow.set_entry_point("collect_evidence")
        
        # Add edges
        workflow.add_edge("collect_evidence", "extract_data")
        workflow.add_edge("extract_data", "validate_data")
        workflow.add_edge("retry_extraction", "validate_data")
        workflow.add_edge("generate_report", "log_completion")
        workflow.add_edge("log_completion", END)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "validate_data",
            self._should_retry_or_continue,
            {
                "retry": "retry_extraction",
                "continue": "generate_report"
            }
        )
        
        return workflow.compile()
    
    async def _collect_evidence_node(self, state: PipelineState) -> PipelineState:
        """Node for collecting evidence."""
        try:
            new_state = await self.evidence_collector.collect_evidence(state)
            self.audit_logger.log_node_execution("collect_evidence", new_state, "success")
            return new_state
        except Exception as e:
            self.audit_logger.log_node_execution("collect_evidence", state, "error", str(e))
            raise
    
    def _extract_data_node(self, state: PipelineState) -> PipelineState:
        """Node for extracting data."""
        try:
            new_state = self.llm_extractor.extract_company_info(state)
            self.audit_logger.log_node_execution("extract_data", new_state, "success")
            return new_state
        except Exception as e:
            self.audit_logger.log_node_execution("extract_data", state, "error", str(e))
            raise
    
    def _validate_data_node(self, state: PipelineState) -> PipelineState:
        """Node for validating data."""
        try:
            new_state = self.validator.validate_extraction(state)
            self.audit_logger.log_node_execution("validate_data", new_state, "success")
            return new_state
        except Exception as e:
            self.audit_logger.log_node_execution("validate_data", state, "error", str(e))
            raise
    
    def _retry_extraction_node(self, state: PipelineState) -> PipelineState:
        """Node for retrying extraction."""
        try:
            new_state = self.llm_extractor.extract_with_retry(state)
            self.audit_logger.log_node_execution("retry_extraction", new_state, "success")
            return new_state
        except Exception as e:
            self.audit_logger.log_node_execution("retry_extraction", state, "error", str(e))
            raise
    
    def _generate_report_node(self, state: PipelineState) -> PipelineState:
        """Node for generating report."""
        try:
            new_state = self.report_generator.generate_report(state)
            self.audit_logger.log_node_execution("generate_report", new_state, "success")
            return new_state
        except Exception as e:
            self.audit_logger.log_node_execution("generate_report", state, "error", str(e))
            raise
    
    def _log_completion_node(self, state: PipelineState) -> PipelineState:
        """Node for logging completion."""
        try:
            summary = self.audit_logger.get_pipeline_summary(state)
            print(f"\nPipeline Summary: {summary}")
            self.audit_logger.log_node_execution("pipeline_complete", state, "success")
            return state
        except Exception as e:
            self.audit_logger.log_node_execution("pipeline_complete", state, "error", str(e))
            raise
    
    def _should_retry_or_continue(self, state: PipelineState) -> str:
        """Determine whether to retry extraction or continue."""
        if self.validator.should_retry(state):
            return "retry"
        return "continue"
    
    async def run(self, url: str) -> PipelineState:
        """Run the complete pipeline."""
        initial_state: PipelineState = {
            "url": url,
            "html": None,
            "extracted_data": None,
            "validated": False,
            "retry_count": 0,
            "report": None
        }
        
        print(f"Starting pipeline for: {url}")
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        print("Pipeline completed successfully!")
        return final_state
