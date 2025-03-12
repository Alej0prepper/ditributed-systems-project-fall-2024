
# Load the .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi
set -e  # Exit on error

# Check if the network exists, if not create it
if ! sudo docker network ls | grep -q "$NETWORK_NAME"; then
    echo "Network $NETWORK_NAME does not exist. Creating..."
    docker network create \
    --subnet $NETWORK_SUBNET \
    $NETWORK_NAME
else
    echo "Network $NETWORK_NAME already exists. Continuing..."
fi

# Build the app image if it doesn't exist
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


# Check if the Neo4j container exists but is stopped
sudo docker rm -f $NEO4J_CONTAINER
sudo docker network connect $NETWORK_NAME $NEO4J_CONTAINER || echo "Neo4j container already connected to $NETWORK_NAME"
    # Create and start the Neo4j container
    echo "Creating and starting Neo4j container"
    sudo docker run -d \
        --name $NEO4J_CONTAINER \
        --restart always \
        --network $NETWORK_NAME \
        -e NEO4J_AUTH=$NEO4J_AUTH \
        -p 7474:7474 \
        -p 7687:7687 \
        $NEO4J_IMAGE
    echo "Neo4j is ready! ✅"


# Create and start the application container
docker rm -f $APP_CONTAINER
echo "Creating and starting the application container..."
eval sudo docker run -it \
    --restart always \
    --name "$APP_CONTAINER" \
    --cap-add NET_ADMIN \
    --network "$NETWORK_NAME" \
    --env-file "$ENV_FILE" \
    -p 5000:5000 \
    -v "$APP_VOLUME" \
    "$APP_IMAGE"

echo "Server is ready! ✅"