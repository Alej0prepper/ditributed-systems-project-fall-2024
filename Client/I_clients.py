from client_methods import (
    register_user, update_user, delete_user, login, logout, create_post,
    repost, quote_post, delete_post, follow_user, unfollow_user, find_users,
    react_to_post, react_to_comment, comment_post, answer_comment, create_gym,
    login_gym, update_gym, get_gym_info, delete_gym, trains_in, add_training_styles
)

session_token = ""

def interactive_register_user():
    name = input("Enter name: ")
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    weight = input("Enter weight: ")
    styles = input("Enter styles (comma-separated): ")
    levels_by_style = input("Enter levels by style (comma-separated): ")
    response = register_user(name, username, email, password, weight, styles, levels_by_style)
    print(response.json())

def interactive_update_user():
    email = input("Enter email: ")
    name = input("Enter name: ")
    password = input("Enter password: ")
    weight = input("Enter weight: ")
    styles = input("Enter styles (comma-separated): ")
    levels_by_style = input("Enter levels by style (comma-separated): ")
    response = update_user(email, name, password, weight, styles, levels_by_style)
    print(response.json())

def interactive_delete_user():
    response = delete_user()
    print(response.json())

def interactive_login():
    username = input("Enter username (or leave blank): ")
    email = input("Enter email (or leave blank): ")
    password = input("Enter password: ")
    response = login(username, email, password)
    global session_token
    session_token = response["token"]
    print(response.json())

def interactive_logout():
    print(session_token)
    response = logout(session_token)
    print(response.json())

def interactive_create_post():
    media = input("Enter media: ")
    caption = input("Enter caption: ")
    response = create_post(media, caption)
    print(response.json())

def interactive_repost():
    reposted_post_id = input("Enter reposted post ID: ")
    response = repost(reposted_post_id)
    print(response.json())

def interactive_quote_post():
    quoted_post_id = input("Enter quoted post ID: ")
    media = input("Enter media: ")
    caption = input("Enter caption: ")
    response = quote_post(quoted_post_id, media, caption)
    print(response.json())

def interactive_delete_post():
    post_id = input("Enter post ID: ")
    response = delete_post(post_id)
    print(response.json())

def interactive_follow_user():
    followed_username = input("Enter username to follow: ")
    response = follow_user(followed_username)
    print(response.json())

def interactive_unfollow_user():
    followed_username = input("Enter username to unfollow: ")
    response = unfollow_user(followed_username)
    print(response.json())

def interactive_find_users():
    query = input("Enter search query: ")
    response = find_users(query)
    print(response.json())

def interactive_react_to_post():
    reaction = input("Enter reaction: ")
    post_id = input("Enter post ID: ")
    response = react_to_post(reaction, post_id)
    print(response.json())

def interactive_react_to_comment():
    reaction = input("Enter reaction: ")
    comment_id = input("Enter comment ID: ")
    response = react_to_comment(reaction, comment_id)
    print(response.json())

def interactive_comment_post():
    caption = input("Enter caption: ")
    media = input("Enter media: ")
    post_id = input("Enter post ID: ")
    response = comment_post(caption, media, post_id)
    print(response.json())

def interactive_answer_comment():
    caption = input("Enter caption: ")
    media = input("Enter media: ")
    comment_id = input("Enter comment ID: ")
    response = answer_comment(caption, media, comment_id)
    print(response.json())

def interactive_create_gym():
    name = input("Enter gym name: ")
    username = input("Enter gym username: ")
    email = input("Enter gym email: ")
    location = input("Enter gym location: ")
    address = input("Enter gym address: ")
    password = input("Enter gym password: ")
    styles = input("Enter gym styles (comma-separated): ")
    phone_number = input("Enter gym phone number (optional): ")
    ig_profile = input("Enter gym Instagram profile (optional): ")
    response = create_gym(name, username, email, location, address, password, styles, phone_number, ig_profile)
    print(response.json())

def interactive_login_gym():
    username = input("Enter gym username (or leave blank): ")
    email = input("Enter gym email (or leave blank): ")
    password = input("Enter gym password: ")
    response = login_gym(username, email, password)
    print(response.json())

def interactive_update_gym():
    name = input("Enter gym name: ")
    email = input("Enter gym email: ")
    location = input("Enter gym location: ")
    address = input("Enter gym address: ")
    styles = input("Enter gym styles (comma-separated): ")
    password = input("Enter gym password: ")
    phone_number = input("Enter gym phone number (optional): ")
    ig_profile = input("Enter gym Instagram profile (optional): ")
    response = update_gym(name, email, location, address, styles, password, phone_number, ig_profile)
    print(response.json())

def interactive_get_gym_info():
    gym_id = input("Enter gym ID: ")
    response = get_gym_info(gym_id)
    print(response.json())

def interactive_delete_gym():
    response = delete_gym()
    print(response.json())

def interactive_trains_in():
    gym_id = input("Enter gym ID: ")
    styles = input("Enter styles (comma-separated): ")
    response = trains_in(gym_id, styles)
    print(response.json())

def interactive_add_training_styles():
    styles = input("Enter styles (comma-separated): ")
    gym_id = input("Enter gym ID: ")
    response = add_training_styles(styles, gym_id)
    print(response.json())

def main_menu():
    options = [
        ("Register User", interactive_register_user),
        ("Update User", interactive_update_user),
        ("Delete User", interactive_delete_user),
        ("Login", interactive_login),
        ("Logout", interactive_logout),
        ("Create Post", interactive_create_post),
        ("Repost", interactive_repost),
        ("Quote Post", interactive_quote_post),
        ("Delete Post", interactive_delete_post),
        ("Follow User", interactive_follow_user),
        ("Unfollow User", interactive_unfollow_user),
        ("Find Users", interactive_find_users),
        ("React to Post", interactive_react_to_post),
        ("React to Comment", interactive_react_to_comment),
        ("Comment on Post", interactive_comment_post),
        ("Answer Comment", interactive_answer_comment),
        ("Create Gym", interactive_create_gym),
        ("Login Gym", interactive_login_gym),
        ("Update Gym", interactive_update_gym),
        ("Get Gym Info", interactive_get_gym_info),
        ("Delete Gym", interactive_delete_gym),
        ("Trains In", interactive_trains_in),
        ("Add Training Styles", interactive_add_training_styles),
    ]

    while True:
        print("\nSelect an option:")
        for i, (description, _) in enumerate(options, start=1):
            print(f"{i}. {description}")
        print("0. Exit")

        choice = input("Enter your choice: ")

        if choice.isdigit():
            choice = int(choice)
            if choice == 0:
                print("Exiting...")
                break
            elif 1 <= choice <= len(options):
                _, action = options[choice - 1]
                action()
            else:
                print("Invalid choice. Please try again.")
        else:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main_menu()