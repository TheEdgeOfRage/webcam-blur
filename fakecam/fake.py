import os

import cv2  # type: ignore
import numpy as np  # type: ignore
import pyfakewebcam  # type: ignore
import requests
from loguru import logger
from requests.exceptions import ConnectionError


height, width = 720, 1280
rem_mask = None
rem = 0
SCALE_FACTOR = 0.5
mask_persist_frame_count = int(os.getenv('MASK_PERSIST_FRAME_COUNT', 1))


def get_mask(frame, bodypix_url='http://bodypix:9000'):
    frame = cv2.resize(frame, (0, 0), fx=SCALE_FACTOR, fy=SCALE_FACTOR)
    _, data = cv2.imencode('.png', frame)
    r = requests.post(
        url=bodypix_url,
        data=data.tobytes(),
        headers={'Content-Type': 'application/octet-stream'}
    )

    mask = np.frombuffer(r.content, dtype=np.uint8)
    mask = mask.reshape((frame.shape[0], frame.shape[1]))
    mask = cv2.resize(mask, (0, 0), fx=1 / SCALE_FACTOR, fy=1 / SCALE_FACTOR,
                      interpolation=cv2.INTER_NEAREST)
    mask = cv2.dilate(mask, np.ones((10, 10), np.uint8), iterations=1)
    mask = cv2.blur(mask.astype(float), (30, 30))

    return mask


def get_frame(cap):
    global rem_mask
    global rem
    _, frame = cap.read()
    mask = None
    if rem_mask is None:
        rem = 0
        while mask is None:
            #  mask = get_mask(frame)
            #  rem_mask = mask
            try:
                mask = get_mask(frame)
                rem_mask = mask
            except ConnectionError:
                continue
    else:
        mask = rem_mask
        rem += 1
        if rem > mask_persist_frame_count:
            rem_mask = None

    #  background = cv2.imread('background.jpg')
    #  background = cv2.resize(background, (width, height))
    background = cv2.blur(frame.astype(float), (30, 30))

    # composite the background
    for c in range(frame.shape[2]):
        frame[:, :, c] = (
            frame[:, :, c] * mask
            + background[:, :, c] * (1 - mask)
        )

    return frame


def main():
    global height
    global width
    cap = cv2.VideoCapture('/dev/video0')
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # In case the real webcam does not support the requested mode.
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    # The scale factor for image sent to bodypix

    # setup the fake camera
    output_cam = pyfakewebcam.FakeWebcam('/dev/video10', width, height)

    logger.info('Starting fakecam service')
    while True:
        frame = get_frame(cap)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        output_cam.schedule_frame(frame)


if __name__ == '__main__':
    main()
