FROM python:3.11.11-alpine@sha256:9ae1ab261b73eeaf88957c42744b8ec237faa8fa0d5be22a3ed697f52673b58a

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
