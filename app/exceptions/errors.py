class ProductNotFoundError(Exception):
    def __init__(self, message: str = "product not found"):
        self.message = message
        super().__init__(message)