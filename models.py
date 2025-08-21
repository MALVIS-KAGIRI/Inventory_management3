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
    preferences = db.Column(db.JSON, default=lambda: {
        'theme': 'light',
        'dashboard_layout': 'default',
        'notifications': True,
        'language': 'en',
        'timezone': 'UTC'
    })

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
    # Industrial Features
    serial_number = db.Column(db.String(100))
    batch_number = db.Column(db.String(100))
    barcode = db.Column(db.String(100))
    rfid_tag = db.Column(db.String(100))
    location = db.Column(db.String(100))
    shelf_position = db.Column(db.String(50))
    weight = db.Column(db.Numeric(10, 3))
    dimensions = db.Column(db.String(100))
    safety_stock = db.Column(db.Integer, default=0)
    lead_time_days = db.Column(db.Integer, default=7)
    expiry_date = db.Column(db.Date)
    compliance_tags = db.Column(db.JSON)
    safety_labels = db.Column(db.JSON)
    tech_specs = db.relationship('TechnicalSpecification', backref='product', lazy=True)
    manuals = db.relationship('ProductManual', backref='product', lazy=True)
    maintenance_logs = db.relationship('MaintenanceLog', backref='product', lazy=True)
    usage_history = db.relationship('UsageHistory', backref='product', lazy=True)

class TechnicalSpecification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    spec_name = db.Column(db.String(100), nullable=False)
    spec_value = db.Column(db.String(200), nullable=False)
    unit = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductManual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(500))
    file_url = db.Column(db.String(500))
    manual_type = db.Column(db.String(50))  # Installation, Operation, Maintenance
    version = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MaintenanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    equipment_id = db.Column(db.String(100))
    maintenance_type = db.Column(db.String(50))  # Preventive, Corrective, Emergency
    description = db.Column(db.Text)
    performed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    scheduled_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Scheduled')
    cost = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UsageHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    equipment_id = db.Column(db.String(100))
    usage_date = db.Column(db.DateTime, default=datetime.utcnow)
    hours_used = db.Column(db.Numeric(8, 2))
    cycles_completed = db.Column(db.Integer)
    efficiency_rating = db.Column(db.Numeric(5, 2))
    operator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.Text)

class EquipmentMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.String(100), unique=True, nullable=False)
    equipment_name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100))
    department = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    installation_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ForecastData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    forecast_date = db.Column(db.Date, nullable=False)
    predicted_demand = db.Column(db.Integer, nullable=False)
    confidence_level = db.Column(db.Numeric(5, 2))
    algorithm_used = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref='forecasts')

class SmartShelf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shelf_id = db.Column(db.String(50), unique=True, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_weight = db.Column(db.Numeric(10, 3))
    temperature = db.Column(db.Numeric(5, 2))
    humidity = db.Column(db.Numeric(5, 2))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Active')
    products = db.relationship('Product', secondary='shelf_products', backref='shelves')

shelf_products = db.Table('shelf_products',
    db.Column('shelf_id', db.Integer, db.ForeignKey('smart_shelf.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('quantity', db.Integer, default=0)
)

class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(100), nullable=False)
    api_key = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    permissions = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)

class Webhook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    events = db.Column(db.JSON)  # List of events to trigger on
    is_active = db.Column(db.Boolean, default=True)
    secret_key = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_triggered = db.Column(db.DateTime)

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
    status = db.Column(db.String(20), default='Reserved')  # Reserved, Used, Returned
    reserved_until = db.Column(db.DateTime)
    product = db.relationship('Product', backref='project_assignments')

class BillOfMaterials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    version = db.Column(db.String(20), default='1.0')
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))  # Final product
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    bom_items = db.relationship('BOMItem', backref='bom', lazy=True, cascade='all, delete-orphan')

class BOMItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bom_id = db.Column(db.Integer, db.ForeignKey('bill_of_materials.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_required = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2))
    notes = db.Column(db.Text)
    product = db.relationship('Product', backref='bom_items')

class Kit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    kit_code = db.Column(db.String(50), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    total_cost = db.Column(db.Numeric(10, 2), default=0.00)
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    kit_items = db.relationship('KitItem', backref='kit', lazy=True, cascade='all, delete-orphan')

class KitItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kit_id = db.Column(db.Integer, db.ForeignKey('kit.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product', backref='kit_items')

class WorkOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_order_number = db.Column(db.String(20), unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Completed, Cancelled
    priority = db.Column(db.String(10), default='Medium')
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    estimated_hours = db.Column(db.Numeric(8, 2))
    actual_hours = db.Column(db.Numeric(8, 2), default=0.00)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    project = db.relationship('Project', backref='work_orders')
    work_order_items = db.relationship('WorkOrderItem', backref='work_order', lazy=True, cascade='all, delete-orphan')

class WorkOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, db.ForeignKey('work_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity_required = db.Column(db.Integer, nullable=False)
    quantity_used = db.Column(db.Integer, default=0)
    unit_cost = db.Column(db.Numeric(10, 2))
    total_cost = db.Column(db.Numeric(10, 2))
    product = db.relationship('Product', backref='work_order_items')

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