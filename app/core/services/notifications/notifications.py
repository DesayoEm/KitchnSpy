from app.core.services.notifications.email import EmailService


class NotificationService:
    def __init__(self):
        self.email_service = EmailService()

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
