"""Stable errors; user-controlled payloads are deliberately excluded from messages."""


class Fail2TestError(Exception):
    """A reportable tooling error with a stable machine code."""

    def __init__(self, code: str, message: str, exit_code: int = 2) -> None:
        self.code = code
        self.message = message
        self.exit_code = exit_code
        super().__init__(f"{code}: {message}")


class IncompleteExecutionError(Fail2TestError):
    """An execution could not establish the selected behavioral outcome."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message, 3)
