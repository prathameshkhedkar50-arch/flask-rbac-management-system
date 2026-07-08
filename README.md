# RBAC Business Management System

A full-stack business management application that demonstrates the implementation of **Role-Based Access Control (RBAC)** using **Flask**, **PostgreSQL**, **TypeScript**, **Vite**, and **Tailwind CSS**.

The project provides a secure and modular platform where authenticated users can access business modules according to the permissions assigned to their roles. It showcases how authentication, authorization, and permission management can be integrated into a real-world business application.

> 🚧 **Project Status:** Work in Progress

---

# 🚀 Project Overview

This project is designed to demonstrate a complete RBAC implementation within a business management system.

Rather than allowing unrestricted access, every authenticated user can only perform actions that are permitted by their assigned role. The application validates permissions before allowing access to protected resources, ensuring secure and controlled business operations.

The system includes multiple business modules such as users, roles, permissions, products, customers, suppliers, and orders, making it a practical example of enterprise application architecture.

---
# ⚙️ Setup Utility

The project includes a setup script that automates the initial environment configuration, making it easier to run the application without manually installing every dependency or configuring the backend.

Depending on your operating system, simply execute the setup script to prepare the development environment.

---

## What the Setup Script Does

The setup utility performs the initial project configuration by:

- Creating a Python virtual environment (if it does not already exist)
- Installing the required Python packages
- Preparing the backend environment
- Installing frontend dependencies (if required)
- Verifying that required project files exist
- Configuring the application for local development
- Displaying useful startup information

This reduces the manual setup steps required before running the application.

---

## Running the Setup Script

### Windows

```bash
setup.bat
```

or

```bash
python setup.py
```

### Linux / macOS

```bash
python3 setup.py
```

---

## After Setup

Once the setup process completes successfully, start the backend server:

```bash
python run.py
```

Then start the frontend (from the dashboard directory):

```bash
npm install
npm run dev
```

Finally, open the application in your browser.

---

## Why Use the Setup Script?

Instead of manually creating virtual environments, installing dependencies, and configuring the project, the setup script automates the entire initialization process, helping developers get the application running more quickly and consistently.

# 🎯 Project Purpose

Modern business applications require different users to have different levels of access.

This project demonstrates how **Role-Based Access Control (RBAC)** can be integrated into a full-stack application to manage authentication, authorization, and permission-based access across multiple business modules.

Instead of granting every user full access, the application verifies user permissions before allowing operations such as viewing, creating, updating, or deleting records.

The project aims to demonstrate:

- Secure user authentication
- Role-based authorization
- Permission management
- Protected REST APIs
- Business module management
- Frontend and backend integration
- Scalable application architecture

---

# ✨ Features

## Authentication

- User login
- Token-based authentication
- Session validation

## Role-Based Access Control

- User management
- Role management
- Permission management
- CRUD permission control
- Authorization middleware
- Protected API endpoints

## Business Modules

- User Management
- Role Management
- Permission Management
- Product Management
- Customer Management
- Supplier Management
- Order Management

## Backend

- RESTful APIs
- SQLAlchemy ORM
- PostgreSQL integration
- Database seeding
- Modular architecture
- Error handling

## Frontend

- Responsive dashboard
- TypeScript application
- Tailwind CSS UI
- Axios API integration
- Permission-aware interface

---

# 🏗 System Architecture

```
                Frontend Dashboard
           (TypeScript + Tailwind CSS)
                        │
                        ▼
                  Axios API Calls
                        │
                        ▼
                  Flask REST API
                        │
                        ▼
               Authentication Layer
                        │
                        ▼
             Authorization Middleware
                        │
                        ▼
             Role & Permission Validation
                        │
                        ▼
                 PostgreSQL Database
```

---

# 🔐 RBAC Workflow

```
User
   │
   ▼
Login
   │
   ▼
Authentication
   │
   ▼
Assigned Role
   │
   ▼
Permission Validation
   │
   ▼
Authorized Business Module
```

Every protected endpoint verifies whether the authenticated user has the required permissions before executing the requested operation.

---

# 🛠 Technologies Used

## Backend

- Python
- Flask
- Flask SQLAlchemy
- Flask CORS
- PostgreSQL

## Frontend

- TypeScript
- Vite
- Tailwind CSS
- Axios

---

# 📂 Project Structure

```text
rbac-business-management-system/

backend/
│
├── app/
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── routes.py
│   ├── seed.py
│   └── __init__.py
│
└── run.py

frontend/
└── dashboard/
    ├── src/
    ├── public/
    ├── package.json
    └── vite.config.ts
```

---

# 📊 Business Modules

The system currently manages:

- Users
- Roles
- Permissions
- Products
- Customers
- Suppliers
- Orders

Each module is protected using Role-Based Access Control.

---

# 💡 Skills Demonstrated

This project demonstrates practical experience with:

### Backend

- Flask
- SQLAlchemy
- PostgreSQL
- REST API Development
- Authentication
- Authorization
- RBAC
- Database Design

### Frontend

- TypeScript
- Vite
- Tailwind CSS
- Axios

### Software Engineering

- Layered Architecture
- Modular Design
- Permission-Based Security
- Full-Stack Development
- Enterprise Application Design

---

# 🔮 Future Improvements

- JWT Authentication
- Refresh Tokens
- Audit Logs
- Activity Tracking
- Dashboard Analytics
- Notifications
- File Upload Support
- Multi-Organization Support
- Advanced Reporting
- Docker Deployment

---

# 📜 License

MIT License

---

# 👨‍💻 Author

**Prathamesh Khedkar**

---

⭐ This project is currently under active development, with additional features and improvements planned.
