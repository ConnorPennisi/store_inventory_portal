import random
import string
from datetime import datetime

from data_access import (
    load_registration_keys,
    save_registration_keys,
    get_next_id
)


VALID_KEY_ROLES = ["owner", "employee"]


def generate_random_key(role):
    prefix = role[:3].upper()
    random_part = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=8)
    )

    return f"{prefix}-{random_part}"


def generate_registration_key(role, created_by):
    if role not in VALID_KEY_ROLES:
        return False, None, "Invalid role for registration key."

    keys = load_registration_keys()

    new_key = {
        "id": get_next_id(keys),
        "key": generate_random_key(role),
        "role": role,
        "created_by": created_by,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "used": False,
        "used_by": None,
        "used_at": None
    }

    keys.append(new_key)
    save_registration_keys(keys)

    return True, new_key, "Registration key created successfully."


def get_registration_keys():
    return load_registration_keys()


def get_unused_registration_keys():
    keys = load_registration_keys()

    return [
        key for key in keys
        if key.get("used") is False
    ]


def validate_registration_key(key_value):
    keys = load_registration_keys()

    if not key_value.strip():
        return False, None, "Registration key is required."

    for key_record in keys:
        if key_record["key"] == key_value.strip():
            if key_record.get("used") is True:
                return False, None, "This registration key has already been used."

            return True, key_record, "Registration key is valid."

    return False, None, "Invalid registration key."


def mark_registration_key_used(key_value, used_by):
    keys = load_registration_keys()

    for key_record in keys:
        if key_record["key"] == key_value.strip():
            key_record["used"] = True
            key_record["used_by"] = used_by
            key_record["used_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            save_registration_keys(keys)
            return True, "Registration key marked as used."

    return False, "Registration key not found."