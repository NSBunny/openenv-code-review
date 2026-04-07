from openenv.core.env_server import create_fastapi_app
from code_review_env.models import CodeReviewAction, CodeReviewObservation
from code_review_env.server.environment import CodeReviewEnvironment

app = create_fastapi_app(CodeReviewEnvironment, CodeReviewAction, CodeReviewObservation)
