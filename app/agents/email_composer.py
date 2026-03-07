"""
Email Composer Agent
Generates professional contextual emails
"""
from crewai import Agent, Task
from langchain_mistralai import ChatMistralAI
from typing import Dict, Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_email_composer_agent() -> Agent:
    """
    Create Email Composer Agent
    
    Returns:
        Configured CrewAI Agent
    """
    llm = ChatMistralAI(
        model=settings.MISTRAL_MODEL,
        api_key=settings.MISTRAL_API_KEY,
        temperature=0.7,
    )
    
    agent = Agent(
        role="Professional Email Composer",
        goal="Compose professional, contextual emails based on document analysis",
        backstory="""You are an expert professional communicator with extensive 
        experience in corporate communications. You excel at crafting clear, 
        concise, and professional emails that are tailored to the context and 
        purpose. You understand tone, formality levels, and how to structure 
        emails for maximum impact and clarity.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )
    
    return agent


def create_email_composition_task(
    agent: Agent,
    analysis_result: Dict[str, Any],
    recipient_email: str
) -> Task:
    """
    Create email composition task
    
    Args:
        agent: The composer agent
        analysis_result: Results from PDF analyzer
        recipient_email: Email recipient
        
    Returns:
        Configured Task
    """
    task_description = f"""
    Based on the following document analysis, compose a professional email:
    
    Document Analysis:
    {analysis_result}
    
    Recipient: {recipient_email}
    
    Your task is to:
    1. Craft an appropriate subject line
    2. Write a professional email body that:
       - References the document appropriately
       - Highlights key findings or points
       - Is clear and concise
       - Uses appropriate tone for the document type
       - Includes a clear call-to-action if needed
    3. Ensure proper email formatting and structure
    
    Return your email as a structured JSON object:
    {{
        "subject": "email subject line",
        "body": "full email body with proper formatting",
        "tone": "formal/semi-formal/casual",
        "key_points": ["list of key points covered"],
        "call_to_action": "any call to action or null"
    }}
    
    Guidelines:
    - Be professional and courteous
    - Keep it concise but informative
    - Use proper email etiquette
    - Tailor the tone to the document type
    """
    
    task = Task(
        description=task_description,
        agent=agent,
        expected_output="A structured JSON object containing the composed email",
    )
    
    return task
