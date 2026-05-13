import streamlit as st

from data_access import ensure_data_files
from auth_service import validate_login, register_user
from registration_key_service import generate_registration_key, get_registration_keys

from inventory_service import (
    get_active_inventory,
    get_all_inventory,
    get_discontinued_inventory,
    get_inventory_summary,
    get_low_stock_items,
    get_out_of_stock_items,
    get_top_selling_items,
    get_categories,
    search_inventory,
    add_product,
    reactivate_product,
    update_product,
    restock_product,
    delete_product,
    build_cart_item,
    submit_cart_sale,
    get_recent_sales,
    get_recent_sales_by_user,
    get_sales,
    get_sales_summary_by_user,
    get_store_sales_summary,
    submit_inventory_flag,
    get_flags,
    filter_flags,
    get_flag_submitters,
    get_open_flags,
    resolve_flag
)

from ai_service import (
    OWNER_FAQ_QUESTIONS,
    EMPLOYEE_FAQ_QUESTIONS,
    answer_faq_question,
    generate_ai_response
)

from ui_components import (
    setup_page,
    render_app_header,
    init_session_state,
    set_flash,
    show_flash,
    login_user_session,
    render_test_accounts_box,
    render_user_sidebar,
    owner_navigation,
    employee_navigation,
    render_metric_row,
    render_inventory_card,
    render_sale_card,
    render_flag_card,
    render_page_section
)
setup_page()
ensure_data_files()
init_session_state()
render_app_header()


def render_login_page():
    show_flash()

    left_col, right_col = st.columns([1.1, 1])

    with left_col:
        st.header("Login or Register")
        st.caption("Use the test accounts below or create a new account.")

        render_test_accounts_box()

    with right_col:
        tab_login, tab_register = st.tabs(["Login", "Register"])

        with tab_login:
            with st.form("login_form"):
                st.subheader("Login")

                login_username = st.text_input("Username", key="login_username")
                login_password = st.text_input("Password", type="password", key="login_password")

                login_submitted = st.form_submit_button("Log In", use_container_width=True)

                if login_submitted:
                    success, user, message = validate_login(login_username, login_password)

                    if success:
                        login_user_session(user)
                        st.rerun()
                    else:
                        set_flash(message, "error")
                        st.rerun()

        with tab_register:
            with st.form("register_form"):
                st.subheader("Register")

                register_name = st.text_input("Full Name", key="register_name")
                register_username = st.text_input("Create Username", key="register_username")
                register_password = st.text_input(
                    "Create Password",
                    type="password",
                    key="register_password"
                )
                registration_key = st.text_input(
                    "Registration Key",
                    key="registration_key",
                    help="Ask the shop owner for a registration key before creating an account."
                )
                register_submitted = st.form_submit_button(
                    "Create Account",
                    use_container_width=True
                )

                if register_submitted:
                    success, new_user, message = register_user(
                        register_name,
                        register_username,
                        register_password,
                        registration_key
                    )

                    if success:
                        login_user_session(new_user)
                        set_flash(message, "success")
                    else:
                        set_flash(message, "error")

                    st.rerun()

def render_owner_dashboard():
    render_page_section(
        "Owner Dashboard",
        "Quick status view of inventory health and issues that need attention today."
    )

    summary = get_inventory_summary()
    low_stock_items = get_low_stock_items()
    out_of_stock_items = get_out_of_stock_items()
    open_flags = get_open_flags()

    render_metric_row([
        {"label": "Active Products", "value": summary["total_products"]},
        {"label": "Inventory Value", "value": f"${summary['inventory_value']:,.2f}"},
        {"label": "Low Stock Items", "value": summary["low_stock_count"]},
        {"label": "Open Flags", "value": summary["open_flags_count"]}
    ])

    st.divider()

    with st.container(border=True):
        st.subheader("Owner Action Center")
        st.caption("Use this section to see what needs attention first.")

        tab1, tab2, tab3, tab4 = st.tabs([
            "Restock Priorities",
            "Out of Stock",
            "Open Flags",
            "Health Summary"
        ])

        with tab1:
            if low_stock_items:
                for item in low_stock_items:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 2])

                        with col1:
                            st.write(f"**{item['name']}**")
                            st.caption(item["category"])

                        with col2:
                            st.write(f"Stock: **{item['stock']}**")
                            st.write(f"Threshold: **{item['low_stock_threshold']}**")

                        with col3:
                            st.warning("Restock Needed")
            else:
                st.success("No products are below their low-stock threshold.")

        with tab2:
            if out_of_stock_items:
                for item in out_of_stock_items:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 2])

                        with col1:
                            st.write(f"**{item['name']}**")
                            st.caption(item["category"])

                        with col2:
                            st.write(f"Stock: **{item['stock']}**")
                            st.write(f"Threshold: **{item['low_stock_threshold']}**")

                        with col3:
                            st.error("Cannot Be Sold")
            else:
                st.success("No products are fully out of stock.")

        with tab3:
            if open_flags:
                for flag in open_flags[:5]:
                    render_flag_card(flag)
            else:
                st.success("No open employee flags.")

        with tab4:
            st.subheader("Inventory Health Summary")

            if not low_stock_items and not out_of_stock_items and not open_flags:
                st.success("Inventory is in good shape. No urgent issues need attention.")
            else:
                if out_of_stock_items:
                    st.error(f"{len(out_of_stock_items)} product(s) are out of stock.")

                    for item in out_of_stock_items[:3]:
                        st.write(f"- **{item['name']}** cannot be sold until restocked.")

                if low_stock_items:
                    st.warning(
                        f"{len(low_stock_items)} product(s) are at or below their low-stock threshold."
                    )

                    lowest_stock_item = sorted(
                        low_stock_items,
                        key=lambda item: int(item["stock"])
                    )[0]

                    st.write(
                        f"Top restock concern: **{lowest_stock_item['name']}** "
                        f"with only **{lowest_stock_item['stock']}** unit(s) left."
                    )

                if open_flags:
                    st.info(f"{len(open_flags)} employee flag(s) are still open.")

                    high_priority_flags = [
                        flag for flag in open_flags
                        if flag.get("urgency") == "High"
                    ]

                    if high_priority_flags:
                        st.write(f"High-priority flags: **{len(high_priority_flags)}**")

def render_owner_view_inventory():
    render_page_section(
        "Inventory Catalog",
        "Search, filter, sort, and review active store products."
    )

    categories = ["All"] + get_categories()

    stock_options = [
        "All",
        "In Stock",
        "Low Stock",
        "Out of Stock"
    ]

    sort_options = [
        "Name A-Z",
        "Name Z-A",
        "Stock Low to High",
        "Stock High to Low",
        "Price Low to High",
        "Price High to Low",
        "Units Sold High to Low",
        "Category A-Z"
    ]

    with st.container(border=True):
        st.subheader("Inventory Filters")

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])

        with col1:
            search_text = st.text_input(
                "Search",
                placeholder="Search by item name or category...",
                key="owner_inventory_search"
            )

        with col2:
            category_filter = st.selectbox(
                "Category",
                categories,
                key="owner_inventory_category"
            )

        with col3:
            stock_filter = st.selectbox(
                "Stock Status",
                stock_options,
                key="owner_inventory_stock_status"
            )

        with col4:
            sort_option = st.selectbox(
                "Sort By",
                sort_options,
                key="owner_inventory_sort"
            )

    filtered_items = search_inventory(
        search_text=search_text,
        category_filter=category_filter,
        stock_filter=stock_filter,
        sort_option=sort_option
    )

    st.caption(f"Showing {len(filtered_items)} matching product(s).")

    if not filtered_items:
        st.info("No matching inventory items found.")
        return

    for item in filtered_items:
        render_inventory_card(item)

def render_owner_add_product():
    render_page_section(
        "Add / Reactivate Product",
        "Create a new product or bring back a discontinued product."
    )

    tab1, tab2 = st.tabs(["Add New Product", "Reactivate Discontinued Product"])

    with tab1:
        with st.form("owner_add_product_form"):
            st.subheader("Add New Product")

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Product Name")
                category = st.text_input("Category")

            with col2:
                price = st.number_input("Price", min_value=0.0, step=0.50)
                stock = st.number_input("Starting Stock", min_value=0, step=1)
                low_stock_threshold = st.number_input(
                    "Low-Stock Threshold",
                    min_value=1,
                    value=5,
                    step=1
                )

            submitted = st.form_submit_button("Add Product", use_container_width=True)

            if submitted:
                success, message = add_product(
                    name=name,
                    category=category,
                    price=price,
                    stock=stock,
                    low_stock_threshold=low_stock_threshold,
                    created_by=st.session_state.current_user["username"]
                )

                set_flash(message, "success" if success else "error")
                st.rerun()

    with tab2:
        st.subheader("Reactivate Discontinued Product")

        discontinued_items = get_discontinued_inventory()

        if not discontinued_items:
            st.info("No discontinued products are available to reactivate.")
            return

        item_options = {
            f"{item['id']} | {item['name']} | {item['category']}": item
            for item in discontinued_items
        }

        selected_label = st.selectbox(
            "Select Discontinued Product",
            list(item_options.keys())
        )

        selected_item = item_options[selected_label]

        with st.container(border=True):
            st.write(f"**{selected_item['name']}**")
            st.write(f"Category: {selected_item['category']}")
            st.write(f"Price: ${float(selected_item['price']):.2f}")
            st.write(f"Previous stock: {selected_item['stock']}")
            st.write(f"Sold before discontinuing: {selected_item.get('sold', 0)}")

        new_stock = st.number_input(
            "Stock to Restore With",
            min_value=0,
            value=max(0, int(selected_item.get("stock", 0))),
            step=1
        )

        if st.button("Reactivate Product", use_container_width=True):
            success, message = reactivate_product(
                selected_item["id"],
                new_stock
            )

            set_flash(message, "success" if success else "error")
            st.rerun()

def render_owner_update_restock():
    render_page_section(
        "Update / Restock",
        "Edit product details or quickly add received units to stock."
    )

    items = get_active_inventory()

    if not items:
        st.info("No active products available.")
        return

    item_options = {
        f"{item['id']} | {item['name']} | Stock: {item['stock']}": item
        for item in items
    }

    selected_label = st.selectbox("Select Product", list(item_options.keys()))
    selected_item = item_options[selected_label]

    st.subheader("Quick Restock")

    col1, col2 = st.columns([1, 1])

    with col1:
        units_added = st.number_input("Units Received", min_value=1, step=1)

    with col2:
        st.write("")
        st.write("")
        if st.button("Add Units to Stock", use_container_width=True):
            success, message = restock_product(selected_item["id"], units_added)
            set_flash(message, "success" if success else "error")
            st.rerun()

    st.divider()

    st.subheader("Edit Product Details")

    with st.form("owner_update_product_form"):
        col3, col4 = st.columns(2)

        with col3:
            name = st.text_input("Product Name", value=selected_item["name"])
            category = st.text_input("Category", value=selected_item["category"])

        with col4:
            price = st.number_input(
                "Price",
                min_value=0.0,
                value=float(selected_item["price"]),
                step=0.50
            )
            stock = st.number_input(
                "Stock",
                min_value=0,
                value=int(selected_item["stock"]),
                step=1
            )
            low_stock_threshold = st.number_input(
                "Low-Stock Threshold",
                min_value=1,
                value=int(selected_item["low_stock_threshold"]),
                step=1
            )

        submitted = st.form_submit_button("Save Product Changes", use_container_width=True)

        if submitted:
            success, message = update_product(
                item_id=selected_item["id"],
                name=name,
                category=category,
                price=price,
                stock=stock,
                low_stock_threshold=low_stock_threshold
            )

            set_flash(message, "success" if success else "error")
            st.rerun()


def render_owner_delete_product():
    render_page_section(
        "Delete Product",
        "Mark products as discontinued so they no longer appear in active inventory."
    )

    items = get_active_inventory()

    if not items:
        st.info("No active products available.")
        return

    item_options = {
        f"{item['id']} | {item['name']} | {item['category']}": item
        for item in items
    }

    selected_label = st.selectbox("Select Product to Delete", list(item_options.keys()))
    selected_item = item_options[selected_label]

    st.warning(
        f"You are about to discontinue **{selected_item['name']}**. "
        "It will be hidden from active inventory, but the record will remain in JSON."
    )

    confirm = st.checkbox("I understand this product will be marked as discontinued.")

    if st.button("Delete Product", use_container_width=True):
        if not confirm:
            set_flash("Check the confirmation box before deleting.", "error")
            st.rerun()

        success, message = delete_product(selected_item["id"])
        set_flash(message, "success" if success else "error")
        st.rerun()


def render_owner_employee_flags():
    render_page_section(
        "Employee Flags",
        "Review, filter, and resolve inventory issues submitted by employees."
    )

    submitters = ["All"] + get_flag_submitters()

    with st.container(border=True):
        st.subheader("Flag Filters")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status_filter = st.selectbox(
                "Status",
                ["All", "open", "resolved"],
                key="flag_status_filter"
            )

        with col2:
            urgency_filter = st.selectbox(
                "Urgency",
                ["All", "Low", "Medium", "High"],
                key="flag_urgency_filter"
            )

        with col3:
            submitted_by_filter = st.selectbox(
                "Submitted By",
                submitters,
                key="flag_submitter_filter"
            )

        with col4:
            sort_option = st.selectbox(
                "Sort By",
                ["Newest First", "Oldest First", "Urgency High to Low"],
                key="flag_sort_option"
            )

    filtered_flags = filter_flags(
        status_filter=status_filter,
        urgency_filter=urgency_filter,
        submitted_by_filter=submitted_by_filter,
        sort_option=sort_option
    )

    st.caption(f"Showing {len(filtered_flags)} matching flag(s).")

    if not filtered_flags:
        st.info("No flags match the selected filters.")
        return

    for flag in filtered_flags:
        render_flag_card(flag)

        if flag.get("status", "open") == "open":
            with st.expander(f"Resolve Flag #{flag['id']}"):
                resolution_note = st.text_area(
                    "Resolution Note",
                    placeholder="Example: Restocked item, corrected shelf count, or reviewed with employee.",
                    key=f"resolution_note_{flag['id']}"
                )

                if st.button(
                    f"Mark Flag #{flag['id']} as Resolved",
                    key=f"resolve_flag_{flag['id']}",
                    use_container_width=True
                ):
                    success, message = resolve_flag(
                        flag_id=flag["id"],
                        resolved_by=st.session_state.current_user["username"],
                        resolution_note=resolution_note
                    )

                    set_flash(message, "success" if success else "error")
                    st.rerun()

def add_cart_item_to_session(cart_item):
    for existing_item in st.session_state.cart:
        if int(existing_item["item_id"]) == int(cart_item["item_id"]):
            existing_item["quantity"] += int(cart_item["quantity"])
            existing_item["line_total"] = round(
                float(existing_item["unit_price"]) * int(existing_item["quantity"]),
                2
            )
            return

    st.session_state.cart.append(cart_item)


def get_quantity_already_in_cart(item_id):
    total = 0

    for cart_item in st.session_state.cart:
        if int(cart_item["item_id"]) == int(item_id):
            total += int(cart_item["quantity"])

    return total


def render_employee_dashboard():
    render_page_section(
        "Employee Dashboard",
        "Your personal sales activity and current inventory alerts."
    )

    username = st.session_state.current_user["username"]

    summary = get_inventory_summary()
    my_sales_summary = get_sales_summary_by_user(username)
    low_stock_items = get_low_stock_items()
    out_of_stock_items = get_out_of_stock_items()
    my_recent_sales = get_recent_sales_by_user(username, limit=5)

    render_metric_row([
        {"label": "My Sales Logged", "value": my_sales_summary["sales_count"]},
        {"label": "My Revenue Logged", "value": f"${my_sales_summary['total_revenue']:,.2f}"},
        {"label": "My Units Sold", "value": my_sales_summary["total_units"]},
        {"label": "My Average Sale", "value": f"${my_sales_summary['average_sale_value']:,.2f}"}
    ])

    st.divider()

    render_metric_row([
        {"label": "Catalog Products", "value": summary["total_products"]},
        {"label": "Low Stock Items", "value": len(low_stock_items)},
        {"label": "Out of Stock", "value": len(out_of_stock_items)},
        {"label": "Open Store Flags", "value": summary["open_flags_count"]}
    ])

    st.divider()

    with st.container(border=True):
        st.subheader("My Work Summary")

        tab1, tab2, tab3 = st.tabs(
            ["Low Stock Items", "My Recent Sales", "Out of Stock Items"]
        )

        with tab1:
            if low_stock_items:
                for item in low_stock_items:
                    with st.container(border=True):
                        st.write(f"**{item['name']}**")
                        st.write(f"Stock: {item['stock']} | Threshold: {item['low_stock_threshold']}")
                        st.caption("This product should be watched or flagged.")
            else:
                st.success("No low-stock items right now.")

        with tab2:
            if my_recent_sales:
                for sale in my_recent_sales:
                    render_sale_card(sale)
            else:
                st.info("You have not logged any sales yet.")

        with tab3:
            if out_of_stock_items:
                for item in out_of_stock_items:
                    with st.container(border=True):
                        st.write(f"**{item['name']}**")
                        st.write(f"Category: {item['category']}")
                        st.caption("This item cannot be sold until restocked.")
            else:
                st.success("No items are currently out of stock.")

def render_employee_catalog():
    render_page_section(
        "Product Catalog",
        "Search, filter, and sort available products."
    )

    categories = ["All"] + get_categories()

    stock_options = [
        "All",
        "In Stock",
        "Low Stock",
        "Out of Stock"
    ]

    sort_options = [
        "Name A-Z",
        "Stock Low to High",
        "Stock High to Low",
        "Price Low to High",
        "Price High to Low",
        "Units Sold High to Low",
        "Category A-Z"
    ]

    with st.container(border=True):
        st.subheader("Catalog Filters")

        col1, col2, col3, col4 = st.columns([2, 1, 1, 1.5])

        with col1:
            search_text = st.text_input(
                "Search",
                placeholder="Search by item name or category...",
                key="employee_catalog_search"
            )

        with col2:
            category_filter = st.selectbox(
                "Category",
                categories,
                key="employee_catalog_category"
            )

        with col3:
            stock_filter = st.selectbox(
                "Stock Status",
                stock_options,
                key="employee_catalog_stock_status"
            )

        with col4:
            sort_option = st.selectbox(
                "Sort By",
                sort_options,
                key="employee_catalog_sort"
            )

    filtered_items = search_inventory(
        search_text=search_text,
        category_filter=category_filter,
        stock_filter=stock_filter,
        sort_option=sort_option
    )

    st.caption(f"Showing {len(filtered_items)} matching product(s).")

    if not filtered_items:
        st.info("No matching products found.")
        return

    for item in filtered_items:
        render_inventory_card(item)

def render_employee_log_sale():
    render_page_section(
        "Log Sale",
        "Add multiple products to a shopping cart, then submit the full sale."
    )

    items = [
        item for item in get_active_inventory()
        if int(item["stock"]) > 0
    ]

    if not items:
        st.info("No products are currently available for sale.")
        return

    st.subheader("Add Item to Cart")

    item_options = {
        f"{item['id']} | {item['name']} | Stock: {item['stock']} | ${float(item['price']):.2f}": item
        for item in items
    }

    selected_label = st.selectbox("Choose Product", list(item_options.keys()))
    selected_item = item_options[selected_label]

    already_in_cart = get_quantity_already_in_cart(selected_item["id"])
    available_remaining = int(selected_item["stock"]) - already_in_cart

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.write(f"Selected: **{selected_item['name']}**")
        st.caption(f"{available_remaining} unit(s) still available after current cart quantity.")

    with col2:
        if available_remaining > 0:
            quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=available_remaining,
                step=1
            )
        else:
            quantity = 0
            st.number_input(
                "Quantity",
                min_value=0,
                max_value=0,
                value=0,
                disabled=True
            )

    with col3:
        st.write("")
        st.write("")
        add_clicked = st.button(
            "Add to Cart",
            use_container_width=True,
            disabled=available_remaining <= 0
        )

    if available_remaining <= 0:
        st.warning("All available stock for this item is already in the cart.")

    if add_clicked:
        success, cart_item, message = build_cart_item(selected_item["id"], quantity)

        if success:
            add_cart_item_to_session(cart_item)
            set_flash("Item added to cart.", "success")
        else:
            set_flash(message, "error")

        st.rerun()

    st.divider()

    st.subheader("Shopping Cart")

    if not st.session_state.cart:
        st.info("Cart is empty.")
        return

    cart_total = sum(float(item["line_total"]) for item in st.session_state.cart)
    cart_units = sum(int(item["quantity"]) for item in st.session_state.cart)

    render_metric_row([
        {"label": "Cart Items", "value": len(st.session_state.cart)},
        {"label": "Total Units", "value": cart_units},
        {"label": "Sale Total", "value": f"${cart_total:.2f}"}
    ])

    for index, cart_item in enumerate(st.session_state.cart):
        with st.container(border=True):
            col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])

            with col_a:
                st.write(f"**{cart_item['name']}**")
                st.caption(f"${float(cart_item['unit_price']):.2f} each")

            with col_b:
                st.write(f"Qty: **{cart_item['quantity']}**")

            with col_c:
                st.write(f"${float(cart_item['line_total']):.2f}")

            with col_d:
                if st.button("Remove", key=f"remove_cart_{index}", use_container_width=True):
                    st.session_state.cart.pop(index)
                    set_flash("Item removed from cart.", "success")
                    st.rerun()

    st.divider()

    col_submit, col_clear = st.columns(2)

    with col_submit:
        if st.button("Submit Full Sale", use_container_width=True):
            success, message = submit_cart_sale(
                st.session_state.cart,
                st.session_state.current_user["username"]
            )

            if success:
                st.session_state.cart = []

            set_flash(message, "success" if success else "error")
            st.rerun()

    with col_clear:
        if st.button("Clear Cart", use_container_width=True):
            st.session_state.cart = []
            set_flash("Cart cleared.", "info")
            st.rerun()


def render_employee_flag_inventory():
    render_page_section(
        "Flag Inventory Issue",
        "Submit a low-stock or inventory concern for the owner to review."
    )

    items = get_active_inventory()

    if not items:
        st.info("No active products available.")
        return

    item_options = {
        f"{item['id']} | {item['name']} | Stock: {item['stock']}": item
        for item in items
    }

    selected_label = st.selectbox("Select Product", list(item_options.keys()))
    selected_item = item_options[selected_label]

    st.subheader("Product Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current Stock", selected_item["stock"])

    with col2:
        st.metric("Low-Stock Threshold", selected_item["low_stock_threshold"])

    with col3:
        if int(selected_item["stock"]) == 0:
            st.error("Out of Stock")
        elif int(selected_item["stock"]) <= int(selected_item["low_stock_threshold"]):
            st.warning("Low Stock")
        else:
            st.success("In Stock")

    st.divider()

    st.subheader("Flag Details")

    issue_options = st.multiselect(
        "Select issue type",
        [
            "Low stock",
            "Out of stock",
            "Damaged item",
            "Wrong price",
            "Wrong category",
            "Customer requested item",
            "Needs manager review"
        ],
        default=[
            "Out of stock"
            if int(selected_item["stock"]) == 0
            else "Low stock"
            if int(selected_item["stock"]) <= int(selected_item["low_stock_threshold"])
            else "Needs manager review"
        ]
    )

    urgency = st.radio(
        "Urgency",
        ["Low", "Medium", "High"],
        horizontal=True,
        index=2 if int(selected_item["stock"]) == 0 else 1
    )

    generated_reason_parts = []

    generated_reason_parts.append(
        f"{selected_item['name']} currently has {selected_item['stock']} unit(s) in stock."
    )

    generated_reason_parts.append(
        f"The low-stock threshold is {selected_item['low_stock_threshold']}."
    )

    if issue_options:
        generated_reason_parts.append(
            "Issue type(s): " + ", ".join(issue_options) + "."
        )

    if int(selected_item["stock"]) == 0:
        generated_reason_parts.append(
            "This item is out of stock and should be restocked as soon as possible."
        )
    elif int(selected_item["stock"]) <= int(selected_item["low_stock_threshold"]):
        generated_reason_parts.append(
            "This item is at or below the low-stock threshold and should be reviewed."
        )
    else:
        generated_reason_parts.append(
            "This item is not currently below the stock threshold, but it may still need review."
        )

    generated_reason = " ".join(generated_reason_parts)

    reason = st.text_area(
        "Auto-Generated Reason",
        value=generated_reason,
        height=140,
        help="This updates based on the selected product and issue boxes. You can edit it before submitting."
    )

    if st.button("Submit Flag", use_container_width=True):
        success, message = submit_inventory_flag(
            item_id=selected_item["id"],
            flagged_by=st.session_state.current_user["username"],
            reason=reason,
            urgency=urgency
        )

        set_flash(message, "success" if success else "error")
        st.rerun()

def render_ai_assistant():
    render_page_section(
        "AI Assistant",
        "Use suggested questions or ask a business question about current inventory data."
    )

    if "clear_assistant_input" not in st.session_state:
        st.session_state.clear_assistant_input = False

    if st.session_state.clear_assistant_input:
        st.session_state.assistant_question = ""
        st.session_state.clear_assistant_input = False

    current_user = st.session_state.current_user
    role = st.session_state.role

    if role == "owner":
        suggested_questions = OWNER_FAQ_QUESTIONS
        st.caption("Owner mode: focused on sales, restocking, inventory risk, and business decisions.")
    else:
        suggested_questions = EMPLOYEE_FAQ_QUESTIONS
        st.caption("Employee mode: focused on daily sales, stock issues, and items that need attention.")

    st.subheader("Suggested Questions")
    st.caption("Click a question to paste it into the assistant box.")

    col1, col2 = st.columns(2)

    for index, question_text in enumerate(suggested_questions):
        target_col = col1 if index % 2 == 0 else col2

        with target_col:
            if st.button(question_text, key=f"role_faq_button_{role}_{index}", use_container_width=True):
                st.session_state.assistant_question = question_text
                st.rerun()

    st.divider()

    question = st.text_input(
        "Question",
        key="assistant_question",
        placeholder="Click a suggested question or type your own question..."
    )

    col_ask, col_faq, col_clear = st.columns(3)

    with col_ask:
        ask_ai_clicked = st.button("Ask AI Assistant", use_container_width=True)

    with col_faq:
        ask_faq_clicked = st.button("Use Built-In Mode", use_container_width=True)

    with col_clear:
        clear_clicked = st.button("Clear Chat", use_container_width=True)

    if clear_clicked:
        st.session_state.chat_history = []
        st.session_state.clear_assistant_input = True
        st.rerun()

    if ask_faq_clicked:
        if not question.strip():
            set_flash("Choose or type a question first.", "error")
            st.rerun()

        answer = answer_faq_question(question, current_user=current_user)

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

        st.rerun()

    if ask_ai_clicked:
        if not question.strip():
            set_flash("Choose or type a question first.", "error")
            st.rerun()

        success, answer = generate_ai_response(question)

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })

        if success:
            set_flash("AI response generated successfully.", "success")
        else:
            set_flash("AI fallback response used.", "warning")

        st.rerun()

    st.subheader("Conversation")

    if not st.session_state.chat_history:
        st.info("No assistant messages yet.")
        return

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

def render_owner_registration_keys():
    render_page_section(
        "Registration Keys",
        "Generate one-time keys for new users to register."
    )

    st.subheader("Create New Registration Key")

    with st.form("generate_key_form"):
        role = st.selectbox(
            "Role for New Account",
            ["employee", "owner"],
            help="The new user will automatically receive this role after using the key."
        )

        submitted = st.form_submit_button("Generate Key", use_container_width=True)

        if submitted:
            success, new_key, message = generate_registration_key(
                role=role,
                created_by=st.session_state.current_user["username"]
            )

            if success:
                set_flash(message, "success")
                st.code(new_key["key"])
                st.success("Copy this key and give it to the new user.")
            else:
                set_flash(message, "error")

            st.rerun()

    st.divider()

    st.subheader("Existing Registration Keys")

    keys = get_registration_keys()

    if not keys:
        st.info("No registration keys have been created yet.")
        return

    for key in reversed(keys):
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])

            with col1:
                st.code(key["key"])

            with col2:
                st.write(f"Role: **{key['role']}**")

            with col3:
                if key.get("used"):
                    st.error("Used")
                else:
                    st.success("Unused")

            with col4:
                st.caption(f"Created by {key['created_by']}")
                st.caption(f"Created at {key['created_at']}")

                if key.get("used"):
                    st.caption(f"Used by {key.get('used_by')}")
                    st.caption(f"Used at {key.get('used_at')}")

def render_owner_sales_insights():
    render_page_section(
        "Sales Insights",
        "Analyze store revenue, employee activity, and product performance."
    )

    sales_summary = get_store_sales_summary()
    recent_sales = get_recent_sales(limit=10)
    top_items = get_top_selling_items(limit=10)
    low_stock_items = get_low_stock_items()

    render_metric_row([
        {"label": "Total Revenue", "value": f"${sales_summary['total_revenue']:,.2f}"},
        {"label": "Sales Logged", "value": sales_summary["sales_count"]},
        {"label": "Units Sold", "value": sales_summary["total_units"]},
        {"label": "Average Sale", "value": f"${sales_summary['average_sale_value']:,.2f}"}
    ])

    st.divider()

    with st.container(border=True):
        st.subheader("Sales Detail View")

        tab1, tab2, tab3, tab4 = st.tabs([
            "Sales by Employee",
            "Top Products",
            "Recent Sales",
            "Slow Movers"
        ])

        with tab1:
            sales_by_employee = sales_summary["sales_by_employee"]

            if not sales_by_employee:
                st.info("No employee sales data available.")
            else:
                for employee, data in sales_by_employee.items():
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.write(f"**{employee}**")

                        with col2:
                            st.write(f"Sales: **{data['sales_count']}**")

                        with col3:
                            st.write(f"Units: **{data['total_units']}**")

                        with col4:
                            st.write(f"Revenue: **${data['total_revenue']:,.2f}**")

        with tab2:
            if not top_items:
                st.info("No product sales data available.")
            else:
                for item in top_items:
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.write(f"**{item['name']}**")
                            st.caption(item["category"])

                        with col2:
                            st.write(f"Sold: **{item.get('sold', 0)}**")

                        with col3:
                            st.write(f"Stock: **{item['stock']}**")

                        with col4:
                            estimated_revenue = float(item["price"]) * int(item.get("sold", 0))
                            st.write(f"Est. Revenue: **${estimated_revenue:,.2f}**")

        with tab3:
            if not recent_sales:
                st.info("No recent sales found.")
            else:
                for sale in recent_sales:
                    render_sale_card(sale)

                with tab4:
                    active_inventory = get_active_inventory()

                    slow_movers = [
                        item for item in active_inventory
                        if int(item.get("sold", 0)) <= 8 and int(item["stock"]) >= 10
                    ]

                    slow_movers = sorted(
                        slow_movers,
                        key=lambda item: (int(item.get("sold", 0)), -int(item["stock"]))
                    )

                    if not slow_movers:
                        st.success("No clear slow-moving products found based on current sales and stock levels.")
                    else:
                        st.caption(
                            "These products have relatively low sales and higher stock. "
                            "They may be good candidates for discounts, promotions, or better shelf placement."
                        )

                        for item in slow_movers:
                            with st.container(border=True):
                                col1, col2, col3, col4 = st.columns(4)

                                with col1:
                                    st.write(f"**{item['name']}**")
                                    st.caption(item["category"])

                                with col2:
                                    st.write(f"Stock: **{item['stock']}**")

                                with col3:
                                    st.write(f"Sold: **{item.get('sold', 0)}**")

                                with col4:
                                    st.warning("Review for Discount")                            


def render_owner_app():
    render_user_sidebar()
    page = owner_navigation()
    show_flash()

    if page == "Dashboard":
        render_owner_dashboard()
    elif page == "Sales Insights":
        render_owner_sales_insights()
    elif page == "Inventory Catalog":
        render_owner_view_inventory()
    elif page == "Add / Reactivate Product":
        render_owner_add_product()
    elif page == "Update / Restock Product":
        render_owner_update_restock()
    elif page == "Discontinue Product":
        render_owner_delete_product()
    elif page == "Employee Flags":
        render_owner_employee_flags()
    elif page == "Registration Keys":
        render_owner_registration_keys()
    elif page == "AI Assistant":
        render_ai_assistant()

def render_employee_app():
    render_user_sidebar()
    page = employee_navigation()
    show_flash()

    if page == "Dashboard":
        render_employee_dashboard()
    elif page == "Product Catalog":
        render_employee_catalog()
    elif page == "Log Sale":
        render_employee_log_sale()
    elif page == "Submit Inventory Flag":
        render_employee_flag_inventory()
    elif page == "AI Assistant":
        render_ai_assistant()

def main():
    if not st.session_state.logged_in:
        render_login_page()
        return

    if st.session_state.role == "owner":
        render_owner_app()
    elif st.session_state.role == "employee":
        render_employee_app()
    else:
        set_flash("Invalid role. Please log in again.", "error")
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.role = None
        st.rerun()


main()