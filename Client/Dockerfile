FROM python:3.11-alpine

WORKDIR /client

RUN apk update && apk add --no-cache iproute2
RUN pip install requests
RUN pip install python-dotenv

COPY . .

EXPOSE 3000

ENTRYPOINT ["/bin/sh", "-c", "/client/default_route.sh && python3 I_clients.py"]
