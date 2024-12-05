FROM python:3.11.11-alpine@sha256:fbcb089a803d5673f225dc923b8e29ecc7945e9335465037b6961107b9da3d61

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
