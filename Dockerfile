FROM python:3.11-slim

WORKDIR /app

# Copy everything into the package directory
COPY . /app/code_review_env/

# Install dependencies
RUN pip install --no-cache-dir openenv-core fastapi "uvicorn[standard]" "pydantic>=2.0" openai pyyaml

ENV PYTHONPATH="/app"

EXPOSE 7860

CMD ["uvicorn", "code_review_env.server.app:app", "--host", "0.0.0.0", "--port", "7860"]
