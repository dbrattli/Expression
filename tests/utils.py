class CustomException(Exception):
    def __init__(self, message):
        self.message = message


def throw(err):
    raise err
