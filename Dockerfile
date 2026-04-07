FROM python:3.11-slim

WORKDIR /app

# Copy everything
COPY . .

# Install dependencies
RUN pip install --no-cache-dir openenv-core fastapi "uvicorn[standard]" "pydantic>=2.0" openai pyyaml

# HF Spaces requires port 7860
EXPOSE 7860

ENV PYTHONPATH="/app"

CMD ["uvicorn", "code_review_env.server.app:app", "--host", "0.0.0.0", "--port", "7860"]
