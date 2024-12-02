# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi


# Check and create the clients network if it doesn't exist
if ! sudo docker network ls --filter "name=$CLIENTS_NETWORK_NAME" | grep -qx "$CLIENTS_NETWORK_NAME"; then
    echo "Network $CLIENTS_NETWORK_NAME does not exist. Creating..."
    sudo docker network create $CLIENTS_NETWORK_NAME --subnet $CLIENTS_NETWORK_SUBNET
else
    echo "Network $CLIENTS_NETWORK_NAME already exists. Continuing..."
fi

# Check and create the servers network if it doesn't exist
if ! sudo docker network ls | grep -qx "$SERVERS_NETWORK_NAME"; then
    echo "Network $SERVERS_NETWORK_NAME does not exist. Creating..."
    sudo docker network create $SERVERS_NETWORK_NAME --subnet $SERVERS_NETWORK_SUBNET 
else
    echo "Network $SERVERS_NETWORK_NAME already exists. Continuing..."
fi


# Remove the existing router container if it exists
if sudo docker ps -a --filter "name=router" | grep -qx "router"; then
    echo "Router container exists. Removing..."
    sudo docker rm -f router
fi
set -e  # Exit on error

# Check if the image exists, if not build it
if ! sudo docker images --format "{{.Repository}}" | grep -qx "$APP_IMAGE"; then
    echo "Docker image $APP_IMAGE not found. Building the image..."
    sudo docker build -t $APP_IMAGE .
else
    echo "Docker image $APP_IMAGE already exists. Skipping build..."
fi

# Check if the router container exists
if sudo docker ps -a --filter "name=$APP_IMAGE" | grep -q "$APP_IMAGE"; then
    echo "Container $APP_IMAGE already exists. Stopping and removing it..."
    sudo docker rm -f $APP_IMAGE
else
    echo "No existing container found with name $APP_IMAGE."
fi

# Run the router container in detached mode
echo "Starting the router container..."
sudo docker run -d --name $APP_IMAGE $APP_IMAGE


# Connect the router container to the clients and servers networks
echo "Connecting the router to the networks..."
sudo docker network connect --ip $ROUTER_IP_IN_CLIENTS_NETWORK $CLIENTS_NETWORK_NAME router
sudo docker network connect --ip $ROUTER_IP_IN_SERVERS_NETWORK $SERVERS_NETWORK_NAME router

echo "Router is ready! ✅"