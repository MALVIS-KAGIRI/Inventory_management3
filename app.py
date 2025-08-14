from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
import urllib
from dotenv import load_dotenv
from config import Config
from database import db, init_app
from models import *
from forms import *
from sqlalchemy import func
import random
import string
from reports_inventory import InventoryReportGenerator
from reports_purchase import PurchaseReportGenerator
from reports_sales import SalesReportGenerator
from reports_performance import PerformanceReportGenerator
from reports_compliance import ComplianceReportGenerator
from reports import ReportGenerator

# Initialize Flask application
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize extensions
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.is_active and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check username, password, and account status.', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Check if user has permission to view dashboard
    if not has_permission('dashboard.view'):
        abort(403)
    
    # Get dashboard statistics
    total_products = Product.query.filter_by(is_active=True).count()
    total_customers = Customer.query.filter_by(is_active=True).count()
    total_orders = Order.query.count()
    low_stock_products = Product.query.filter(Product.quantity_in_stock <= Product.reorder_level).count()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Low stock products
    low_stock_items = Product.query.filter(Product.quantity_in_stock <= Product.reorder_level).limit(5).all()
    
    return render_template('dashboard.html', 
                         title='Dashboard', 
                         has_permission=has_permission,
                         total_products=total_products,
                         total_customers=total_customers,
                         total_orders=total_orders,
                         low_stock_products=low_stock_products,
                         recent_orders=recent_orders,
                         low_stock_items=low_stock_items)

@app.route('/inventory')
@login_required
def inventory():
    # Check if user has permission to view inventory
    if not has_permission('inventory.view'):
        abort(403)
    
    products = Product.query.filter_by(is_active=True).all()
    categories = Category.query.all()
    suppliers = Supplier.query.filter_by(is_active=True).all()
    
    return render_template('inventory.html', 
                         title='Inventory Management', 
                         has_permission=has_permission,
                         products=products,
                         categories=categories,
                         suppliers=suppliers)

@app.route('/inventory/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if not has_permission('inventory.edit'):
        abort(403)
    
    form = ProductForm()
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    form.supplier.choices = [(0, 'Select Supplier')] + [(s.id, s.name) for s in Supplier.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            description=form.description.data,
            sku=form.sku.data,
            category_id=form.category.data,
            supplier_id=form.supplier.data if form.supplier.data != 0 else None,
            price=form.price.data,
            cost=form.cost.data,
            quantity_in_stock=form.quantity_in_stock.data,
            reorder_level=form.reorder_level.data,
            is_active=form.is_active.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('inventory'))
    
    return render_template('add_product.html', title='Add Product', form=form, has_permission=has_permission)

@app.route('/inventory/categories')
@login_required
def categories():
    if not has_permission('inventory.view'):
        abort(403)
    
    categories_list = Category.query.all()
    return render_template('categories.html', title='Categories', categories=categories_list, has_permission=has_permission)

@app.route('/inventory/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if not has_permission('inventory.edit'):
        abort(403)
    
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!', 'success')
        return redirect(url_for('categories'))
    
    return render_template('add_category.html', title='Add Category', form=form, has_permission=has_permission)

@app.route('/inventory/suppliers')
@login_required
def suppliers():
    if not has_permission('inventory.view'):
        abort(403)
    
    suppliers_list = Supplier.query.all()
    return render_template('suppliers.html', title='Suppliers', suppliers=suppliers_list, has_permission=has_permission)

@app.route('/inventory/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if not has_permission('inventory.edit'):
        abort(403)
    
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            contact_person=form.contact_person.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            is_active=form.is_active.data
        )
        db.session.add(supplier)
        db.session.commit()
        flash('Supplier added successfully!', 'success')
        return redirect(url_for('suppliers'))
    
    return render_template('add_supplier.html', title='Add Supplier', form=form, has_permission=has_permission)

@app.route('/customers')
@login_required
def customers():
    # Check if user has permission to view customers
    if not has_permission('customers.view'):
        abort(403)
    
    customers_list = Customer.query.filter_by(is_active=True).all()
    return render_template('customers.html', title='Customer Management', customers=customers_list, has_permission=has_permission)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if not has_permission('customers.edit'):
        abort(403)
    
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            customer_type=form.customer_type.data,
            is_active=form.is_active.data
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('add_customer.html', title='Add Customer', form=form, has_permission=has_permission)

@app.route('/operations')
@login_required
def operations():
    # Check if user has permission to perform basic operations
    if not has_permission('operations.basic'):
        abort(403)
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('operations.html', title='Basic Operations', orders=orders, has_permission=has_permission)

@app.route('/operations/orders/add', methods=['GET', 'POST'])
@login_required
def add_order():
    if not has_permission('operations.basic'):
        abort(403)
    
    form = OrderForm()
    form.customer.choices = [(c.id, c.full_name) for c in Customer.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        # Generate order number
        order_number = 'ORD' + ''.join(random.choices(string.digits, k=6))
        
        order = Order(
            order_number=order_number,
            customer_id=form.customer.data,
            status=form.status.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(order)
        db.session.commit()
        flash('Order created successfully!', 'success')
        return redirect(url_for('operations'))
    
    return render_template('add_order.html', title='Add Order', form=form, has_permission=has_permission)

@app.route('/operations/stock-adjustment', methods=['GET', 'POST'])
@login_required
def stock_adjustment():
    if not has_permission('operations.basic'):
        abort(403)
    
    form = StockAdjustmentForm()
    form.product.choices = [(p.id, f"{p.name} (Current: {p.quantity_in_stock})") for p in Product.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product.data)
        
        # Create stock movement record
        movement = StockMovement(
            product_id=form.product.data,
            movement_type=form.movement_type.data,
            quantity=form.quantity.data,
            reference_type='ADJUSTMENT',
            notes=form.notes.data,
            created_by=current_user.id
        )
        
        # Update product stock
        if form.movement_type.data == 'IN':
            product.quantity_in_stock += form.quantity.data
        elif form.movement_type.data == 'OUT':
            product.quantity_in_stock = max(0, product.quantity_in_stock - form.quantity.data)
        else:  # ADJUSTMENT
            product.quantity_in_stock = form.quantity.data
        
        db.session.add(movement)
        db.session.commit()
        flash('Stock adjustment processed successfully!', 'success')
        return redirect(url_for('operations'))
    
    return render_template('stock_adjustment.html', title='Stock Adjustment', form=form, has_permission=has_permission)

@app.route('/users')
@login_required
def users():
    # Check if user has permission to view users
    if not has_permission('users.view'):
        abort(403)
        
    users_list = User.query.all()
    return render_template('users.html', title='User Management', users=users_list, has_permission=has_permission)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    # Check if user has permission to create users
    if not has_permission('users.create'):
        abort(403)
        
    form = UserForm()
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            role_id=form.role.data,
            is_active=form.is_active.data
        )
        db.session.add(user)
        db.session.commit()
        flash(f'User {form.username.data} has been created!', 'success')
        return redirect(url_for('users'))
    
    return render_template('add_user.html', title='Add User', form=form, has_permission=has_permission)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Check if user has permission to edit users
    if not has_permission('users.edit'):
        abort(403)
        
    user = User.query.get_or_404(user_id)
    form = UserForm()
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role_id = form.role.data
        user.is_active = form.is_active.data
        
        if form.password.data:
            user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            
        db.session.commit()
        flash('User has been updated!', 'success')
        return redirect(url_for('users'))
    
    elif request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role_id
        form.is_active.data = user.is_active
    
    return render_template('edit_user.html', title='Edit User', form=form, user=user, has_permission=has_permission)

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    # Check if user has permission to delete users
    if not has_permission('users.delete'):
        abort(403)
        
    user = User.query.get_or_404(user_id)
    
    # Prevent deletion of own account
    if user.id == current_user.id:
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User has been deleted!', 'success')
    return redirect(url_for('users'))

@app.route('/roles')
@login_required
def roles():
    # Check if user has permission to manage roles
    if not has_permission('roles.manage'):
        abort(403)
        
    roles_list = Role.query.all()
    permissions = Permission.query.all()
    return render_template('roles.html', title='Role Management', roles=roles_list, permissions=permissions, has_permission=has_permission)

@app.route('/roles/<int:role_id>/permissions', methods=['GET', 'POST'])
@login_required
def role_permissions(role_id):
    # Check if user has permission to manage roles
    if not has_permission('roles.manage'):
        abort(403)
        
    role = Role.query.get_or_404(role_id)
    permissions = Permission.query.all()
    
    if request.method == 'POST':
        # Update permissions for the role
        role_permissions = []
        for permission in permissions:
            if str(permission.id) in request.form.getlist('permissions'):
                role_permissions.append(permission)
        
        role.permissions = role_permissions
        db.session.commit()
        flash(f'Permissions for {role.name} role have been updated!', 'success')
        return redirect(url_for('roles'))
    
    return render_template('role_permissions.html', title='Role Permissions', role=role, permissions=permissions, has_permission=has_permission)

# Helper function to check user permissions
def has_permission(permission_name):
    if not current_user.is_authenticated:
        return False
    
    # Fetch the user's role and its permissions
    role = Role.query.get(current_user.role_id)
    if not role:
        return False
    
    # Admin role has all permissions
    if role.name == 'Admin':
        return True
    
    permission = Permission.query.filter_by(name=permission_name).first()
    if not permission:
        return False
    
    return permission in role.permissions

# Analytics Routes
@app.route('/analytics')
@login_required
def analytics():
    if not has_permission('analytics.view'):
        abort(403)
    
    # Get current date and calculate periods
    today = datetime.now().date()
    thirty_days_ago = today - timedelta(days=30)
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    last_month_end = this_month_start - timedelta(days=1)
    
    # Inventory Analytics
    total_products = Product.query.filter_by(is_active=True).count()
    low_stock_count = Product.query.filter(Product.quantity_in_stock <= Product.reorder_level).count()
    total_inventory_value = db.session.query(func.sum(Product.price * Product.quantity_in_stock)).filter_by(is_active=True).scalar() or 0
    
    # Top categories by product count
    top_categories = db.session.query(
        Category.name,
        func.count(Product.id).label('product_count')
    ).join(Product).filter(Product.is_active == True).group_by(Category.name).order_by(func.count(Product.id).desc()).limit(5).all()
    
    # Customer Analytics
    total_customers = Customer.query.filter_by(is_active=True).count()
    new_customers_this_month = Customer.query.filter(
        Customer.created_at >= this_month_start,
        Customer.is_active == True
    ).count()
    
    # Customer types distribution
    customer_types = db.session.query(
        Customer.customer_type,
        func.count(Customer.id).label('count')
    ).filter_by(is_active=True).group_by(Customer.customer_type).all()
    
    # Sales Analytics
    total_sales = Sale.query.count()
    this_month_sales = Sale.query.filter(Sale.sale_date >= this_month_start).count()
    this_month_revenue = db.session.query(func.sum(Sale.total_amount)).filter(Sale.sale_date >= this_month_start).scalar() or 0
    last_month_revenue = db.session.query(func.sum(Sale.total_amount)).filter(
        and_(Sale.sale_date >= last_month_start, Sale.sale_date <= last_month_end)
    ).scalar() or 0
    
    # Revenue growth
    revenue_growth = 0
    if last_month_revenue > 0:
        revenue_growth = ((this_month_revenue - last_month_revenue) / last_month_revenue) * 100
    
    # Project Analytics
    total_projects = Project.query.count()
    active_projects = Project.query.filter_by(status='Active').count()
    completed_projects = Project.query.filter_by(status='Completed').count()
    
    # Project status distribution
    project_status = db.session.query(
        Project.status,
        func.count(Project.id).label('count')
    ).group_by(Project.status).all()
    
    # Recent stock movements
    recent_movements = StockMovement.query.order_by(StockMovement.created_at.desc()).limit(10).all()
    
    return render_template('analytics.html',
                         title='Analytics Dashboard',
                         has_permission=has_permission,
                         # Inventory
                         total_products=total_products,
                         low_stock_count=low_stock_count,
                         total_inventory_value=total_inventory_value,
                         top_categories=top_categories,
                         # Customers
                         total_customers=total_customers,
                         new_customers_this_month=new_customers_this_month,
                         customer_types=customer_types,
                         # Sales
                         total_sales=total_sales,
                         this_month_sales=this_month_sales,
                         this_month_revenue=this_month_revenue,
                         revenue_growth=revenue_growth,
                         # Projects
                         total_projects=total_projects,
                         active_projects=active_projects,
                         completed_projects=completed_projects,
                         project_status=project_status,
                         recent_movements=recent_movements)

# Project Management Routes
@app.route('/projects')
@login_required
def projects():
    if not has_permission('projects.view'):
        abort(403)
    
    projects_list = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', title='Project Management', projects=projects_list, has_permission=has_permission)

@app.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    if not has_permission('projects.edit'):
        abort(403)
    
    form = ProjectForm()
    form.customer.choices = [(0, 'Select Customer (Optional)')] + [(c.id, c.full_name) for c in Customer.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        # Generate project code if not provided
        project_code = form.project_code.data
        if not project_code:
            project_code = 'PRJ' + ''.join(random.choices(string.digits, k=6))
        
        project = Project(
            name=form.name.data,
            description=form.description.data,
            project_code=project_code,
            customer_id=form.customer.data if form.customer.data != 0 else None,
            status=form.status.data,
            start_date=datetime.strptime(form.start_date.data, '%Y-%m-%d').date() if form.start_date.data else None,
            end_date=datetime.strptime(form.end_date.data, '%Y-%m-%d').date() if form.end_date.data else None,
            estimated_budget=form.estimated_budget.data,
            priority=form.priority.data,
            created_by=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        flash('Project created successfully!', 'success')
        return redirect(url_for('projects'))
    
    return render_template('add_project.html', title='Add Project', form=form, has_permission=has_permission)

@app.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    if not has_permission('projects.view'):
        abort(403)
    
    project = Project.query.get_or_404(project_id)
    assignments = ProjectAssignment.query.filter_by(project_id=project_id).all()
    
    # Calculate total assigned cost
    total_assigned_cost = sum(assignment.total_cost or 0 for assignment in assignments)
    
    return render_template('project_detail.html', 
                         title=f'Project: {project.name}', 
                         project=project, 
                         assignments=assignments,
                         total_assigned_cost=total_assigned_cost,
                         has_permission=has_permission)

@app.route('/projects/<int:project_id>/assign', methods=['GET', 'POST'])
@login_required
def assign_to_project(project_id):
    if not has_permission('projects.edit'):
        abort(403)
    
    project = Project.query.get_or_404(project_id)
    form = ProjectAssignmentForm()
    form.product.choices = [(p.id, f"{p.name} (Stock: {p.quantity_in_stock})") for p in Product.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        product = Product.query.get(form.product.data)
        
        # Check if enough stock is available
        if product.quantity_in_stock < form.quantity_assigned.data:
            flash(f'Insufficient stock! Only {product.quantity_in_stock} units available.', 'danger')
            return render_template('assign_to_project.html', title='Assign Parts', form=form, project=project, has_permission=has_permission)
        
        # Calculate costs
        unit_cost = product.cost
        total_cost = unit_cost * form.quantity_assigned.data
        
        # Create assignment
        assignment = ProjectAssignment(
            project_id=project_id,
            product_id=form.product.data,
            quantity_assigned=form.quantity_assigned.data,
            unit_cost=unit_cost,
            total_cost=total_cost,
            notes=form.notes.data,
            assigned_by=current_user.id
        )
        
        # Update product stock
        product.quantity_in_stock -= form.quantity_assigned.data
        
        # Create stock movement record
        movement = StockMovement(
            product_id=form.product.data,
            movement_type='OUT',
            quantity=form.quantity_assigned.data,
            reference_type='PROJECT',
            reference_id=project_id,
            notes=f'Assigned to project: {project.name}',
            created_by=current_user.id
        )
        
        # Update project actual cost
        project.actual_cost = (project.actual_cost or 0) + total_cost
        
        db.session.add(assignment)
        db.session.add(movement)
        db.session.commit()
        
        flash(f'Successfully assigned {form.quantity_assigned.data} units of {product.name} to project!', 'success')
        return redirect(url_for('project_detail', project_id=project_id))
    
    return render_template('assign_to_project.html', title='Assign Parts', form=form, project=project, has_permission=has_permission)

@app.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    if not has_permission('projects.delete'):
        abort(403)
    
    project = Project.query.get_or_404(project_id)
    
    # Return assigned parts to inventory
    for assignment in project.assignments:
        product = assignment.product
        product.quantity_in_stock += assignment.quantity_assigned
        
        # Create stock movement record
        movement = StockMovement(
            product_id=assignment.product_id,
            movement_type='IN',
            quantity=assignment.quantity_assigned,
            reference_type='PROJECT_RETURN',
            reference_id=project_id,
            notes=f'Returned from deleted project: {project.name}',
            created_by=current_user.id
        )
        db.session.add(movement)
    
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted and parts returned to inventory!', 'success')
    return redirect(url_for('projects'))

# Sales Routes
@app.route('/sales')
@login_required
def sales():
    if not has_permission('sales.view'):
        abort(403)
    
    sales_list = Sale.query.order_by(Sale.sale_date.desc()).all()
    return render_template('sales.html', title='Sales Management', sales=sales_list, has_permission=has_permission)

@app.route('/sales/add', methods=['GET', 'POST'])
@login_required
def add_sale():
    if not has_permission('sales.edit'):
        abort(403)
    
    form = SaleForm()
    form.customer.choices = [(c.id, c.full_name) for c in Customer.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        # Generate sale number
        sale_number = 'SAL' + ''.join(random.choices(string.digits, k=6))
        
        sale = Sale(
            sale_number=sale_number,
            customer_id=form.customer.data,
            payment_method=form.payment_method.data,
            payment_status=form.payment_status.data,
            notes=form.notes.data,
            created_by=current_user.id
        )
        db.session.add(sale)
        db.session.commit()
        flash('Sale created successfully!', 'success')
        return redirect(url_for('sales'))
    
    return render_template('add_sale.html', title='Add Sale', form=form, has_permission=has_permission)

# Reports Routes
@app.route('/reports')
@login_required
def reports():
    if not has_permission('analytics.view'):
        abort(403)
    
    return render_template('reports/index.html', title='Reports Dashboard', has_permission=has_permission)

# Inventory Reports
@app.route('/reports/inventory', methods=['GET', 'POST'])
@login_required
def inventory_reports():
    if not has_permission('analytics.view'):
        abort(403)
    
    from forms import InventoryReportForm
    form = InventoryReportForm()
    
    # Populate choices
    form.category_id.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in Category.query.all()]
    form.supplier_id.choices = [(0, 'All Suppliers')] + [(s.id, s.name) for s in Supplier.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        return generate_inventory_report(form)
    
    return render_template('reports/inventory.html', title='Inventory Reports', form=form, has_permission=has_permission)

def generate_inventory_report(form):
    """Generate and export inventory report"""
    report_type = form.report_type.data
    start_date = form.start_date.data
    end_date = form.end_date.data
    category_id = form.category_id.data
    supplier_id = form.supplier_id.data
    include_inactive = form.include_inactive.data
    export_format = form.export_format.data
    
    # Generate report data based on type
    if report_type == 'inventory_status':
        data = InventoryReportGenerator.generate_inventory_status_report(
            start_date, end_date, category_id, supplier_id, include_inactive
        )
        title = 'Inventory Status Report'
        headers = ['name', 'sku', 'category_name', 'supplier_name', 'quantity_in_stock', 'reorder_level', 'price', 'stock_value', 'needs_reorder']
    elif report_type == 'low_stock':
        data = InventoryReportGenerator.generate_low_stock_report(
            start_date, end_date, category_id, supplier_id
        )
        title = 'Low Stock Report'
        headers = ['name', 'sku', 'category_name', 'supplier_name', 'quantity_in_stock', 'reorder_level', 'shortage', 'shortage_value']
    elif report_type == 'stock_movement':
        data = InventoryReportGenerator.generate_stock_movement_history(
            start_date, end_date, category_id, supplier_id
        )
        title = 'Stock Movement History'
        headers = ['product_name', 'product_sku', 'movement_type', 'quantity', 'reference', 'created_at', 'user_name']
    elif report_type == 'inventory_valuation':
        data = InventoryReportGenerator.generate_inventory_valuation_report(
            start_date, end_date, category_id, supplier_id, include_inactive
        )
        title = 'Inventory Valuation Report'
        headers = ['name', 'sku', 'category_name', 'quantity_in_stock', 'cost', 'price', 'cost_value', 'retail_value', 'profit_potential', 'margin_percentage']
    else:  # inventory_aging
        data = InventoryReportGenerator.generate_inventory_aging_analysis(
            start_date, end_date, category_id, supplier_id
        )
        title = 'Inventory Aging Analysis'
        headers = ['name', 'sku', 'category_name', 'quantity_in_stock', 'days_in_stock', 'aging_category', 'inventory_value']
    
    # Export based on format
    filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if export_format == 'csv':
        return ReportGenerator.export_as_csv(data, filename, headers)
    elif export_format == 'excel':
        return ReportGenerator.export_as_excel(data, filename, headers)
    else:  # pdf
        return ReportGenerator.export_as_pdf(data, filename, headers, title)

# Sales Reports
@app.route('/reports/sales', methods=['GET', 'POST'])
@login_required
def sales_reports():
    if not has_permission('analytics.view'):
        abort(403)
    
    from forms import SalesReportForm
    form = SalesReportForm()
    
    # Populate choices
    form.customer_id.choices = [(0, 'All Customers')] + [(c.id, c.full_name) for c in Customer.query.filter_by(is_active=True).all()]
    form.product_id.choices = [(0, 'All Products')] + [(p.id, p.name) for p in Product.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        return generate_sales_report(form)
    
    return render_template('reports/sales.html', title='Sales Reports', form=form, has_permission=has_permission)

def generate_sales_report(form):
    """Generate and export sales report"""
    report_type = form.report_type.data
    start_date = form.start_date.data
    end_date = form.end_date.data
    customer_id = form.customer_id.data
    product_id = form.product_id.data
    payment_status = form.payment_status.data
    export_format = form.export_format.data
    
    # Generate report data based on type
    if report_type == 'sales_history':
        data = SalesReportGenerator.generate_sales_history_report(
            start_date, end_date, customer_id, payment_status
        )
        title = 'Sales History Report'
        headers = ['sale_number', 'customer_name', 'sale_date', 'total_amount', 'payment_status', 'payment_method', 'item_count']
    elif report_type == 'product_performance':
        data = SalesReportGenerator.generate_product_performance_report(
            start_date, end_date, product_id
        )
        title = 'Product Sales Performance'
        headers = ['name', 'sku', 'category_name', 'total_quantity_sold', 'total_revenue', 'profit', 'profit_margin']
    elif report_type == 'customer_sales':
        data = SalesReportGenerator.generate_customer_sales_report(
            start_date, end_date, customer_id
        )
        title = 'Customer Sales Analysis'
        headers = ['name', 'customer_type', 'total_orders', 'total_spent', 'avg_order_value', 'last_order_date']
    elif report_type == 'profit_margin':
        data = SalesReportGenerator.generate_profit_margin_report(
            start_date, end_date, product_id
        )
        title = 'Profit Margin Analysis'
        headers = ['name', 'sku', 'total_quantity_sold', 'total_revenue', 'total_cost', 'profit', 'profit_margin']
    else:  # payment_collection
        data = SalesReportGenerator.generate_payment_collection_report(
            start_date, end_date, payment_status
        )
        title = 'Payment Collection Status'
        headers = ['sale_number', 'customer_name', 'sale_date', 'total_amount', 'payment_status', 'days_outstanding']
    
    # Export based on format
    filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if export_format == 'csv':
        return ReportGenerator.export_as_csv(data, filename, headers)
    elif export_format == 'excel':
        return ReportGenerator.export_as_excel(data, filename, headers)
    else:  # pdf
        return ReportGenerator.export_as_pdf(data, filename, headers, title)

# Purchase Reports
@app.route('/reports/purchase', methods=['GET', 'POST'])
@login_required
def purchase_reports():
    if not has_permission('analytics.view'):
        abort(403)
    
    from forms import PurchaseReportForm
    form = PurchaseReportForm()
    
    # Populate choices
    form.supplier_id.choices = [(0, 'All Suppliers')] + [(s.id, s.name) for s in Supplier.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        return generate_purchase_report(form)
    
    return render_template('reports/purchase.html', title='Purchase Reports', form=form, has_permission=has_permission)

def generate_purchase_report(form):
    """Generate and export purchase report"""
    report_type = form.report_type.data
    start_date = form.start_date.data
    end_date = form.end_date.data
    supplier_id = form.supplier_id.data
    export_format = form.export_format.data
    
    # Generate report data based on type
    if report_type == 'supplier_performance':
        data = PurchaseReportGenerator.generate_supplier_performance_analysis(
            start_date, end_date, supplier_id
        )
        title = 'Supplier Performance Analysis'
        headers = ['name', 'contact_person', 'email', 'product_count', 'total_orders', 'on_time_delivery_rate']
    elif report_type == 'cost_analysis':
        data = PurchaseReportGenerator.generate_cost_analysis(
            start_date, end_date, supplier_id
        )
        title = 'Purchase Cost Analysis'
        headers = ['name', 'sku', 'supplier_name', 'cost', 'price', 'margin', 'margin_percentage']
    else:  # reorder_suggestions
        data = PurchaseReportGenerator.generate_reorder_suggestions_report(
            start_date, end_date, supplier_id
        )
        title = 'Reorder Suggestions Report'
        headers = ['name', 'sku', 'supplier_name', 'quantity_in_stock', 'reorder_level', 'reorder_amount', 'estimated_cost', 'priority']
    
    # Export based on format
    filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if export_format == 'csv':
        return ReportGenerator.export_as_csv(data, filename, headers)
    elif export_format == 'excel':
        return ReportGenerator.export_as_excel(data, filename, headers)
    else:  # pdf
        return ReportGenerator.export_as_pdf(data, filename, headers, title)

# Performance Reports
@app.route('/reports/performance', methods=['GET', 'POST'])
@login_required
def performance_reports():
    if not has_permission('analytics.view'):
        abort(403)
    
    from forms import PerformanceReportForm
    form = PerformanceReportForm()
    
    if form.validate_on_submit():
        return generate_performance_report(form)
    
    return render_template('reports/performance.html', title='Performance Reports', form=form, has_permission=has_permission)

def generate_performance_report(form):
    """Generate and export performance report"""
    report_type = form.report_type.data
    start_date = form.start_date.data
    end_date = form.end_date.data
    period_grouping = form.period_grouping.data
    export_format = form.export_format.data
    
    # Generate report data based on type
    if report_type == 'sales_trend':
        data = PerformanceReportGenerator.generate_sales_trend_report(
            start_date, end_date, period_grouping
        )
        title = 'Sales Trend Analysis'
        headers = ['period', 'order_count', 'total_revenue']
    elif report_type == 'inventory_turnover':
        data = PerformanceReportGenerator.generate_inventory_turnover_report(
            start_date, end_date, period_grouping
        )
        title = 'Inventory Turnover Analysis'
        headers = ['product_name', 'sku', 'category_name', 'current_stock', 'sales_quantity', 'turnover_ratio', 'days_to_sell', 'performance']
    elif report_type == 'revenue_forecast':
        data = PerformanceReportGenerator.generate_revenue_forecast_report(
            start_date, end_date, period_grouping
        )
        title = 'Revenue Forecast Report'
        headers = ['period', 'type', 'revenue', 'confidence']
    elif report_type == 'product_profitability':
        data = PerformanceReportGenerator.generate_product_profitability_report(
            start_date, end_date
        )
        title = 'Product Profitability Analysis'
        headers = ['name', 'sku', 'category_name', 'quantity_sold', 'total_revenue', 'total_profit', 'profit_margin', 'profitability_rank']
    else:  # business_growth
        data = PerformanceReportGenerator.generate_business_growth_report(
            start_date, end_date
        )
        title = 'Business Growth Analysis'
        headers = ['metric', 'current_period', 'previous_period', 'growth_rate', 'trend']
    
    # Export based on format
    filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if export_format == 'csv':
        return ReportGenerator.export_as_csv(data, filename, headers)
    elif export_format == 'excel':
        return ReportGenerator.export_as_excel(data, filename, headers)
    else:  # pdf
        return ReportGenerator.export_as_pdf(data, filename, headers, title)

# Compliance Reports
@app.route('/reports/compliance', methods=['GET', 'POST'])
@login_required
def compliance_reports():
    if not has_permission('analytics.view'):
        abort(403)
    
    from forms import ComplianceReportForm
    form = ComplianceReportForm()
    
    # Populate choices
    form.user_id.choices = [(0, 'All Users')] + [(u.id, u.username) for u in User.query.filter_by(is_active=True).all()]
    
    if form.validate_on_submit():
        return generate_compliance_report(form)
    
    return render_template('reports/compliance.html', title='Compliance Reports', form=form, has_permission=has_permission)

def generate_compliance_report(form):
    """Generate and export compliance report"""
    report_type = form.report_type.data
    start_date = form.start_date.data
    end_date = form.end_date.data
    user_id = form.user_id.data
    activity_type = form.activity_type.data
    export_format = form.export_format.data
    
    # Generate report data based on type
    if report_type == 'stock_audit':
        data = ComplianceReportGenerator.generate_stock_audit_report(
            start_date, end_date
        )
        title = 'Stock Audit Report'
        headers = ['name', 'sku', 'category_name', 'current_stock', 'total_in', 'total_out', 'net_movement', 'audit_status']
    elif report_type == 'user_activity':
        data = ComplianceReportGenerator.generate_user_activity_report(
            start_date, end_date, user_id, activity_type
        )
        title = 'User Activity Logs'
        headers = ['username', 'activity_type', 'activity_date', 'details', 'status']
    elif report_type == 'price_changes':
        data = ComplianceReportGenerator.generate_price_changes_report(
            start_date, end_date
        )
        title = 'Price Change History'
        headers = ['product_name', 'sku', 'category_name', 'change_date', 'old_price', 'new_price', 'price_change', 'change_percentage']
    elif report_type == 'tax_report':
        data = ComplianceReportGenerator.generate_tax_report(
            start_date, end_date
        )
        title = 'Tax Calculation Report'
        headers = ['sale_number', 'customer_name', 'sale_date', 'subtotal', 'tax_amount', 'total_amount', 'tax_rate']
    else:  # custom_report
        data = ComplianceReportGenerator.generate_custom_report(
            start_date, end_date
        )
        title = 'Custom Report'
        headers = ['report_section', 'metric', 'value', 'period']
    
    # Export based on format
    filename = f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if export_format == 'csv':
        return ReportGenerator.export_as_csv(data, filename, headers)
    elif export_format == 'excel':
        return ReportGenerator.export_as_excel(data, filename, headers)
    else:  # pdf
        return ReportGenerator.export_as_pdf(data, filename, headers, title)

# Profile and Settings Routes
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='User Profile', has_permission=has_permission)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UserForm()
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        if form.password.data:
            current_user.password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.role.data = current_user.role_id
        form.is_active.data = current_user.is_active
    
    return render_template('edit_profile.html', title='Edit Profile', form=form, has_permission=has_permission)

@app.route('/notifications')
@login_required
def notifications():
    # Get recent activities for notifications
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    low_stock_items = Product.query.filter(Product.quantity_in_stock <= Product.reorder_level).limit(5).all()
    
    return render_template('notifications.html', 
                         title='Notifications', 
                         recent_orders=recent_orders,
                         low_stock_items=low_stock_items,
                         has_permission=has_permission)

@app.route('/settings')
@login_required
def settings():
    if not has_permission('settings.edit'):
        abort(403)
    
    return render_template('settings.html', title='System Settings', has_permission=has_permission)

# Initialize the database with default data
def init_db():
    db.create_all()
    
    # Create default roles if they don't exist
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(name='Admin', description='Full system access')
        db.session.add(admin_role)
    
    manager_role = Role.query.filter_by(name='Manager').first()
    if not manager_role:
        manager_role = Role(name='Manager', description='Access to inventory and customer management')
        db.session.add(manager_role)
    
    operator_role = Role.query.filter_by(name='Operator').first()
    if not operator_role:
        operator_role = Role(name='Operator', description='Access to basic operations')
        db.session.add(operator_role)
    
    viewer_role = Role.query.filter_by(name='Viewer').first()
    if not viewer_role:
        viewer_role = Role(name='Viewer', description='Read-only access to the system')
        db.session.add(viewer_role)
    
    # Create permissions if they don't exist
    permissions_data = [
        ('users.view', 'View Users'),
        ('users.create', 'Create Users'),
        ('users.edit', 'Edit Users'),
        ('users.delete', 'Delete Users'),
        ('roles.manage', 'Manage Roles'),
        ('dashboard.view', 'View Dashboard'),
        ('settings.edit', 'Edit Settings'),
        ('inventory.view', 'View Inventory'),
        ('inventory.edit', 'Edit Inventory'),
        ('customers.view', 'View Customers'),
        ('customers.edit', 'Edit Customers'),
        ('operations.basic', 'Perform Basic Operations')
    ]
    
    for name, description in permissions_data:
        permission = Permission.query.filter_by(name=name).first()
        if not permission:
            permission = Permission(name=name, description=description)
            db.session.add(permission)
    
    # Add new permissions for analytics and projects
    new_permissions = [
        ('analytics.view', 'View Analytics'),
        ('projects.view', 'View Projects'),
        ('projects.edit', 'Edit Projects'),
        ('projects.delete', 'Delete Projects'),
        ('sales.view', 'View Sales'),
        ('sales.edit', 'Edit Sales'),
        ('reports.view', 'View Reports'),
        ('reports.export', 'Export Reports')
    ]
    
    for name, description in new_permissions:
        permission = Permission.query.filter_by(name=name).first()
        if not permission:
            permission = Permission(name=name, description=description)
            db.session.add(permission)
    
    db.session.commit()
    
    # Create default categories
    default_categories = [
        ('Electronics', 'Electronic devices and components'),
        ('Clothing', 'Apparel and accessories'),
        ('Books', 'Books and publications'),
        ('Home & Garden', 'Home improvement and gardening supplies'),
        ('Sports', 'Sports equipment and accessories')
    ]
    
    for name, description in default_categories:
        category = Category.query.filter_by(name=name).first()
        if not category:
            category = Category(name=name, description=description)
            db.session.add(category)
    
    db.session.commit()
    
    # Assign permissions to roles
    admin_role = Role.query.filter_by(name='Admin').first()
    manager_role = Role.query.filter_by(name='Manager').first()
    operator_role = Role.query.filter_by(name='Operator').first()
    viewer_role = Role.query.filter_by(name='Viewer').first()
    
    # Get all permissions
    all_permissions = Permission.query.all()
    dashboard_view = Permission.query.filter_by(name='dashboard.view').first()
    users_view = Permission.query.filter_by(name='users.view').first()
    users_create = Permission.query.filter_by(name='users.create').first()
    users_edit = Permission.query.filter_by(name='users.edit').first()
    users_delete = Permission.query.filter_by(name='users.delete').first()
    roles_manage = Permission.query.filter_by(name='roles.manage').first()
    settings_edit = Permission.query.filter_by(name='settings.edit').first()
    inventory_view = Permission.query.filter_by(name='inventory.view').first()
    inventory_edit = Permission.query.filter_by(name='inventory.edit').first()
    customers_view = Permission.query.filter_by(name='customers.view').first()
    customers_edit = Permission.query.filter_by(name='customers.edit').first()
    operations_basic = Permission.query.filter_by(name='operations.basic').first()
    analytics_view = Permission.query.filter_by(name='analytics.view').first()
    projects_view = Permission.query.filter_by(name='projects.view').first()
    projects_edit = Permission.query.filter_by(name='projects.edit').first()
    projects_delete = Permission.query.filter_by(name='projects.delete').first()
    sales_view = Permission.query.filter_by(name='sales.view').first()
    sales_edit = Permission.query.filter_by(name='sales.edit').first()
    reports_view = Permission.query.filter_by(name='reports.view').first()
    reports_export = Permission.query.filter_by(name='reports.export').first()
    
    # Admin gets all permissions
    admin_role.permissions = all_permissions
    
    # Manager gets inventory and customer management permissions
    manager_role.permissions = [
        dashboard_view, 
        inventory_view, 
        inventory_edit, 
        customers_view, 
        customers_edit,
        operations_basic,
        analytics_view,
        projects_view,
        projects_edit,
        sales_view,
        sales_edit,
        reports_view,
        reports_export
    ]
    
    # Operator gets basic operation permissions
    operator_role.permissions = [
        dashboard_view, 
        operations_basic, 
        inventory_view, 
        customers_view,
        projects_view,
        sales_view,
        reports_view
    ]
    
    # Viewer gets view-only permissions
    viewer_role.permissions = [
        dashboard_view, 
        inventory_view, 
        customers_view,
        analytics_view,
        projects_view,
        sales_view,
        reports_view
    ]
    
    db.session.commit()
    
    # Create default admin user if no users exist
    if User.query.count() == 0:
        admin_password = bcrypt.generate_password_hash('admin').decode('utf-8')
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=admin_password,
            role_id=admin_role.id,
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()

# Copy environment file from uploads if it exists
def copy_env_from_uploads():
    uploads_env_path = '/workspace/uploads/.env'
    local_env_path = '.env'
    
    if os.path.exists(uploads_env_path) and not os.path.exists(local_env_path):
        try:
            import shutil
            shutil.copy(uploads_env_path, local_env_path)
            print(f"Copied environment file from {uploads_env_path}")
        except Exception as e:
            print(f"Error copying environment file: {e}")

if __name__ == '__main__':
    try:
        # Copy environment file from uploads directory if available
        copy_env_from_uploads()
        
        # Initialize database with app
        if init_app(app):
            with app.app_context():
                # Initialize database with default data after tables are created
                init_db()
            print("Database initialized successfully with all tables and default data")
            app.run(debug=True, port=5000, host='0.0.0.0')
        else:
            print("Database initialization failed. Please check your configuration.")
    except Exception as e:
        print(f"Application initialization error: {e}")
        print("Please check configuration and try again.")