import json
from pathlib import Path


DATA_DIR = Path("data")

USERS_FILE = DATA_DIR / "users.json"
INVENTORY_FILE = DATA_DIR / "inventory.json"
SALES_FILE = DATA_DIR / "sales.json"
FLAGS_FILE = DATA_DIR / "flags.json"
REGISTRATION_KEYS_FILE = DATA_DIR / "registration_keys.json"

DEFAULT_USERS = [
    {
        "id": 1,
        "name": "Owner Demo",
        "username": "owner",
        "password": "owner123",
        "role": "owner"
    },
    {
        "id": 2,
        "name": "Employee Demo",
        "username": "employee",
        "password": "employee123",
        "role": "employee"
    }
]


DEFAULT_INVENTORY = [
    {
        "id": 1,
        "name": "Hammer",
        "category": "Tools",
        "price": 12.99,
        "stock": 20,
        "sold": 4,
        "low_stock_threshold": 5,
        "status": "active",
        "created_by": "owner"
    },
    {
        "id": 2,
        "name": "Screwdriver Set",
        "category": "Tools",
        "price": 18.5,
        "stock": 8,
        "sold": 2,
        "low_stock_threshold": 5,
        "status": "active",
        "created_by": "owner"
    },
    {
        "id": 3,
        "name": "Drill Bits Pack",
        "category": "Hardware",
        "price": 9.99,
        "stock": 4,
        "sold": 6,
        "low_stock_threshold": 5,
        "status": "active",
        "created_by": "owner"
    },
    {
        "id": 4,
        "name": "Work Gloves",
        "category": "Safety",
        "price": 7.49,
        "stock": 3,
        "sold": 10,
        "low_stock_threshold": 6,
        "status": "active",
        "created_by": "owner"
    },
    {
        "id": 5,
        "name": "Tape Measure",
        "category": "Tools",
        "price": 11.25,
        "stock": 15,
        "sold": 3,
        "low_stock_threshold": 5,
        "status": "active",
        "created_by": "owner"
    }
]


DEFAULT_SALES = [
    {
        "id": 1,
        "items": [
            {
                "item_id": 1,
                "name": "Hammer",
                "quantity": 2,
                "unit_price": 12.99,
                "line_total": 25.98
            }
        ],
        "total": 25.98,
        "sold_by": "employee",
        "created_at": "2026-05-01 10:30:00"
    },
    {
        "id": 2,
        "items": [
            {
                "item_id": 3,
                "name": "Drill Bits Pack",
                "quantity": 1,
                "unit_price": 9.99,
                "line_total": 9.99
            },
            {
                "item_id": 4,
                "name": "Work Gloves",
                "quantity": 2,
                "unit_price": 7.49,
                "line_total": 14.98
            }
        ],
        "total": 24.97,
        "sold_by": "employee",
        "created_at": "2026-05-02 14:15:00"
    }
]


DEFAULT_FLAGS = [
    {
        "id": 1,
        "item_id": 3,
        "item_name": "Drill Bits Pack",
        "flagged_by": "employee",
        "reason": "This item is below the low-stock threshold and should be restocked soon.",
        "urgency": "Medium",
        "status": "open",
        "created_at": "2026-05-03 09:20:00"
    }
]


def ensure_data_files():
    DATA_DIR.mkdir(exist_ok=True)

    default_files = [
        (USERS_FILE, DEFAULT_USERS),
        (INVENTORY_FILE, DEFAULT_INVENTORY),
        (SALES_FILE, DEFAULT_SALES),
        (FLAGS_FILE, DEFAULT_FLAGS),
        (REGISTRATION_KEYS_FILE, [])
    ]

    for file_path, default_data in default_files:
        if not file_path.exists():
            save_json(file_path, default_data)


def load_json(file_path):
    ensure_parent_folder(file_path)

    if not file_path.exists():
        save_json(file_path, [])

    with open(file_path, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def save_json(file_path, data):
    ensure_parent_folder(file_path)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def ensure_parent_folder(file_path):
    file_path.parent.mkdir(parents=True, exist_ok=True)


def get_next_id(records):
    if not records:
        return 1

    return max(record.get("id", 0) for record in records) + 1


def load_users():
    return load_json(USERS_FILE)


def save_users(users):
    save_json(USERS_FILE, users)


def load_inventory():
    return load_json(INVENTORY_FILE)


def save_inventory(inventory):
    save_json(INVENTORY_FILE, inventory)


def load_sales():
    return load_json(SALES_FILE)


def save_sales(sales):
    save_json(SALES_FILE, sales)


def load_flags():
    return load_json(FLAGS_FILE)


def save_flags(flags):
    save_json(FLAGS_FILE, flags)

def load_registration_keys():
    return load_json(REGISTRATION_KEYS_FILE)

def save_registration_keys(keys):
    save_json(REGISTRATION_KEYS_FILE, keys)