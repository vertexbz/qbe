from qbe.cli import Error
class OperationFailed(Error):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason
