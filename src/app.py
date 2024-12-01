import secrets
from flask import Flask, request, jsonify, session
from network.controllers.users import delete_user_account, get_users_by_search_term, login_user, register_user
from network.controllers.posts import create_post, repost_existing_post, quote_existing_post, delete_post
from flask_cors import CORS
from network.controllers.users import follow_user
from network.controllers.users import unfollow_user
from network.controllers.comments import create_comment_answer, create_post_comment
from network.controllers.reactions import react_to_a_comment, react_to_a_post
from network.controllers.gyms import add_gym_controller, update_gym_controller, get_gym_info_controller,delete_gym_controller
from network.controllers.trains_in import trains_in, add_training_styles, remove_training_styles
from network.controllers.gyms import login_gym
from network.controllers.users import update_user_account
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
    wheigth = data.get("wheigth")
    styles = data.get("styles")
    levels_by_style = data.get("levels_by_style")

    if not password or (not email and not username):
        return jsonify({"message": "Password and either email or username are required."}), 500

    user_id, error = register_user(name, username, email, password, wheigth, styles, levels_by_style)
    if error == None:
        return jsonify({"message": f"User registered successfully. ID: {user_id}"}), 201
    return jsonify({"Error": f"{error}"}), 500

# Endpoint to update logged in user info
@app.route('/update-user', methods=['POST'])
def updateUser():
    data = request.form
    email = data.get("email")
    name = data.get("name") 
    password = data.get("password")
    wheight = data.get("wheight")
    styles = data.get("styles")
    levels_by_style = data.get("levels_by_style")

    # Check if all required fields are present
    if not all([email, name, password, wheight, styles, levels_by_style]):
        return jsonify({"error": "All fields (email, name, password, weight, styles and levels) are required"}), 400

    _, ok, error = update_user_account(name, email, password, wheight, styles, levels_by_style)
    if ok:
        return jsonify({"message": f"User updated successfully."}), 201
    return jsonify({"Error": f"{error}"}), 500



#delete user account
@app.route('/delete-user', methods=['POST'])
def delete_user():
    _, ok, error = delete_user_account()
    if ok:
        return jsonify({"message": "User deleted successfully."}), 200
    return jsonify({"error": error}), 500

# Endpoint to log in a user
@app.route('/login', methods=['POST'])
def login():
    data = request.form
    _, ok, error = login_user(data.get("password"), data.get("username"), data.get("email")) 
    if ok:
        return jsonify({"message": "User logged in."}), 201
    else:
        return jsonify({"error": error}), 500

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

    if not media and not caption:
        return jsonify({"message": f"Media or caption are required."}), 500
    
    response, ok, error = create_post(data["media"], data["caption"])
    if ok:
        return jsonify({"message": f"Post created successfully. ID: {response}"}), 201
    else:
        return jsonify({"error": error})

# Endpoint to repost an existing post
@app.route('/repost', methods=['POST'])
def repost():
    data = request.form
    reposted_post_id = data.get("reposted_post_id")
    if not reposted_post_id:
        return jsonify({"error": "Reposted post ID is required"}), 500
    reposted_post_id = int(reposted_post_id)
    _, ok, error = repost_existing_post(reposted_post_id)
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
    if not quoted_post_id:
        return jsonify({"error": "Quoted post ID is required"}), 500
    if not media and not caption:
        return jsonify({"error": "Media or caption is required"}), 500
    quoted_post_id = int(quoted_post_id)
   
    _, ok, error = quote_existing_post(quoted_post_id, media, caption)
    if ok:
        return jsonify({"message": f"Post quoted successfully."}), 201
    else:
        return jsonify({"error": error})

# Endpoint to delete a post
@app.route('/delete-post', methods=['DELETE'])
def remove_post():
    data = request.form
    post_id = data.get("post_id")
    if not post_id:
        return jsonify({"error": "Post ID is required"}), 500
    post_id = int(post_id)
    _, ok, error = delete_post(post_id)
    if not ok:
        return jsonify({"error": error}), 500 
    return jsonify({"message": "Post deleted successfully"}), 200

# Endpoint to follow a user
@app.route('/follow', methods=['POST'])
def follow():
    data = request.form
    followed_username = data.get("followed")
    if not followed_username:
        return jsonify({"error": "Followed username is required"}), 500
    _, ok, error = follow_user(followed_username)
    if ok:
        return jsonify({"message": f"Now following user {followed_username}"}), 200
    return jsonify({"error": error}), 500

# Endpoint to unfollow a user
@app.route('/unfollow', methods=['POST'])
def unfollow():
    data = request.form
    followed_username = data.get("followed")
    if not followed_username:
        return jsonify({"error": "Followed username is required"}), 500
    _, ok, error = unfollow_user(followed_username)
    if ok:
        return jsonify({"message": f"Unfollowed user {followed_username}"}), 200
    return jsonify({"error": error}), 500

# endpoint to get and user by username or email 
@app.route('/find-users', methods=['POST'])
def get_users():
    data = request.form
    query = data.get("query")
    if not query:
        return jsonify({"error": "Query is required"}), 500
    users, ok, error = get_users_by_search_term(query)
    if ok:
        return jsonify({"users": users}), 200
    return jsonify({"error": error}), 500

# Endpoint to react to a post
@app.route('/react-post', methods=['POST'])
def react_post():
    data = request.form
    reaction = data.get("reaction")
    post_id = int(data.get("post_id"))
    if not reaction:
        return jsonify({"error": "Reaction is required"}), 500
    if not post_id:
        return jsonify({"error": "Post ID is required"}), 500
    _, ok, error = react_to_a_post(reaction, post_id)
    if ok:
        return jsonify({"message": "Reaction sent"}), 201
    return jsonify({"error": error}), 500

# Endpoint to react to a comment
@app.route('/react-comment', methods=['POST'])
def react_comment():
    data = request.form
    reaction = data.get("reaction")
    comment_id = int(data.get("comment_id"))
    if not reaction or not comment_id:
        return jsonify({"error": "Reaction and comment ID are required"}), 500
    _, ok, error = react_to_a_comment(reaction, comment_id)
    if ok:
        return jsonify({"message": "Reaction sent"}), 201
    return jsonify({"error": error}), 500

# Endpoint to comment a post
@app.route('/comment-post', methods=['POST'])
def comment():
    data = request.form
    caption = data.get("caption")
    media = data.get("media")
    post_id = int(data.get("post_id"))
    if not caption and not media:
        return jsonify({"error": "Caption or media is required"}), 500
    if not post_id:
        return jsonify({"error": "Post ID is required"}), 500
    comment_id, ok, error = create_post_comment(caption, media, post_id)
    if ok:
        return jsonify({"message": f"Comment sent. ID: {comment_id}"}), 201
    return jsonify({"error": error}), 500

# Endpoint to answer a comment
@app.route('/answer-comment', methods=['POST'])
def answer():
    data = request.form
    caption = data.get("caption")
    media = data.get("media")
    comment_id = int(data.get("comment_id"))
    if not caption and not media:
        return jsonify({"error": "Caption or media is required"}), 500
    if not comment_id:
        return jsonify({"error": "Comment ID is required"}), 500
    new_comment_id, ok, error = create_comment_answer(caption, media, comment_id)
    if ok:
        return jsonify({"message": f"Comment sent. ID: {new_comment_id}"}), 201
    return jsonify({"error": error}), 500

# Endpoint to create a gym
@app.route('/create-gym',methods=['POST'])
def create_gym():
    data = request.form
    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    location = data.get("location")
    address = data.get("address")
    password = data.get("password")
    styles = data.get("styles")
    phone_number = data.get("phone_number") if data.get("phone_number") else None
    ig_profile = data.get("ig_profile") if data.get("ig_profile") else None
    if not name or not username or not email or not location or not address or not password or not styles:
        return jsonify({"error": "All fields (name, username, email, location, address, password and styles) are required"}), 400
    gym_id, ok, error = add_gym_controller(name,username,email,location,address,styles,password,phone_number,ig_profile)

    if ok:
        return jsonify({"message": f"Gym created. username: {username}"}), 201
    return jsonify({"error": error}), 500

# Endpoint to log in as gym
@app.route('/gym-login',methods=['POST'])
def loginGym():
    data = request.form
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not username and not email:
        return jsonify({"error": "Username or email is required"}), 400
    if not password:
        return jsonify({"error": "Password is required"}), 400
    _, ok, error = login_gym(username,email,password)

    if ok:
        return jsonify({"message": f"Gym logged in."}), 201
    return jsonify({"error": error}), 500

@app.route('/update-gym',methods=['POST'])
def update_gym():

    data = request.form
    name = data.get("name")
    email = data.get("email")
    location = data.get("location")
    address = data.get("address")
    styles = data.get("styles")
    password = data.get("password")
    phone_number = data.get("phone_number") if data.get("phone_number") else None
    ig_profile = data.get("ig_profile") if data.get("ig_profile") else None
    if not name or not email or not location or not address or not styles or not password:
        return jsonify({"error": "All fields (name, email, location, address, styles and password) are required"}), 400
    username,ok,error = update_gym_controller(name,session['username'],email,location,address,styles,password,phone_number,ig_profile)
    if ok:
        return jsonify({"message": f"Gym updated with username {session['username']}"}),201
    return jsonify({"error": error}), 500

@app.route('/get-gym-info',methods=['POST'])
def get_gym_info():
    data = request.form
    gym_id = data.get("gym_id")
    if not gym_id:
        return jsonify({"error": "Gym ID is required"}), 400
    info,ok,error = get_gym_info_controller(gym_id)

    if ok:
        return jsonify(info),201
    return jsonify({"error": error}), 500

@app.route('/delete-gym',  methods=['POST'])  
def delete_gym():

    _,ok,error = delete_gym_controller(session['username'])

    if ok:
        return jsonify({"message": f"Gym with username {session['username']} deleted succesfully." })
    return jsonify({"error": error})

@app.route('/trains-in', methods=['POST'])
def trains_in_main():
    data = request.form
    gym_id = data.get("gym_id")
    styles = data.get("styles") 
    if not gym_id or not styles:
        return jsonify({"error": "Gym ID and styles are required"}), 400
    _,ok,error = trains_in(styles,gym_id)
    if ok:
        return jsonify({"message": f"User trains in gym with ID {gym_id}"})
    return jsonify({"error": error}), 500

@app.route('/add-training-styles', methods=['POST'])
def add_training_styles():
    data = request.form
    styles = data.get("styles")
    gym_id = data.get("gym_id")
    if not gym_id or not styles:
        return jsonify({"error": "Gym ID and styles are required"}), 400    
    _,ok,error = add_training_styles(styles,gym_id)
    if ok:
        return jsonify({"message": f"Styles added to user in a gym with ID {gym_id}"})
    return jsonify({"error": error}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
