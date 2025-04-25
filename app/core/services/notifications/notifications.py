from app.core.services.notifications.email import EmailService


class NotificationService:
    def __init__(self):
        self.email_service = EmailService()


    def send_subscription_confirmation(
            self,
            to_email: str,
            name: str,
            product_name: str,
            unsubscribe_link: str
    ) -> bool:
        """Send a welcome/confirmation email after user subscribes."""

        subject = f"You're in! We'll watch {product_name} for you"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #ffffff; color: #283618; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: auto; padding: 20px; }}
                .header {{ background-color: #606c38; color: #fefae0; padding: 20px; border-radius: 12px; text-align: center; }}
                .content {{ background-color: #fefae0; padding: 20px; border-radius: 12px; margin-top: 20px; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Nice one, {name}!</h2>
                </div>
                <div class="content">
                    <p>You're all set — I'm keeping an eye on <strong>{product_name}</strong> for you.</p>
                    <p>Whenever the price changes, we’ll let you know. Until then, just sit back and relax. </p>
                    <p style="font-size: 0.9em;"><a href="{unsubscribe_link}">Unsubscribe</a> if you ever change your mind.</p>
                </div>
                <div class="footer">
                     Just updates when things actually change.
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Hey {name},

        You're in! I'll keep an eye on {product_name} for you.

        Whenever the price changes, you'll be the first to know.
        If you ever want to unsubscribe, use this link: {unsubscribe_link}

        — Desayo
        """

        return self.email_service.send_email(to_email, subject, html_body, text_body)

    def send_unsubscribed_confirmation(
            self,
            to_email: str,
            name: str,
            product_name: str,
            subscription_link: str
    ) -> bool:
        """Send a confirmation email after a user unsubscribes."""

        subject = f"You’ve unsubscribed from {product_name} alerts"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #ffffff;
                    color: #283618;
                    line-height: 1.6;
                }}
                .container {{
                    max-width: 600px;
                    margin: auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #bc6c25;
                    color: #fefae0;
                    padding: 20px;
                    text-align: center;
                    border-radius: 12px;
                }}
                .content {{
                    background-color: #fefae0;
                    padding: 20px;
                    border-radius: 12px;
                    margin-top: 20px;
                    color: #283618;
                }}
                .footer {{
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>You're all set, {name}</h2>
                </div>
                <div class="content">
                    <p>You’ve been unsubscribed from alerts for <strong>{product_name}</strong>.</p>
                    <p>No more notifications from us about this item — but you’re always welcome back if you change your mind.</p>
                    
                </div>
                <div class="footer">
                    This was a one-time unsubscribe confirmation. No further emails will be sent.
                    <br>
                    f"{subscription_link}"
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Hi {name},

        You've been unsubscribed from price alerts for '{product_name}'.

        No more notifications from us — but you can re-subscribe if you change your mind.
        
        f"{subscription_link}"

        """

        return self.email_service.send_email(to_email, subject, html_body, text_body)

    def send_price_change_notification(
            self,
            to_email: str,
            name: str,
            product_name: str,
            old_price: str,
            new_price: str,
            date: str,
            product_link: str
    ) -> bool:

        """Send a notification email to a subscriber."""

        subject = f"Price Update for {product_name}"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #ffffff;
                    color: #283618;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #606c38;
                    color: #fefae0;
                    padding: 20px;
                    text-align: center;
                    border-radius: 12px;
                }}
                .content {{
                    padding: 20px;
                    background-color: #fefae0;
                    border-radius: 12px;
                    margin-top: 20px;
                    color: #283618;
                }}
                .price {{
                    background-color: #dda15e;
                    padding: 10px;
                    border-radius: 8px;
                    display: inline-block;
                    margin: 10px 0;
                    font-weight: bold;
                    color: #283618;
                }}
                .button {{
                    background-color: #bc6c25;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 8px;
                    display: inline-block;
                    margin-top: 15px;
                }}
                .footer {{
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Heads up, {name} 👋</h2>
                    <p>Your watched item has a new price!</p>
                </div>
                <div class="content">
                    <p><strong>{product_name}</strong> had a little price shake-up:</p>
                    <p class="price">Before: £{old_price}</p>
                    <p class="price">Now: £{new_price}</p>
                    <p><small>(as of {date})</small></p>
                    <p>If this one's been sitting on your wishlist, now might be your moment.</p>
                    <a href="{product_link}" class="button">Check it out</a>
                </div>
                <div class="footer">
                    I’ll let you know if anything else changes.  
                    <p>Desayo.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Hey {name},

        Quick heads-up: the price on '{product_name}' just changed.

        Before: £{old_price}
        Now: £{new_price}
        (as of {date})

        If it's been on your radar, now might be the time to check it out:
        {product_link}

        I'll keep you posted with more useful updates (promise — no spam).

        — Desayo
        """

        return self.email_service.send_email(to_email, subject, html_body, text_body)
