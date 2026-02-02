"""
FastAPI wrapper for Code Suggester Agent
Deploy on Render as a Web Service
"""

import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import CodeSuggester

app = FastAPI(
    title="Code Suggester Agent",
    description="AI-powered code suggestions based on screen context",
    version="1.0.0"
)


class AgentRequest(BaseModel):
    command: str  # The code context/intent
    context: Optional[str] = None  # Additional context
    user_id: Optional[str] = None


class AgentResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
async def health():
    """Health check endpoint for Render."""
    return {"status": "healthy", "agent": "code-suggester", "version": "1.0.0"}


@app.post("/", response_model=AgentResponse)
async def handle_command(request: AgentRequest, raw_request: Request):
    """
    Main endpoint for Friday to call.

    The command should contain code context like:
    - Current code snippets visible
    - Error messages
    - File type/language
    - What the user seems to be doing
    """
    # Check for API key override in headers
    api_key = raw_request.headers.get("X-OpenRouter-Api-Key")
    if api_key:
        os.environ["OPENROUTER_API_KEY"] = api_key

    command = request.command.strip()
    additional_context = request.context or ""

    if not command:
        return AgentResponse(success=False, error="Missing command/context")

    # Combine command and additional context
    full_context = command
    if additional_context:
        full_context = f"{command}\n\nAdditional context:\n{additional_context}"

    try:
        agent = CodeSuggester()
        result = agent.run(full_context)

        if result.startswith("Error"):
            return AgentResponse(success=False, error=result)

        return AgentResponse(success=True, result=result)

    except ValueError as e:
        return AgentResponse(success=False, error=str(e))
    except Exception as e:
        return AgentResponse(success=False, error=f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
