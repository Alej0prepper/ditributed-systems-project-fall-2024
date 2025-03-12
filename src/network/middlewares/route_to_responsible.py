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
import time


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
        print(f"Entity in all gyms: {entity}")

        if entity[0] == "Gym":
            responsible_node = chord.find_successor(get_hash(entity[2]))
            endpoint = f"http://{responsible_node['ip']}:{responsible_node['port']}/gyms/{entity[2]}"
            response = requests.get(endpoint)
            print(f"Entity in all gyms: {entity}")
            print(f"Endpoint: {endpoint}")
            print(f"Responsible node: {responsible_node['id']}")
            try:
                gym = response.json()["gym"]
            except Exception as e:
              print(f"Received gym: {response.json()}")
              continue
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
                print("Quote:", response.json())
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
                print('getAllReposts exception:', str(e))
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
            local_routing_key = routing_key or (
                request.view_args.get("id") or 
                request.args.get("id") or 
                request.form.get("id") or 
                request.form.get("userId")
            )

            if local_routing_key is None:
                signature = inspect.signature(func)
                bound_args = signature.bind_partial(*args, **kwargs)
                bound_args.apply_defaults()
                local_routing_key = bound_args.arguments.get("id")
            if local_routing_key in ["getAllUsers", "getAllQuotes", "getAllReposts", "getAllGyms", "getAllPosts", "getAllUserPosts"]:
                handlers = {
                    "getAllUsers": getAllUsers,
                    "getAllQuotes": getAllQuotes,
                    "getAllReposts": getAllReposts,
                    "getAllGyms": getAllGyms,
                    "getAllPosts": getAllPosts,
                    "getAllUserPosts": lambda: getAllUserPosts(request.view_args.get("id")),
                }
                return func(handlers[local_routing_key]())

            if local_routing_key == "me":
                auth_header = request.headers.get("Authorization")
                if auth_header == "null":
                    return jsonify({"error": "No token was provided"}), 401
                payload = validate_token(auth_header)
                local_routing_key = payload.get("id")

            elif local_routing_key == "login":
                email = request.form.get("email")
                filtered_entities = [entity for entity in chord_logic.system_entities_set if entity[1] == email]
                print(filtered_entities, chord_logic.system_entities_set)
                local_routing_key = filtered_entities[0][1] if filtered_entities else None

            if local_routing_key is None:
                return jsonify({"error": "Invalid routing key"}), 400

            key = chord_node.get_hash(local_routing_key)
            responsible_node = chord.find_successor(key)
            self_id = chord_node.current_node.to_dict()["id"]

            if responsible_node["id"] == self_id or local_routing_key is None:
                return func(*args, **kwargs)

            target_url = f"http://{responsible_node['ip']}:{responsible_node['port']}{request.full_path}"
            max_retries = 3
            retry_delay = 1  # Initial delay in seconds

            for attempt in range(max_retries):
                try:
                    method = request.method.lower()
                    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

                    if request.is_json:
                        json_data = request.get_json(silent=True)
                        response = getattr(requests, method)(
                            target_url, headers=headers, json=json_data
                        )
                    else:
                        # Handle form data
                        form_data = request.form  # Keep as ImmutableMultiDict to preserve multi-values
                        form_data = form_data.to_dict()  # Convert to dict if modification is needed
                        if routing_key != "login":
                            form_data["id"] = local_routing_key

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

                    if response.status_code == 502 and attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay * 2  # Exponential backoff
                        continue

                    return response.content, response.status_code, dict(response.headers)

                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        return jsonify({"error": "Failed to forward request", "details": str(e)}), 502

                time.sleep(retry_delay)

            return jsonify({"error": "Failed after retries"}), 502

        return wrapper
    return decorator