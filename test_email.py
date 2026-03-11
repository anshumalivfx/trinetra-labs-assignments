import asyncio
from app.services.email_service import EmailService

async def test_email():
    result = await EmailService.send_email(
        to_email="anshumali.karna99@gmail.com",
        subject="Test Email from AI Agent System",
        body="This is a test email to verify Gmail SMTP configuration.",
        html_body="<h1>Test Successful!</h1><p>Gmail SMTP is working correctly.</p>"
    )
    print(result)

asyncio.run(test_email())