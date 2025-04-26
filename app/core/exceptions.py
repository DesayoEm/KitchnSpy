class KitchnSpyExceptions(Exception):
    """ Base class for all KitchnSpy exceptions"""


class DBInsertionError(KitchnSpyExceptions):
    def __init__(self, error: str, data: str):
        super().__init__()
        self.display = "An unexpected error occurred"
        self.log = f"Price log error for {data}: {error}"

class NotFoundError(KitchnSpyExceptions):
    def __init__(self, url: str):
        super().__init__()
        self.display = "An unexpected error occurred"
        self.log = f"Product with url {url} not found"


class PriceLoggingError(KitchnSpyExceptions):
    def __init__(self, error: str, product_id: str):
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


class URIConnectionError(KitchnSpyExceptions):
    def __init__(self):
        super().__init__()
        self.display = "An unexpected error occurred"
        self.log = f"Missing or invalid DB_URI"


class EmailFailedError(KitchnSpyExceptions):
    def __init__(self, detail: str):
        super().__init__()
        self.display = "An unexpected error occurred"
        self.log = f"Email failed to send. DETAIL: {detail}"

class InvalidIdError(KitchnSpyExceptions):
    def __init__(self, detail: str):
        super().__init__()
        self.display = "An unexpected error occurred"
        self.log = f"Invalid id: {detail}"