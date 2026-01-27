FROM python:3.12-bullseye

WORKDIR /app

# Copy only the dependency files to leverage Docker cache
COPY pyproject.toml .
COPY uv.lock .
RUN pip install uv==0.9.26 && uv sync --frozen

# Copy the rest of the application code
COPY src/ /app/src

CMD ["uv", "run", "src/main.py"]