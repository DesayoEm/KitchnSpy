import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.exceptions import EmailFailedError
from app.infra.config import email_settings

class EmailService:
    def __init__(self):
        self.username = email_settings.MAIL_USERNAME
        self.password = email_settings.MAIL_PASSWORD
        self.server = email_settings.MAIL_SERVER
        self.port = email_settings.MAIL_PORT
        self.sender = email_settings.MAIL_FROM
        self.use_tls = email_settings.MAIL_TLS
        self.use_ssl = email_settings.MAIL_SSL


    def send_email(self, recipient: str, subject: str, body_html: str,
                            body_text: str = None) -> bool:
        """Send email_service to a recipient with a given subject and body."""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender
        message["To"] = recipient

        if body_text:
            message.attach(MIMEText(body_text, "plain"))

        message.attach(MIMEText(body_html, "html"))
        try:
            with smtplib.SMTP(self.server, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.sender, recipient, message.as_string())
                return True

        except Exception as e:
            raise EmailFailedError(detail = str(e))