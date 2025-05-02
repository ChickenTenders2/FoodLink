FROM continuumio/miniconda3

# Create and activate Conda environment
RUN conda create -n foodlink python=3.9 -y

# Set working directory
WORKDIR /app

# Copy your app code into the container
COPY . .

# Install packages: Conda for heavy stuff, pip for mariadb
RUN /bin/bash -c "source activate foodlink && \
    conda install -y flask gunicorn opencv pyzbar numpy scipy && \
    pip install --no-cache-dir mariadb && \
    pip install --no-cache-dir -r requirements.txt"

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV PYTHONUNBUFFERED=1

# Make Conda env the default for all CMD/ENTRYPOINTs
ENV PATH=/opt/conda/envs/foodlink/bin:$PATH

# Expose port OpenShift allows
EXPOSE 8080

# Start app with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
