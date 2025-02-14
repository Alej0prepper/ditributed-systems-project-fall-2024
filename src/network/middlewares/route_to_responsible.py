import os
import requests
from functools import wraps
from flask import request, session, jsonify
from chord.node import get_hash  
import chord.protocol_logic as chord

def route_to_responsible(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Determine the key to hash.
        username = session.get("username")
        if username:
            key = get_hash(username)
            print("hashed_username: "+str(key))
        else:
            # Fallback: use the client's IP address.
            # If behind a proxy, check for X-Forwarded-For.
            client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            key = get_hash(client_ip)
            print("hashed_ip: "+str(key))
        
        # Find the responsible node for this key using your Chord ring.
        responsible_node = chord.find_successor(key)
        print(f"Responsible_node: {responsible_node}")
        
        # Get self-identity from environment variables.
        self_ip = os.getenv("NODE_IP", "127.0.0.1")
        self_port = int(os.getenv("FLASK_RUN_PORT", "5000"))
        
        # Check if the responsible node is this node.
        if responsible_node["ip"] == self_ip and responsible_node["port"] == self_port:
            # This node is responsible, so process the request normally.
            return func(*args, **kwargs)
        else:
            # Not responsible: forward the request to the correct node.
            target_url = f"http://{responsible_node['ip']}:{responsible_node['port']}{request.full_path}"
            try:
                method = request.method.lower()
                # Prepare headers (excluding Host header to avoid conflicts).
                headers = {k: v for k, v in request.headers if k.lower() != "host"}
                
                # Forward the request using the same HTTP method.
                forwarded = getattr(requests, method)(
                    target_url,
                    headers=headers,
                    params=request.args,
                    json=request.get_json(silent=True),
                    data=request.get_data() if not request.is_json else None,
                )
                
                # Build a response using the forwarded response.
                return (
                    forwarded.content,
                    forwarded.status_code,
                    dict(forwarded.headers)
                )
            except Exception as e:
                return jsonify({"error": "Error forwarding request", "details": str(e)}), 500

    return wrapper
