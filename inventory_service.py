from datetime import datetime

from data_access import (
    load_inventory,
    save_inventory,
    load_sales,
    save_sales,
    load_flags,
    save_flags,
    get_next_id
)
from models import InventoryItem, Sale, InventoryFlag


def get_active_inventory():
    inventory = load_inventory()

    return [
        item for item in inventory
        if item.get("status", "active") == "active"
    ]


def get_all_inventory():
    return load_inventory()

def get_discontinued_inventory():
    inventory = load_inventory()

    return [
        item for item in inventory
        if item.get("status") == "discontinued"
    ]


def reactivate_product(item_id, stock):
    inventory = load_inventory()

    if int(stock) < 0:
        return False, "Stock cannot be negative."

    for item in inventory:
        if int(item["id"]) == int(item_id):
            item["status"] = "active"
            item["stock"] = int(stock)

            save_inventory(inventory)
            return True, f"{item['name']} has been reactivated."

    return False, "Product not found."

def find_item_by_id(item_id):
    inventory = load_inventory()

    for item in inventory:
        if int(item["id"]) == int(item_id):
            return item

    return None


def add_product(name, category, price, stock, low_stock_threshold, created_by):
    inventory = load_inventory()

    if not name.strip():
        return False, "Product name is required."

    if not category.strip():
        return False, "Category is required."

    if float(price) < 0:
        return False, "Price cannot be negative."

    if int(stock) < 0:
        return False, "Stock cannot be negative."

    if int(low_stock_threshold) < 1:
        return False, "Low-stock threshold must be at least 1."

    new_item = InventoryItem(
        item_id=get_next_id(inventory),
        name=name.strip(),
        category=category.strip(),
        price=float(price),
        stock=int(stock),
        sold=0,
        low_stock_threshold=int(low_stock_threshold),
        status="active",
        created_by=created_by
    )

    inventory.append(new_item.to_dict())
    save_inventory(inventory)

    return True, "Product added successfully."


def update_product(item_id, name, category, price, stock, low_stock_threshold):
    inventory = load_inventory()

    if not name.strip():
        return False, "Product name is required."

    if not category.strip():
        return False, "Category is required."

    if float(price) < 0:
        return False, "Price cannot be negative."

    if int(stock) < 0:
        return False, "Stock cannot be negative."

    if int(low_stock_threshold) < 1:
        return False, "Low-stock threshold must be at least 1."

    for item in inventory:
        if int(item["id"]) == int(item_id):
            item["name"] = name.strip()
            item["category"] = category.strip()
            item["price"] = float(price)
            item["stock"] = int(stock)
            item["low_stock_threshold"] = int(low_stock_threshold)

            save_inventory(inventory)
            return True, "Product updated successfully."

    return False, "Product not found."


def restock_product(item_id, units_added):
    inventory = load_inventory()

    if int(units_added) <= 0:
        return False, "Units added must be greater than zero."

    for item in inventory:
        if int(item["id"]) == int(item_id):
            item["stock"] = int(item["stock"]) + int(units_added)
            save_inventory(inventory)
            return True, f"{units_added} unit(s) added to {item['name']}."

    return False, "Product not found."


def delete_product(item_id):
    inventory = load_inventory()

    for item in inventory:
        if int(item["id"]) == int(item_id):
            item["status"] = "discontinued"
            save_inventory(inventory)
            return True, "Product marked as discontinued."

    return False, "Product not found."


def get_low_stock_items():
    inventory = get_active_inventory()

    return [
        item for item in inventory
        if int(item["stock"]) <= int(item["low_stock_threshold"])
    ]


def get_out_of_stock_items():
    inventory = get_active_inventory()

    return [
        item for item in inventory
        if int(item["stock"]) == 0
    ]


def get_inventory_value():
    inventory = get_active_inventory()

    return round(
        sum(float(item["price"]) * int(item["stock"]) for item in inventory),
        2
    )


def get_top_selling_items(limit=3):
    inventory = get_active_inventory()

    return sorted(
        inventory,
        key=lambda item: int(item.get("sold", 0)),
        reverse=True
    )[:limit]


def get_categories():
    inventory = get_active_inventory()

    categories = sorted(set(item["category"] for item in inventory))

    return categories


def search_inventory(
    search_text="",
    category_filter="All",
    stock_filter="All",
    sort_option="Name A-Z"
):
    inventory = get_active_inventory()

    filtered_items = inventory

    if category_filter != "All":
        filtered_items = [
            item for item in filtered_items
            if item["category"] == category_filter
        ]

    if stock_filter == "In Stock":
        filtered_items = [
            item for item in filtered_items
            if int(item["stock"]) > int(item["low_stock_threshold"])
        ]

    elif stock_filter == "Low Stock":
        filtered_items = [
            item for item in filtered_items
            if 0 < int(item["stock"]) <= int(item["low_stock_threshold"])
        ]

    elif stock_filter == "Out of Stock":
        filtered_items = [
            item for item in filtered_items
            if int(item["stock"]) == 0
        ]

    if search_text.strip():
        filtered_items = [
            item for item in filtered_items
            if search_text.lower() in item["name"].lower()
            or search_text.lower() in item["category"].lower()
        ]

    if sort_option == "Name A-Z":
        filtered_items = sorted(filtered_items, key=lambda item: item["name"].lower())

    elif sort_option == "Name Z-A":
        filtered_items = sorted(filtered_items, key=lambda item: item["name"].lower(), reverse=True)

    elif sort_option == "Stock Low to High":
        filtered_items = sorted(filtered_items, key=lambda item: int(item["stock"]))

    elif sort_option == "Stock High to Low":
        filtered_items = sorted(filtered_items, key=lambda item: int(item["stock"]), reverse=True)

    elif sort_option == "Price Low to High":
        filtered_items = sorted(filtered_items, key=lambda item: float(item["price"]))

    elif sort_option == "Price High to Low":
        filtered_items = sorted(filtered_items, key=lambda item: float(item["price"]), reverse=True)

    elif sort_option == "Units Sold High to Low":
        filtered_items = sorted(filtered_items, key=lambda item: int(item.get("sold", 0)), reverse=True)

    elif sort_option == "Category A-Z":
        filtered_items = sorted(filtered_items, key=lambda item: item["category"].lower())

    return filtered_items

def build_cart_item(item_id, quantity):
    item = find_item_by_id(item_id)

    if item is None:
        return False, None, "Product not found."

    if item.get("status", "active") != "active":
        return False, None, "This product is not active."

    if int(quantity) <= 0:
        return False, None, "Quantity must be greater than zero."

    if int(quantity) > int(item["stock"]):
        return False, None, "Quantity cannot be greater than current stock."

    cart_item = {
        "item_id": int(item["id"]),
        "name": item["name"],
        "quantity": int(quantity),
        "unit_price": float(item["price"]),
        "line_total": round(float(item["price"]) * int(quantity), 2)
    }

    return True, cart_item, "Item added to cart."


def submit_cart_sale(cart_items, sold_by):
    if not cart_items:
        return False, "Cart is empty."

    inventory = load_inventory()
    sales = load_sales()

    for cart_item in cart_items:
        matching_item = None

        for item in inventory:
            if int(item["id"]) == int(cart_item["item_id"]):
                matching_item = item
                break

        if matching_item is None:
            return False, f"{cart_item['name']} was not found."

        if matching_item.get("status", "active") != "active":
            return False, f"{cart_item['name']} is discontinued."

        if int(cart_item["quantity"]) > int(matching_item["stock"]):
            return False, f"Not enough stock for {cart_item['name']}."

    for cart_item in cart_items:
        for item in inventory:
            if int(item["id"]) == int(cart_item["item_id"]):
                item["stock"] = int(item["stock"]) - int(cart_item["quantity"])
                item["sold"] = int(item.get("sold", 0)) + int(cart_item["quantity"])

    sale_total = round(
        sum(float(item["line_total"]) for item in cart_items),
        2
    )

    new_sale = Sale(
        sale_id=get_next_id(sales),
        items=cart_items,
        total=sale_total,
        sold_by=sold_by,
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    sales.append(new_sale.to_dict())

    save_inventory(inventory)
    save_sales(sales)

    return True, "Sale submitted successfully."


def get_sales():
    return load_sales()


def get_recent_sales(limit=5):
    sales = load_sales()

    return list(reversed(sales))[:limit]

def get_sales_by_user(username):
    sales = load_sales()

    return [
        sale for sale in sales
        if sale.get("sold_by") == username
    ]


def get_recent_sales_by_user(username, limit=5):
    user_sales = get_sales_by_user(username)

    return list(reversed(user_sales))[:limit]


def get_sales_summary_by_user(username):
    user_sales = get_sales_by_user(username)

    total_revenue = sum(float(sale.get("total", 0)) for sale in user_sales)

    total_units = 0

    for sale in user_sales:
        for item in sale.get("items", []):
            total_units += int(item.get("quantity", 0))

    average_sale_value = 0

    if user_sales:
        average_sale_value = total_revenue / len(user_sales)

    return {
        "sales_count": len(user_sales),
        "total_revenue": round(total_revenue, 2),
        "total_units": total_units,
        "average_sale_value": round(average_sale_value, 2)
    }


def get_store_sales_summary():
    sales = load_sales()

    total_revenue = sum(float(sale.get("total", 0)) for sale in sales)

    total_units = 0

    for sale in sales:
        for item in sale.get("items", []):
            total_units += int(item.get("quantity", 0))

    average_sale_value = 0

    if sales:
        average_sale_value = total_revenue / len(sales)

    sales_by_employee = {}

    for sale in sales:
        employee = sale.get("sold_by", "unknown")

        if employee not in sales_by_employee:
            sales_by_employee[employee] = {
                "sales_count": 0,
                "total_revenue": 0,
                "total_units": 0
            }

        sales_by_employee[employee]["sales_count"] += 1
        sales_by_employee[employee]["total_revenue"] += float(sale.get("total", 0))

        for item in sale.get("items", []):
            sales_by_employee[employee]["total_units"] += int(item.get("quantity", 0))

    for employee in sales_by_employee:
        sales_by_employee[employee]["total_revenue"] = round(
            sales_by_employee[employee]["total_revenue"],
            2
        )

    return {
        "sales_count": len(sales),
        "total_revenue": round(total_revenue, 2),
        "total_units": total_units,
        "average_sale_value": round(average_sale_value, 2),
        "sales_by_employee": sales_by_employee
    }

def submit_inventory_flag(item_id, flagged_by, reason, urgency):
    flags = load_flags()
    item = find_item_by_id(item_id)

    if item is None:
        return False, "Product not found."

    if not reason.strip():
        return False, "Flag reason is required."

    if urgency not in ["Low", "Medium", "High"]:
        return False, "Invalid urgency level."

    new_flag = InventoryFlag(
        flag_id=get_next_id(flags),
        item_id=int(item["id"]),
        item_name=item["name"],
        flagged_by=flagged_by,
        reason=reason.strip(),
        urgency=urgency,
        status="open",
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    flags.append(new_flag.to_dict())
    save_flags(flags)

    return True, "Inventory flag submitted successfully."


def get_flags():
    return load_flags()

def filter_flags(status_filter="All", urgency_filter="All", submitted_by_filter="All", sort_option="Newest First"):
    flags = load_flags()

    filtered_flags = flags

    if status_filter != "All":
        filtered_flags = [
            flag for flag in filtered_flags
            if flag.get("status", "open") == status_filter
        ]

    if urgency_filter != "All":
        filtered_flags = [
            flag for flag in filtered_flags
            if flag.get("urgency") == urgency_filter
        ]

    if submitted_by_filter != "All":
        filtered_flags = [
            flag for flag in filtered_flags
            if flag.get("flagged_by") == submitted_by_filter
        ]

    urgency_rank = {
        "High": 3,
        "Medium": 2,
        "Low": 1
    }

    if sort_option == "Newest First":
        filtered_flags = sorted(
            filtered_flags,
            key=lambda flag: flag.get("created_at", ""),
            reverse=True
        )

    elif sort_option == "Oldest First":
        filtered_flags = sorted(
            filtered_flags,
            key=lambda flag: flag.get("created_at", "")
        )

    elif sort_option == "Urgency High to Low":
        filtered_flags = sorted(
            filtered_flags,
            key=lambda flag: urgency_rank.get(flag.get("urgency"), 0),
            reverse=True
        )

    return filtered_flags


def get_flag_submitters():
    flags = load_flags()

    submitters = sorted(set(flag.get("flagged_by", "Unknown") for flag in flags))

    return submitters

def resolve_flag(flag_id, resolved_by, resolution_note):
    flags = load_flags()

    if not resolution_note.strip():
        return False, "Resolution note is required."

    for flag in flags:
        if int(flag["id"]) == int(flag_id):
            flag["status"] = "resolved"
            flag["resolved_by"] = resolved_by
            flag["resolved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            flag["resolution_note"] = resolution_note.strip()

            save_flags(flags)
            return True, "Flag marked as resolved."

    return False, "Flag not found."

def get_open_flags():
    flags = load_flags()

    return [
        flag for flag in flags
        if flag.get("status", "open") == "open"
    ]


def get_inventory_summary():
    inventory = get_active_inventory()
    sales = get_sales()
    low_stock = get_low_stock_items()
    out_of_stock = get_out_of_stock_items()
    open_flags = get_open_flags()

    total_units = sum(int(item["stock"]) for item in inventory)
    inventory_value = get_inventory_value()
    total_sales_value = sum(float(sale.get("total", 0)) for sale in sales)

    return {
        "total_products": len(inventory),
        "total_units": total_units,
        "low_stock_count": len(low_stock),
        "out_of_stock_count": len(out_of_stock),
        "inventory_value": inventory_value,
        "sales_count": len(sales),
        "total_sales_value": round(total_sales_value, 2),
        "open_flags_count": len(open_flags)
    }