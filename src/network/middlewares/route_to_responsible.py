from functools import wraps
import chord.protocol_logic as chord
import os
import requests
from flask import request, jsonify
from network.middlewares.token import validate_token
import chord.node as chord_node 
import inspect
import chord.protocol_logic as chord_logic
from chord.node import get_hash


def getAllUsers():
    users = []
    for entity in chord.system_entities_set:
        if entity[0] == "User":
            responsible_node = chord.find_successor(get_hash(entity[2]))
            endpoint = f"http://{responsible_node['ip']}:{responsible_node['port']}/users/{entity[2]}"
            response = requests.get(endpoint)
            user = response.json()["user"]
            users.append(user)
    return users

def getAllGyms():
    gyms = []
    for entity in chord.system_entities_set:
        if entity[0] == "Gym":
            responsible_node = chord.find_successor(get_hash(entity[2]))
            endpoint = f"http://{responsible_node['ip']}:{responsible_node['port']}/gyms/{entity[2]}"
            response = requests.get(endpoint)
            gym = response.json()["gym"]
            gyms.append(gym)
    return gyms

def getAllPosts():
    posts = []
    for entity in chord.system_entities_set:
        if entity[0] == "Post":
            responsible_node = chord.find_successor(get_hash(entity[2]))
            endpoint = f"http://{responsible_node['ip']}:{responsible_node['port']}/posts/{entity[2]}"
            try:
                response = requests.get(endpoint)
                post = response.json()["post"]
                if post:
                    posts.append(post)
            except Exception as e:
                print('getAllPosts exception:',str(e))
    return posts

def getAllQuotes():
    quotes = []
    for entity in chord.system_entities_set:
        if entity[0] == "Post":
            responsible_node = chord.find_successor(get_hash(entity[2]))
            endpoint = f"http://{responsible_node['ip']}:{responsible_node['port']}/quotes/{entity[2]}"
            try:
                response = requests.get(endpoint)
                quote = response.json()["quote"]
                quoted = response.json()["quoted"]
                if quote != dict() and quoted != dict():
                    quotes.append((quote, quoted))
            except Exception as e:
              print('getAllQuotes exception:', str(e))
    return quotes

def getAllReposts():
    reposts = []
    for entity in chord.system_entities_set:
        if entity[0] == "Post":
            responsible_node = chord.find_successor(get_hash(entity[2]))
            endpoint = f"http://{responsible_node['ip']}:{responsible_node['port']}/reposts/{entity[2]}"
            try:
                response = requests.get(endpoint)
                repost = response.json()["repost"]
                if repost != dict():
                    reposts.append(repost)
            except Exception as e:
                print('getAllQuotes exception:', str(e))
    return reposts
    
def getAllUserPosts(userId):
    user_posts = []
    all_posts = getAllPosts()
    for post in all_posts:
        if post['publisherId'] == userId:
            user_posts.append(post)
    return user_posts

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
                    or request.form.get("id")
                    or request.form.get("userId")
                )

            # If still None, try to get from function defaults
            if local_routing_key is None:
                signature = inspect.signature(func)
                bound_args = signature.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                local_routing_key = bound_args.arguments.get("id")


            elif local_routing_key == "getAllUsers":
                users = getAllUsers()
                return func(users)
            elif local_routing_key == "getAllQuotes":
                quotes = getAllQuotes()
                return func(quotes)
            elif local_routing_key == "getAllReposts":
                reposts = getAllReposts()
                return func(reposts)
            elif local_routing_key == "getAllGyms":
                gyms = getAllGyms()
                return func(gyms)
            elif local_routing_key == "getAllPosts":
                posts = getAllPosts()
                return func(posts)
            elif local_routing_key == "getAllUserPosts":
                posts = getAllUserPosts(request.view_args.get("id"))
                return func(posts)
            elif local_routing_key == "me":
                auth_header = request.headers.get("Authorization")

                if auth_header == "null":
                    return jsonify({"error": "No token was provided"}), 401
                
                payload = validate_token(auth_header)
                local_routing_key = payload.get("id")
            elif local_routing_key == "login":
                email = request.form.get("email")

                filtered_entities = [entity for entity in chord_logic.system_entities_set if entity[1] == email]
                
                # Get the first coincidence by email in entities' emails
                if(len(filtered_entities) > 0):
                    local_routing_key = filtered_entities[0][1]
                else: 
                    local_routing_key = None

            if local_routing_key is None:
                return jsonify({"error": "Invalid routing key"}), 400


            key = chord_node.get_hash(local_routing_key)

            # Determine the responsible node in the Chord ring
            responsible_node = chord.find_successor(key)

            # Retrieve self-identity
            self_id = chord_node.current_node.to_dict()["id"]

            if responsible_node["id"] == self_id or local_routing_key is None:
                return func(*args, **kwargs)
            else:
                # Forward the request to the responsible node
                target_url = f"http://{responsible_node['ip']}:{responsible_node['port']}{request.full_path}"
                try:
                    method = request.method.lower()
                    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

                    if request.is_json:
                        # Handle JSON data
                        json_data = request.get_json(silent=True)
                        response = getattr(requests, method)(
                            target_url,
                            headers=headers,
                            json=json_data
                        )
                    else:
                        # Handle form data
                        form_data = request.form  # Keep as ImmutableMultiDict to preserve multi-values
                        form_data = form_data.to_dict()  # Convert to dict if modification is needed
                        form_data["id"] = local_routing_key  # Add your parameter

                        # Ensure the correct Content-Type for form data
                        headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
                        headers["Content-Type"] = "application/x-www-form-urlencoded"  # Set explicitly

                        print(f"Forwarding {method} request to: {target_url}")
                        print(f"Modified Data: {form_data}")

                        # Forward the request with form data
                        response = getattr(requests, method)(
                            target_url,
                            headers=headers,
                            data=form_data  # Use `data` for form-urlencoded
                        )

                    return response.content, response.status_code, dict(response.headers)

                except requests.exceptions.RequestException as e:
                    return jsonify({
                        "error": "Failed to forward request to responsible node",
                        "details": str(e)
                    }), 502
                except Exception as e:
                    return jsonify({
                        "error": "Internal server error during request forwarding",
                        "details": str(e)
                    }), 500

        return wrapper
    return decorator