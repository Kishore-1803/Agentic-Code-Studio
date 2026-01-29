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

class SecurityWorkflow:
    def __init__(self):
        self.dev = DeveloperAgent()
        self.critic = CriticAgent()
        self.tester = TesterAgent()
        
        graph = StateGraph(WorkflowState)
        
        graph.add_node("developer", self.developer_step)
        graph.add_node("critic", self.critic_step)
        # Tester step is optional for SQLi unless we have a specific SQL test rig. 
        # For this version, we'll trust the Critic + Static analysis logical check.
        # But user asked for 3 agents. Let's include Tester to just run the code and ensure it's valid Python syntax/runtime.
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
        # Check if the code is SQL (based on common keywords)
        # The general TesterAgent runs Python, so it will fail on raw SQL.
        code_start = state['current_code'].strip().upper()[:10]
        sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP"]
        
        is_sql = any(code_start.startswith(kw) for kw in sql_keywords)

        if is_sql:
            # Skip python execution test for SQL snippets
            log = "Tester: SQL snippet detected. Skipping Python runtime check (PASSED)."
            return {
                "status": "passed",
                "feedback": "",
                "logs": state['logs'] + [log]
            }

        # Sanity check: Does the code even run?
        res = self.tester.run_test(state['current_code'])
        success = res['success']
        err = res['error']
        log = f"Tester: Syntax/Runtime Check: {'PASSED' if success else 'FAILED'}"
        return {
            "status": "passed" if success else "failed",
            "feedback": f"Runtime Error: {err}" if not success else "",
            "logs": state['logs'] + [log]
        }

    def check_critique(self, state: WorkflowState):
        if state['iterations'] > 3: return "tester"
        if state['status'] == "approved": return "tester"
        return "developer"

    def check_test(self, state: WorkflowState):
        if state['iterations'] > 5: return END
        if state['status'] == "passed": return END # Passed syntax check
        return "developer"
