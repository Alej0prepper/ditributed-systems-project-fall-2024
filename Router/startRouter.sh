if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

if ! sudo docker network ls | grep -q "$SERVERS_NETWORK_NAME"; then
    echo "Network $SERVERS_NETWORK_NAME does not exist. Creating..."
    sudo docker network create $SERVERS_NETWORK_NAME --subnet $SERVERS_NETWORK_SUBNET 
else
    echo "Network $SERVERS_NETWORK_NAME already exists. Continuing..."
fi

if ! sudo docker network ls | grep -q "$CLIENTS_NETWORK_NAME"; then
    echo "Network $CLIENTS_NETWORK_NAME does not exist. Creating..."
    sudo docker network create $CLIENTS_NETWORK_NAME --subnet $CLIENTS_NETWORK_SUBNET 
else
    echo "Network $CLIENTS_NETWORK_NAME already exists. Continuing..."
fi


sudo docker build -t router .
sudo docker run -itd --name router router
sudo docker network connect --ip $ROUTER_IP_IN_CLIENTS_NETWORK $CLIENTS_NETWORK_NAME router
sudo docker network connect --ip $ROUTER_IP_IN_SERVERS_NETWORK $SERVERS_NETWORK_NAME router

echo Router is ready! ✅