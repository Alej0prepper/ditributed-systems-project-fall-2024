FROM python:3.10-alpine

WORKDIR /mma-social-network

RUN apk update && apk add --no-cache iproute2 build-base

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["sh", "-c", "/mma-social-network/change_default_route.sh && python3 /mma-social-network/src/app.py"]
