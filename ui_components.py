import streamlit as st


def setup_page():
    st.set_page_config(
        page_title="Store Inventory Portal",
        page_icon="📦",
        layout="wide"
    )


def render_app_header():
    st.title("Store Inventory Portal")
    st.caption("A role-based inventory, sales, and business assistant system for small retail shops.")


def init_session_state():
    defaults = {
        "logged_in": False,
        "current_user": None,
        "role": None,
        "cart": [],
        "assistant_question": "",
        "chat_history": [],
        "flash_message": "",
        "flash_type": "info"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def set_flash(message, message_type="info"):
    st.session_state.flash_message = message
    st.session_state.flash_type = message_type


def show_flash():
    if not st.session_state.flash_message:
        return

    if st.session_state.flash_type == "success":
        st.success(st.session_state.flash_message)
    elif st.session_state.flash_type == "error":
        st.error(st.session_state.flash_message)
    elif st.session_state.flash_type == "warning":
        st.warning(st.session_state.flash_message)
    else:
        st.info(st.session_state.flash_message)

    st.session_state.flash_message = ""
    st.session_state.flash_type = "info"


def login_user_session(user):
    st.session_state.logged_in = True
    st.session_state.current_user = user
    st.session_state.role = user["role"]
    st.session_state.cart = []
    st.session_state.assistant_question = ""
    st.session_state.chat_history = []
    set_flash(f"Welcome, {user['name']}!", "success")


def logout_user_session():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.role = None
    st.session_state.cart = []
    st.session_state.assistant_question = ""
    st.session_state.chat_history = []
    set_flash("You have been logged out.", "info")


def render_test_accounts_box():
    st.info(
        """
        **Test Accounts**

        **Shop Owner**
        - Username: `owner`
        - Password: `owner123`

        **Employee**
        - Username: `employee`
        - Password: `employee123`

        New users must use an owner-generated registration key.
        """
    )

def render_user_sidebar():
    user = st.session_state.current_user

    with st.sidebar:
        st.subheader("User")
        st.write(f"**Name:** {user['name']}")
        st.write(f"**Role:** {user['role'].title()}")

        if st.button("Log Out", use_container_width=True):
            logout_user_session()
            st.rerun()


def owner_navigation():
    with st.sidebar:
        st.divider()
        st.subheader("Owner Navigation")

        return st.radio(
            "Choose a page",
            [
                "Dashboard",
                "Sales Insights",
                "Inventory Catalog",
                "Add / Reactivate Product",
                "Update / Restock Product",
                "Discontinue Product",
                "Employee Flags",
                "Registration Keys",
                "AI Assistant"
            ],
            label_visibility="collapsed"
        )

def employee_navigation():
    with st.sidebar:
        st.divider()
        st.subheader("Employee Navigation")

        return st.radio(
            "Choose a page",
            [
                "Dashboard",
                "Product Catalog",
                "Log Sale",
                "Submit Inventory Flag",
                "AI Assistant"
            ],
            label_visibility="collapsed"
        )

def render_metric_row(metrics):
    columns = st.columns(len(metrics))

    for column, metric in zip(columns, metrics):
        label = metric.get("label", "")
        value = metric.get("value", "")
        delta = metric.get("delta", None)

        column.metric(label, value, delta=delta)


def render_inventory_status_badge(item):
    stock = int(item["stock"])
    threshold = int(item["low_stock_threshold"])

    if stock == 0:
        st.error("Out of Stock")
    elif stock <= threshold:
        st.warning("Low Stock")
    else:
        st.success("In Stock")


def render_inventory_card(item):
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
            st.write(f"**{item['name']}**")
            st.caption(item["category"])

        with col2:
            st.write(f"Price: **${float(item['price']):.2f}**")
            st.write(f"Sold: **{int(item.get('sold', 0))}**")

        with col3:
            st.write(f"Stock: **{int(item['stock'])}**")
            st.write(f"Threshold: **{int(item['low_stock_threshold'])}**")

        with col4:
            render_inventory_status_badge(item)


def render_sale_card(sale):
    with st.container(border=True):
        st.write(f"**Sale #{sale['id']}**")
        st.caption(f"Sold by {sale['sold_by']} on {sale['created_at']}")

        for item in sale["items"]:
            st.write(
                f"- {item['name']}: {item['quantity']} × ${float(item['unit_price']):.2f} "
                f"= ${float(item['line_total']):.2f}"
            )

        st.write(f"**Total:** ${float(sale['total']):.2f}")


def render_flag_card(flag, show_status=True):
    with st.container(border=True):
        st.write(f"**{flag['item_name']}**")
        st.write(f"Reason: {flag['reason']}")
        st.write(f"Urgency: **{flag['urgency']}**")

        if show_status:
            status = flag.get("status", "open")

            if status == "resolved":
                st.success("Status: Resolved")
            else:
                st.warning("Status: Open")

        st.caption(f"Submitted by {flag['flagged_by']} on {flag['created_at']}")

        if flag.get("status") == "resolved":
            st.divider()
            st.write("**Resolution Details**")
            st.write(f"Resolved by: **{flag.get('resolved_by', 'Unknown')}**")
            st.write(f"Resolved at: **{flag.get('resolved_at', 'Unknown')}**")
            st.write(f"Resolution note: {flag.get('resolution_note', 'No note provided.')}")

def render_page_section(title, description=None):
    st.header(title)

    if description:
        st.caption(description)

    st.divider()