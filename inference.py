#!/usr/bin/env python3
"""
inference.py — Baseline inference script for CodeReview environment.

Uses an LLM to review code snippets and identify issues.
Follows the mandatory [START], [STEP], [END] log format.
"""
import os
import sys

# Add the parent directory to sys.path so 'code_review_env' is resolvable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import uuid
import warnings
from openai import OpenAI
from code_review_env.client import CodeReviewEnv, CodeReviewAction

warnings.filterwarnings("ignore")

# ----- Environment variables (MANDATORY) -----
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama-3.3-70b-versatile")

# ----- Environment URL -----
ENV_URL = os.environ.get("ENV_URL", "http://localhost:8000")

# Initialize OpenAI client — API key MUST be set via environment variable
API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not API_KEY:
    print("WARNING: OPENAI_API_KEY not set. LLM calls will fail.", file=sys.stderr)

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)


def call_llm(code_snippet: str, task_description: str, num_issues: int, difficulty: str) -> dict:
    """Use LLM to review code and return structured issues."""
    prompt = f"""You are an elite Python Code Review Expert performing a thorough review.
Review the following code and identify exactly {num_issues} issue(s).

Task Description: {task_description}
Difficulty: {difficulty}

Code:
```python
{code_snippet}
```

MANDATORY REVIEW CHECKLIST — go through each one carefully:

1. DIVISION BY ZERO: Can any division operation receive zero? Check len() calls used as divisors with potentially empty collections.
2. RESOURCE MANAGEMENT: Are file handles properly closed? Is 'with' statement used? If not, category="style", mention "file handle" and "close" and "with statement" in description.
3. ERROR HANDLING: Is there missing error handling? e.g., FileNotFoundError for file operations. If missing, category="logic", mention the specific error type.
4. OFF-BY-ONE / INDEX ERRORS: Are array bounds correct? e.g., len(arr) vs len(arr)-1. If wrong, category="logic", mention "IndexError" or the specific boundary issue.
5. INTEGER OVERFLOW: Can (left + right) cause overflow? Safer: left + (right - left) // 2. If applicable, category="logic", mention "overflow" or "integer overflow".
6. TYPE HINTS / STYLE: Are type hints missing? If so, category="style", mention "type hints".
7. KWARGS HANDLING: Does a wrapper/decorator handle **kwargs? If it only handles *args, category="logic", mention "kwargs" or "keyword arg".
8. MEMORY LEAKS: Do caches/dicts/lists grow unboundedly without eviction? category="logic", mention "unbounded" or "memory leak" or "eviction".
9. UNHASHABLE TYPES: Can unhashable types (list, dict) be used as dict keys or in sets? category="logic", mention "unhashable" and "TypeError".
10. WEAK CRYPTOGRAPHY: Is MD5 or SHA1 used for passwords? category="security", mention "MD5" and suggest "bcrypt" or "argon2".
11. TIMING ATTACKS: Are hashes compared with == instead of hmac.compare_digest()? category="security", mention "timing attack" and "hmac.compare_digest".
12. AUTHORIZATION: Are there missing permission/authorization checks? category="security", mention "authorization" and what is missing.
13. THREAD SAFETY: Is shared mutable state accessed without locks? category="security", mention "thread-safe" or "concurrent" or "race".
14. PERFORMANCE: Is there O(n) work that could be O(1) with a better data structure like deque? category="logic", mention the inefficiency.
15. STALE DATA: Can a function return stale/outdated data because it doesn't refresh first? category="logic", mention "stale".
16. HARDCODED SECRETS: Are passwords or credentials hardcoded in test/example code? category="security", mention "hardcoded" and the specific value.
17. PERSISTENCE: Is important data stored only in memory with no persistence? category="logic", mention "memory only" or "persistence".

CRITICAL CATEGORY RULES:
- File handle not closed / missing 'with' statement → category = "style"
- Missing error handling, wrong bounds, division by zero, memory leaks, missing kwargs, unhashable types, overflow, stale data, persistence → category = "logic"
- Weak crypto, timing attacks, missing auth, thread safety, hardcoded secrets → category = "security"

For each issue provide:
- line: the line number as a string
- severity: "low", "medium", or "high"  
- category: MUST be one of "syntax", "logic", "style", "security" following the rules above
- description: detailed explanation including the specific keywords from the checklist above

Respond ONLY with valid JSON in this exact format:
{{
  "issues": [
    {{"line": "1", "severity": "high", "category": "logic", "description": "..."}}
  ],
  "summary": "..."
}}"""

    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a top-tier Code Review and Information Security Engineer. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content.strip()
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                content = match.group(0)
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                import yaml
                return yaml.safe_load(content)
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "rate limit" in err_msg or "quota" in err_msg:
                print(f"Rate limited by API. Waiting 60 seconds before retry {attempt+1}... ({e})", file=sys.stderr)
                time.sleep(60)
                continue
            print(f"LLM Error: {e}", file=sys.stderr)
            return {"issues": [], "summary": f"Error: {str(e)}"}
    return {"issues": [], "summary": "Failed after multiple rate limit retries."}


def run_inference():
    """Run the baseline inference across all tasks."""
    session_id = str(uuid.uuid4())
    tasks = ["easy_001", "easy_002", "medium_001", "medium_002", "hard_001", "hard_002"]
    
    total_reward = 0.0
    results = []
    
    # [START] log
    print(f"[START] session_id={session_id} tasks={len(tasks)} model={MODEL_NAME}")
    
    env_client = CodeReviewEnv(base_url=ENV_URL).sync()
    with env_client:
        for i, task_id in enumerate(tasks):
            step_start = time.time()
            time.sleep(4)
            
            try:
                res = env_client.reset(options={"task_id": task_id})
                obs = res.observation
            except Exception as e:
                print(f"Failed to reset environment: {e}")
                continue
                
            # Call LLM for review
            print(f"  > Requesting LLM for {task_id}...", file=sys.stderr)
            llm_result = call_llm(obs.code_snippet, obs.task_description, obs.num_hidden_issues, obs.difficulty)
            
            try:
                step_res = env_client.step(CodeReviewAction(
                    issues=llm_result.get("issues", []),
                    summary=llm_result.get("summary", "")
                ))
                obs = step_res.observation
            except Exception as e:
                print(f"Failed to step environment: {e}")
                continue
            
            reward = step_res.reward
            feedback = obs.feedback
            step_time = time.time() - step_start
            
            if reward is None:
                reward = 0.0
                
            total_reward += float(reward)
            
            # [STEP] log
            print(f"[STEP] task_id={task_id} difficulty={obs.difficulty} reward={reward:.4f} "
                  f"time={step_time:.2f}s feedback=\"{feedback}\"")
            
            results.append({
                "task_id": task_id,
                "difficulty": obs.difficulty,
                "reward": reward,
                "time": step_time,
            })
    
    avg_reward = total_reward / len(tasks) if tasks else 0.0
    
    # [END] log
    print(f"[END] session_id={session_id} total_reward={total_reward:.4f} "
          f"avg_reward={avg_reward:.4f} tasks_completed={len(results)}")
    
    return results


if __name__ == "__main__":
    run_inference()
