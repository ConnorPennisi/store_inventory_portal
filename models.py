from datetime import datetime


class User:
    def __init__(self, user_id, name, username, password, role):
        self.user_id = user_id
        self.name = name
        self.username = username
        self.password = password
        self.role = role

    def to_dict(self):
        return {
            "id": self.user_id,
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "role": self.role
        }

    def is_owner(self):
        return self.role == "owner"

    def is_employee(self):
        return self.role == "employee"


class InventoryItem:
    def __init__(
        self,
        item_id,
        name,
        category,
        price,
        stock,
        sold,
        low_stock_threshold,
        status,
        created_by
    ):
        self.item_id = item_id
        self.name = name
        self.category = category
        self.price = float(price)
        self.stock = int(stock)
        self.sold = int(sold)
        self.low_stock_threshold = int(low_stock_threshold)
        self.status = status
        self.created_by = created_by

    def to_dict(self):
        return {
            "id": self.item_id,
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
            "sold": self.sold,
            "low_stock_threshold": self.low_stock_threshold,
            "status": self.status,
            "created_by": self.created_by
        }

    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold

    def is_out_of_stock(self):
        return self.stock == 0

    def inventory_value(self):
        return round(self.price * self.stock, 2)


class Sale:
    def __init__(self, sale_id, items, total, sold_by, created_at=None):
        self.sale_id = sale_id
        self.items = items
        self.total = float(total)
        self.sold_by = sold_by
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.sale_id,
            "items": self.items,
            "total": round(self.total, 2),
            "sold_by": self.sold_by,
            "created_at": self.created_at
        }


class InventoryFlag:
    def __init__(
        self,
        flag_id,
        item_id,
        item_name,
        flagged_by,
        reason,
        urgency,
        status="open",
        created_at=None
    ):
        self.flag_id = flag_id
        self.item_id = item_id
        self.item_name = item_name
        self.flagged_by = flagged_by
        self.reason = reason
        self.urgency = urgency
        self.status = status
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "id": self.flag_id,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "flagged_by": self.flagged_by,
            "reason": self.reason,
            "urgency": self.urgency,
            "status": self.status,
            "created_at": self.created_at
        }