from openenv.core.env_server import create_fastapi_app
from fastapi.responses import HTMLResponse
from code_review_env.models import CodeReviewAction, CodeReviewObservation
from code_review_env.server.environment import CodeReviewEnvironment

app = create_fastapi_app(CodeReviewEnvironment, CodeReviewAction, CodeReviewObservation)


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CodeReview AI Environment</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .card { background: rgba(255,255,255,0.08); backdrop-filter: blur(10px); border-radius: 20px; padding: 50px; max-width: 700px; text-align: center; border: 1px solid rgba(255,255,255,0.15); }
            h1 { font-size: 2.5em; margin-bottom: 10px; }
            .emoji { font-size: 3em; margin-bottom: 20px; }
            p { color: #ccc; font-size: 1.1em; line-height: 1.6; }
            .badge { display: inline-block; background: #22c55e; color: #fff; padding: 6px 16px; border-radius: 20px; font-size: 0.9em; margin: 10px 5px; }
            .badge.blue { background: #3b82f6; }
            .badge.purple { background: #8b5cf6; }
            table { width: 100%; margin-top: 20px; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
            th { color: #a78bfa; }
            .score { color: #22c55e; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="emoji">🔍</div>
            <h1>CodeReview AI Environment</h1>
            <p>An OpenEnv RL environment where an AI agent reviews Python code for bugs, security vulnerabilities, and style issues.</p>
            <p>
                <span class="badge">✅ Running</span>
                <span class="badge blue">WebSocket: /ws</span>
                <span class="badge purple">Meta × PyTorch Hackathon 2026</span>
            </p>
            <table>
                <tr><th>Task</th><th>Difficulty</th><th>Reward</th></tr>
                <tr><td>easy_001</td><td>Easy</td><td class="score">0.50 – 1.00</td></tr>
                <tr><td>easy_002</td><td>Easy</td><td class="score">1.00 ✅</td></tr>
                <tr><td>medium_001</td><td>Medium</td><td class="score">1.00 ✅</td></tr>
                <tr><td>medium_002</td><td>Medium</td><td class="score">0.33 – 0.67</td></tr>
                <tr><td>hard_001</td><td>Hard</td><td class="score">0.60 – 0.80</td></tr>
                <tr><td>hard_002</td><td>Hard</td><td class="score">0.25 – 0.50</td></tr>
                <tr><td><strong>Average</strong></td><td></td><td class="score"><strong>0.65 – 0.74</strong></td></tr>
            </table>
        </div>
    </body>
    </html>
    """
