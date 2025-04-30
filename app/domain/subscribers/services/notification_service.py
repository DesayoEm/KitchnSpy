from app.infra.email.email_config import EmailService

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
                .header {{ background-color: #5e2945; color: #000000; padding: 8px; border-radius: 12px; text-align: center; }}
                .content {{ background-color: #f1e8ed; padding: 20px; border-radius: 12px; margin-top: 20px; }}
                .footer {{ font-size: 12px; color: #666; text-align: center; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Nice one, {name.title()}!</h2>
                </div>
                <div class="content">
                    <p>You're all set. We're keeping an eye on <strong>{product_name}</strong> for you.</p>
                    <p>Whenever the price changes, we’ll let you know. Until then, just sit back and relax. </p>
                    </br></br>
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
        Hey {name.title()},

        You're in! We'll keep an eye on {product_name} for you.

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
                    background-color: #893959;
                    color: #000000;
                    padding: 20px;
                    text-align: center;
                    border-radius: 12px;
                }}
                .content {{
                    background-color: #f1e8ed;
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
                    <h2>You're all set, {name.title()}. </h2>
                </div>
                <div class="content">
                    <p>You’ve been unsubscribed from alerts for <strong>{product_name}</strong>.</p>
                    <p>No more notifications from us about this item but you’re always welcome back if you change your mind.</p>
                    </br>
                    <p style="font-size: 0.9em;"><a href="{subscription_link}">Subscribe again</a> if you ever change your mind.</p>
                    
                </div>
                <div class="footer">
                    This was a one-time unsubscribe confirmation. No further emails will be sent.
                    <br>
                    
        
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Hi {name},

        You've been unsubscribed from price alerts for '{product_name}'.

        No more notifications from us but you can re-subscribe if you change your mind.
        
        "{subscription_link}"

        """

        return self.email_service.send_email(to_email, subject, html_body, text_body)

    def send_price_change_notification(
            self,
            to_email: str,
            name: str,
            product_name: str,
            previous_price: float,
            new_price: float,
            price_diff: float,
            change_type: str,
            date_checked: str,
            product_link: str
    ) -> bool:
        """Send a notification email to a subscriber."""

        change_dir = "less" if change_type == "drop" else "more"

        subject = f"Price {change_type} Update for {product_name}"

        html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #ffffff;
                    color: #000000;
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
                    background-color: #893959;
                    color: #000000;
                    padding: 12px;
                    text-align: center;
                    border-radius: 12px;
                }}
                .content {{
                    padding: 20px;
                    background-color: #fdeef0;
                    border-radius: 12px;
                    margin-top: 20px;
                    color: #283618;
                }}
                .price {{
                    background-color: #dfebae;
                    padding: 10px;
                    border-radius: 8px;
                    display: inline-block;
                    margin: 10px 0;
                    font-weight: bold;
                    font-size: 0.9em;
                    color: #000000;
                }}
                .button {{
                    background-color: #893959;
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
                    <h2>Heads up, {name.title()}! 👋</h2>
                    <p>Your watched item has a new price!</p>
                </div>
                <div class="content">
                    <p><strong>{product_name}</strong> had a little price shake-up:</p>
                    <p class="price">Before: £{previous_price:.2f}</p>
                    <p class="price">Now: £{new_price:.2f}</p>
                    <p class="price">Change: £{price_diff:.2f} {change_dir}</p>

                    <p><small>(as of {date_checked})</small></p>
                    <p>If this one's been sitting on your wishlist, now might be your moment.</p>
                    <a href="{product_link}" style="color: #000000;" class="button">Check it out</a>
                </div>
                <div class="footer">
                    We’ll let you know if anything else changes.  
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
    Hey {name.title()},

    Quick heads-up: the price on '{product_name}' just changed.

    Before: £{previous_price:.2f}
    Now: £{new_price:.2f}
    (as of {date_checked})

    If it's been on your radar, now might be the time to check it out:
    {product_link}

    I'll keep you posted with more useful updates (promise — no spam).

    — Desayo
    """

        return self.email_service.send_email(to_email, subject, html_body, text_body)


    def send_product_removed_notification(
            self,
            to_email: str,
            name: str,
            product_name: str
    ) -> bool:
        """
        Send a notification email when a product is no longer being tracked.

        Args:
            to_email (str): Subscriber's email address.
            name (str): Subscriber's name.
            product_name (str): Name of the product that is being removed.

        Returns:
            bool: Whether the email was sent successfully.
        """
        subject = f"Update: We're no longer tracking {product_name}"

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
                    background-color: #893959;
                    color: #000000;
                    padding: 8px;
                    text-align: center;
                    border-radius: 12px;
                }}
                .content {{
                    background-color: #fdeef0;
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
                    <h2>Hello {name.title()},</h2>
                </div>
                <div class="content">
                    <p>We wanted to let you know that we are no longer tracking <strong>{product_name}</strong> on KitchnSpy.</p>
                    <p>Thank you for subscribing and trusting us to keep you updated. We hope you'll continue exploring more great deals with us!</p>
                    <p>If you're interested, you can always subscribe to track other products on our site.</p>
                </div>
                <div class="footer">
                    Thank you for being part of the KitchnSpy community.
                
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Hello {name.title()},

        We wanted to let you know that we are no longer tracking '{product_name}' on KitchnSpy.

        Thank you for subscribing and trusting us to keep you updated.
        We hope you'll continue exploring more great deals with us!

        — Desayo
        """

        return self.email_service.send_email(to_email, subject, html_body, text_body)

