
from app.infra.services.notifications.email_templates import EmailTemplateService

class UnqueuedNotificationDispatcher:
    def __init__(self):
        self.template = EmailTemplateService()

    def send_product_removed_notification(self, deleted_product_data: dict):
        return self.template.send_product_removed_notification(
            to_email=deleted_product_data["to_email"],
            name=deleted_product_data["name"],
            product_name=deleted_product_data["product_name"]
        )

