"""
PDF Analyzer Agent
Extracts and structures document data
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


def create_pdf_analyzer_agent() -> Agent:
    """
    Create PDF Analyzer Agent

    Returns:
        Configured CrewAI Agent
    """
    llm = MistralAIWrapper(
        model=settings.MISTRAL_MODEL,
        mistral_api_key=settings.MISTRAL_API_KEY,
        temperature=0.3,
    )

    agent = Agent(
        role="PDF Document Analyzer",
        goal="Extract and structure key information from PDF documents",
        backstory="""You are an expert document analyst with years of experience 
        in extracting, categorizing, and structuring information from various documents. 
        You excel at identifying key entities, important sections, and creating 
        well-structured summaries that capture the essence of any document.""",
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )

    return agent


def create_pdf_analysis_task(agent: Agent, pdf_content: Dict[str, Any]) -> Task:
    """
    Create PDF analysis task

    Args:
        agent: The analyzer agent
        pdf_content: Extracted PDF content

    Returns:
        Configured Task
    """
    text_excerpt = pdf_content.get("text", "")[:5000]  # Limit for context
    page_count = len(pdf_content.get("pages", []))
    tables = pdf_content.get("tables", [])
    entities = pdf_content.get("entities", [])

    task_description = f"""
    Analyze the following PDF document and extract structured information:
    
    Document Statistics:
    - Total Pages: {page_count}
    - Tables Found: {len(tables)}
    - Entities Detected: {len(entities)}
    
    Text Content (first 5000 chars):
    {text_excerpt}
    
    Your task is to:
    1. Identify the document type (resume, report, letter, invoice, etc.)
    2. Extract key entities (names, organizations, dates, amounts, etc.)
    3. Create a structured summary with main sections
    4. Identify the primary purpose or topic
    5. Extract any action items or important dates
    
    Return your analysis as a structured JSON object with the following schema:
    {{
        "document_type": "string",
        "summary": "string",
        "key_entities": {{
            "names": ["list of names"],
            "organizations": ["list of organizations"],
            "dates": ["list of important dates"],
            "amounts": ["list of monetary amounts"]
        }},
        "main_topics": ["list of main topics"],
        "action_items": ["list of action items"],
        "sentiment": "positive/neutral/negative",
        "confidence_score": 0.0-1.0
    }}
    """

    task = Task(
        description=task_description,
        agent=agent,
        expected_output="A structured JSON object containing document analysis",
    )

    return task
