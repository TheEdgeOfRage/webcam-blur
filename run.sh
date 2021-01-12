#!/bin/bash

set -e

docker build -t bodypix bodypix
docker build -t fakecam fakecam

docker network rm fakecam >/dev/null 2>&1 || echo ""
docker network create --driver bridge fakecam

docker run -d \
	--name=bodypix \
	--network=fakecam \
	-p 9000:9000 \
	--gpus=all --shm-size=1g --ulimit memlock=-1 --ulimit stack=67108864 \
	bodypix

docker run -d \
	--name=fakecam \
	--network=fakecam \
	-e MASK_PERSIST_FRAME_COUNT=4 \
	-u "$(id -u):$(getent group video | cut -d: -f3)" \
	$(find /dev -name 'video*' -printf "--device %p ") \
	fakecam
