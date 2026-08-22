# 🐠 Bunny Mart – Aquarium E-Commerce Website

Bunny Mart is a web-based aquarium shopping and management system developed for selling aquarium fish, fish food, pets and aquarium accessories.

The system provides a customer side for browsing products, managing cart and wishlist, placing orders and making payments. It also provides an admin panel for managing products, categories, stock, customers, orders, payments and customer messages.

---

## 📌 Project Description

Bunny Mart provides an online platform where customers can view aquarium-related products, check their details and prices, add products to their cart or wishlist, and place orders.

The system also provides an administration panel through which the administrator can manage the main activities of the online store.

---

## 🎯 Objectives

- To provide an online platform for aquarium products.
- To allow customers to view available products and their details.
- To provide cart and wishlist functionality.
- To allow customers to place orders online.
- To provide COD and QR-based payment options.
- To allow customers to upload QR payment proof.
- To allow the administrator to verify payments.
- To provide product, category and stock management.
- To manage customer orders efficiently.
- To provide a centralized MySQL database for storing system information.

---

## 🛠️ Technologies Used

### Frontend
- HTML
- CSS
- Jinja2 Templates

### Backend
- Python
- Flask

### Database
- MySQL

### Python Libraries / Components
- Flask
- mysql.connector
- Werkzeug
- python-dotenv

### Development Tools
- Visual Studio Code
- MySQL Workbench

---

## 👥 System Modules

### 1. Customer Module

The customer module provides functionality for customers to:

- Register an account
- Login
- Logout
- Browse products
- View product details
- Add products to cart
- Update cart quantity
- Remove products from cart
- Add products to wishlist
- Manage wishlist
- Checkout
- Place orders
- Select payment method
- Use Cash on Delivery
- Use QR payment
- Upload payment proof
- View order confirmation
- View order information
- Send contact messages

---

### 2. Admin Module

The admin module provides functionality for the administrator to:

- Login to the admin panel
- View dashboard statistics
- Manage products
- Add products
- Edit products
- Delete products
- Manage categories
- Manage stock
- View customers
- View orders
- Update order status
- Manage payments
- Verify payment proofs
- Manage customer messages
- Reply to customer messages
- Upload/change the customer payment QR code

---

## 💳 Payment System

Bunny Mart provides two payment methods:

### Cash on Delivery (COD)

Customers can select COD during payment selection.

### QR Payment

Customers can select QR payment and:

1. Open the QR payment page.
2. Scan the payment QR code.
3. Complete the payment.
4. Upload the payment screenshot.
5. Wait for administrator verification.

The administrator can change the QR code from the admin panel.

Supported QR/payment proof image formats:

- PNG
- JPG
- JPEG
- WEBP

---

## 🗄️ Database

The project uses MySQL database.

Database name:

```text
bunny_mart

📦 Product Categories
The database contains the following product categories:
Aquarium Fish
Pets
Fish Food
Accessories

📊 Order Status
Orders can have the following statuses:
Pending
Confirmed
Processing
Shipped
Delivered
Cancelled

💰 Payment Status
Payments can have the following statuses:
Pending
Pending Verification
Paid
Failed

🐠 Payment QR Management
The administrator can upload and update the QR code used for customer payments.
The customer payment page displays the active QR code configured by the administrator.

🔐 Security
The project includes basic security mechanisms such as:
Password hashing using Werkzeug
Session-based authentication
Admin authentication protection
Customer authentication protection
Parameterized SQL queries
Secure filenames for uploaded images
File extension validation
Access control for customer orders
Protection of products linked to existing orders

🎨 User Interface
The Bunny Mart interface is designed around an aquarium theme.
The design includes:
Aquarium-inspired colors
Fish and water elements
Animated visual effects
Responsive layouts
Customer-friendly shopping pages
Dedicated admin dashboard
Creative payment interface
The frontend is implemented using HTML and CSS with Flask/Jinja2 templates.


Bunny Mart/
│
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── auth_utils.py
│   │
│   ├── blueprints/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   ├── wishlist.py
│   │   ├── orders.py
│   │   ├── payments.py
│   │   └── contact.py
│   │
│   ├── templates/
│   │   ├── customer/
│   │   └── admin/
│   │
│   └── static/
│
├── schema.sql
├── requirements.txt
├── run.py
├── seed_admin.py
├── .env
├── .env.example
└── README.md

🎯 Project Objectives
The main objectives of Bunny Mart are:
To develop an online aquarium and pet product shopping system.
To provide an easy-to-use customer shopping interface.
To provide a separate administrator management system.
To manage products, categories and stock efficiently.
To manage customer orders and payments.
To provide QR/UPI payment functionality.
To allow customers to upload payment proof.
To maintain customer and order information using MySQL.
To provide a simple and attractive aquarium-themed interface.


🔮 Future Scope
The project can be enhanced in the future by adding:
Online payment gateway integration
Email notifications
SMS notifications
Advanced product search
Product reviews and ratings
Delivery tracking
Sales reports
Inventory alerts
Advanced analytics
Mobile application


👨‍💻 Project
Project Name: Bunny Mart
Project Type: Web-Based E-Commerce Application
Domain: Aquarium & Pet Products
Backend: Python Flask
Database: MySQL

📄 License
This project is developed for educational and academic purposes.