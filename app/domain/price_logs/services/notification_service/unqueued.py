
from app.infra.services.notifications.email_templates import EmailTemplateService

class UnqueuedNotificationDispatcher:
    def __init__(self):
        self.template = EmailTemplateService()

    def send_price_change_notification(self, price_change_data: dict):
        return self.template.send_price_change_notification(
            to_email=price_change_data["to_email"],
            name=price_change_data["name"],
            product_name=price_change_data["product_name"],
            previous_price=price_change_data["previous_price"],
            new_price=price_change_data["new_price"],
            price_diff=price_change_data["to_email"],
            change_type=price_change_data["to_email"],
            date_checked=price_change_data["to_email"],
            product_link=price_change_data["to_email"]
        )