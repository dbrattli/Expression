class ObjectDisposedException(Exception):
    def __init__(self):
        super().__init__("The operation was canceled")


class OperationCanceledError(Exception):
    pass
