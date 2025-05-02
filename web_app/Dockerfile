FROM python:3.9

RUN apt-get update && apt-get install -y \
    gcc g++ make build-essential pkg-config \
    libmariadb-dev default-libmysqlclient-dev mariadb-client \
    libssl-dev libffi-dev libglib2.0-0 libsm6 libxext6 libxrender1 \
    zlib1g-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]