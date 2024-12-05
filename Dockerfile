FROM python:3.12.8-alpine@sha256:bb94273467caf397de28b4e6dd09ca4a2dd1b53fa9b130d5b2c7c82719258356

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
