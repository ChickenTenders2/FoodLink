FROM python:3.9-buster

# Install system dependencies — all the common ones used in your stack
RUN apt-get update && apt-get install -y \
    gcc g++ make build-essential pkg-config \
    libmariadb-dev default-libmysqlclient-dev mariadb-client \
    libssl-dev libffi-dev \
    libglib2.0-0 libsm6 libxext6 libxrender1 libgl1 \
    libzbar0 \
    zlib1g-dev curl git unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy app code (assumes everything is inside web_app/)
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set env variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose app port
EXPOSE 8080

# Run the app
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
