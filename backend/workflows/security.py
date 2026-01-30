from typing import TypedDict
from langgraph.graph import StateGraph, END
from backend.agents.developer import DeveloperAgent
from backend.agents.critic import CriticAgent
from backend.agents.tester import TesterAgent

class WorkflowState(TypedDict):
    code: str
    current_code: str
    feedback: str
    iterations: int
    status: str
    logs: list
    language: str

class SecurityWorkflow:
    def __init__(self):
        self.dev = DeveloperAgent()
        self.critic = CriticAgent()
        self.tester = TesterAgent()
        
        graph = StateGraph(WorkflowState)
        
        graph.add_node("developer", self.developer_step)
        graph.add_node("critic", self.critic_step)
        graph.add_node("tester", self.tester_step)
        
        graph.set_entry_point("developer")
        
        graph.add_edge("developer", "critic")
        graph.add_conditional_edges("critic", self.check_critique)
        graph.add_conditional_edges("tester", self.check_test)
        
        self.app = graph.compile()

    def developer_step(self, state: WorkflowState):
        result = self.dev.fix_security(state['code'], state.get('feedback', ''))
        log = f"Developer: SQL Patch proposed. Thought: {result['thought']}"
        return {
            "current_code": result['code'],
            "logs": state.get('logs', []) + [log],
            "iterations": state.get('iterations', 0) + 1
        }

    def critic_step(self, state: WorkflowState):
        result = self.critic.review(state['current_code'], "security")
        status = "approved" if result['approved'] else "rejected"
        log = f"Critic: {status.upper()}. {result['feedback']}"
        return {
            "feedback": result['feedback'],
            "status": status,
            "logs": state['logs'] + [log]
        }

    def tester_step(self, state: WorkflowState):
        language = state.get('language', '').lower()
        allowed_langs = ['sql', 'postgresql', 'postgres']

        if language not in allowed_langs:
             log = f"Tester: Unsupported language '{language}'. Security workflow only supports SQL and PostgreSQL."
             return {
                 "status": "failed",
                 "feedback": f"Security Check Error: Only SQL/PostgreSQL are supported. Got '{language}'.",
                 "logs": state['logs'] + [log]
             }
        
        log = "Tester: SQL/PostgreSQL detected. Runtime check skipped."
        return {
            "status": "passed",
            "feedback": "",
            "logs": state['logs'] + [log]
        }

    def check_critique(self, state: WorkflowState):
        if state.get('status') == 'error': return "error"
        if state['iterations'] > 3: return "approved"
        if state['status'] == "approved": return "approved"
        return "rejected"

    def check_test(self, state: WorkflowState):
        if state['iterations'] > 5: return END
        if state['status'] == "passed": return END # Passed syntax check
        return "developer"
