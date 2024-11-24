# BEFORE RUNNING THIS SCRIPT YOU SHOULD LOAD THE mma-social-network IMAGE IN YOUR DOCKER IMAGES

# Load the .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi


# Check if the network exists, if not create it
if ! sudo docker network ls | grep -q "$NETWORK_NAME"; then
    echo "Network $NETWORK_NAME does not exist. Creating..."
    sudo docker network create $NETWORK_NAME
else
    echo "Network $NETWORK_NAME already exists. Continuing..."
fi


# Check if the Neo4j container is already running
if sudo docker ps --filter "name=$NEO4J_CONTAINER" --filter "status=running" | grep -q "$NEO4J_CONTAINER"; then
    echo "Neo4j container is already running. Continuing..."
else
    # Check if the Neo4j container exists but is stopped
    if sudo docker ps -a --filter "name=$NEO4J_CONTAINER" | grep -q "$NEO4J_CONTAINER"; then
        echo "Neo4j container exists but is stopped. Starting..."
        sudo docker start $NEO4J_CONTAINER
        # Ensure it's connected to the network
        sudo docker network connect $NETWORK_NAME $NEO4J_CONTAINER || echo "Neo4j container already connected to $NETWORK_NAME"
    else
        # Create and start the Neo4j container
        echo "Neo4j container does not exist. Creating and starting..."
        sudo docker run -d \
            --name $NEO4J_CONTAINER \
            --network $NETWORK_NAME \
            -p 7474:7474 -p 7687:7687 \
            -e NEO4J_AUTH=$NEO4J_AUTH \
            -v $NEO4J_DATA_PATH:/data \
            -v $NEO4J_LOGS_PATH:/logs \
            -v $NEO4J_IMPORT_PATH:/var/lib/neo4j/import \
            --restart unless-stopped \
            $NEO4J_IMAGE
    fi
fi

# Check if the application container is running
if sudo docker ps --filter "name=$APP_CONTAINER" --filter "status=running" | grep -q "$APP_CONTAINER"; then
    echo "Application container is running. Stopping..."
    sudo docker stop $APP_CONTAINER
fi

# Check if the application container exists
if sudo docker ps -a --filter "name=$APP_CONTAINER" | grep -q "$APP_CONTAINER"; then
    echo "Application container exists. Removing..."
    sudo docker rm $APP_CONTAINER
fi

# Create and start the application container
echo "Creating and starting the application container..."
eval sudo docker run -it \
    --name "$APP_CONTAINER" \
    --network "$NETWORK_NAME" \
    --env-file "$ENV_FILE" \
    --restart unless-stopped \
    -v "$APP_VOLUME" \
    "$APP_IMAGE"