import random
import uuid
from typing import Optional

from openenv.core.env_server import Environment

from code_review_env.models import CodeReviewAction, CodeReviewObservation, CodeReviewState
from code_review_env.tasks.task_bank import TASKS, get_task_by_id, get_all_task_ids
from .grader import grade_review


class CodeReviewEnvironment(Environment):
    """
    AI Code Review Environment.
    
    The agent receives a Python code snippet and must identify bugs,
    style issues, and security vulnerabilities. Rewards are based on
    precision/recall of correctly identified issues.
    """
    
    SUPPORTS_CONCURRENT_SESSIONS = True
    
    def __init__(self):
        self._state = CodeReviewState()
        self._current_task = None
        self._done = False
    
    def reset(self, seed=None, episode_id=None, options=None, **kwargs) -> CodeReviewObservation:
        """Start a new code review episode."""
        options = options or {}
        
        # Select task
        task_id = options.get("task_id")
        difficulty = options.get("difficulty")
        
        if task_id:
            self._current_task = get_task_by_id(task_id)
        elif difficulty:
            pool = [t for t in TASKS if t["difficulty"] == difficulty]
            self._current_task = random.choice(pool) if pool else random.choice(TASKS)
        else:
            self._current_task = random.choice(TASKS)
            
        if self._current_task is None: # fallback
            self._current_task = TASKS[0]
            
        self._done = False
        
        self._state = CodeReviewState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_id=self._current_task["task_id"],
            difficulty=self._current_task["difficulty"],
            max_steps=1,
            total_issues=len(self._current_task["ground_truth_issues"]),
        )
        
        return CodeReviewObservation(
            done=False,
            reward=None,
            task_id=self._current_task["task_id"],
            difficulty=self._current_task["difficulty"],
            code_snippet=self._current_task["code_snippet"],
            task_description=self._current_task["description"],
            num_hidden_issues=len(self._current_task["ground_truth_issues"]),
            feedback="",
            issues_found=0,
            issues_total=len(self._current_task["ground_truth_issues"]),
            false_positives=0,
            message=f"Review this {self._current_task['difficulty']} code snippet. "
                    f"Find {len(self._current_task['ground_truth_issues'])} issue(s). "
                    f"Submit your review as a list of issues.",
        )
    
    def step(self, action: CodeReviewAction, timeout_s=None, **kwargs) -> CodeReviewObservation:
        """Process the agent's code review submission."""
        self._state.step_count += 1
        
        if self._done:
            return CodeReviewObservation(
                done=True,
                reward=0.0,
                task_id=self._current_task["task_id"],
                difficulty=self._current_task["difficulty"],
                code_snippet=self._current_task["code_snippet"],
                task_description=self._current_task["description"],
                num_hidden_issues=len(self._current_task["ground_truth_issues"]),
                feedback="Episode already finished.",
                issues_found=0,
                issues_total=len(self._current_task["ground_truth_issues"]),
                false_positives=0,
                message="Episode already complete. Call reset() to start a new one.",
            )
        
        # Grade the submission
        reward, feedback, tp, fp = grade_review(
            submitted_issues=action.issues,
            ground_truth_issues=self._current_task["ground_truth_issues"],
            difficulty=self._current_task["difficulty"],
        )
        
        self._done = True
        
        return CodeReviewObservation(
            done=True,
            reward=reward,
            task_id=self._current_task["task_id"],
            difficulty=self._current_task["difficulty"],
            code_snippet=self._current_task["code_snippet"],
            task_description=self._current_task["description"],
            num_hidden_issues=len(self._current_task["ground_truth_issues"]),
            feedback=feedback,
            issues_found=tp,
            issues_total=len(self._current_task["ground_truth_issues"]),
            false_positives=fp,
            message=feedback,
        )
    
    @property
    def state(self) -> CodeReviewState:
        return self._state
