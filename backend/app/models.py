from datetime import datetime

from .db import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Role(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


class User(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id", ondelete="RESTRICT"), nullable=False)

    role = db.relationship("Role", backref=db.backref("users", passive_deletes=True))


class Menu(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


class Permission(TimestampMixin, db.Model):
    __table_args__ = (
        db.UniqueConstraint("role_id", "menu_id", name="uq_permission_role_menu"),
    )

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id", ondelete="CASCADE"), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu.id", ondelete="CASCADE"), nullable=False)
    can_create = db.Column(db.Boolean, default=False, nullable=False)
    can_read = db.Column(db.Boolean, default=False, nullable=False)
    can_update = db.Column(db.Boolean, default=False, nullable=False)
    can_delete = db.Column(db.Boolean, default=False, nullable=False)

    role = db.relationship("Role", backref=db.backref("permissions", cascade="all, delete-orphan"))
    menu = db.relationship("Menu", backref=db.backref("permissions", cascade="all, delete-orphan"))


class Product(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, default=0, nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)


class Customer(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))


class Supplier(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    company = db.Column(db.String(100))


class Order(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id", ondelete="RESTRICT"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id", ondelete="RESTRICT"), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.String(50), default="Pending", nullable=False)

    customer = db.relationship("Customer", backref=db.backref("orders", passive_deletes=True))
    product = db.relationship("Product", backref=db.backref("orders", passive_deletes=True))
