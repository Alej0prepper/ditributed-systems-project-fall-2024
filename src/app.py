import secrets
from flask import Flask, request, jsonify, session
from network.controllers.users import login_user, register_user
from network.controllers.posts import create_post, repost_existing_post, quote_existing_post
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = secrets.token_hex(16) 

# Endpoint to register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.form

    email = data.get("email")
    name = data.get("name")
    username = data.get("username")
    password = data.get("password")

    if not email or not username or not password:
        return jsonify({"message": f"Email, username and password are required."}), 400

    user_id, error = register_user(name, username, email, password)
    if error == None:
        return jsonify({"message": f"User registered successfully. ID: {user_id}"}), 201
    return jsonify({"Error": f"{error}"}), 400

# Endpoint to log in a user
@app.route('/login', methods=['POST'])
def login():
    data = request.form
    if login_user(data.get("password"), data.get("username"), data.get("email")):
        return jsonify({"message": "User logged in."}), 201
    else:
        return jsonify({"message": "Invalid credentials"}), 400

# Endpoint to log out a user
@app.route('/logout', methods=['POST'])
def logout():
    session["username"] = ""
    session["email"] = ""
    return jsonify({"message": "Logged out."}), 201

# Endpoint to create a new post
@app.route('/post', methods=['POST'])
def post():
    data = request.form
    media = data.get("media")
    caption = data.get("caption")

    if not media or not caption:
        return jsonify({"message": f"Media or caption are required."}), 400
    
    response, ok, error = create_post(data["media"], data["caption"])
    if ok:
        return jsonify({"message": f"Post created successfully. ID: {response}"}), 201
    else:
        return jsonify({"error": error})

# Endpoint to repost an existing post
@app.route('/repost', methods=['POST'])
def repost():
    data = request.form
    _, ok, error = repost_existing_post(int(data["reposted_post_id"]))
    if ok:
        return jsonify({"message": f"Post reposted successfully."}), 201
    else:
        return jsonify({"error": error})

# Endpoint to quote an existing post
@app.route('/quote', methods=['POST'])
def quote():
    data = request.form
    quoted_post_id = int(data.get("quoted_post_id"))
    media = data.get("media")
    caption = data.get("caption")
    _, ok, error = quote_existing_post(quoted_post_id, media, caption)
    if ok:
        return jsonify({"message": f"Post quoted successfully."}), 201
    else:
        return jsonify({"error": error})

# Endpoint to delete a post
@app.route('/delete-post', methods=['DELETE'])
def delete_post():
    data = request.form
    return jsonify({"message": "Post deleted successfully"}), 200

# Endpoint to follow a user
@app.route('/follow', methods=['POST'])
def follow():
    data = request.form
    return jsonify({"message": "Now following user"}), 200

# Endpoint to unfollow a user
@app.route('/unfollow', methods=['POST'])
def unfollow():
    data = request.form
    return jsonify({"message": "User unfollowed"}), 200

# Endpoint to react to a post
@app.route('/react', methods=['POST'])
def react():
    data = request.form
    return jsonify({"message": "Reaction sent"}), 201

# Endpoint to comment a post
@app.route('/comment', methods=['POST'])
def comment():
    data = request.form
    return jsonify({"message": "Comment sent"}), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
