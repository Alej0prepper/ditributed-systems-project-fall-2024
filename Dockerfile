FROM python:3.10-slim

WORKDIR /mma-social-network

COPY /default_route.sh ./default_route.sh
COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
iproute2 \
&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["/bin/bash", "-c", "/mma-social-network/default_route.sh && python3 /mma-social-network/src/app.py"]