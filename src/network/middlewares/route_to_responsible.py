import os
import requests
from functools import wraps
from flask import request, session, jsonify
from chord.node import get_hash  
import chord.protocol_logic as chord

def route_to_responsible():
   
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            #Passing a routing key as a kwarg.
            key_value = kwargs.pop('routing_key', None)

            print("Routing key:", key_value)
            key = get_hash(key_value)
            print("Computed hash:", key)
            
            # Determine the responsible node in the Chord ring.
            responsible_node = chord.find_successor(key)
            print("Responsible node:", responsible_node)
            
            # Retrieve self-identity.
            self_ip = os.getenv("NODE_IP", "127.0.0.1")
            self_port = int(os.getenv("FLASK_RUN_PORT", "5000"))
            
            if responsible_node["ip"] == self_ip and responsible_node["port"] == self_port:
                # This node is responsible.
                return func(*args, **kwargs)
            else:
                # Forward the request to the responsible node.
                target_url = f"http://{responsible_node['ip']}:{responsible_node['port']}{request.full_path}"
                try:
                    method = request.method.lower()
                    headers = {k: v for k, v in request.headers if k.lower() != "host"}
                    forwarded = getattr(requests, method)(
                        target_url,
                        headers=headers,
                        params=request.args,
                        json=request.get_json(silent=True),
                        data=request.get_data() if not request.is_json else None,
                    )
                    return forwarded.content, forwarded.status_code, dict(forwarded.headers)
                except Exception as e:
                    return jsonify({"error": "Error forwarding request", "details": str(e)}), 500
        return wrapper
    return decorator
