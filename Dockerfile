FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y && apt upgrade -y && \
    apt install -y libboost-all-dev && \
    apt upgrade -y libboost-all-dev && \
    apt-get install -y libfmt-dev && \
    apt-get install build-essential g++ python3-dev autotools-dev libicu-dev libbz2-dev libboost-all-dev curl -y

RUN apt install -yqq iputils-ping telnet wget vim git

RUN apt install -yqq gcc g++ libsasl2-modules-gssapi-mit sasl2-bin libsasl2-2 libsasl2-dev libsasl2-modules jq

#Conda
RUN wget --no-verbose https://repo.anaconda.com/miniconda/Miniconda3-py39_23.3.1-0-Linux-x86_64.sh -O miniconda.sh && \
    /bin/bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh
ENV PATH=/opt/conda/bin:/opt/conda/condabin:/opt/conda/bin:$PATH
RUN conda init

WORKDIR /workspace
COPY ./ ./
RUN pip install --upgrade -r requirements.txt

## bitsandbytes
#RUN git clone https://github.com/TimDettmers/bitsandbytes.git && \
#    cd bitsandbytes && \
#    git checkout 0.40.0 && \
#    CUDA_VERSION=118 make cuda11x && \
#    pip install .

ENV RAY_memory_monitor_refresh_ms=0
ENV CUDA_VISIBLE_DEVICES=0,1
ENV PYTHONPATH=.
ENV MQ_SERVER=rabbitmq-backoffice.databases.svc.cluster.local
ENV MQ_USER=default_user_I4azCn5HqKRKPfrQdF-
ENV MQ_PASSWORD=iaD9VVSE_H1y7CZuRd2DE7f8IRU-BXqb

ENV LLM_TYPE=din
#ENV ENABLE_MQ=true


#ENV CMAKE_ARGS="-DLLAMA_CUBLAS=on"
#ENV FORCE_CMAKE=1
#RUN pip install --upgrade --force-reinstall llama-cpp-python==0.1.78 --no-cache-dir

WORKDIR /workspace
CMD ./start.sh
