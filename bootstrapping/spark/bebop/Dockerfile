#v1.4
FROM docker.stackable.tech/demos/pyspark-k8s-with-kafka-and-iceberg:3.3.0-stackable23.4

USER root

# Install Conda
RUN curl -o miniconda.sh -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    chmod +x miniconda.sh && \
    ./miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh


# Set the environment variable for Conda
ENV PATH="/opt/conda/bin:${PATH}"

# Install additional dependencies using Conda
RUN conda install -c conda-forge textblob

# Download TextBlob corpora
RUN python -m textblob.download_corpora

# Create Conda environment and pack it
RUN conda create -y -n pyspark_conda_env -c conda-forge pyarrow pandas conda-pack textblob
RUN conda run -n pyspark_conda_env /opt/conda/bin/conda pack -f -o /opt/pyspark_conda_env.tar.gz

ENV PATH /opt/conda/envs/pyspark_conda_env/bin:$PATH
RUN /bin/bash -c "source activate pyspark_conda_env"

RUN chmod 644 /opt/pyspark_conda_env.tar.gz

USER 1001

ENV PYSPARK_DRIVER_PYTHON=/opt/conda/bin/python
ENV PYSPARK_PYTHON=/opt/conda/bin/python
ENV PYTHONPATH=/opt/conda/bin/python

# Downloda cor
RUN python -m textblob.download_corpora
ENV PATH /opt/conda/envs/pyspark_conda_env/bin:$PATH
RUN /bin/bash -c "source activate pyspark_conda_env"
