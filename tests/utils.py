class CustomException(Exception):
    def __init__(self, message: str):
        self.message = message


def throw(err: Exception):
    raise err
