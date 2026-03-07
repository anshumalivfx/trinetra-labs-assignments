"""
Email Service
Handles email sending via SMTP or SendGrid
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """Email service for sending emails"""
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send email via configured provider
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML body
            
        Returns:
            Result dict with status and message_id
        """
        if settings.EMAIL_PROVIDER == "sendgrid":
            return await EmailService._send_via_sendgrid(
                to_email, subject, body, html_body
            )
        else:
            return await EmailService._send_via_smtp(
                to_email, subject, body, html_body
            )
    
    @staticmethod
    async def _send_via_sendgrid(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send email via SendGrid API"""
        try:
            if not settings.SENDGRID_API_KEY:
                raise ValueError("SendGrid API key not configured")
            
            payload = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": settings.EMAIL_FROM},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": body}
                ]
            }
            
            if html_body:
                payload["content"].append({"type": "text/html", "value": html_body})
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    timeout=30.0,
                )
                
                response.raise_for_status()
                
                message_id = response.headers.get("X-Message-Id", "unknown")
                
                logger.info(
                    "email_sent_sendgrid",
                    to_email=to_email,
                    message_id=message_id,
                    status_code=response.status_code,
                )
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "provider": "sendgrid",
                    "status_code": response.status_code,
                }
                
        except Exception as e:
            logger.error(
                "email_send_failed_sendgrid",
                to_email=to_email,
                error=str(e),
            )
            return {
                "success": False,
                "error": str(e),
                "provider": "sendgrid",
            }
    
    @staticmethod
    async def _send_via_smtp(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send email via SMTP"""
        try:
            if not all([settings.SMTP_HOST, settings.SMTP_PORT, 
                       settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
                raise ValueError("SMTP configuration incomplete")
            
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = settings.EMAIL_FROM
            message["To"] = to_email
            message["Subject"] = subject
            
            # Attach plain text
            message.attach(MIMEText(body, "plain"))
            
            # Attach HTML if provided
            if html_body:
                message.attach(MIMEText(html_body, "html"))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=True,
            )
            
            logger.info(
                "email_sent_smtp",
                to_email=to_email,
                smtp_host=settings.SMTP_HOST,
            )
            
            return {
                "success": True,
                "message_id": f"smtp_{to_email}_{subject}",
                "provider": "smtp",
            }
            
        except Exception as e:
            logger.error(
                "email_send_failed_smtp",
                to_email=to_email,
                error=str(e),
            )
            return {
                "success": False,
                "error": str(e),
                "provider": "smtp",
            }
