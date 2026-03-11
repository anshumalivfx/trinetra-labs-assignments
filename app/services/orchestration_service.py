"""
Agent Orchestration Service
Coordinates CrewAI agents for PDF processing and email generation
"""

import json
import time
from typing import Dict, Any, Optional
from crewai import Crew, Process

from app.agents.pdf_analyzer import (
    create_pdf_analyzer_agent,
    create_pdf_analysis_task,
)
from app.agents.email_composer import (
    create_email_composer_agent,
    create_email_composition_task,
)
from app.agents.email_delivery import (
    create_email_delivery_agent,
    create_email_validation_task,
)
from app.services.email_service import EmailService
from app.core.logging import get_logger

logger = get_logger(__name__)


class OrchestrationService:
    """Service for orchestrating multi-agent workflows"""

    @staticmethod
    async def process_document_and_send_email(
        pdf_content: Dict[str, Any],
        recipient_email: str,
        document_id: int,
        job_id: str,
    ) -> Dict[str, Any]:
        """
        Main orchestration workflow

        Args:
            pdf_content: Extracted PDF content
            recipient_email: Email recipient
            document_id: Document ID
            job_id: Job ID for tracking

        Returns:
            Workflow result dict
        """
        start_time = time.time()
        result = {
            "job_id": job_id,
            "document_id": document_id,
            "stages": {},
            "success": False,
        }

        try:
            # Stage 1: PDF Analysis
            logger.info(
                "orchestration_stage_1_started", job_id=job_id, stage="pdf_analysis"
            )
            analysis_result = await OrchestrationService._analyze_pdf(
                pdf_content, job_id
            )
            result["stages"]["pdf_analysis"] = analysis_result

            if not analysis_result.get("success"):
                raise Exception("PDF analysis failed")

            # Stage 2: Email Composition
            logger.info(
                "orchestration_stage_2_started",
                job_id=job_id,
                stage="email_composition",
            )
            composition_result = await OrchestrationService._compose_email(
                analysis_result["data"],
                recipient_email,
                job_id,
            )
            result["stages"]["email_composition"] = composition_result

            if not composition_result.get("success"):
                raise Exception("Email composition failed")

            # Stage 3: Email Validation
            logger.info(
                "orchestration_stage_3_started", job_id=job_id, stage="email_validation"
            )
            validation_result = await OrchestrationService._validate_email(
                composition_result["data"],
                job_id,
            )
            result["stages"]["email_validation"] = validation_result

            if not validation_result.get("ready_to_send"):
                logger.warning(
                    "email_not_ready_to_send",
                    job_id=job_id,
                    issues=validation_result.get("issues"),
                )
                # Send anyway but log the issues

            # Stage 4: Email Delivery
            logger.info(
                "orchestration_stage_4_started", job_id=job_id, stage="email_delivery"
            )
            email_data = composition_result["data"]
            delivery_result = await EmailService.send_email(
                to_email=recipient_email,
                subject=email_data.get("subject", "Document Analysis Results"),
                body=email_data.get("body", ""),
            )
            result["stages"]["email_delivery"] = delivery_result

            # Final result
            result["success"] = delivery_result.get("success", False)
            result["execution_time_ms"] = int((time.time() - start_time) * 1000)

            logger.info(
                "orchestration_completed",
                job_id=job_id,
                success=result["success"],
                execution_time_ms=result["execution_time_ms"],
            )

            return result

        except Exception as e:
            logger.error(
                "orchestration_failed",
                job_id=job_id,
                error=str(e),
                execution_time_ms=int((time.time() - start_time) * 1000),
            )
            result["success"] = False
            result["error"] = str(e)
            result["execution_time_ms"] = int((time.time() - start_time) * 1000)
            return result

    @staticmethod
    async def _analyze_pdf(
        pdf_content: Dict[str, Any],
        job_id: str,
    ) -> Dict[str, Any]:
        """Run PDF analysis agent"""
        try:
            start_time = time.time()

            # Create agent and task
            analyzer = create_pdf_analyzer_agent()
            task = create_pdf_analysis_task(analyzer, pdf_content)

            # Create crew with single agent
            crew = Crew(
                agents=[analyzer],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )

            # Execute
            output = crew.kickoff()

            # Parse output
            try:
                # Try to extract JSON from output
                output_str = str(output)
                # Look for JSON content
                if "{" in output_str and "}" in output_str:
                    json_start = output_str.find("{")
                    json_end = output_str.rfind("}") + 1
                    json_str = output_str[json_start:json_end]
                    parsed_output = json.loads(json_str)
                else:
                    # Fallback to basic structure
                    parsed_output = {
                        "document_type": "unknown",
                        "summary": output_str,
                        "raw_output": output_str,
                    }
            except json.JSONDecodeError:
                parsed_output = {
                    "document_type": "unknown",
                    "summary": str(output),
                    "raw_output": str(output),
                }

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "data": parsed_output,
                "execution_time_ms": execution_time,
                "agent_name": "PDF Analyzer",
            }

        except Exception as e:
            logger.error("pdf_analysis_failed", job_id=job_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "agent_name": "PDF Analyzer",
            }

    @staticmethod
    async def _compose_email(
        analysis_result: Dict[str, Any],
        recipient_email: str,
        job_id: str,
    ) -> Dict[str, Any]:
        """Run email composition agent"""
        try:
            start_time = time.time()

            # Create agent and task
            composer = create_email_composer_agent()
            task = create_email_composition_task(
                composer, analysis_result, recipient_email
            )

            # Create crew
            crew = Crew(
                agents=[composer],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )

            # Execute
            output = crew.kickoff()

            # Parse output
            try:
                output_str = str(output)
                if "{" in output_str and "}" in output_str:
                    json_start = output_str.find("{")
                    json_end = output_str.rfind("}") + 1
                    json_str = output_str[json_start:json_end]
                    parsed_output = json.loads(json_str)
                else:
                    # Fallback
                    parsed_output = {
                        "subject": "Document Analysis Results",
                        "body": output_str,
                    }
            except json.JSONDecodeError:
                parsed_output = {
                    "subject": "Document Analysis Results",
                    "body": str(output),
                }

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "data": parsed_output,
                "execution_time_ms": execution_time,
                "agent_name": "Email Composer",
            }

        except Exception as e:
            logger.error("email_composition_failed", job_id=job_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "agent_name": "Email Composer",
            }

    @staticmethod
    async def _validate_email(
        email_content: Dict[str, Any],
        job_id: str,
    ) -> Dict[str, Any]:
        """Run email validation agent"""
        try:
            start_time = time.time()

            # Create agent and task
            validator = create_email_delivery_agent()
            task = create_email_validation_task(validator, email_content)

            # Create crew
            crew = Crew(
                agents=[validator],
                tasks=[task],
                process=Process.sequential,
                verbose=True,
            )

            # Execute
            output = crew.kickoff()

            # Parse output
            try:
                output_str = str(output)
                if "{" in output_str and "}" in output_str:
                    json_start = output_str.find("{")
                    json_end = output_str.rfind("}") + 1
                    json_str = output_str[json_start:json_end]
                    parsed_output = json.loads(json_str)
                else:
                    # Default to pass
                    parsed_output = {
                        "is_valid": True,
                        "ready_to_send": True,
                        "risk_level": "low",
                    }
            except json.JSONDecodeError:
                parsed_output = {
                    "is_valid": True,
                    "ready_to_send": True,
                    "risk_level": "low",
                }

            execution_time = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "ready_to_send": parsed_output.get("ready_to_send", True),
                "data": parsed_output,
                "execution_time_ms": execution_time,
                "agent_name": "Email Validator",
            }

        except Exception as e:
            logger.error("email_validation_failed", job_id=job_id, error=str(e))
            # Default to allowing send if validation fails
            return {
                "success": False,
                "ready_to_send": True,
                "error": str(e),
                "agent_name": "Email Validator",
            }
