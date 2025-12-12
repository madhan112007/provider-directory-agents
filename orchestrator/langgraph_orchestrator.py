"""
LangGraph-based Orchestrator with State Machine
"""
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
import operator
from datetime import datetime

class ProviderState(TypedDict):
    provider_id: str
    provider_data: dict
    validation_result: dict
    enrichment_result: dict
    qa_result: dict
    correction_result: dict
    action: str
    errors: Annotated[Sequence[str], operator.add]
    retry_count: int

class LangGraphOrchestrator:
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(ProviderState)
        
        # Add nodes
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("enrich", self._enrich_node)
        workflow.add_node("qa", self._qa_node)
        workflow.add_node("correct", self._correct_node)
        workflow.add_node("manual_review", self._manual_review_node)
        workflow.add_node("complete", self._complete_node)
        
        # Define edges
        workflow.set_entry_point("validate")
        
        workflow.add_edge("validate", "enrich")
        workflow.add_edge("enrich", "qa")
        
        # Conditional routing from QA
        workflow.add_conditional_edges(
            "qa",
            self._route_after_qa,
            {
                "correct": "correct",
                "manual_review": "manual_review",
                "retry": "validate"
            }
        )
        
        workflow.add_edge("correct", "complete")
        workflow.add_edge("manual_review", "complete")
        workflow.add_edge("complete", END)
        
        return workflow.compile()
    
    def _validate_node(self, state: ProviderState) -> ProviderState:
        """Validation Agent Node"""
        from data_validation_agent.agent import DataValidationAgent
        
        agent = DataValidationAgent()
        try:
            result = agent.validate_contact_info(state["provider_data"])
            state["validation_result"] = result
        except Exception as e:
            state["errors"].append(f"Validation error: {str(e)}")
            state["retry_count"] += 1
        
        return state
    
    def _enrich_node(self, state: ProviderState) -> ProviderState:
        """Enrichment Agent Node"""
        # Simulated enrichment
        state["enrichment_result"] = {
            "education": "MD",
            "board_certified": True,
            "years_experience": 10
        }
        return state
    
    def _qa_node(self, state: ProviderState) -> ProviderState:
        """QA Agent Node"""
        from agentic_ai import QualityAssuranceAgent
        
        agent = QualityAssuranceAgent()
        qa_input = {
            "original": state["provider_data"],
            "npi": state["validation_result"].get("fields", {}).get("npi", {}),
            "website": state["enrichment_result"],
            "pdf": {},
            "license_db": {"status": "active"},
            "meta": {"member_count": 500}
        }
        
        result = agent.process_provider(qa_input)
        state["qa_result"] = result
        state["action"] = result["action"]
        
        return state
    
    def _correct_node(self, state: ProviderState) -> ProviderState:
        """Correction Agent Node"""
        from automative_correction_agent import AutomativeCorrectionAgent
        
        agent = AutomativeCorrectionAgent()
        result = agent.process_provider(state["provider_data"])
        state["correction_result"] = result
        
        return state
    
    def _manual_review_node(self, state: ProviderState) -> ProviderState:
        """Manual Review Queue Node"""
        state["action"] = "manual_review_queued"
        return state
    
    def _complete_node(self, state: ProviderState) -> ProviderState:
        """Completion Node"""
        state["action"] = "completed"
        return state
    
    def _route_after_qa(self, state: ProviderState) -> str:
        """Routing logic after QA"""
        if state["retry_count"] >= 3:
            return "manual_review"
        
        if state["qa_result"]["action"] == "auto_resolve":
            return "correct"
        else:
            return "manual_review"
    
    def process_provider(self, provider_data: dict) -> dict:
        """Process a single provider through the graph"""
        initial_state = ProviderState(
            provider_id=provider_data.get("provider_id"),
            provider_data=provider_data,
            validation_result={},
            enrichment_result={},
            qa_result={},
            correction_result={},
            action="pending",
            errors=[],
            retry_count=0
        )
        
        final_state = self.graph.invoke(initial_state)
        return final_state

# Example usage
if __name__ == "__main__":
    orchestrator = LangGraphOrchestrator()
    
    test_provider = {
        "provider_id": "P001",
        "name": "Dr. Smith",
        "npi": "1234567890",
        "phone": "555-1234",
        "address": "123 Main St",
        "specialty": "Cardiology",
        "state": "CA"
    }
    
    result = orchestrator.process_provider(test_provider)
    print(f"Final action: {result['action']}")
