"""One exception type for every AI-related failure.

`user_message` is safe to show to the user.
`log_detail` is technical and is only written to the server log.
"""


class LLMError(Exception):
    def __init__(self, status_code: int, user_message: str, log_detail: str = ""):
        super().__init__(user_message)
        self.status_code = status_code
        self.user_message = user_message
        self.log_detail = log_detail
