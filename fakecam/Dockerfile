FROM python:3-slim

WORKDIR /src

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY background.jpg fake.py ./

ENTRYPOINT python3 -u fake.py
