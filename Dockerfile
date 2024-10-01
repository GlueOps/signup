FROM python:3.11.9-alpine@sha256:f9ce6fe33d9a5499e35c976df16d24ae80f6ef0a28be5433140236c2ca482686

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
