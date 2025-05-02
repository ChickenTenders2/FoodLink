FROM continuumio/miniconda3

# Install system dependency for pyzbar
RUN apt-get update && apt-get install -y libzbar0 && rm -rf /var/lib/apt/lists/*

# Create and activate Conda environment
RUN conda create -n foodlink python=3.9 -y

WORKDIR /app
COPY . .

# Install Python packages: Conda first, then pip
RUN /bin/bash -c "source activate foodlink && \
    conda install -y flask gunicorn opencv numpy scipy && \
    pip install --no-cache-dir pyzbar mariadb && \
    pip install --no-cache-dir -r requirements.txt"

# Set env vars
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PATH=/opt/conda/envs/foodlink/bin:$PATH

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
