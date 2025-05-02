FROM continuumio/miniconda3

# Create and activate conda env
RUN conda create -n foodlink python=3.9 -y

# Activate env + install all major deps
RUN /bin/bash -c "source activate foodlink && \
    conda install -y flask gunicorn opencv pyzbar mariadb numpy scipy && \
    pip install --no-cache-dir -r /app/requirements.txt"

# Set working dir
WORKDIR /app

# Copy everything into container
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV PYTHONUNBUFFERED=1

# Make conda env the default
ENV PATH=/opt/conda/envs/foodlink/bin:$PATH

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
