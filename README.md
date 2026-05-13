# Store Inventory Portal

Store Inventory Portal is a Streamlit-based inventory management web application for a small retail shop. The app helps store owners and employees manage inventory, track sales, flag stock issues, and use an AI assistant for inventory and business questions.

This project was built for MISY350 as a two-phase web application project.

## Project Purpose

Small retail stores need a simple way to track products, monitor low-stock items, record sales, and communicate inventory issues. Store Inventory Portal gives different users role-based access to the tools they need.

The app supports two main roles:

- **Owner**
- **Employee**

Each role has a different dashboard, navigation menu, and workflow.

---

## Test Accounts

Use these accounts to test the app immediately.

### Owner Account

- Username: `owner`
- Password: `owner123`

### Employee Account

- Username: `employee`
- Password: `employee123`

Additional sample accounts may also exist in `data/users.json`.

---

## User Roles

## Owner

Owners can:

- View inventory health from a dashboard
- Search, filter, and sort the inventory catalog
- Add new products
- Reactivate discontinued products
- Update product details
- Restock products
- Discontinue products
- Review and resolve employee inventory flags
- Generate registration keys for new users
- View sales insights
- Use the AI assistant for business analysis

## Employee

Employees can:

- View their own dashboard
- Search, filter, and sort the product catalog
- Log multi-item sales using a shopping cart
- Submit inventory flags
- View their own recent sales
- Use the AI assistant for daily inventory questions

---

## Main Features

## Authentication

The app includes:

- Login
- Logout
- Registration
- Session state
- Role-based routing

After login, users are routed to the correct dashboard based on their role.

## Registration Key System

New users cannot freely choose their own role.

An owner must generate a registration key first. The new user enters that key during registration. The app then assigns the correct role based on the key.

Registration keys are stored in:

```text
data/registration_keys.json