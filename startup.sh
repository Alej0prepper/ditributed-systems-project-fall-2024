# BEFORE RUNNING THIS SCRIPT YOU SHOULD LOAD THE mma-social-network DOCKER IMAGE

# Load the .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi
set -e  # Exit on error

# Build the Docker image if it doesn't exist
if ! sudo docker images --format "{{.Repository}}"  "$APP_IMAGE" | grep -qx "$APP_IMAGE"; then
    echo "Image $APP_IMAGE not found. Building the image..."
    sudo docker build -t "$APP_IMAGE" .
else
    echo "Image $APP_IMAGE already exists. Continuing..."
fi

# Build the Neo4j image if it doesn't exist
if ! sudo docker images --format "{{.Repository}}" "$NEO4J_IMAGE" | grep -qx "$NEO4J_IMAGE"; then
    echo "Image $NEO4J_IMAGE not found. Building the image..."
    sudo docker build -t "$NEO4J_IMAGE" .
else
    echo "Image $NEO4J_IMAGE already exists. Continuing..."
fi


# Check if the network exists, if not create it
if ! sudo docker network ls | grep "$NETWORK_NAME"; then
    echo "Network $NETWORK_NAME does not exist. Creating..."
    sudo docker network create $NETWORK_NAME --subnet $NETWORK_SUBNET 
else
    echo "Network $NETWORK_NAME already exists. Continuing..."
fi


# Check if the Neo4j container is already running
if sudo docker ps --filter "name=$NEO4J_CONTAINER" --filter "status=running" | grep -q "$NEO4J_CONTAINER"; then
    echo "Neo4j container is already running. Stopping..."
    sudo docker rm $NEO4J_CONTAINER -f
fi
# Check if the Neo4j container exists but is stopped
if sudo docker ps -a --filter "name=$NEO4J_CONTAINER" | grep -q "$NEO4J_CONTAINER"; then
    echo "Neo4j container exists but is stopped. Starting..."
    sudo docker rm $NEO4J_CONTAINER
    # Ensure it's connected to the network
    sudo docker network connect $NETWORK_NAME $NEO4J_CONTAINER || echo "Neo4j container already connected to $NETWORK_NAME"
else
    # Create and start the Neo4j container
    echo "Neo4j container does not exist. Creating and starting..."
    sudo docker run -d \
        --name $NEO4J_CONTAINER \
        --restart unless-stopped \
        --network $NETWORK_NAME \
        -e NEO4J_AUTH=$NEO4J_AUTH \
        -v $NEO4J_DATA_PATH:/data \
        -v $NEO4J_LOGS_PATH:/logs \
        -v $NEO4J_IMPORT_PATH:/var/lib/neo4j/import \
        -p 7474:7474 \
        -p 7687:7687 \
        $NEO4J_IMAGE
    echo "Neo4j is ready! ✅"
fi


# Check if the application container exists
if sudo docker ps -a --filter "name=$APP_CONTAINER" | grep -q "$APP_CONTAINER"; then
    echo "Application container exists. Removing..."
    sudo docker rm $APP_CONTAINER -f
fi

# Create and start the application container
echo "Creating and starting the application container..."
eval sudo docker run -idt \
    --name "$APP_CONTAINER" \
    --cap-add NET_ADMIN \
    --network "$NETWORK_NAME" \
    -p 5000:5000 \
    --env-file "$ENV_FILE" \
    -v "$APP_VOLUME" \
    "$APP_IMAGE"

echo "Server is ready! ✅"

# Start router
cd Router/
bash startRouter.sh
cd ..


# Start client
cd Client/
bash startClient.sh
cd ..

