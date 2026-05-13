from data_access import load_users, save_users, get_next_id
from models import User
from registration_key_service import validate_registration_key, mark_registration_key_used

VALID_ROLES = ["owner", "employee"]


def find_user_by_username(username):
    users = load_users()

    for user in users:
        if user["username"].lower() == username.lower():
            return user

    return None


def validate_login(username, password):
    if not username.strip() or not password.strip():
        return False, None, "Username and password are required."

    user = find_user_by_username(username)

    if user is None:
        return False, None, "No account found with that username."

    if user["password"] != password:
        return False, None, "Incorrect password."

    return True, user, "Login successful."


def register_user(name, username, password, registration_key):
    users = load_users()

    if not name.strip():
        return False, None, "Name is required."

    if not username.strip():
        return False, None, "Username is required."

    if not password.strip():
        return False, None, "Password is required."

    existing_user = find_user_by_username(username)

    if existing_user:
        return False, None, "That username is already taken."

    key_valid, key_record, key_message = validate_registration_key(registration_key)

    if not key_valid:
        return False, None, key_message

    role = key_record["role"]

    new_user = User(
        user_id=get_next_id(users),
        name=name.strip(),
        username=username.strip(),
        password=password.strip(),
        role=role
    )

    new_user_dict = new_user.to_dict()

    users.append(new_user_dict)
    save_users(users)

    mark_registration_key_used(registration_key, username.strip())

    return True, new_user_dict, f"Account created successfully as {role}. You are now logged in."

def user_can_access_owner_pages(user):
    return user is not None and user.get("role") == "owner"


def user_can_access_employee_pages(user):
    return user is not None and user.get("role") == "employee"


def get_dashboard_for_role(user):
    if user is None:
        return "login"

    if user.get("role") == "owner":
        return "owner"

    if user.get("role") == "employee":
        return "employee"

    return "login"