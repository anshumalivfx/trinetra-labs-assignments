"""
Email Composer Agent
Generates professional contextual emails
"""

from crewai import Agent, Task
from langchain_mistralai import ChatMistralAI
from typing import Dict, Any, Optional, List
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class MistralAIWrapper(ChatMistralAI):
    """Wrapper to filter out unsupported parameters for older Mistral API versions"""

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Any:
        """Override to remove stop parameter"""
        # Remove stop from kwargs as mistralai 0.0.8 doesn't support it
        kwargs.pop("stop", None)
        return super()._generate(messages, stop=None, run_manager=run_manager, **kwargs)


def create_email_composer_agent() -> Agent:
    """
    Create Email Composer Agent

    Returns:
        Configured CrewAI Agent
    """
    llm = MistralAIWrapper(
        model=settings.MISTRAL_MODEL,
        mistral_api_key=settings.MISTRAL_API_KEY,
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
        max_iter=5,
    )

    return agent


def create_email_composition_task(
    agent: Agent, analysis_result: Dict[str, Any], recipient_email: str
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
    # Extract key information from analysis
    doc_type = analysis_result.get("document_type", "document")
    summary = analysis_result.get("summary", "No summary available")
    main_topics = analysis_result.get("main_topics", [])
    action_items = analysis_result.get("action_items", [])

    task_description = f"""
    Compose a professional email to {recipient_email} about the analyzed document.
    
    Document Type: {doc_type}
    Summary: {summary}
    Main Topics: {', '.join(main_topics[:5])}
    
    Create an email with:
    1. A clear, relevant subject line
    2. A professional greeting
    3. A brief summary of the document (2-3 sentences)
    4. Key highlights or findings
    5. A professional closing
    
    Format as JSON:
    {{
        "subject": "your subject line here",
        "body": "your full email text here"
    }}
    
    Keep the email concise and professional.
    """

    task = Task(
        description=task_description,
        agent=agent,
        expected_output="JSON with subject and body fields",
    )

    return task
