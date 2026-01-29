from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from backend.workflows.bug_detection import BugDetectionWorkflow
from backend.workflows.optimization import OptimizationWorkflow
from backend.workflows.security import SecurityWorkflow

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestBody(BaseModel):
    code: str
    issue: str = "" # For bug fix
    test_code: str = "" # Optional test case
    language: str = "python" # Default language

@app.get("/")
def home():
    return {"message": "Agent Backend Ready"}

@app.post("/api/bug-fix")
async def analyze_bug(body: RequestBody):
    workflow = BugDetectionWorkflow()
    initial_state = {
        "code": body.code, 
        "issue": body.issue, 
        "test_code": body.test_code,
        "language": body.language,
        "logs": []
    }
    result = workflow.app.invoke(initial_state)
    return {
        "final_code": result.get("current_code"),
        "logs": result.get("logs"),
        "status": result.get("status")
    }

@app.post("/api/optimize")
async def optimize_code(body: RequestBody):
    workflow = OptimizationWorkflow()
    initial_state = {
        "code": body.code, 
        "test_code": body.test_code,
        "language": body.language,
        "logs": []
    }
    result = workflow.app.invoke(initial_state)
    return {
        "final_code": result.get("current_code"),
        "logs": result.get("logs"),
        "initial_time": result.get("initial_time"),
        "final_time": result.get("final_time"),
        # Return complexity info
        "complexity": {
            "orig_time": result.get("orig_time_complexity"),
            "orig_space": result.get("orig_space_complexity"),
            "opt_time": result.get("opt_time_complexity"),
            "opt_space": result.get("opt_space_complexity")
        }
    }

@app.post("/api/security")
async def analyze_security(body: RequestBody):
    workflow = SecurityWorkflow()
    initial_state = {
        "code": body.code, 
        "language": body.language,
        "logs": []
    }
    result = workflow.app.invoke(initial_state)
    return {
        "final_code": result.get("current_code"),
        "logs": result.get("logs"),
        "status": result.get("status")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
