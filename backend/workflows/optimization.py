from typing import TypedDict
from langgraph.graph import StateGraph, END
from backend.agents.developer import DeveloperAgent
from backend.agents.critic import CriticAgent
from backend.agents.tester import TesterAgent

class WorkflowState(TypedDict):
    code: str
    current_code: str
    test_code: str # Used for validation/timing
    language: str # New field
    feedback: str
    iterations: int
    status: str
    logs: list
    initial_time: float
    final_time: float
    # Complexity fields
    orig_time_complexity: str
    orig_space_complexity: str
    opt_time_complexity: str
    opt_space_complexity: str

class OptimizationWorkflow:
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
        graph.add_edge("tester", END) # Optimization is usually one-shot or verified once
        
        self.app = graph.compile()

    def generate_test_driver(self, state: WorkflowState):
        # Only clear logs if it's the very first step
        logs = state.get('logs', [])
        
        # If test_code is empty or just raw data, try to generate a driver
        test_input = state.get('test_code', '').strip()
        code = state.get('code', '')
        language = state.get('language', 'python')
        
        if not test_input:
            logs.append("System: No test input provided. AI will generate one.")
            # Continue to generation with empty input, letting the agent invent it.

        try:
            # Ask developer agent to create a driver
            result = self.dev.generate_test_driver(code, test_input, language)
            driver = result['driver_code']
            log = f"System: Generated test driver for {language}."
            return {
                "test_code": driver, # Update the state with executable driver
                "logs": logs + [log]
            }
        except Exception as e:
            return {"logs": logs + [f"System Warning: Failed to generate test driver: {str(e)}"]}

    def check_developer(self, state: WorkflowState):
        if state.get('status') == 'error':
            return "error"
        return "continue"

    def developer_step(self, state: WorkflowState):
        result = self.dev.optimize_code(state['code'], state.get('language', 'python'), state.get('feedback', ''))
        
        if result.get('error'):
             return {
                 "logs": state.get('logs', []) + [f"Developer Error: {result['error']}"],
                 "status": "error"
             }

        log = f"Developer: Optimization proposed. Thought: {result['thought']}"
        
        return {
            "current_code": result['code'],
            "logs": state.get('logs', []) + [log],
            "iterations": state.get('iterations', 0) + 1,
            "orig_time_complexity": result['original_time_complexity'],
            "orig_space_complexity": result['original_space_complexity'],
            "opt_time_complexity": result['optimized_time_complexity'],
            "opt_space_complexity": result['optimized_space_complexity']
        }

    def critic_step(self, state: WorkflowState):
        result = self.critic.review(state['current_code'], "optimization")
        status = "approved" if result['approved'] else "rejected"
        log = f"Critic: {status.upper()}. {result['feedback']}"
        return {
            "feedback": result['feedback'],
            "status": status,
            "logs": state['logs'] + [log]
        }

    def tester_step(self, state: WorkflowState):
        test_driver = state.get('test_code', '')
        
        # If we have a generated driver, we use that INSTEAD of appending.
        # But wait, the driver usually needs the function definition too.
        # The generate_test_driver prompt asks to "Call the relevant function from the 'Code'".
        # This implies we still need to combine them.
        # BUT, if the driver imports libraries, putting it at the end might be late for Python (but usually okay).
        # For C++, includes must be at top.
        
        # Strategy:
        # We will NOT append test_code blindly anymore in TesterAgent if we can help it.
        # But TesterAgent logic is: write code + "\n\n" + test_code.
        
        # For Python: It works fine.
        # For C++: A driver usually means a `main()` function.
        # The `code` (optimized function) + `test_code` (main function) = Valid C++.
        # So the standard concatenation logic is actually fine for C++ structure,
        # PROVIDED the driver includes necessary headers if they are missing from the function snippet.
        
        # Run original first if not done
        initial_time = state.get('initial_time', 0.0)
        language = state.get('language', 'python')
        
        if initial_time == 0.0:
            res_orig = self.tester.run_test(state['code'], test_driver, language)
            initial_time = res_orig['execution_time']
            
        res_opt = self.tester.run_test(state['current_code'], test_driver, language)
        final_time = res_opt['execution_time']
        
        success = res_opt['success']
        improvement = "Slower" if final_time > initial_time else "Faster"
        
        # Log simplified to just success/failure status as requested
        log = f"Tester: Test Case {'Passed' if success else 'Failed'}"
        
        new_logs = state['logs'] + [log]
        
        # If failed, append the error to logs so user knows why
        if not success:
             # Check if output has useful info if error is empty (sometimes stdout has stack trace)
            error_msg = res_opt.get('error', '').strip() or res_opt.get('output', '').strip()
            if error_msg:
                # Format it slightly for readability
                new_logs.append(f"Error Details: {error_msg[:500]}") # Limit length

        return {
            "initial_time": initial_time,
            "final_time": final_time,
            "logs": new_logs
        }

    def check_critique(self, state: WorkflowState):
        if state.get('status') == 'error': return "error"
        if state['iterations'] > 3: return "approved"
        if state['status'] == "approved": return "approved"
        return "rejected"
