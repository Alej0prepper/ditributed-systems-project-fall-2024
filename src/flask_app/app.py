
from flask import Flask, request, jsonify

app = Flask(__name__)

# Endpoint to register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    return jsonify({"message": "User registered successfully"}), 201

# Endpoint to log in a user
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    return jsonify({"message": "User logged in successfully"}), 200

# Endpoint to create a new post
@app.route('/post', methods=['POST'])
def post():
    data = request.json
    return jsonify({"message": "Post created successfully"}), 201

# Endpoint to repost an existing post
@app.route('/repost', methods=['POST'])
def repost():
    data = request.json
    return jsonify({"message": "Post reposted successfully"}), 201

# Endpoint to delete a post
@app.route('/delete-post', methods=['DELETE'])
def delete_post():
    data = request.json
    return jsonify({"message": "Post deleted successfully"}), 200

# Endpoint to follow a user
@app.route('/follow', methods=['POST'])
def follow():
    data = request.json
    return jsonify({"message": "Now following user"}), 200

# Endpoint to unfollow a user
@app.route('/unfollow', methods=['POST'])
def unfollow():
    data = request.json
    return jsonify({"message": "User unfollowed"}), 200

# Endpoint to react to a post
@app.route('/react', methods=['POST'])
def unfollow():
    data = request.json
    return jsonify({"message": "Reaction sent"}), 201

# Endpoint to comment a post
@app.route('/comment', methods=['POST'])
def unfollow():
    data = request.json
    return jsonify({"message": "Comment sent"}), 201

if __name__ == '__main__':
    app.run(debug=True)
