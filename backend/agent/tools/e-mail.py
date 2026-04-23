from backend.agent import ToolsRegistry
import os
import smtplib
from email.message import EmailMessage

def _send_email(to: str, subject: str, body: str) -> str:
    smtp_host = os.getenv('SMTP_HOST', '')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')

    if not smtp_host or not smtp_user:
        return "no configurations，please set SMTP_HOST、SMTP_USER、SMTP_PASSWORD"

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        return f"e-mail sent {to}"
    except Exception as e:
        return f"send e-mail fail: {e}"


ToolsRegistry.register(
    name="e-mail",
    description="发送邮件，参数：to（收件人）、subject（主题）、body（内容）",
    func=_send_email
)