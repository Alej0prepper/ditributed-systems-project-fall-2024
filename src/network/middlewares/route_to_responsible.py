from functools import wraps
import chord.protocol_logic as chord
import os
import requests
from flask import request, jsonify
from network.middlewares.token import validate_token
from chord.node import get_hash
import inspect
import chord.protocol_logic as chord_logic


def getAllUsers():
    pass

def getAllGyms():
    pass

def route_to_responsible(routing_key=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Determine the routing key
            local_routing_key = routing_key  # Default to the decorator argument

            # If the function is called with a parameter that overrides the routing key, use it
            if local_routing_key is None:
                local_routing_key = (
                    request.view_args.get("id")  # Route parameters
                    or request.args.get("id")    # Query parameters
                    or request.form.get("id")    # Form data
                )

            # If still None, try to get from function defaults
            if local_routing_key is None:
                signature = inspect.signature(func)
                bound_args = signature.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                local_routing_key = bound_args.arguments.get("id")


            if local_routing_key == "getAllUsers":
                return getAllUsers()
            elif local_routing_key == "getAllGyms":
                return getAllGyms()
            elif local_routing_key == "me":
                auth_header = request.headers.get("Authorization")

                if auth_header == "null":
                    return jsonify({"error": "No token was provided"}), 401
                
                payload = validate_token(auth_header)
                local_routing_key = payload.get("id")
            elif local_routing_key == "login":
                email = request.form.get("email")

                filtered_entities = [entity for entity in chord_logic.system_entities_list if entity[0] == email]
                
                # Get the first coincidence by email in entities' emails
                local_routing_key = filtered_entities[0][1]

            if local_routing_key is None:
                return jsonify({"error": "Invalid routing key"}), 400

            print("Routing key:", local_routing_key)
            key = get_hash(local_routing_key)
            print("Computed hash:", key)

            # Determine the responsible node in the Chord ring
            responsible_node = chord.find_successor(key)
            print("Responsible node:", responsible_node)

            # Retrieve self-identity
            self_ip = os.getenv("NODE_IP", "127.0.0.1")
            self_port = int(os.getenv("FLASK_RUN_PORT", "5000"))

            if responsible_node["ip"] == self_ip and responsible_node["port"] == self_port:
                # This node is responsible, call the original function with the extracted arguments
                return func(*args, **kwargs)
            else:
                # Forward the request to the responsible node
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