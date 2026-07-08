from .db import db
from .models import Menu, Permission, Role, User


ROLE_NAMES = ["Admin", "Manager", "User"]
MENU_NAMES = [
    "Dashboard",
    "Users",
    "Orders",
    "Products",
    "Reports",
    "Settings",
    "Invoices",
    "Customers",
    "Suppliers",
    "Analytics",
    "Admin",
]

DEFAULT_PERMISSIONS = {
    "Admin": {
        "*": {"can_create": True, "can_read": True, "can_update": True, "can_delete": True},
    },
    "Manager": {
        "Dashboard": {"can_read": True},
        "Orders": {"can_create": True, "can_read": True, "can_update": True, "can_delete": False},
        "Products": {"can_create": True, "can_read": True, "can_update": True, "can_delete": False},
        "Customers": {"can_create": True, "can_read": True, "can_update": True, "can_delete": False},
        "Suppliers": {"can_create": True, "can_read": True, "can_update": True, "can_delete": False},
    },
    "User": {
        "Dashboard": {"can_read": True},
        "Orders": {"can_read": True},
        "Products": {"can_read": True},
        "Customers": {"can_read": True},
        "Suppliers": {"can_read": True},
    },
}


def default_flags(role_name, menu_name):
    role_defaults = DEFAULT_PERMISSIONS.get(role_name, {})
    flags = role_defaults.get("*", role_defaults.get(menu_name, {}))

    return {
        "can_create": bool(flags.get("can_create", False)),
        "can_read": bool(flags.get("can_read", False)),
        "can_update": bool(flags.get("can_update", False)),
        "can_delete": bool(flags.get("can_delete", False)),
    }


def get_or_create_role(name):
    role = Role.query.filter(db.func.lower(Role.name) == name.lower()).first()

    if not role:
        role = Role(name=name)
        db.session.add(role)
        db.session.flush()
    elif role.name != name:
        role.name = name

    return role


def get_or_create_menu(name):
    menu = Menu.query.filter(db.func.lower(Menu.name) == name.lower()).first()

    if not menu:
        menu = Menu(name=name)
        db.session.add(menu)
        db.session.flush()
    elif menu.name != name:
        menu.name = name

    return menu


def seed_data():
    roles = {name: get_or_create_role(name) for name in ROLE_NAMES}
    menus = {name: get_or_create_menu(name) for name in MENU_NAMES}

    admin = User.query.filter(db.func.lower(User.username) == "admin").first()
    if not admin:
        db.session.add(User(username="admin", password="admin123", role_id=roles["Admin"].id))
    else:
        admin.role_id = roles["Admin"].id

    for role_name, role in roles.items():
        for menu_name, menu in menus.items():
            permission = Permission.query.filter_by(role_id=role.id, menu_id=menu.id).first()
            created = False
            if not permission:
                permission = Permission(role_id=role.id, menu_id=menu.id)
                db.session.add(permission)
                created = True

            if created or role_name == "Admin":
                flags = default_flags(role_name, menu_name)
                for key, value in flags.items():
                    setattr(permission, key, value)

    db.session.commit()
