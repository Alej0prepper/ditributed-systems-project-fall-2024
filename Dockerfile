FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /mma-social-network

COPY . /mma-social-network

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x startup.sh

EXPOSE 5000

WORKDIR /mma-social-network/src

CMD ["python3", "app.py"]