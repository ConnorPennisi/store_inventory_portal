import streamlit as st
from openai import OpenAI

from inventory_service import (
    get_active_inventory,
    get_low_stock_items,
    get_out_of_stock_items,
    get_top_selling_items,
    get_inventory_value,
    get_sales,
    get_open_flags,
    get_inventory_summary,
    get_sales_by_user,
    get_recent_sales_by_user,
    get_store_sales_summary
)


OWNER_FAQ_QUESTIONS = [
    "Which products should I restock first?",
    "Which products are selling well but running low?",
    "What products should I discount?",
    "Summarize the biggest inventory risks.",
    "Which employee has logged the most sales?"
]


EMPLOYEE_FAQ_QUESTIONS = [
    "What items are low on stock?",
    "What items are out of stock?",
    "What should I flag today?",
    "Which products can I still sell?",
    "What are my recent sales?"
]


FAQ_QUESTIONS = [
    "What items are low on stock?",
    "What items are out of stock?",
    "What are the top-selling products?",
    "What is the total inventory value?",
    "What should we restock first?"
]


def answer_faq_question(question, current_user=None):
    question = question.strip()

    if question == "What items are low on stock?":
        low_stock_items = get_low_stock_items()

        if not low_stock_items:
            return "No items are currently low on stock."

        response_lines = ["Low-stock items:"]
        for item in low_stock_items:
            response_lines.append(
                f"- {item['name']}: {item['stock']} in stock, threshold is {item['low_stock_threshold']}"
            )

        return "\n".join(response_lines)

    if question == "What items are out of stock?":
        out_of_stock_items = get_out_of_stock_items()

        if not out_of_stock_items:
            return "No items are currently out of stock."

        response_lines = ["Out-of-stock items:"]
        for item in out_of_stock_items:
            response_lines.append(f"- {item['name']}")

        return "\n".join(response_lines)

    if question == "What are the top-selling products?":
        top_items = get_top_selling_items(limit=3)

        if not top_items:
            return "There are no products available to rank."

        if sum(int(item.get("sold", 0)) for item in top_items) == 0:
            return "No products have been sold yet."

        response_lines = ["Top-selling products:"]
        for item in top_items:
            response_lines.append(
                f"- {item['name']}: {item.get('sold', 0)} units sold"
            )

        return "\n".join(response_lines)

    if question == "What is the total inventory value?":
        inventory_value = get_inventory_value()
        return f"The current total inventory value is ${inventory_value:,.2f}."

    if question == "What should we restock first?" or question == "Which products should I restock first?":
        low_stock_items = get_low_stock_items()

        if not low_stock_items:
            return "No restock is needed right now based on current low-stock thresholds."

        sorted_items = sorted(
            low_stock_items,
            key=lambda item: int(item["stock"])
        )

        response_lines = ["Restock these items first:"]
        for item in sorted_items:
            response_lines.append(
                f"- {item['name']}: only {item['stock']} left"
            )

        return "\n".join(response_lines)

    if question == "Which products are selling well but running low?":
        low_stock_items = get_low_stock_items()

        strong_candidates = [
            item for item in low_stock_items
            if int(item.get("sold", 0)) >= 10
        ]

        if not strong_candidates:
            return "No products currently match both conditions: strong sales and low stock."

        response_lines = ["Products selling well but running low:"]
        for item in strong_candidates:
            response_lines.append(
                f"- {item['name']}: {item.get('sold', 0)} sold, {item['stock']} in stock"
            )

        return "\n".join(response_lines)

    if question == "What products should I discount?":
        inventory = get_active_inventory()

        discount_candidates = [
            item for item in inventory
            if int(item.get("sold", 0)) <= 8 and int(item["stock"]) >= 10
        ]

        if not discount_candidates:
            return "No obvious discount candidates right now. Most products either have decent sales or limited stock."

        response_lines = ["Possible discount candidates:"]
        for item in discount_candidates:
            response_lines.append(
                f"- {item['name']}: {item.get('sold', 0)} sold, {item['stock']} in stock"
            )

        return "\n".join(response_lines)

    if question == "Summarize the biggest inventory risks.":
        low_stock_items = get_low_stock_items()
        out_of_stock_items = get_out_of_stock_items()
        open_flags = get_open_flags()

        response_lines = ["Biggest inventory risks:"]

        if out_of_stock_items:
            response_lines.append(f"- {len(out_of_stock_items)} item(s) are out of stock.")

        if low_stock_items:
            response_lines.append(f"- {len(low_stock_items)} item(s) are low on stock.")

        if open_flags:
            response_lines.append(f"- {len(open_flags)} employee flag(s) are still open.")

        if len(response_lines) == 1:
            return "No major inventory risks found right now."

        return "\n".join(response_lines)

    if question == "Which employee has logged the most sales?":
        sales_summary = get_store_sales_summary()
        sales_by_employee = sales_summary.get("sales_by_employee", {})

        if not sales_by_employee:
            return "No employee sales data is available yet."

        top_employee = max(
            sales_by_employee.items(),
            key=lambda item: item[1]["sales_count"]
        )

        username = top_employee[0]
        data = top_employee[1]

        return (
            f"{username} has logged the most sales with {data['sales_count']} sale(s), "
            f"{data['total_units']} unit(s) sold, and ${data['total_revenue']:,.2f} in revenue."
        )

    if question == "What should I flag today?":
        low_stock_items = get_low_stock_items()
        out_of_stock_items = get_out_of_stock_items()

        if not low_stock_items and not out_of_stock_items:
            return "Nothing needs to be flagged right now."

        response_lines = ["Items worth flagging today:"]

        for item in out_of_stock_items:
            response_lines.append(f"- {item['name']}: out of stock")

        for item in low_stock_items:
            if int(item["stock"]) > 0:
                response_lines.append(
                    f"- {item['name']}: low stock with {item['stock']} left"
                )

        return "\n".join(response_lines)

    if question == "Which products can I still sell?":
        inventory = get_active_inventory()

        sellable_items = [
            item for item in inventory
            if int(item["stock"]) > 0
        ]

        if not sellable_items:
            return "No products are currently available to sell."

        response_lines = ["Products currently available to sell:"]
        for item in sellable_items:
            response_lines.append(
                f"- {item['name']}: {item['stock']} available"
            )

        return "\n".join(response_lines)

    if question == "What are my recent sales?":
        if current_user is None:
            return "I cannot find your user session."

        username = current_user["username"]
        recent_sales = get_recent_sales_by_user(username, limit=5)

        if not recent_sales:
            return "You have not logged any sales yet."

        response_lines = [f"Recent sales for {username}:"]

        for sale in recent_sales:
            response_lines.append(
                f"- Sale #{sale['id']}: ${float(sale['total']):.2f} on {sale['created_at']}"
            )

        return "\n".join(response_lines)

    return "Please choose one of the suggested questions or ask a business question using the AI assistant."

def build_business_context():
    inventory = get_active_inventory()
    low_stock_items = get_low_stock_items()
    out_of_stock_items = get_out_of_stock_items()
    top_selling_items = get_top_selling_items(limit=5)
    sales = get_sales()
    open_flags = get_open_flags()
    summary = get_inventory_summary()

    context = {
        "summary": summary,
        "inventory": inventory,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock_items,
        "top_selling_items": top_selling_items,
        "sales": sales,
        "open_flags": open_flags
    }

    return context


def openai_key_available():
    try:
        return bool(st.secrets.get("OPENAI_API_KEY"))
    except Exception:
        return False


def generate_ai_response(user_question):
    if not user_question.strip():
        return False, "Please enter a question first."

    if not openai_key_available():
        fallback_answer = answer_faq_question(user_question)

        return (
            False,
            "OpenAI API key is not configured, so the app used the Phase 1 FAQ assistant instead.\n\n"
            + fallback_answer
        )

    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        business_context = build_business_context()

        system_prompt = """
You are a helpful business analyst for a small retail store inventory system.

Your job is to help the shop owner and employees understand inventory, sales, low-stock risks, and restocking priorities.

Use the provided business data only. Do not invent products, sales, prices, or inventory numbers.

Give clear, practical advice. Keep answers concise but useful.
"""

        user_prompt = f"""
Business data:
{business_context}

User question:
{user_question}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.3
        )

        answer = response.choices[0].message.content

        return True, answer

    except Exception as error:
        fallback_answer = answer_faq_question(user_question)

        return (
            False,
            f"The AI assistant could not connect successfully. Error: {error}\n\n"
            f"Fallback FAQ response:\n\n{fallback_answer}"
        )