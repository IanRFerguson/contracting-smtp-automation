FROM python:3.11-bullseye

WORKDIR /app

COPY pyproject.toml .
RUN pip install .

RUN mkdir /app/src
COPY src/ /app/src

CMD ["python", "src/run_automation.py"]