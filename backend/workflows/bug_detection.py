from typing import TypedDict
from langgraph.graph import StateGraph, END
from backend.agents.developer import DeveloperAgent
from backend.agents.critic import CriticAgent
from backend.agents.tester import TesterAgent

class WorkflowState(TypedDict):
    code: str
    issue: str
    test_code: str
    language: str # New field
    current_code: str
    feedback: str
    iterations: int
    status: str
    logs: list

class BugDetectionWorkflow:
    def __init__(self):
        self.dev = DeveloperAgent()
        self.critic = CriticAgent()
        self.tester = TesterAgent()
        
        graph = StateGraph(WorkflowState)
        
        graph.add_node("developer", self.developer_step)
        graph.add_node("critic", self.critic_step)
        graph.add_node("tester", self.tester_step)
        
        graph.set_entry_point("developer")
        
        graph.add_conditional_edges(
            "developer", 
            self.check_developer,
            {"continue": "critic", "error": END}
        )
        graph.add_conditional_edges("critic", self.check_critique, {"approved": "tester", "rejected": "developer", "error": END})
        graph.add_conditional_edges("tester", self.check_test)
        
        self.app = graph.compile()

    def check_developer(self, state: WorkflowState):
        if state.get('status') == 'error':
            return "error"
        return "continue"

    def developer_step(self, state: WorkflowState):
        result = self.dev.fix_bug(state['code'], state['issue'], state.get('language', 'python'), state.get('feedback', ''))
        
        if result.get('error'):
             return {
                 "logs": state.get('logs', []) + [f"Developer Error: {result['error']}"],
                 "status": "error"
             }

        log = f"Developer: Fix proposed. Thought: {result['thought']}"
        return {
            "current_code": result['code'],
            "logs": state.get('logs', []) + [log],
            "iterations": state.get('iterations', 0) + 1
        }

    def critic_step(self, state: WorkflowState):
        result = self.critic.review(state['current_code'], "bug_fix")
        status = "approved" if result['approved'] else "rejected"
        log = f"Critic: {status.upper()}. {result['feedback']}"
        return {
            "feedback": result['feedback'],
            "status": status,
            "logs": state['logs'] + [log]
        }

    def tester_step(self, state: WorkflowState):
        # We assume test_code is provided or we just run the code to check for runtime errors
        test_res = self.tester.run_test(state['current_code'], state.get('test_code', ''))
        success = test_res['success']
        output = test_res['error'] if not success else test_res['output']
        log = f"Tester: {'PASSED' if success else 'FAILED'}. Output: {output[:100]}..."
        
        feedback = f"Test Output:\n{output}"
        return {
            "status": "passed" if success else "failed",
            "feedback": feedback,
            "logs": state['logs'] + [log]
        }

    def check_critique(self, state: WorkflowState):
        if state.get('status') == 'error': return "error"
        if state['iterations'] > 3: return "tester" # Force test after 3 tries
        if state['status'] == "approved": return "tester"
        return "developer"

    def check_test(self, state: WorkflowState):
        if state['iterations'] > 5: return END
        if state['status'] == "passed": return END
        return "developer"
