import re

class PriceUtils:
    def __init__(self):
        pass

    @staticmethod
    def parse_price(price_str: str) -> float:
        return float(price_str.replace("£", "").replace(",", ""))

    @staticmethod
    def validate_price_format(value: str) -> str:
        """Validate that the price starts with '£' and format it."""

        if not value.strip().startswith("£"):
            raise ValueError("Price must start with '£'")

        matches = re.findall(r'£\s*(\d+(?:\.\d{2})?)', value)
        if not matches:
            return value

        numeric_prices = [float(p) for p in matches]
        highest_price = max(numeric_prices)

        return f"£ {highest_price:.2f}"

    @staticmethod
    def detect_change(previous_price: float, new_price: float):
        if new_price > previous_price:
            price_diff = new_price-previous_price
            change_type = "Rise"
            trigger = True
        elif previous_price > new_price:
            price_diff = previous_price - new_price
            change_type = "Drop"
            trigger = True
        else:
            price_diff = 0.0
            change_type = "No change"
            trigger = False

        return {
            "trigger": trigger,
            "price_diff": price_diff,
            "change_type": change_type
        }
