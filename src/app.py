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
    """
    Register a new user endpoint.
    
    Accepts POST request with form data containing user registration details.
    Required fields:
    - password
    - Either email or username
    
    Optional fields:
    - name
    - wheigth 
    - styles
    - levels_by_style
    
    Returns:
        201: JSON with success message and user ID if registration successful
        400: JSON with error if required fields missing
        500: JSON with error if registration fails
    """
    data = request.form

    email = data.get("email")
    name = data.get("name")
    username = data.get("username")
    password = data.get("password")
    wheigth = data.get("wheigth")
    styles = data.get("styles")
    levels_by_style = data.get("levels_by_style")

    # Check that either email+password or username+password are provided
    if not password:
        return jsonify({"message": "Password is required."}), 400
    if not email and not username:
        return jsonify({"message": "Either email or username is required."}), 400

    user_id, error = register_user(name, username, email, password, wheigth, styles, levels_by_style)
    if error == None:
        return jsonify({"message": f"User registered successfully. ID: {user_id}"}), 201
    return jsonify({"Error": f"{error}"}), 500

# Endpoint to update logged in user info
@app.route('/update-user', methods=['PUT'])
def updateUser():
    """
    Update logged in user information endpoint.
    
    Accepts PUT request with form data containing user details to update.
    Optional fields that can be updated:
    - email
    - username 
    - password
    - name
    - wheight
    - styles 
    - levels_by_style
    At least one field is required for update.
    Returns:
        201: JSON with success message if update successful
        500: JSON with error message if update fails
    """
    data = request.form
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")
    name = data.get("name") 
    wheight = data.get("wheight")
    styles = data.get("styles")
    levels_by_style = data.get("levels_by_style")  
    if name is None and email is None and password is None and wheight is None and styles is None and levels_by_style is None:
        return jsonify({"error": "At least one field is required for update"}), 400
    _, ok, error = update_user_account(name, email, password, wheight, styles, levels_by_style)
    if ok:
        return jsonify({"message": f"User updated successfully."}), 201
    return jsonify({"Error": f"{error}"}), 500


#delete user account
@app.route('/delete-user', methods=['DELETE'])
def delete_user():
    """
    Delete logged in user account endpoint.
    
    Accepts DELETE request to remove the currently logged in user's account.
    No request body required as it uses session data to identify user.

    Returns:
        200: JSON with success message if deletion successful
        500: JSON with error message if deletion fails
    """
    _, ok, error = delete_user_account()
    if ok:
        return jsonify({"message": "User deleted successfully."}), 200
    return jsonify({"error": error}), 500

# Endpoint to log in a user
@app.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Accepts POST request with form data containing login credentials.
    Required fields:
    - password
    And one of:
    - username
    - email

    Returns:
        201: JSON with authentication token if login successful
        500: JSON with error message if login fails
    """
    data = request.form
    token, ok, error = login_user(data.get("password"), data.get("username"), data.get("email")) 
    if ok:
        return jsonify({"token": token}), 201
    else:
        return jsonify({"error": error}), 500

# Endpoint to log out a user
@app.route('/logout', methods=['POST'])
def logout():
    """
    User logout endpoint.
    
    Accepts POST request to log out the currently authenticated user.
    Clears the username and email from the session.
    No request body required.

    Returns:
        201: JSON with success message confirming logout
    """
    session["username"] = ""
    session["email"] = ""
    return jsonify({"message": "Logged out."}), 201

# Endpoint to create a new post
@app.route('/post', methods=['POST'])
def post():
    """
    Create a new post endpoint.
    
    Accepts POST request with form data containing post content.
    Required fields (at least one must be present):
    - media: Media content for the post
    - caption: Text caption for the post

    Returns:
        201: JSON with success message and post ID if creation successful
        500: JSON with error message if creation fails or required fields missing
    """
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
    """
    Repost an existing post endpoint.
    
    Accepts POST request with form data containing post ID to repost.
    Required fields:
    - reposted_post_id: ID of the post to repost

    Returns:
        201: JSON with success message if repost successful
        500: JSON with error message if repost fails or post ID missing
    """
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
    """
    Quote an existing post endpoint.
    
    Accepts POST request with form data containing post ID to quote and new content.
    Required fields:
    - quoted_post_id: ID of the post to quote
    - media: Media content for the quote (optional if caption provided)
    - caption: Text caption for the quote (optional if media provided)

    Returns:
        201: JSON with success message if quote successful
        500: JSON with error message if quote fails or required fields missing
    """
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
    """
    Delete a post endpoint.
    
    Accepts DELETE request with form data containing post ID to delete.
    Required fields:
    - post_id: ID of the post to delete

    Returns:
        200: JSON with success message if deletion successful
        500: JSON with error message if deletion fails or post ID missing
    """
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
    """
    Follow a user endpoint.
    
    Accepts POST request with form data containing username to follow.
    Required fields:
    - followed: Username of the user to follow

    Returns:
        200: JSON with success message if follow successful
        500: JSON with error message if follow fails or username missing
    """
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
    """
    Unfollow a user endpoint.
    
    Accepts POST request with form data containing username to unfollow.
    Required fields:
    - followed: Username of the user to unfollow

    Returns:
        200: JSON with success message if unfollow successful
        500: JSON with error message if unfollow fails or username missing
    """
    data = request.form
    followed_username = data.get("followed")
    if not followed_username:
        return jsonify({"error": "Followed username is required"}), 500
    _, ok, error = unfollow_user(followed_username)
    if ok:
        return jsonify({"message": f"Unfollowed user {followed_username}"}), 200
    return jsonify({"error": error}), 500

@app.route('/find-users', methods=['GET'])
def get_users():
    """
    Find users endpoint.
    
    Accepts GET request with query parameter for searching users.
    Required parameters:
    - query: Search term to find users

    Returns:
        200: JSON with list of matching users if search successful
        500: JSON with error message if search fails or query missing
    """
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query is required"}), 500    
    if query == "": return jsonify({"users": []}), 200
    users, ok, error = get_users_by_search_term(query)
    if ok:
        return jsonify({"users": users}), 200
    return jsonify({"error": error}), 500

# Endpoint to react to a post
@app.route('/react-post', methods=['POST'])
def react_post():
    """
    React to a post endpoint.
    
    Accepts POST request with form data containing reaction and post ID.
    Required fields:
    - reaction: The reaction to add to the post
    - post_id: ID of the post to react to

    Returns:
        201: JSON with success message if reaction successful
        500: JSON with error message if reaction fails or required fields missing
    """
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
    """
    React to a comment endpoint.
    
    Accepts POST request with form data containing reaction and comment ID.
    Required fields:
    - reaction: The reaction to add to the comment
    - comment_id: ID of the comment to react to

    Returns:
        201: JSON with success message if reaction successful
        500: JSON with error message if reaction fails or required fields missing
    """
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
    """
    Create a comment on a post endpoint.
    
    Accepts POST request with form data containing comment details.
    Required fields:
    - post_id: ID of the post to comment on
    Optional fields:
    - caption: Text content of the comment
    - media: Media content of the comment
    At least one of caption or media must be provided.

    Returns:
        201: JSON with success message and comment ID if comment created successfully
        500: JSON with error message if comment fails or required fields missing
    """
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
    """
    Create a reply to an existing comment endpoint.
    
    Accepts POST request with form data containing reply details.
    Required fields:
    - comment_id: ID of the comment to reply to
    Optional fields:
    - caption: Text content of the reply
    - media: Media content of the reply
    At least one of caption or media must be provided.

    Returns:
        201: JSON with success message and reply comment ID if created successfully
        500: JSON with error message if reply fails or required fields missing
    """
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
    """
    Create a new gym endpoint.
    
    Accepts POST request with form data containing gym details.
    Required fields:
    - name: Name of the gym
    - username: Username for gym account
    - email: Email address for gym
    - location: Location of the gym
    - address: Street address of the gym
    - password: Password for gym account
    - styles: Training styles offered
    Optional fields:
    - phone_number: Contact phone number
    - ig_profile: Instagram profile handle

    Returns:
        201: JSON with success message if gym created successfully
        400: JSON with error if required fields are missing
        500: JSON with error if gym creation fails
    """
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
    """
    Log in a gym account endpoint.
    
    Accepts POST request with form data containing login credentials.
    Required fields (at least one of):
    - username: Username for gym account
    - email: Email address for gym
    Required field:
    - password: Password for gym account

    Returns:
        201: JSON with success message if login successful
        400: JSON with error if required fields are missing
        500: JSON with error if login fails
    """
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

@app.route('/update-gym',methods=['PUT'])
def update_gym():
    """
    Update a gym account endpoint.
    
    Accepts PUT request with form data containing fields to update.
    Optional fields:
    - name: New name for the gym
    - email: New email address
    - location: New location
    - address: New address
    - styles: New training styles offered
    - password: New password
    - phone_number: New phone number
    - ig_profile: New Instagram profile link
    
    At least one field is required for update.
    Returns:
        201: JSON with success message if update successful
        400: JSON with error if no fields provided for update
        500: JSON with error if update fails
    """
    data = request.form
    name = data.get("name")
    email = data.get("email")
    location = data.get("location")
    address = data.get("address")
    styles = data.get("styles")
    password = data.get("password")
    phone_number = data.get("phone_number") if data.get("phone_number") else None
    ig_profile = data.get("ig_profile") if data.get("ig_profile") else None
    username,ok,error = update_gym_controller(name,session['username'],email,location,address,styles,password,phone_number,ig_profile)
    if name is None and email is None and location is None and address is None and styles is None and password is None and phone_number is None and ig_profile is None:
        return jsonify({"error": "At least one field is required for update"}), 400
    if ok:
        return jsonify({"message": f"Gym updated with username {session['username']}"}),201
    return jsonify({"error": error}), 500


@app.route('/get-gym-info',methods=['POST'])
def get_gym_info():
    """
    Get information about a specific gym.
    
    Accepts POST request with form data containing gym ID.
    Required fields:
    - gym_id: ID of the gym to get info for
    
    Returns:
        201: JSON with gym information if successful
        400: JSON with error if gym ID not provided
        500: JSON with error if lookup fails
    """
    data = request.form
    gym_id = data.get("gym_id")
    if not gym_id:
        return jsonify({"error": "Gym ID is required"}), 400
    info,ok,error = get_gym_info_controller(gym_id)

    if ok:
        return jsonify(info),201
    return jsonify({"error": error}), 500

@app.route('/delete-gym',  methods=['DELETE'])  
def delete_gym():
    """
    Delete logged in gym account endpoint.
    
    Accepts DELETE request to remove the currently logged in gym's account.
    No request body required as it uses session data to identify gym.

    Returns:
        200: JSON with success message if deletion successful
        500: JSON with error message if deletion fails
    """
    _,ok,error = delete_gym_controller(session['username'])

    if ok:
        return jsonify({"message": f"Gym with username {session['username']} deleted succesfully." }), 200
    return jsonify({"error": error}), 500

@app.route('/trains-in', methods=['POST'])
def trains_in_endpoint():
    """
    Create a trains-in relationship between logged in user and a gym.
    
    Accepts POST request with form data containing gym and training details.
    Required fields:
    - gym_id: ID of the gym to train at
    - styles: Training styles to associate with relationship
    
    Returns:
        200: JSON with success message if relationship created
        400: JSON with error if required fields missing
        500: JSON with error if creation fails
    """
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
    """
    Add training styles to an existing trains-in relationship.
    
    Accepts POST request with form data containing gym and training styles.
    Required fields:
    - gym_id: ID of the gym to add styles for
    - styles: Additional training styles to associate with relationship
    
    Returns:
        200: JSON with success message if styles added
        400: JSON with error if required fields missing
        500: JSON with error if addition fails
    """
    data = request.form
    styles = data.get("styles")
    gym_id = data.get("gym_id")
    if not gym_id or not styles:
        return jsonify({"error": "Gym ID and styles are required"}), 400    
    _,ok,error = add_training_styles(styles,gym_id)
    if ok:
        return jsonify({"message": f"Styles added to user in a gym with ID {gym_id}"})
    return jsonify({"error": error}), 500

@app.route('/remove-training-styles', methods=['POST'])
def remove_training_styles():
    """
    Remove training styles from an existing trains-in relationship.
    
    Accepts POST request with form data containing gym and training styles.
    Required fields:
    - gym_id: ID of the gym to remove styles from
    - styles: Training styles to remove from relationship
    
    Returns:
        200: JSON with success message if styles removed
        400: JSON with error if required fields missing
        500: JSON with error if removal fails
    """
    data = request.form
    styles = data.get("styles")
    gym_id = data.get("gym_id")
    if not gym_id or not styles:
        return jsonify({"error": "Gym ID and styles are required"}), 400
    _,ok,error = remove_training_styles(styles,gym_id)
    if ok:
        return jsonify({"message": f"Styles removed from user in a gym with ID {gym_id}"})
    return jsonify({"error": error}), 500
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
