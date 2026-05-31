FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgomp1 \
    curl

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -e .

RUN pip install gunicorn

EXPOSE 8080

CMD ["gunicorn","-b","0.0.0.0:8080","application:app"]
