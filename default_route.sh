if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "Setting up default route..."
ip route del default || true  # Ignore errors if no default route exists
ip route add default via $ROUTER_IP
echo "Ready✅"

exec "$@"