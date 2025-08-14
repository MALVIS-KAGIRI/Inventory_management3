from database import db
from datetime import datetime
from flask_login import UserMixin

# Association table for many-to-many relationship between roles and permissions
role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(200))
    users = db.relationship('User', backref='role', lazy=True)
    permissions = db.relationship('Permission', secondary=role_permissions, 
                                  lazy='subquery', backref=db.backref('roles', lazy=True))

class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    quantity_in_stock = db.Column(db.Integer, default=0, nullable=False)
    reorder_level = db.Column(db.Integer, default=10, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    products = db.relationship('Product', backref='supplier', lazy=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))
    customer_type = db.Column(db.String(20), default='Regular')  # Regular, Premium, VIP
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    orders = db.relationship('Order', backref='customer', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, Processing, Shipped, Delivered, Cancelled
    total_amount = db.Column(db.Numeric(10, 2), default=0.00)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    product = db.relationship('Product', backref='order_items')

class StockMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # IN, OUT, ADJUSTMENT
    quantity = db.Column(db.Integer, nullable=False)
    reference_type = db.Column(db.String(20))  # ORDER, PURCHASE, ADJUSTMENT
    reference_id = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    product = db.relationship('Product', backref='stock_movements')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_code = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    status = db.Column(db.String(20), default='Planning')  # Planning, Active, On Hold, Completed, Cancelled
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    estimated_budget = db.Column(db.Numeric(12, 2))
    actual_cost = db.Column(db.Numeric(12, 2), default=0.00)
    priority = db.Column(db.String(10), default='Medium')  # Low, Medium, High, Critical
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer = db.relationship('Customer', backref='projects')
    assignments = db.relationship('ProjectAssignment', backref='project', lazy=True, cascade='all, delete-orphan')

class ProjectAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_assigned = db.Column(db.Integer, nullable=False)
    quantity_used = db.Column(db.Integer, default=0)
    unit_cost = db.Column(db.Numeric(10, 2))
    total_cost = db.Column(db.Numeric(10, 2))
    assignment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    notes = db.Column(db.Text)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    product = db.relationship('Product', backref='project_assignments')

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), default=0.00)
    tax_amount = db.Column(db.Numeric(10, 2), default=0.00)
    total_amount = db.Column(db.Numeric(10, 2), default=0.00)
    payment_method = db.Column(db.String(20))  # Cash, Credit Card, Check, Bank Transfer
    payment_status = db.Column(db.String(20), default='Pending')  # Pending, Paid, Partial, Overdue
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    customer = db.relationship('Customer', backref='sales')
    sale_items = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    product = db.relationship('Product', backref='sale_items')