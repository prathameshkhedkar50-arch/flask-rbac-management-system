import uuid
from functools import wraps

from flask import jsonify, request

from .db import db
from .models import Customer, Menu, Order, Permission, Product, Role, Supplier, User


tokens = {}
SYSTEM_ROLES = {"Admin"}
VALID_ORDER_STATUSES = {"Pending", "Processing", "Completed", "Cancelled"}


def success_response(data=None, message="OK", status=200):
    return jsonify({"success": True, "message": message, "data": data}), status


def error_response(message, status=400, details=None):
    payload = {"success": False, "error": message, "message": message}
    if details:
        payload["details"] = details
    return jsonify(payload), status


def clean_text(value):
    return str(value or "").strip()


def to_float(value, default=0):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if number >= 0 else default


def to_int(value, default=0):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number


def current_user():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None

    token = auth.split(" ", 1)[1].strip()
    user_id = tokens.get(token)
    return User.query.get(user_id) if user_id else None


def find_menu(name):
    return Menu.query.filter(db.func.lower(Menu.name) == clean_text(name).lower()).first()


def menu_name(menu):
    return "Admin" if menu.name.lower() == "admin" else menu.name


def is_admin(user):
    return bool(user and user.role and user.role.name == "Admin")


def validate_permission(user, module, action):
    if not user:
        return False

    menu = find_menu(module)
    if not menu:
        return False

    permission = Permission.query.filter_by(role_id=user.role_id, menu_id=menu.id).first()
    if not permission:
        return False

    action_key = {
        "create": "can_create",
        "read": "can_read",
        "update": "can_update",
        "delete": "can_delete",
    }.get(action)
    return bool(action_key and getattr(permission, action_key))


def require_permission(module, action):
    def decorator(handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user:
                return error_response("Unauthorized", 401)
            if not validate_permission(user, module, action):
                return error_response("Permission denied", 403)
            return handler(user, *args, **kwargs)

        return wrapper

    return decorator


def require_admin(handler):
    @wraps(handler)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not is_admin(user):
            return error_response("Permission denied", 403)
        return handler(user, *args, **kwargs)

    return wrapper


def role_payload(role):
    return {"id": role.id, "name": role.name}


def user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "role_id": user.role_id,
        "role_name": user.role.name if user.role else "",
    }


def product_payload(product):
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
    }


def customer_payload(customer):
    return {
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone or "",
        "email": customer.email or "",
    }


def supplier_payload(supplier):
    return {
        "id": supplier.id,
        "name": supplier.name,
        "contact": supplier.contact or "",
        "company": supplier.company or "",
    }


def order_payload(order):
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "product_id": order.product_id,
        "customer_name": order.customer.name if order.customer else "",
        "product_name": order.product.name if order.product else "",
        "quantity": order.quantity,
        "status": order.status,
    }


def role_name_exists(name, ignore_id=None):
    query = Role.query.filter(db.func.lower(Role.name) == name.lower())
    if ignore_id:
        query = query.filter(Role.id != ignore_id)
    return query.first()


def require_name(data, label):
    name = clean_text(data.get("name"))
    if not name:
        return None, f"{label} name is required"
    return name, None


def register_routes(app):
    @app.errorhandler(404)
    def not_found(_):
        return error_response("Route not found", 404)

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception(error)
        return error_response("Internal server error", 500)

    @app.route("/login", methods=["POST"])
    def login():
        data = request.json or {}
        username = clean_text(data.get("username"))
        password = clean_text(data.get("password"))

        if not username or not password:
            return error_response("Username and password are required", 400)

        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return error_response("Invalid credentials", 401)

        token = str(uuid.uuid4())
        tokens[token] = user.id

        return success_response(
            {
                "user": user.username,
                "role_id": user.role_id,
                "role_name": user.role.name if user.role else None,
                "token": token,
            },
            "Login successful",
        )

    @app.route("/my-menus")
    def menus():
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)

        perms = Permission.query.filter_by(role_id=user.role_id, can_read=True).all()
        seen = set()
        rows = []

        for permission in perms:
            if permission.menu_id in seen or not permission.menu:
                continue
            seen.add(permission.menu_id)
            rows.append({"name": menu_name(permission.menu), "menu_id": permission.menu.id})

        return success_response(rows)

    @app.route("/my-permissions")
    def my_permissions():
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)

        rows = []
        for permission in Permission.query.filter_by(role_id=user.role_id).all():
            if not permission.menu:
                continue
            rows.append(
                {
                    "menu_id": permission.menu.id,
                    "menu": menu_name(permission.menu),
                    "module": permission.menu.name.lower(),
                    "can_create": permission.can_create,
                    "can_read": permission.can_read,
                    "can_update": permission.can_update,
                    "can_delete": permission.can_delete,
                }
            )

        return success_response(rows)

    @app.route("/roles", methods=["GET", "POST"])
    @require_admin
    def roles(_user):
        if request.method == "GET":
            rows = [role_payload(role) for role in Role.query.order_by(Role.id).all()]
            return success_response(rows)

        data = request.json or {}
        name = clean_text(data.get("name"))
        if not name:
            return error_response("Role name is required", 400)
        if role_name_exists(name):
            return error_response("Role name already exists", 400)

        role = Role(name=name)
        db.session.add(role)
        db.session.flush()

        for menu in Menu.query.order_by(Menu.id).all():
            db.session.add(Permission(role_id=role.id, menu_id=menu.id))

        db.session.commit()
        return success_response(role_payload(role), "Role created", 201)

    @app.route("/roles/<int:role_id>", methods=["PUT", "DELETE"])
    @require_admin
    def role_detail(_user, role_id):
        role = Role.query.get(role_id)
        if not role:
            return error_response("Role not found", 404)

        if request.method == "PUT":
            if role.name in SYSTEM_ROLES:
                return error_response("System roles cannot be renamed", 400)

            name = clean_text((request.json or {}).get("name"))
            if not name:
                return error_response("Role name is required", 400)
            if role_name_exists(name, role.id):
                return error_response("Role name already exists", 400)

            role.name = name
            db.session.commit()
            return success_response(role_payload(role), "Role updated")

        if role.name in SYSTEM_ROLES:
            return error_response("System roles cannot be deleted", 400)
        if User.query.filter_by(role_id=role.id).first():
            return error_response("Role is assigned to users", 400)

        Permission.query.filter_by(role_id=role.id).delete()
        db.session.delete(role)
        db.session.commit()
        return success_response({"id": role_id}, "Role deleted")

    @app.route("/role-options")
    @require_permission("Users", "read")
    def role_options(_user):
        return success_response([role_payload(r) for r in Role.query.order_by(Role.id).all()])

    @app.route("/menus")
    @require_admin
    def get_all_menus(_user):
        return success_response([{"id": m.id, "name": menu_name(m)} for m in Menu.query.order_by(Menu.id).all()])

    @app.route("/permissions")
    @require_admin
    def get_permissions(_user):
        role_id = to_int(request.args.get("role_id"))
        if not role_id:
            return error_response("role_id is required", 400)
        if not Role.query.get(role_id):
            return error_response("Role not found", 404)

        rows = []
        for menu in Menu.query.order_by(Menu.id).all():
            permission = Permission.query.filter_by(role_id=role_id, menu_id=menu.id).first()
            rows.append(
                {
                    "menu_id": menu.id,
                    "menu": menu_name(menu),
                    "can_create": permission.can_create if permission else False,
                    "can_read": permission.can_read if permission else False,
                    "can_update": permission.can_update if permission else False,
                    "can_delete": permission.can_delete if permission else False,
                }
            )
        return success_response(rows)

    @app.route("/permissions/update", methods=["POST"])
    @require_admin
    def update_permissions(_user):
        data = request.json or {}
        role_id = to_int(data.get("role_id"))
        permissions = data.get("permissions")

        if not role_id:
            return error_response("role_id is required", 400)
        if not Role.query.get(role_id):
            return error_response("Role not found", 404)
        if not isinstance(permissions, list):
            return error_response("permissions must be a list", 400)

        cleaned = {}
        for row in permissions:
            menu_id = to_int(row.get("menu_id"))
            menu = Menu.query.get(menu_id)
            if not menu:
                return error_response("Invalid menu_id", 400)
            cleaned[menu_id] = {
                "can_create": bool(row.get("can_create")),
                "can_read": bool(row.get("can_read")),
                "can_update": bool(row.get("can_update")),
                "can_delete": bool(row.get("can_delete")),
            }

        Permission.query.filter_by(role_id=role_id).delete()
        for menu_id, row in cleaned.items():
            db.session.add(Permission(role_id=role_id, menu_id=menu_id, **row))

        db.session.commit()
        return success_response({"role_id": role_id}, "Permissions saved successfully")

    @app.route("/users", methods=["GET", "POST"])
    def users():
        action = "read" if request.method == "GET" else "create"
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not validate_permission(user, "Users", action):
            return error_response("Permission denied", 403)

        if request.method == "GET":
            return success_response([user_payload(u) for u in User.query.order_by(User.id).all()])

        data = request.json or {}
        username = clean_text(data.get("username"))
        password = clean_text(data.get("password"))
        role_id = to_int(data.get("role_id"))

        if not username or not password or not role_id:
            return error_response("username, password, and role are required", 400)
        if User.query.filter(db.func.lower(User.username) == username.lower()).first():
            return error_response("Username already exists", 400)

        role = Role.query.get(role_id)
        if not role:
            return error_response("Role not found", 400)

        new_user = User(username=username, password=password, role_id=role.id)
        db.session.add(new_user)
        db.session.commit()
        return success_response(user_payload(new_user), "User created", 201)

    @app.route("/users/<int:user_id>", methods=["PUT", "DELETE"])
    def user_detail(user_id):
        action = "update" if request.method == "PUT" else "delete"
        current = current_user()
        if not current:
            return error_response("Unauthorized", 401)
        if not validate_permission(current, "Users", action):
            return error_response("Permission denied", 403)

        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", 404)

        if request.method == "PUT":
            data = request.json or {}
            username = clean_text(data.get("username"))
            password = clean_text(data.get("password"))
            role_id = to_int(data.get("role_id"))

            if not username or not role_id:
                return error_response("username and role are required", 400)

            existing = User.query.filter(db.func.lower(User.username) == username.lower()).first()
            if existing and existing.id != user.id:
                return error_response("Username already exists", 400)

            role = Role.query.get(role_id)
            if not role:
                return error_response("Role not found", 400)

            user.username = username
            user.role_id = role.id
            if password:
                user.password = password

            db.session.commit()
            return success_response(user_payload(user), "User updated")

        if user.id == current.id:
            return error_response("You cannot delete your own account", 400)

        db.session.delete(user)
        db.session.commit()
        return success_response({"id": user_id}, "User deleted")

    @app.route("/products", methods=["GET", "POST"])
    def products():
        action = "read" if request.method == "GET" else "create"
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not validate_permission(user, "Products", action):
            return error_response("Permission denied", 403)

        if request.method == "GET":
            return success_response([product_payload(p) for p in Product.query.order_by(Product.id).all()])

        name, error = require_name(request.json or {}, "Product")
        if error:
            return error_response(error, 400)

        product = Product(name=name, price=to_float(request.json.get("price")), stock=max(0, to_int(request.json.get("stock"))))
        db.session.add(product)
        db.session.commit()
        return success_response(product_payload(product), "Product created", 201)

    @app.route("/products/<int:product_id>", methods=["PUT", "DELETE"])
    def product_detail(product_id):
        action = "update" if request.method == "PUT" else "delete"
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not validate_permission(user, "Products", action):
            return error_response("Permission denied", 403)

        product = Product.query.get(product_id)
        if not product:
            return error_response("Product not found", 404)

        if request.method == "PUT":
            data = request.json or {}
            name, error = require_name(data, "Product")
            if error:
                return error_response(error, 400)

            product.name = name
            product.price = to_float(data.get("price"))
            product.stock = max(0, to_int(data.get("stock")))
            db.session.commit()
            return success_response(product_payload(product), "Product updated")

        if Order.query.filter_by(product_id=product.id).first():
            return error_response("Product is used by orders", 400)
        db.session.delete(product)
        db.session.commit()
        return success_response({"id": product_id}, "Product deleted")

    @app.route("/customers", methods=["GET", "POST"])
    def customers():
        action = "read" if request.method == "GET" else "create"
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not validate_permission(user, "Customers", action):
            return error_response("Permission denied", 403)

        if request.method == "GET":
            return success_response([customer_payload(c) for c in Customer.query.order_by(Customer.id).all()])

        data = request.json or {}
        name, error = require_name(data, "Customer")
        if error:
            return error_response(error, 400)

        customer = Customer(name=name, phone=clean_text(data.get("phone")), email=clean_text(data.get("email")))
        db.session.add(customer)
        db.session.commit()
        return success_response(customer_payload(customer), "Customer created", 201)

    @app.route("/customers/<int:customer_id>", methods=["PUT", "DELETE"])
    def customer_detail(customer_id):
        action = "update" if request.method == "PUT" else "delete"
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not validate_permission(user, "Customers", action):
            return error_response("Permission denied", 403)

        customer = Customer.query.get(customer_id)
        if not customer:
            return error_response("Customer not found", 404)

        if request.method == "PUT":
            data = request.json or {}
            name, error = require_name(data, "Customer")
            if error:
                return error_response(error, 400)

            customer.name = name
            customer.phone = clean_text(data.get("phone"))
            customer.email = clean_text(data.get("email"))
            db.session.commit()
            return success_response(customer_payload(customer), "Customer updated")

        if Order.query.filter_by(customer_id=customer.id).first():
            return error_response("Customer is used by orders", 400)
        db.session.delete(customer)
        db.session.commit()
        return success_response({"id": customer_id}, "Customer deleted")

    @app.route("/suppliers", methods=["GET", "POST"])
    def suppliers():
        action = "read" if request.method == "GET" else "create"
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not validate_permission(user, "Suppliers", action):
            return error_response("Permission denied", 403)

        if request.method == "GET":
            return success_response([supplier_payload(s) for s in Supplier.query.order_by(Supplier.id).all()])

        data = request.json or {}
        name, error = require_name(data, "Supplier")
        if error:
            return error_response(error, 400)

        supplier = Supplier(name=name, contact=clean_text(data.get("contact")), company=clean_text(data.get("company")))
        db.session.add(supplier)
        db.session.commit()
        return success_response(supplier_payload(supplier), "Supplier created", 201)

    @app.route("/suppliers/<int:supplier_id>", methods=["PUT", "DELETE"])
    def supplier_detail(supplier_id):
        action = "update" if request.method == "PUT" else "delete"
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not validate_permission(user, "Suppliers", action):
            return error_response("Permission denied", 403)

        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return error_response("Supplier not found", 404)

        if request.method == "PUT":
            data = request.json or {}
            name, error = require_name(data, "Supplier")
            if error:
                return error_response(error, 400)

            supplier.name = name
            supplier.contact = clean_text(data.get("contact"))
            supplier.company = clean_text(data.get("company"))
            db.session.commit()
            return success_response(supplier_payload(supplier), "Supplier updated")

        db.session.delete(supplier)
        db.session.commit()
        return success_response({"id": supplier_id}, "Supplier deleted")

    @app.route("/orders", methods=["GET", "POST"])
    def orders():
        action = "read" if request.method == "GET" else "create"
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not validate_permission(user, "Orders", action):
            return error_response("Permission denied", 403)

        if request.method == "GET":
            return success_response([order_payload(o) for o in Order.query.order_by(Order.id).all()])

        data = request.json or {}
        customer = Customer.query.get(to_int(data.get("customer_id")))
        product = Product.query.get(to_int(data.get("product_id")))
        status = clean_text(data.get("status")) or "Pending"
        quantity = to_int(data.get("quantity"), 1)

        if not customer:
            return error_response("Customer is required", 400)
        if not product:
            return error_response("Product is required", 400)
        if quantity < 1:
            return error_response("Quantity must be at least 1", 400)
        if status not in VALID_ORDER_STATUSES:
            return error_response("Invalid order status", 400)

        order = Order(customer_id=customer.id, product_id=product.id, quantity=quantity, status=status)
        db.session.add(order)
        db.session.commit()
        return success_response(order_payload(order), "Order created", 201)

    @app.route("/order-options")
    @require_permission("Orders", "read")
    def order_options(_user):
        return success_response(
            {
                "customers": [customer_payload(c) for c in Customer.query.order_by(Customer.name).all()],
                "products": [product_payload(p) for p in Product.query.order_by(Product.name).all()],
                "statuses": sorted(VALID_ORDER_STATUSES),
            }
        )

    @app.route("/orders/<int:order_id>", methods=["PUT", "DELETE"])
    def order_detail(order_id):
        action = "update" if request.method == "PUT" else "delete"
        user = current_user()
        if not user:
            return error_response("Unauthorized", 401)
        if not validate_permission(user, "Orders", action):
            return error_response("Permission denied", 403)

        order = Order.query.get(order_id)
        if not order:
            return error_response("Order not found", 404)

        if request.method == "PUT":
            data = request.json or {}
            customer = Customer.query.get(to_int(data.get("customer_id")))
            product = Product.query.get(to_int(data.get("product_id")))
            status = clean_text(data.get("status")) or "Pending"
            quantity = to_int(data.get("quantity"), 1)

            if not customer:
                return error_response("Customer is required", 400)
            if not product:
                return error_response("Product is required", 400)
            if quantity < 1:
                return error_response("Quantity must be at least 1", 400)
            if status not in VALID_ORDER_STATUSES:
                return error_response("Invalid order status", 400)

            order.customer_id = customer.id
            order.product_id = product.id
            order.quantity = quantity
            order.status = status
            db.session.commit()
            return success_response(order_payload(order), "Order updated")

        db.session.delete(order)
        db.session.commit()
        return success_response({"id": order_id}, "Order deleted")

    @app.route("/dashboard-stats")
    @require_permission("Dashboard", "read")
    def dashboard_stats(_user):
        return success_response(
            {
                "users": User.query.count(),
                "products": Product.query.count(),
                "orders": Order.query.count(),
                "customers": Customer.query.count(),
                "suppliers": Supplier.query.count(),
            }
        )
