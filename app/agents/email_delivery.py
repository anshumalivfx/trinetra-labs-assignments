"""
Email Delivery Agent
Validates and prepares emails for delivery
"""
from crewai import Agent, Task
from langchain_mistralai import ChatMistralAI
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_email_delivery_agent() -> Agent:
    """
    Create Email Delivery Agent
    
    Returns:
        Configured CrewAI Agent
    """
    llm = ChatMistralAI(
        model=settings.MISTRAL_MODEL,
        api_key=settings.MISTRAL_API_KEY,
        temperature=0.1,
    )
    
    agent = Agent(
        role="Email Delivery Validator",
        goal="Validate and prepare emails for safe delivery",
        backstory="""You are a meticulous email delivery specialist who ensures 
        that every email meets quality standards before being sent. You check for 
        sensitive information, validate formatting, ensure compliance with email 
        best practices, and flag any potential issues.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
    )
    
    return agent


def create_email_validation_task(
    agent: Agent,
    email_content: Dict[str, Any]
) -> Task:
    """
    Create email validation task
    
    Args:
        agent: The delivery agent
        email_content: Composed email content
        
    Returns:
        Configured Task
    """
    task_description = f"""
    Validate the following email before delivery:
    
    Email Content:
    {email_content}
    
    Your task is to:
    1. Check for any sensitive or confidential information that shouldn't be shared
    2. Verify the email formatting is correct
    3. Ensure the subject line is appropriate and not spam-like
    4. Check for any obvious errors or issues
    5. Validate the tone is professional
    6. Confirm the email has a clear purpose
    
    Return your validation result as a structured JSON object:
    {{
        "is_valid": true/false,
        "validation_passed": true/false,
        "issues_found": ["list of any issues"],
        "warnings": ["list of warnings"],
        "recommendations": ["list of recommendations"],
        "risk_level": "low/medium/high",
        "ready_to_send": true/false
    }}
    
    If the email is ready to send, set ready_to_send to true.
    If there are critical issues, set is_valid to false and explain the issues.
    """
    
    task = Task(
        description=task_description,
        agent=agent,
        expected_output="A structured JSON object containing validation results",
    )
    
    return task
