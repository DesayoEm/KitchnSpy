class KitchnSpyExceptions(Exception):
    """ Base class for all KitchnSpy exceptions"""


class DocsNotFoundError(KitchnSpyExceptions):
    def __init__(self, entities:str, page: int):
        super().__init__()
        self.display = f"{entities} not found"
        self.log = f"No {entities} found on page {page}"

class DocNotFoundError(KitchnSpyExceptions):
    def __init__(self, identifier: str, entity:str):
        super().__init__()
        self.display = f"{entity} not found"
        self.log = f"{entity} with id {identifier} not found"

class DuplicateEntityError(KitchnSpyExceptions):
    def __init__(self, entry:str, entity:str):
        super().__init__()
        self.display = f"{entity} already exists"
        self.log = f"{entity} with id {entry} already exists"

class EmptySearchError(KitchnSpyExceptions):
    def __init__(self, entry:str):
        super().__init__()
        self.display = "Search term must not be empty"
        self.log = f"Empty search term attempted. Entry: {entry}"

class InvalidIdError(KitchnSpyExceptions):
    def __init__(self, entity: str, detail: str):
        super().__init__()
        self.display = "Invalid Identifier"
        self.log = f"Invalid id for {entity}. Detail: {detail}"

class ExistingSubscriptionError(KitchnSpyExceptions):
    def __init__(self, email_address: str, product_id: str):
        super().__init__()
        self.display = "You're already subscribed to notifications for this item"
        self.log = f"Subscriber {email_address} already exists for product - {product_id}"

class NotSubscribedError(KitchnSpyExceptions):
    def __init__(self, email_address: str):
        super().__init__()
        self.display = "You're not subscribed to  notifications for this item"
        self.log = f"Non subscriber attempted to unsubscribe {email_address}"

class DBInsertionError(KitchnSpyExceptions):
    def __init__(self, error: str, data: str):
        super().__init__()
        self.display = "Price log error"
        self.log = f"Price log error for {data}: {error}"

class URLNotFoundError(KitchnSpyExceptions):
    def __init__(self, url: str):
        super().__init__()
        self.display = "URL not found"
        self.log = f"Product with URL {url} not found"

class PriceLoggingError(KitchnSpyExceptions):
    def __init__(self, error: str, product_id: str):
        super().__init__()
        self.display = "An unexpected error occurred"
        self.log = f"DB insert/update error for {product_id}: {error}"

class FailedRequestError(KitchnSpyExceptions):
    def __init__(self, attempt: int, detail: str, tries: int):
        super().__init__()
        self.display = "Failed HTTP request"
        self.log = f"Request failed: {attempt}/{tries}. DETAIL:{detail}"

class ParsingError(KitchnSpyExceptions):
    def __init__(self, error: str, url: str):
        super().__init__()
        self.display = "Error parsing url"
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


