FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the environment package code into the container
# We copy the entire directory so python package imports work
COPY . /app/code_review_env/

ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "code_review_env.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
