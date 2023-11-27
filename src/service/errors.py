class AccountProcessingError(Exception):
    def __init__(self, error_message):
        self.message = error_message
        super().__init__(error_message)
