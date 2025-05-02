FROM continuumio/miniconda3

# Install native libs for mariadb and pyzbar
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    libzbar0 \
    && ln -s /usr/lib/x86_64-linux-gnu/libzbar.so.0 /usr/lib/libzbar.so.0 \
    && rm -rf /var/lib/apt/lists/*

# Create and activate Conda environment
RUN conda create -n foodlink python=3.9 -y

WORKDIR /app
COPY . .

# Install packages
RUN /bin/bash -c "source activate foodlink && \
    conda install -y flask gunicorn opencv numpy scipy && \
    pip install --no-cache-dir mariadb pyzbar && \
    pip install --no-cache-dir -r requirements.txt"

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PATH=/opt/conda/envs/foodlink/bin:$PATH
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
