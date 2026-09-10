class CodeReviewerError(Exception):
    """Base class for all project-specific errors."""


class UnsupportedFileTypeError(CodeReviewerError):
    """Raised when the file extension isn't .py, .js, or .java."""


class FileIngestionError(CodeReviewerError):
    """Raised when a file can't be safely read."""


class AIResponseError(CodeReviewerError):
    """Raised when the AI call fails or returns nothing usable."""


class ResponseValidationError(CodeReviewerError):
    """Raised when the AI response doesn't match the required structure."""