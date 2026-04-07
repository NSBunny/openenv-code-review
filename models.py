from typing import List, Optional, Dict
from pydantic import Field
from openenv.core.env_server import Action, Observation, State


class CodeReviewAction(Action):
    """Agent submits a code review with identified issues."""
    issues: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of issues found. Each dict has: "
                    "'line' (int as str), 'severity' (low/medium/high), "
                    "'category' (syntax/logic/style/security), "
                    "'description' (explanation of the issue)"
    )
    summary: str = Field(
        default="",
        description="Overall summary of the code quality"
    )


class CodeReviewObservation(Observation):
    """What the agent sees — the code to review and feedback."""
    task_id: str = ""                          # Unique task identifier
    difficulty: str = ""                       # "easy", "medium", or "hard"
    code_snippet: str = ""                     # The Python code to review
    task_description: str = ""                 # What the code is supposed to do
    num_hidden_issues: int = 0                 # How many issues exist (hint)
    feedback: str = ""                         # Grader feedback after submission
    issues_found: int = 0                      # How many correct issues agent found
    issues_total: int = 0                      # Total ground-truth issues
    false_positives: int = 0                   # Incorrect issues reported
    message: str = ""                          # System message


class CodeReviewState(State):
    """Episode metadata."""
    task_id: str = ""
    difficulty: str = ""
    max_steps: int = 1                         # Single-step environment (review once)
    total_issues: int = 0
