FROM python:3.11-bullseye

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir /app/src
COPY src/ /app/src

CMD ["python", "src/run_automation.py"]