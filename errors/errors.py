class CustomError(Exception):
    pass


class DatabaseConnectionError(CustomError):
    def __init__(self, message="Error with connection to db"):
        self.message = message
        super().__init__(self.message)


class Error404(CustomError):
    def __init__(self, message="Error with status code 404"):
        self.message = message
        super().__init__(self.message)


class Error409(CustomError):
    def __init__(self, message="Error with status code 409"):
        self.message = message
        super().__init__(self.message)


class ContentError(CustomError):
    def __init__(self, message="GPT response is incorrect"):
        self.message = message
        super().__init__(self.message)


class ParseError(CustomError):
    def __init__(self, message="Error with processing GPT answer"):
        self.message = message
        super().__init__(self.message)
