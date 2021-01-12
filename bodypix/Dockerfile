# Base image with TensorFlow GPU requirements
FROM nvcr.io/nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04

RUN apt update \
	&& apt install -y curl make build-essential \
	&& curl -sL https://deb.nodesource.com/setup_12.x | bash - \
	&& apt-get -y install nodejs \
	&& mkdir /.npm \
	&& chmod 777 /.npm

ENV TF_FORCE_GPU_ALLOW_GROWTH=true

WORKDIR /src
COPY package.json ./
RUN npm install

COPY app.js ./

ENTRYPOINT node ./app.js
