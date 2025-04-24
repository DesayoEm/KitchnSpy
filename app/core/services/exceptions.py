class KitchnSpyExceptions(Exception):
    """ Base class for all KitchnSpy exceptions"""


class DBInsertionError(KitchnSpyExceptions):
    def __init__(self, error: str, data: str):
        super().__init__()
        self.message = f"Price log error for {data}: {error}"


class PriceLoggingError(KitchnSpyExceptions):
    def __init__(self, error: str, product_id: int):
        super().__init__()
        self.display = "An unexpected error occurred"
        self.log = f"DB insert/update error for {product_id}: {error}"


class FailedRequestError(KitchnSpyExceptions):
    def __init__(self, attempt: int, detail: str, tries: int):
        super().__init__()
        self.display = "An unexpected error occurred"
        self.log = f"Request failed: {attempt}/{tries}. DETAIL:{detail}"


class ParsingError(KitchnSpyExceptions):
    def __init__(self, error: str, url: str):
        super().__init__()
        self.display = "An unexpected error occurred"
        self.log = f"Error parsing {url}: Detail: {error}"
