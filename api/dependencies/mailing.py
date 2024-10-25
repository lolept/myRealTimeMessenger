from api.services import MailingService


def get_mailing_service() -> MailingService:
    return MailingService()
