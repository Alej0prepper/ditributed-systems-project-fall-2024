import secrets
import os
import threading
import chord.node as chord
import json
import uuid
from flask_cors import CORS
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, session, send_from_directory
from network.controllers.users import delete_user_account, get_users_by_search_term, login_user, register_user
from network.controllers.posts import create_post, repost_existing_post, quote_existing_post, delete_post
from network.controllers.users import follow_account
from network.controllers.users import unfollow_user
from network.controllers.comments import create_comment_answer, create_post_comment
from network.controllers.reactions import react_to_a_comment, react_to_a_post
from network.controllers.gyms import add_gym_controller, delete_gym_controller
from network.controllers.trains_in import trains_in, add_training_styles, remove_training_styles
from network.controllers.gyms import login_gym
from network.controllers.users import update_user_account
from network.controllers.gyms import get_gyms_by_search_term
from chord.routes import chord_routes
from chord.protocol_logic import check_predecessor, stabilize
from network.middlewares.route_to_responsible import route_to_responsible
from network.controllers.users import get_user_by_id_controller
from network.controllers.gyms import get_gym_by_id_controller, update_gym_controller
from network.controllers.users import get_logged_user_controller
from network.controllers.gyms import get_logged_gym_controller
from chord.protocol_logic import listen_for_chord_updates
import chord.protocol_logic as chord_logic
from network.middlewares.use_db_connection import use_db_connection
from chord.replication import replicate_to_owners



app = Flask(__name__)

app.register_blueprint(chord_routes)

app.secret_key = secrets.token_hex(16) 

CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

""" @app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
 """

@app.route('/register', methods=['POST'])
@route_to_responsible()
def register(id=str(uuid.uuid4())):
    """
    Register a new user endpoint.
    
    Accepts POST request with form data containing user registration details.
    Required fields:
    - password
    - Either email or username
    
    Optional fields:
    - name
    - weigth 
    - styles
    - levels_by_style
    - birth_date
    - gyms_ids
    - image
    - description`  

    
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
    weight = data.get("weight")
    styles = data.get("styles")
    levels_by_style = data.get("levels_by_style")
    gyms_ids = data.get("gyms_ids")
    birth_date = data.get("birthDate")
    description = data.get("description")

    profile_image = request.files.get("image")
    image_url = None

    if profile_image and allowed_file(profile_image.filename):
        filename = secure_filename(profile_image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_image.save(image_path)
        image_url = 'uploads/' + filename


    # Check that either email+password or username+password are provided
    if not password:
        return jsonify({"message": "Password is required."}), 400
    if not email and not username:
        return jsonify({"message": "Either email or username is required."}), 400

    user_id, error = register_user(id, name, username, email, image_url, password, weight, styles, levels_by_style, birth_date, gyms_ids,description)
    if error == None:
        user_info = f"{email},{id}"
        chord_logic.send_chord_update(user_info)
        return jsonify({"message": f"User registered successfully. ID: {user_id}"}), 201
    return jsonify({"Error": f"{error}"}), 500

@app.route('/update-user/<id>', methods=['PUT'])
@route_to_responsible(routing_key=None)
def updateUser(id):
    """
    Update logged in user information endpoint.
    
    Accepts PUT request with form data containing user details to update.
    Optional fields that can be updated:
    - email
    - username 
    - password
    - name
    - weight
    - styles 
    - levels_by_style
    - birthDate
    - image
    - description
    At least one field is required for update.
    Returns:
        201: JSON with success message if update successful
        500: JSON with error message if update fails
    """
    data = request.form
    email = data.get("email")
    password = data.get("password")
    name = data.get("name") 
    weight = data.get("weight")
    styles = data.get("styles")
    levels_by_style = data.get("levels_by_style")  
    birth_date = data.get("birthDate")  
    description = data.get("description")


    profile_image = request.files.get("image")
    image_url = None

    if profile_image and allowed_file(profile_image.filename):
        filename = secure_filename(profile_image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_image.save(image_path)
        image_url = 'uploads/' + filename

    if name is None and email is None and password is None and weight is None and styles is None and levels_by_style is None and description is None:
        return jsonify({"error": "At least one field is required for update"}), 400
    
    _, ok, error = update_user_account(name, email, password, image_url, weight, styles, levels_by_style, birth_date,description)
    if ok:
        return jsonify({"message": f"User updated successfully."}), 201
    return jsonify({"Error": f"{error}"}), 500

@app.route('/delete-user<id>', methods=['DELETE'])
@route_to_responsible(routing_key=None)
def delete_user(id):
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

@app.route('/login', methods=['POST'])
@route_to_responsible(routing_key="login")
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
    data, ok, error = login_user(data.get("password"), data.get("username"), data.get("email")) 
    if ok:
        return jsonify({"data": data}), 201
    else:
        return jsonify({"error": error}), 401

@app.route('/users',methods=['GET'])
@route_to_responsible(routing_key="getAllUsers")
def get_all_users(users):
    """
    Get all users endpoint.
    
    Returns:
        200: JSON with users
        500: JSON with error if users fetch had an error
    """

    if users:
        return jsonify({"users": users}), 200
    return jsonify({"error"}), 500

@app.route('/users/<id>',methods=['GET'])
@route_to_responsible(routing_key=None)
def get_user_by_id(id):
    """
    Get specific user endpoint.
    
    Returns:
        200: JSON with user
        500: JSON with error if user fetch had an error
    """
    user, ok, error = get_user_by_id_controller(id)

    if ok:
        return jsonify({"user": user}), 200
    return jsonify({"error": error}), 500

@app.route('/gyms/<id>',methods=['GET'])
@route_to_responsible(routing_key=None)
def get_gym_by_id(id):
    """
    Get specific gym endpoint.
    
    Returns:
        200: JSON with gym
        500: JSON with error if gym fetch had an error
    """
    gym, ok, error = get_gym_by_id_controller(id)

    if ok:
        return jsonify({"gym": gym}), 200
    return jsonify({"error": error}), 500

@app.route('/post', methods=['POST'])
@route_to_responsible()
def post(id=str(uuid.uuid4())):
    """
    Create a new post endpoint.
    
    Accepts POST request with form data containing post content.
    Required fields (at least one must be present):
    - media: One or more media files for the post
    - caption: Text caption for the post (optional)

    Returns:
        201: JSON with success message and post ID if creation successful
        500: JSON with error message if creation fails or required fields missing
    """
    data = request.form
    caption = data.get("caption", "")

    media_files = request.files.getlist("media")  # Retrieve multiple media files
    media_urls = []

    if media_files:
        for media_file in media_files:
            if media_file and allowed_file(media_file.filename):
                filename = secure_filename(media_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                media_file.save(image_path)
                media_urls.append('uploads/' + filename)

    if not media_files and not caption:
        return jsonify({"message": "At least one media file or a caption is required."}), 500

    response, ok, error = create_post(media_urls, caption, id=id)  # Pass media_urls as a list
    if ok:
        return jsonify({"message": f"Post created successfully. ID: {response}"}), 201
    else:
        return jsonify({"error": error}), 500

@app.route('/users/me',methods=['GET'])
@route_to_responsible(routing_key="me")
def get_my_user():
    """
    Get specific user endpoint.
    
    Returns:
        200: JSON with user
        500: JSON with error if user fetch had an error
    """
    user, ok, error = get_logged_user_controller()
    if ok:
        return jsonify({"user": user}), 200
    return jsonify({"error": error}), 500

@app.route('/gyms/me',methods=['GET'])
@route_to_responsible(routing_key="me")
def get_my_gym():
    """
    Get specific user endpoint.
    
    Returns:
        200: JSON with user
        500: JSON with error if user fetch had an error
    """
    gym, ok, error = get_logged_gym_controller()

    if ok:
        return jsonify({"gym": gym}), 200
    return jsonify({"error": error}), 500

@app.route('/repost/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def repost(id):
    """
    Repost an existing post endpoint.
    
    Accepts POST request

    Returns:
        201: JSON with success message if repost successful
        500: JSON with error message if repost fails or post ID missing
    """
    reposted_post_id = int(id)
    if not reposted_post_id:
        return jsonify({"error": "Reposted post ID is required"}), 500
    reposted_post_id = int(reposted_post_id)
    _, ok, error = repost_existing_post(reposted_post_id)
    if ok:
        return jsonify({"message": f"Post reposted successfully."}), 201
    else:
        return jsonify({"error": error})

@app.route('/quote/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def quote(id):
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
    quoted_post_id = int(id)
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

@app.route('/delete-post/<id>', methods=['DELETE'])
@route_to_responsible(routing_key=None)
def remove_post(id):
    """
    Delete a post endpoint.
    
    Accepts DELETE request

    Returns:
        200: JSON with success message if deletion successfull
        500: JSON with error message if deletion fails or post ID missing
    """
    post_id = int(id)
    if not post_id:
        return jsonify({"error": "Post ID is required"}), 500
    post_id = int(post_id)
    _, ok, error = delete_post(post_id)
    if not ok:
        return jsonify({"error": error}), 500 
    return jsonify({"message": "Post deleted successfully"}), 200

@app.route('/follow/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def follow(id):
    """
    Follow user with id: <id>
    
    Accepts POST request 

    Returns:
        201: JSON with success message if follow successfull
        500: JSON with error message if follow fails or username missing
    """
    followed_user, _, _ = get_user_by_id_controller(id)
    followed_username = followed_user.username
    if not followed_username:
        return jsonify({"error": "Followed username is required"}), 500
    _, ok, error = follow_account(followed_username)
    
    if ok:
        return jsonify({"message": f"Now following user {followed_username}"}), 201
    return jsonify({"error": error}), 500

@app.route('/unfollow<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def unfollow(id):
    """
    Unfollow the user with id: <id>.
    
    Accepts POST request

    Returns:
        201: JSON with success message if unfollow successful
        500: JSON with error message if unfollow fails or username missing
    """
    followed_user, _, _ = get_user_by_id_controller(id)
    followed_username = followed_user.username
    if not followed_username:
        return jsonify({"error": "Followed username is required"}), 500
    _, ok, error = unfollow_user(followed_username)
    if ok:
        return jsonify({"message": f"Unfollowed user {followed_username}"}), 201
    return jsonify({"error": error}), 500
@app.route('/follow_gym/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def follow_gym_by_id(id):
    """
    Follow gym with id: <id>
    
    Accepts POST request 

    Returns:
        201: JSON with success message if follow successful
        500: JSON with error message if follow fails or id missing
    """
    gym, _, _ = get_gym_by_id_controller(id)
    if not gym:
        return jsonify({"error": "Gym id is required"}), 500
    gym_username = gym["username"]
    _, ok, error = follow_account(gym_username, "Gym")
    
    if ok:
        return jsonify({"message": f"Now following gym {gym_username}"}), 201
    return jsonify({"error": error}), 500
@app.route('/unfollow_gym/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def unfollow_gym_by_id(id):
    """
    Unfollow the gym with id: <id>.
    
    Accepts POST request

    Returns:
        201: JSON with success message if unfollow successful
        500: JSON with error message if unfollow fails or id missing
    """
    gym, _, _ = get_gym_by_id_controller(id)
    if not gym:
        return jsonify({"error": "Gym id is required"}), 500
    gym_username = gym["username"]
    _, ok, error = unfollow_user(driver, session["username"], gym_username)
    if ok:
        return jsonify({"message": f"Unfollowed gym {gym_username}"}), 201
    return jsonify({"error": error}), 500


@app.route('/find-users', methods=['GET'])
@route_to_responsible(routing_key="getAllUsers")
def get_users(users):
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
        return jsonify({"error": "query is required"}), 500    
    if query == "": return jsonify({"users": []}), 200
    users, ok, error = get_users_by_search_term(users, query)
    if ok:
        return jsonify({"users": users}), 200
    return jsonify({"error": error}), 500

@app.route('/find-gyms', methods=['GET'])
@route_to_responsible(routing_key="getAllGyms")
def get_gyms(gyms):
    """
    Find gyms endpoint.
    
    Accepts GET request with query parameter for searching users.
    Required parameters:
    - query: Search term to find gyms

    Returns:
        200: JSON with list of matching gyms if search successful
        500: JSON with error message if search fails or query missing
    """
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query is required"}), 500    
    if query == "": return jsonify({"gyms": []}), 200
    gyms, ok, error = get_gyms_by_search_term(gyms, query)
    if ok:
        return jsonify({"gyms": gyms}), 200
    return jsonify({"error": error}), 500

@app.route('/react-post/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def react_post(id):
    """
    React to a post with id: <id>.
    
    Accepts POST request with form data containing reaction.
    Required fields:
    - reaction: The reaction to add to the post

    Returns:
        201: JSON with success message if reaction successful
        500: JSON with error message if reaction fails or required fields missing
    """
    data = request.form
    reaction = data.get("reaction")
    post_id = int(id)
    if not reaction:
        return jsonify({"error": "Reaction is required"}), 500
    if not post_id:
        return jsonify({"error": "Post ID is required"}), 500
    _, ok, error = react_to_a_post(reaction, post_id)
    if ok:
        return jsonify({"message": "Reaction sent"}), 201
    return jsonify({"error": error}), 500

@app.route('/react-comment/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def react_comment(id):
    """
    React to a comment endpoint.
    
    Accepts POST request with form data containing reaction.
    Required fields:
    - reaction: The reaction to add to the comment

    Returns:
        201: JSON with success message if reaction successful
        500: JSON with error message if reaction fails or required fields missing
    """
    data = request.form
    reaction = data.get("reaction")
    comment_id = int(id)
    if not reaction or not comment_id:
        return jsonify({"error": "Reaction and comment ID are required"}), 500
    _, ok, error = react_to_a_comment(reaction, comment_id)
    if ok:
        return jsonify({"message": "Reaction sent"}), 201
    return jsonify({"error": error}), 500

@app.route('/comment-post/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def comment(id):
    """
    Create a comment on a post endpoint.
    
    Accepts POST request with form data containing comment details.

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
    post_id = int(id)
    if not caption and not media:
        return jsonify({"error": "Caption or media is required"}), 500
    if not post_id:
        return jsonify({"error": "Post ID is required"}), 500
    comment_id, ok, error = create_post_comment(caption, media, post_id)
    if ok:
        return jsonify({"message": f"Comment sent. ID: {comment_id}"}), 201
    return jsonify({"error": error}), 500

@app.route('/answer-comment/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def answer(id):
    """
    Create a reply to an existing comment endpoint.
    
    Accepts POST request with form data containing reply details.

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
    comment_id = int(id)
    if not caption and not media:
        return jsonify({"error": "Caption or media is required"}), 500
    if not comment_id:
        return jsonify({"error": "Comment ID is required"}), 500
    new_comment_id, ok, error = create_comment_answer(caption, media, comment_id)
    if ok:
        return jsonify({"message": f"Comment sent. ID: {new_comment_id}"}), 201
    return jsonify({"error": error}), 500

@app.route('/create-gym',methods=['POST'])
@route_to_responsible()
def create_gym(id=str(uuid.uuid4())):
    """
    Create a new gym endpoint.
    
    Accepts POST request with form data containing gym details.
    Required fields:
    - name: Name of the gym
    - username: Username for gym account
    - email: Email address for gym
    - location: Location of the gym
    - password: Password for gym account
    - styles: Training styles offered
    Optional fields:
    - phone_number: Contact phone number
    - ig_profile: Instagram profile handle
    - description: Gym description
    - image: Gym's profile image

    Returns:
        201: JSON with success message if gym created successfully
        400: JSON with error if required fields are missing
        500: JSON with error if gym creation fails
    """
    data = request.form
    name = data.get("name")
    username = data.get("username")
    email = data.get("email")
    
    print("Receiving request in create gym")

    if email in [email if entity == "Gym" else None for entity, email, id in chord_logic.system_entities_list]:
        return jsonify({"error": "There is another gym using that email"}), 400


    location = data.get("location") 
    if isinstance(location, str): 
        try:
            location = json.loads(location) 
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid location format"}), 400
        
    password = data.get("password")
    styles = data.get("styles")
    description = data.get("description")
    phone_number = data.get("phone_number") if data.get("phone_number") else None
    ig_profile = data.get("ig_profile") if data.get("ig_profile") else None

    # Handle profile image
    profile_image = request.files.get("image")
    image_url = None  # Default if no image is uploaded

    if profile_image and allowed_file(profile_image.filename):
        filename = secure_filename(profile_image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_image.save(image_path)
        image_url = 'uploads/' + filename

    
    required_fields = {
        "name": name,
        "username": username,
        "email": email,
        "location": location,
        "password": password,
        "styles": styles,
    }

    # Identify missing fields
    missing_fields = [field for field, value in required_fields.items() if not value]

    # Return error if any field is missing
    if missing_fields:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400
    
    gym_id, ok, error = add_gym_controller(name,username,email,description,image_url,location,styles,password,phone_number,ig_profile, id=id)

    if ok:
        gym_info = f"{email},{id}"
        chord_logic.send_chord_update(gym_info)
        return jsonify({"message": f"Gym created. username: {username}"}), 201
    return jsonify({"error": error}), 500

@app.route('/gyms',methods=['GET'])
@route_to_responsible(routing_key="getAllGyms")
def get_all_gyms(gyms):
    """
    Get all gyms endpoint.
    
    Accepts GET request with form data containing gym details.
    
    Returns:
        200: JSON with gyms
        500: JSON with error if gyms fetch had an error
    """
    return jsonify({"gyms": gyms}), 200

@app.route('/gym-login',methods=['POST'])
@route_to_responsible(routing_key="login")
def loginGym():
    """
    Log in a gym account endpoint.
    
    Accepts POST request with form data containing login credentials.
    Required fields (at least one of):
    - id: id for gym account
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
    data, ok, error = login_gym(username,email,password)

    if ok:
        return jsonify({"data": data}), 201
    return jsonify({"error": error}), 500

@app.route('/update-gym/<id>',methods=['PUT'])
@route_to_responsible(routing_key=None)
def update_gym(id):
    """
    Update a gym account endpoint.
    
    Accepts PUT request with form data containing fields to update.
    Optional fields:
    - name: New name for the gym
    - email: New email address
    - location: New location
    - description: New Description
    - image: New image
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

    profile_image = request.files.get("image")
    image_url = None

    if profile_image and allowed_file(profile_image.filename):
        filename = secure_filename(profile_image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        profile_image.save(image_path)
        image_url = 'uploads/' + filename
    
    location = data.get("location") 
    if isinstance(location, str): 
        try:
            location = json.loads(location) 
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid location format"}), 400
    
    address = data.get("address")
    styles = data.get("styles")
    password = data.get("password")
    description = data.get("description")
    phone_number = data.get("phone_number") if data.get("phone_number") else None
    ig_profile = data.get("ig_profile") if data.get("ig_profile") else None

    username,ok,error = update_gym_controller(name,session['username'],email, description, image_url, location,address,styles,password,phone_number,ig_profile)
   
    if name is None and email is None and location is None and address is None and styles is None and password is None and phone_number is None and ig_profile is None:
        return jsonify({"error": "At least one field is required for update"}), 400
    
    if ok:
        return jsonify({"message": f"Gym updated with username {session['username']}"}),201
    return jsonify({"error": error}), 500

@app.route('/delete-gym/<id>',  methods=['DELETE'])
@route_to_responsible(routing_key=None)
def delete_gym(id):
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

@app.route('/trains-in/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def trains_in_endpoint(id):
    """
    Create a trains-in relationship between logged in user and a gym with id: <id>.
    
    Accepts POST request with form data containing training details.

    Required fields:
    - styles: Training styles to associate with relationship
    
    Returns:
        201: JSON with success message if relationship created
        400: JSON with error if required fields missing
        500: JSON with error if creation fails
    """
    data = request.form
    gym_id = str(id)
    styles = data.get("styles") 
    if not gym_id or not styles:
        return jsonify({"error": "Gym ID and styles are required"}), 400
    _,ok,error = trains_in(styles,gym_id)
    if ok:
        return jsonify({"message": f"User trains in gym with ID {gym_id}"}), 201
    return jsonify({"error": error}), 500

@app.route('/add-training-styles/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def add_training_styles(id):
    """
    Add training styles to an existing trains-in relationship with the gym with id: <id>.
    
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
    gym_id = str(id)
    if not gym_id or not styles:
        return jsonify({"error": "Gym ID and styles are required"}), 400    
    _,ok,error = add_training_styles(styles,gym_id)
    if ok:
        return jsonify({"message": f"Styles added to user in a gym with ID {gym_id}"})
    return jsonify({"error": error}), 500

@app.route('/remove-training-styles/<id>', methods=['POST'])
@route_to_responsible(routing_key=None)
def remove_training_styles(id):
    """
    Remove training styles from an existing trains-in relationship with the gym with id: <id>.
    
    Accepts POST request with form data containing gym and training styles.
    Required fields:
    - styles: Training styles to remove from relationship
    
    Returns:
        200: JSON with success message if styles removed
        400: JSON with error if required fields missing
        500: JSON with error if removal fails
    """
    data = request.form
    styles = data.get("styles")
    gym_id = str(id)
    if not gym_id or not styles:
        return jsonify({"error": "Gym ID and styles are required"}), 400
    _,ok,error = remove_training_styles(styles,gym_id)
    if ok:
        return jsonify({"message": f"Styles removed from user in a gym with ID {gym_id}"})
    return jsonify({"error": error}), 500

@app.route('/replicate', methods=['POST'])
@use_db_connection
def replicate_graph(driver=None):
    # Receive replicated graph data and store it in Neo4j.
    data = request.get_json()
    print(data)

    if not data or ("nodes" not in data and "relationships" not in data):
        return jsonify({"error": "Invalid graph data"}), 400

    try:
        with driver.session() as session:
            # Insert new nodes
            for node in data["nodes"]:
                print("Merging: ", node)
                session.execute_write(lambda tx: tx.run(
                    "MERGE (n {id: $id}) SET n += $properties, n.labels = $labels",
                    id=node["id"], properties=node["properties"], labels=node["labels"]
                ))

            # Insert new relationships
            for relationship in data["relationships"]:
                session.execute_write(lambda tx: tx.run(
                    """
                        MATCH (a {id: $start}), (b {id: $end})
                        MERGE (a)-[r:REL {id: $id}]->(b) 
                        SET r += $properties, r.type = $type
                        ,
                        id=relationship["id"], start=relationship["start"], end=relationship["end"],
                        properties=relationship["properties"], type=relationship["type"]
                    """
                ))

        return jsonify({"message": "Graph replicated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':

    print("Initiating node: ",chord.current_node.to_dict())
    threading.Thread(target=stabilize, daemon=True).start()
    threading.Thread(target=check_predecessor, daemon=True).start()
    threading.Thread(target=listen_for_chord_updates, daemon=True).start()
    threading.Thread(target=chord_logic.send_local_system_entities_copy, daemon=True).start()
    threading.Thread(target=chord_logic.announce_node_to_router, daemon=True).start()
    #threading.Thread(target=replicate_to_owners, daemon=True).start()
    

    app.run(
        host="0.0.0.0", 
        port=5000, 
        debug=True
    )