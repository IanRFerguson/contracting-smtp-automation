FROM python:3.12-bullseye

WORKDIR /app

# Copy only the dependency files to leverage Docker cache
COPY pyproject.toml .
RUN pip install uv && uv sync

# Copy the rest of the application code
COPY src/ /app/src

CMD ["uv", "run", "src/main.py"]