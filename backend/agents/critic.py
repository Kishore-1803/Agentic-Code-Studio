from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import time

class CriticOutput(BaseModel):
    approved: bool = Field(description="True if the code is good enough, False otherwise.")
    feedback: str = Field(description="Constructive feedback or 'Looks good'.")

class CriticAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.1)
        self.parser = JsonOutputParser(pydantic_object=CriticOutput)

    def review(self, code: str, task: str) -> dict:
        prompt = ChatPromptTemplate.from_template(
            """You are a Senior Code Reviewer.
            Task: Review the code for {task}.
            
            Criteria:
            - If task is 'bug_fix': Check if logic seems correct and bug is gone.
            - If task is 'optimization': Check if complexity is actually improved and code is readable.
            - If task is 'security': STRICTLY check for SQL Injection. If any string concatenation is used for SQL queries, REJECT IT.
            
            Code:
            {code}
            
            Return JSON with 'approved' (boolean) and 'feedback' (string).
            {format_instructions}
            """
        )
        time.sleep(15)
        chain = prompt | self.llm | self.parser
        return chain.invoke({
            "code": code, 
            "task": task,
            "format_instructions": self.parser.get_format_instructions()
        })
