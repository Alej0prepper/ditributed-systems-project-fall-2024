# Load the .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

set -e  # Exit on error

# Check if the image exists, if not build it
if ! sudo docker images --format "{{.Repository}}" | grep -qx "$APP_IMAGE"; then
    echo "Docker image $APP_IMAGE not found. Building the image..."
    sudo docker build -t $APP_IMAGE .
else
    echo "Docker image $APP_IMAGE already exists. Skipping build..."
fi

# Remove the application container if it exists
if sudo docker ps -a --filter "name=$APP_CONTAINER" | grep -q "$APP_CONTAINER"; then
    echo "Application container exists. Removing..."
    sudo docker rm $APP_CONTAINER -f
fi

# Create and start the application container
echo "Creating and starting the application container..."
eval sudo docker run -it \
    --name "$APP_CONTAINER" \
    --cap-add NET_ADMIN \
    --network "$NETWORK_NAME" \
    --env-file "$ENV_FILE" \
    "$APP_IMAGE"

echo "Client is ready! ✅"
