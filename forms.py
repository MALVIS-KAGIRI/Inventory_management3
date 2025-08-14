from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DecimalField, BooleanField, SubmitField, PasswordField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from datetime import datetime, timedelta

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6, message="Password must be at least 6 characters")])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match')])
    role = SelectField('Role', coerce=int, validators=[DataRequired()])
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Length(max=200)])
    submit = SubmitField('Save')

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    sku = StringField('SKU', validators=[DataRequired(), Length(max=50)])
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    supplier = SelectField('Supplier', coerce=int, validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    cost = DecimalField('Cost', validators=[DataRequired(), NumberRange(min=0)])
    quantity_in_stock = IntegerField('Quantity in Stock', validators=[DataRequired(), NumberRange(min=0)])
    reorder_level = IntegerField('Reorder Level', validators=[DataRequired(), NumberRange(min=0)])
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

class SupplierForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    contact_person = StringField('Contact Person', validators=[Length(max=100)])
    email = StringField('Email', validators=[Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Length(max=20)])
    address = TextAreaField('Address')
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

class CustomerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Length(max=20)])
    address = TextAreaField('Address')
    city = StringField('City', validators=[Length(max=50)])
    state = StringField('State', validators=[Length(max=50)])
    zip_code = StringField('ZIP Code', validators=[Length(max=10)])
    customer_type = SelectField('Customer Type', choices=[('Regular', 'Regular'), ('Premium', 'Premium'), ('VIP', 'VIP')])
    is_active = BooleanField('Active')
    submit = SubmitField('Save')

class OrderForm(FlaskForm):
    customer = SelectField('Customer', coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[('Pending', 'Pending'), ('Processing', 'Processing'), 
                                           ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')])
    notes = TextAreaField('Notes')
    submit = SubmitField('Save')

class StockAdjustmentForm(FlaskForm):
    product = SelectField('Product', coerce=int, validators=[DataRequired()])
    movement_type = SelectField('Movement Type', choices=[('IN', 'Stock In'), ('OUT', 'Stock Out'), ('ADJUSTMENT', 'Direct Adjustment')])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Process Adjustment')

class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    project_code = StringField('Project Code', validators=[Length(max=20)])
    customer = SelectField('Customer', coerce=int)
    status = SelectField('Status', choices=[('Planning', 'Planning'), ('Active', 'Active'), 
                                          ('On Hold', 'On Hold'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')])
    start_date = StringField('Start Date')
    end_date = StringField('End Date')
    estimated_budget = DecimalField('Estimated Budget', validators=[Optional(), NumberRange(min=0)])
    priority = SelectField('Priority', choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'), ('Critical', 'Critical')])
    submit = SubmitField('Save')

class ProjectAssignmentForm(FlaskForm):
    product = SelectField('Product', coerce=int, validators=[DataRequired()])
    quantity_assigned = IntegerField('Quantity to Assign', validators=[DataRequired(), NumberRange(min=1)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Assign')

class SaleForm(FlaskForm):
    customer = SelectField('Customer', coerce=int, validators=[DataRequired()])
    payment_method = SelectField('Payment Method', choices=[('Cash', 'Cash'), ('Credit Card', 'Credit Card'), 
                                                          ('Check', 'Check'), ('Bank Transfer', 'Bank Transfer')])
    payment_status = SelectField('Payment Status', choices=[('Pending', 'Pending'), ('Paid', 'Paid'), 
                                                          ('Partial', 'Partial'), ('Overdue', 'Overdue')])
    notes = TextAreaField('Notes')
    submit = SubmitField('Save')

# New Report Forms
class ReportFilterForm(FlaskForm):
    start_date = StringField('Start Date', default=lambda: (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = StringField('End Date', default=lambda: datetime.now().strftime('%Y-%m-%d'))
    export_format = SelectField('Export Format', choices=[
        ('pdf', 'PDF'), 
        ('csv', 'CSV'), 
        ('excel', 'Excel')
    ], default='pdf')
    submit = SubmitField('Generate Report')

class InventoryReportForm(ReportFilterForm):
    report_type = SelectField('Report Type', choices=[
        ('inventory_status', 'Inventory Status Report'),
        ('low_stock', 'Low Stock Report'),
        ('stock_movement', 'Stock Movement History'),
        ('inventory_valuation', 'Inventory Valuation Report'),
        ('inventory_aging', 'Inventory Aging Analysis')
    ], default='inventory_status')
    category_id = SelectField('Category', coerce=int, validators=[Optional()], default=0)
    supplier_id = SelectField('Supplier', coerce=int, validators=[Optional()], default=0)
    include_inactive = BooleanField('Include Inactive Products', default=False)

class PurchaseReportForm(ReportFilterForm):
    report_type = SelectField('Report Type', choices=[
        ('purchase_history', 'Purchase History Report'),
        ('supplier_performance', 'Supplier Performance Analysis'),
        ('cost_analysis', 'Purchase Cost Analysis'),
        ('reorder_suggestions', 'Reorder Suggestions Report'),
        ('supplier_payment', 'Supplier Payment Status')
    ], default='purchase_history')
    supplier_id = SelectField('Supplier', coerce=int, validators=[Optional()], default=0)
    payment_status = SelectField('Payment Status', choices=[
        ('all', 'All'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('overdue', 'Overdue')
    ], default='all')

class SalesReportForm(ReportFilterForm):
    report_type = SelectField('Report Type', choices=[
        ('sales_history', 'Sales History Report'),
        ('product_performance', 'Product Sales Performance'),
        ('customer_sales', 'Customer Sales Analysis'),
        ('profit_margin', 'Profit Margin Analysis'),
        ('payment_collection', 'Payment Collection Status')
    ], default='sales_history')
    customer_id = SelectField('Customer', coerce=int, validators=[Optional()], default=0)
    payment_status = SelectField('Payment Status', choices=[
        ('all', 'All'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial', 'Partial'),
        ('overdue', 'Overdue')
    ], default='all')
    product_id = SelectField('Product', coerce=int, validators=[Optional()], default=0)

class PerformanceReportForm(ReportFilterForm):
    report_type = SelectField('Report Type', choices=[
        ('sales_trend', 'Sales Trend Analysis'),
        ('inventory_turnover', 'Inventory Turnover Analysis'),
        ('revenue_forecast', 'Revenue Forecast Report'),
        ('product_profitability', 'Product Profitability Analysis'),
        ('business_growth', 'Business Growth Analysis')
    ], default='sales_trend')
    period_grouping = SelectField('Period Grouping', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly')
    ], default='monthly')

class ComplianceReportForm(ReportFilterForm):
    report_type = SelectField('Report Type', choices=[
        ('stock_audit', 'Stock Audit Report'),
        ('user_activity', 'User Activity Logs'),
        ('price_changes', 'Price Change History'),
        ('tax_report', 'Tax Calculation Report'),
        ('custom_report', 'Custom Report')
    ], default='stock_audit')
    user_id = SelectField('User', coerce=int, validators=[Optional()], default=0)
    activity_type = SelectField('Activity Type', choices=[
        ('all', 'All Activities'),
        ('login', 'User Logins'),
        ('inventory', 'Inventory Changes'),
        ('sales', 'Sales Activities'),
        ('purchase', 'Purchase Activities'),
        ('user_mgmt', 'User Management')
    ], default='all')