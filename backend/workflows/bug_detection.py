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
        
        graph.add_node("test_gen", self.generate_test_driver)
        graph.add_node("developer", self.developer_step)
        graph.add_node("critic", self.critic_step)
        graph.add_node("tester", self.tester_step)
        
        graph.set_entry_point("test_gen")
        graph.add_edge("test_gen", "developer")
        
        graph.add_conditional_edges(
            "developer", 
            self.check_developer,
            {"continue": "critic", "error": END}
        )
        graph.add_conditional_edges("critic", self.check_critique, {"approved": "tester", "rejected": "developer", "error": END})
        graph.add_conditional_edges("tester", self.check_test)
        
        self.app = graph.compile()

    def generate_test_driver(self, state: WorkflowState):
        logs = state.get('logs', [])
        test_input = state.get('test_code', '').strip()
        code = state.get('code', '')
        language = state.get('language', 'python')
        
        if not test_input:
            logs.append("System: No test input provided. AI will generate one.")

        try:
            result = self.dev.generate_test_driver(code, test_input, language)
            driver = result['driver_code']
            log = f"System: Generated test driver for {language}."
            return {
                "test_code": driver,
                "logs": logs + [log]
            }
        except Exception as e:
            return {"logs": logs + [f"System Warning: Failed to generate test driver: {str(e)}"]}

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
        test_driver = state.get('test_code', '')
        
        # 1. Run the test driver against the FIXED code
        res_fix = self.tester.run_test(state['current_code'], test_driver, language=state.get('language', 'python'))
        success = res_fix['success']
        output = res_fix['error'] if not success else res_fix['output']
        
        log = f"Tester: {'PASSED' if success else 'FAILED'}. Output: {output[:100]}..."
        feedback = f"Test Output:\n{output}"
        
        if not success:
             logs = state['logs'] + [log, f"Error Details: {output[:500]}"]
        else:
             logs = state['logs'] + [log]

        return {
            "status": "passed" if success else "failed",
            "feedback": feedback,
            "logs": logs
        }

    def check_critique(self, state: WorkflowState):
        if state.get('status') == 'error': return "error"
        if state['iterations'] > 3: return "approved" 
        if state['status'] == "approved": return "approved"
        return "rejected"

    def check_test(self, state: WorkflowState):
        if state['iterations'] > 5: return END
        if state['status'] == "passed": return END
        return "developer"
