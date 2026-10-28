"""Public, framework-independent regression interfaces."""

from fail2test.errors import Fail2TestError, IncompleteExecutionError
from fail2test.execution import RunContext
from fail2test.models import Case, RunResult

__version__ = "0.1.0"
__all__ = [
    "Case",
    "Fail2TestError",
    "IncompleteExecutionError",
    "RunContext",
    "RunResult",
    "__version__",
]
