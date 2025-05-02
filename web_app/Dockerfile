FROM python:3.9

# Set working directory
# Install ALL the system packages you need
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    build-essential \
    pkg-config \
    libmariadb-dev \
    default-libmysqlclient-dev \
    mariadb-client \
    libssl-dev \
    libffi-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    libzbar0 \
    zlib1g-dev \
    curl \
    && ln -s /usr/lib/x86_64-linux-gnu/libzbar.so.0 /usr/lib/libzbar.so.0 || true \
    && rm -rf /var/lib/apt/lists/*


# Set working directory
WORKDIR /app

COPY . .

# Install Python deps via pip
RUN pip install --upgrade pip && \
    pip install --no-cache-dir mariadb pyzbar && \
    pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080