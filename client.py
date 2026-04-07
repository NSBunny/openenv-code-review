from openenv.core.env_client import EnvClient
from openenv.core.client_types import StepResult
from code_review_env.models import CodeReviewAction, CodeReviewObservation, CodeReviewState


class CodeReviewEnv(EnvClient[CodeReviewAction, CodeReviewObservation, CodeReviewState]):
    """Client for the CodeReview environment."""
    
    def _step_payload(self, action: CodeReviewAction) -> dict:
        return {
            "issues": [dict(i) for i in action.issues],
            "summary": action.summary,
        }
    
    def _parse_result(self, payload: dict) -> StepResult:
        obs_data = payload.get("observation", {})
        return StepResult(
            observation=CodeReviewObservation(
                done=payload.get("done", False),
                reward=payload.get("reward"),
                task_id=obs_data.get("task_id", ""),
                difficulty=obs_data.get("difficulty", ""),
                code_snippet=obs_data.get("code_snippet", ""),
                task_description=obs_data.get("task_description", ""),
                num_hidden_issues=obs_data.get("num_hidden_issues", 0),
                feedback=obs_data.get("feedback", ""),
                issues_found=obs_data.get("issues_found", 0),
                issues_total=obs_data.get("issues_total", 0),
                false_positives=obs_data.get("false_positives", 0),
                message=obs_data.get("message", ""),
            ),
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )
    
    def _parse_state(self, payload: dict) -> CodeReviewState:
        return CodeReviewState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            task_id=payload.get("task_id", ""),
            difficulty=payload.get("difficulty", ""),
            max_steps=payload.get("max_steps", 1),
            total_issues=payload.get("total_issues", 0),
        )
