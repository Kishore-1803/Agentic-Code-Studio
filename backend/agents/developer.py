from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional
import time

class DeveloperOutput(BaseModel):
    thought: str = Field(description="Reasoning behind the changes.")
    code: str = Field(description="The complete modified code.")
    error: Optional[str] = Field(description="Error message if the code doesn't match the language or cannot be processed.", default=None)

class OptimizationOutput(BaseModel):
    thought: str = Field(description="Reasoning behind the optimization.")
    code: str = Field(description="The complete optimized code.")
    original_time_complexity: str = Field(description="Time complexity of original code (e.g. O(n))")
    original_space_complexity: str = Field(description="Space complexity of original code")
    optimized_time_complexity: str = Field(description="Time complexity of optimized code")
    optimized_space_complexity: str = Field(description="Space complexity of optimized code")
    error: Optional[str] = Field(description="Error message if language mismatch.", default=None)

class DeveloperAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.1)
        self.parser = JsonOutputParser(pydantic_object=DeveloperOutput)
        self.opt_parser = JsonOutputParser(pydantic_object=OptimizationOutput)

    def fix_bug(self, code: str, issue: str, language: str, feedback: str = "") -> dict:
        prompt = ChatPromptTemplate.from_template(
            """You are an expert {language} Developer. 
            Task: Fix the reported bug in the code.
            
            First, CHECK if the code provided is actually {language}. 
            If it is clearly NOT {language} (e.g., C++ code provided when Python is expected), 
            return valid JSON with "error": "Language mismatch: Expected {language}" and empty code.
            
            Code:
            {code}
            
            Issue Description:
            {issue}
            
            Previous Feedback (if any):
            {feedback}
            
            Return JSON with 'thought', 'code', and optional 'error'.
            {format_instructions}
            """
        )
        time.sleep(15)
        chain = prompt | self.llm | self.parser
        return chain.invoke({
            "code": code, 
            "issue": issue, 
            "language": language,
            "feedback": feedback,
            "format_instructions": self.parser.get_format_instructions()
        })

    def optimize_code(self, code: str, language: str, feedback: str = "") -> dict:
        prompt = ChatPromptTemplate.from_template(
            """You are an expert {language} Developer. 
            Task: Optimize the following code for time and space complexity. 
            Keep functionality exactly the same.
            
            First, CHECK if the code provided is actually {language}. 
            If not, return valid JSON with "error": "Language mismatch" and empty code.
            
            Also analyze the complexity of BOTH the original and optimized code.
            
            Code:
            {code}
            
            Previous Feedback (if any):
            {feedback}
            
            Return JSON with 'thought', 'code', 'original_time_complexity', 'original_space_complexity', 
            'optimized_time_complexity', 'optimized_space_complexity'.
            {format_instructions}
            """
        )
        time.sleep(15)
        chain = prompt | self.llm | self.opt_parser
        return chain.invoke({
            "code": code, 
            "language": language,
            "feedback": feedback,
            "format_instructions": self.opt_parser.get_format_instructions()
        })

    def fix_security(self, code: str, feedback: str = "") -> dict:
        # Security is language agnostic mostly, or we assume it's Python/SQL from context usually?
        # But let's assume Python for now as per previous, or user could supply language.
        # User request "security(only for SQL)".
        # Let's keep it simple.
        prompt = ChatPromptTemplate.from_template(
            """You are an expert Security Engineer. 
            Task: Identify and fix SQL Injection vulnerabilities in the code.
            Use parameterized queries.
            
            IMPORTANT:
            - If the input is just a SQL query, return ONLY the corrected SQL query (using placeholders like ? or %s).
            - If the input is Python code, return ONLY the corrected Python function/snippet.
            - Do NOT generate a full runnable script with database setup/mocking unless the input was already a full script.
            - Keep the output minimal and focused on the fix.
            
            Code:
            {code}
            
            Previous Feedback (if any):
            {feedback}
            
            Return JSON with 'thought' and secure 'code'.
            {format_instructions}
            """
        )
        chain = prompt | self.llm | self.parser
        time.sleep(15)
        return chain.invoke({
            "code": code, 
            "feedback": feedback,
            "format_instructions": self.parser.get_format_instructions()
        })

    def generate_test_driver(self, code: str, test_input: str, language: str) -> dict:
        prompt = ChatPromptTemplate.from_template(
            """You are an expert {language} QA Engineer.
            Task: Create a test driver script to run the functionality in the provided code using the test input.
            
            Code to test:
            {code}
            
            Test Input (could be raw data like JSON, array, or a partial script):
            {test_input}
            
            Goal:
            Generate a TEST DRIVER (the 'main' execution part) that:
            1. Imports necessary libraries (if not likely present in the code).
            2. Defines the main execution block (e.g. `if __name__ == "__main__":` or `int main()`).
            3. Calls the relevant function from the 'Code' with the 'Test Input' data.
            4. Prints output so execution time can be measured.
            
            IMPORTANT:
            - Do NOT re-write or include the original 'Code' in your response. Assume it will be prepended to your driver automatically.
            - Just provide the code that calls the function and handles input/output.
            
            IF 'Test Input' is provided:
            - If it is a complete script, return it as is.
            - If it is just data, wrap it in a function call.
            
            IF 'Test Input' IS EMPTY or NULL:
            - ANALYZE the 'Code' to determine valid input types.
            - GENERATE a challenging test case (large input for benchmarking if possible) inside the driver.
            - Create the driver using this generated input.
            
            Return JSON with 'thought' and 'driver_code'.
            {format_instructions}
            """
        )
        # Use a simple output parser for this new structure
        class TestDriverOutput(BaseModel):
            thought: str = Field(description="How you constructed the driver.")
            driver_code: str = Field(description="The executable test driver code.")

        parser = JsonOutputParser(pydantic_object=TestDriverOutput)
        time.sleep(15)
        chain = prompt | self.llm | parser
        
        return chain.invoke({
            "code": code,
            "test_input": test_input,
            "language": language,
            "format_instructions": parser.get_format_instructions()
        })
