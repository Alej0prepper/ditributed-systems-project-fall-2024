import secrets
from flask import Flask, request, jsonify, session
from network.controllers.users import login_user, register_user

app = Flask(__name__)
app.secret_key = secrets.token_hex(16) 

# Endpoint to register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.form
    user_id, error = register_user(data.get("name"), data.get("username"), data.get("email"), data.get("password"))
    if error == None:
        return jsonify({"message": f"User registered successfully. ID: {user_id}"}), 201
    return jsonify({"Error": f"{error}"}), 400

# Endpoint to log in a user
@app.route('/login', methods=['POST'])
def login():
    data = request.form
    if login_user(data.get("password"), data.get("username"), data.get("email")):
        if data.get("username"):
            session["username"] = data.get("username")
        return jsonify({"message": "User logged in successfully"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 400

# Endpoint to create a new post
@app.route('/post', methods=['POST'])
def post():
    data = request.form
    return jsonify({"message": "Post created successfully"}), 201

# Endpoint to repost an existing post
@app.route('/repost', methods=['POST'])
def repost():
    data = request.form
    return jsonify({"message": "Post reposted successfully"}), 201

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
    app.run(debug=True)
