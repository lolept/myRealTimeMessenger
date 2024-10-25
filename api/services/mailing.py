import logging

import fastapi_mail
import jinja2

from api.config import settings
from api.schemas.user import UserReadSchema

logger = logging.getLogger(__name__)


class MailingService:
    
    def __init__(self):
        self.fm = fastapi_mail.FastMail(
            fastapi_mail.ConnectionConfig(
                MAIL_USERNAME=settings.EMAIL_USERNAME,
                MAIL_PASSWORD=settings.EMAIL_PASSWORD,
                MAIL_FROM=settings.EMAIL_FROM,
                MAIL_PORT=settings.EMAIL_PORT,
                MAIL_SERVER=settings.EMAIL_HOST,
                MAIL_STARTTLS=False,
                MAIL_SSL_TLS=settings.EMAIL_TLS,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True,
                MAIL_DEBUG=True,
            )
        )
        self.jinja_env = jinja2.Environment(
            loader=jinja2.PackageLoader("frontend", "templates"),
            autoescape=jinja2.select_autoescape(["html", "xml"]),
        )
    
    async def _send_mail(
            self,
            subject: str,
            template: str,
            email: list[str],
            data: str | int,
            name: str
    ) -> None:
        template = self.jinja_env.get_template(f"{template}.html")
        rendered_template = template.render(
            data=data,
            first_name=name,
            subject=subject
        )
        message = fastapi_mail.MessageSchema(
            subject=subject,
            recipients=email,
            body=rendered_template,
            subtype=fastapi_mail.MessageType.html
        )
        logger.info("Sending email to %s", email)
        await self.fm.send_message(message)
    
    async def send_email_verification_mail(
            self,
            email: str,
            url: str
    ) -> None:
        logger.info("Sending email verification mail to %s", email)
        try:
            await self._send_mail(
                "Ваш код подтверждения",
                "verification_mail",
                [email],
                url,
                email
            )
        except Exception as e:
            logger.exception(e)
            raise e
    
    async def send_reset_password_code(self, email: str, code: int) -> None:
        logger.info("Sending email verification email to %s", email)
        await self._send_mail(
            "Ваш код сброса пароля",
            "reset_password",
            [email],
            code,
            email
        )
