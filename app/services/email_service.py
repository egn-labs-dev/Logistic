import os

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("SMTP_USER", "test"),
    MAIL_PASSWORD=os.getenv("SMTP_PASSWORD", "test"),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@zt-dispatch.com"),
    MAIL_PORT=int(os.getenv("SMTP_PORT", 587)),
    MAIL_SERVER=os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_password_reset_email(email: EmailStr, token: str):
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_link = f"{frontend_url}/reset-password?token={token}"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4f46e5;">Zero Trust Dispatch</h2>
        <p>You have requested to reset your password.</p>
        <p>Please click the button below to set a new password. This link is valid for 30 minutes.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                Reset Password
            </a>
        </div>
        <p style="color: #64748b; font-size: 12px;">If you did not request a password reset, please ignore this email or contact support if you have concerns.</p>
    </div>
    """

    message = MessageSchema(
        subject="Password Reset Request - Zero Trust Dispatch",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
