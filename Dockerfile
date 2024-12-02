FROM python:3.10-alpine

WORKDIR /mma-social-network

RUN apk update && apk add --no-cache iproute2 build-base

COPY /default_route.sh ./default_route.sh
COPY . .

RUN chmod +x ./default_route.sh

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["/bin/sh", "-c", "/mma-social-network/default_route.sh && python3 /mma-social-network/src/app.py"]
