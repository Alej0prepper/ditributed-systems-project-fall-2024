if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "Setting up default route..."
ip route del default || true 
ip route add default via $ROUTER_IP
echo "Ready✅"

exec "$@"