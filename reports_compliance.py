from reports import ReportGenerator
from models import *
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from decimal import Decimal

class ComplianceReportGenerator(ReportGenerator):
    """Handles all compliance, audit, and custom reports"""
    
    @staticmethod
    def generate_stock_audit_report(start_date, end_date, category_id=None, supplier_id=None):
        """Generate stock audit report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Get all products with their stock movements in the period
        query = db.session.query(
            Product,
            Category.name.label('category_name'),
            Supplier.name.label('supplier_name')
        ).join(Category).outerjoin(Supplier)
        
        # Apply filters
        if category_id and int(category_id) > 0:
            query = query.filter(Product.category_id == category_id)
        if supplier_id and int(supplier_id) > 0:
            query = query.filter(Product.supplier_id == supplier_id)
            
        products = query.all()
        
        result = []
        for product, category_name, supplier_name in products:
            # Get stock movements for this product in the period
            movements = StockMovement.query.filter(
                StockMovement.product_id == product.id,
                StockMovement.created_at.between(start_dt, end_dt)
            ).all()
            
            # Calculate movement totals
            total_in = sum([m.quantity for m in movements if m.movement_type == 'IN'])
            total_out = sum([m.quantity for m in movements if m.movement_type == 'OUT'])
            total_adjustments = sum([m.quantity for m in movements if m.movement_type == 'ADJUSTMENT'])
            
            # Calculate expected vs actual stock
            # This is simplified - in reality you'd track beginning inventory
            net_movement = total_in - total_out + total_adjustments
            
            product_dict = ReportGenerator.convert_to_dict(product)
            product_dict['category_name'] = category_name
            product_dict['supplier_name'] = supplier_name or "No Supplier"
            product_dict['total_in'] = total_in
            product_dict['total_out'] = total_out
            product_dict['total_adjustments'] = total_adjustments
            product_dict['net_movement'] = net_movement
            product_dict['current_stock'] = product.quantity_in_stock
            product_dict['movement_count'] = len(movements)
            product_dict['audit_status'] = 'Normal' if abs(total_adjustments) < 5 else 'Review Required'
            
            result.append(product_dict)
        
        # Sort by audit status (review required first)
        result.sort(key=lambda x: (0 if x['audit_status'] == 'Review Required' else 1, x['name']))
        
        return result
    
    @staticmethod
    def generate_user_activity_report(start_date, end_date, user_id=None, activity_type='all'):
        """Generate user activity logs report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        result = []
        
        # Get user login activities
        if activity_type in ['all', 'login']:
            users_query = User.query
            if user_id and int(user_id) > 0:
                users_query = users_query.filter(User.id == user_id)
                
            users = users_query.filter(
                User.last_login.between(start_dt, end_dt) if User.last_login else False
            ).all()
            
            for user in users:
                if user.last_login and start_dt <= user.last_login <= end_dt:
                    result.append({
                        'user_id': user.id,
                        'username': user.username,
                        'activity_type': 'Login',
                        'activity_date': user.last_login,
                        'details': f"User {user.username} logged in",
                        'ip_address': 'N/A',  # Would need to track this
                        'status': 'Success'
                    })
        
        # Get inventory activities
        if activity_type in ['all', 'inventory']:
            movements_query = db.session.query(
                StockMovement,
                User.username.label('user_name'),
                Product.name.label('product_name')
            ).outerjoin(User, StockMovement.created_by == User.id).join(Product)
            
            if user_id and int(user_id) > 0:
                movements_query = movements_query.filter(StockMovement.created_by == user_id)
                
            movements = movements_query.filter(
                StockMovement.created_at.between(start_dt, end_dt)
            ).all()
            
            for movement, user_name, product_name in movements:
                result.append({
                    'user_id': movement.created_by,
                    'username': user_name or 'System',
                    'activity_type': 'Inventory Change',
                    'activity_date': movement.created_at,
                    'details': f"{movement.movement_type} {movement.quantity} units of {product_name}",
                    'reference': movement.reference_type or 'Manual',
                    'status': 'Completed'
                })
        
        # Get sales activities
        if activity_type in ['all', 'sales']:
            sales_query = db.session.query(
                Sale,
                User.username.label('user_name'),
                Customer.first_name.label('customer_first_name'),
                Customer.last_name.label('customer_last_name')
            ).outerjoin(User, Sale.created_by == User.id).join(Customer)
            
            if user_id and int(user_id) > 0:
                sales_query = sales_query.filter(Sale.created_by == user_id)
                
            sales = sales_query.filter(
                Sale.created_at.between(start_dt, end_dt)
            ).all()
            
            for sale, user_name, customer_first_name, customer_last_name in sales:
                result.append({
                    'user_id': sale.created_by,
                    'username': user_name or 'System',
                    'activity_type': 'Sale Created',
                    'activity_date': sale.created_at,
                    'details': f"Sale {sale.sale_number} for {customer_first_name} {customer_last_name} - ${sale.total_amount}",
                    'reference': sale.sale_number,
                    'status': sale.payment_status
                })
        
        # Sort by activity date (most recent first)
        result.sort(key=lambda x: x['activity_date'], reverse=True)
        
        return result
    
    @staticmethod
    def generate_price_changes_report(start_date, end_date, category_id=None):
        """Generate price change history report"""
        # This is a placeholder since we don't track price history
        # In a real system, you would have a PriceHistory table
        
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Get all products that were updated in the period
        query = db.session.query(
            Product,
            Category.name.label('category_name')
        ).join(Category).filter(Product.updated_at.between(start_dt, end_dt))
        
        if category_id and int(category_id) > 0:
            query = query.filter(Product.category_id == category_id)
            
        products = query.all()
        
        result = []
        for product, category_name in products:
            # This is simulated data - in reality you'd track price history
            result.append({
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'category_name': category_name,
                'change_date': product.updated_at,
                'old_price': product.price * Decimal('0.95'),  # Simulated old price
                'new_price': product.price,
                'price_change': product.price * Decimal('0.05'),  # Simulated change
                'change_percentage': 5.26,  # Simulated percentage
                'changed_by': 'System',  # Would track this in reality
                'reason': 'Regular price update'
            })
        
        # Sort by change date (most recent first)
        result.sort(key=lambda x: x['change_date'], reverse=True)
        
        return result
    
    @staticmethod
    def generate_tax_report(start_date, end_date):
        """Generate tax calculation report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Get all sales in the period
        sales = db.session.query(
            Sale,
            Customer.first_name.label('customer_first_name'),
            Customer.last_name.label('customer_last_name')
        ).join(Customer).filter(Sale.sale_date.between(start_dt, end_dt)).all()
        
        result = []
        total_tax_collected = Decimal('0.00')
        
        for sale, customer_first_name, customer_last_name in sales:
            tax_amount = sale.tax_amount or Decimal('0.00')
            total_tax_collected += tax_amount
            
            result.append({
                'sale_id': sale.id,
                'sale_number': sale.sale_number,
                'sale_date': sale.sale_date,
                'customer_name': f"{customer_first_name} {customer_last_name}",
                'subtotal': sale.subtotal,
                'tax_amount': tax_amount,
                'total_amount': sale.total_amount,
                'tax_rate': (tax_amount / sale.subtotal * 100) if sale.subtotal else 0
            })
        
        # Add summary row
        result.append({
            'sale_number': 'TOTAL',
            'customer_name': '',
            'subtotal': sum([s['subtotal'] or 0 for s in result[:-1]]),
            'tax_amount': total_tax_collected,
            'total_amount': sum([s['total_amount'] or 0 for s in result[:-1]]),
            'tax_rate': ''
        })
        
        return result
    
    @staticmethod
    def generate_custom_report(start_date, end_date, report_config=None):
        """Generate custom report based on configuration"""
        # This is a flexible report generator that can be customized
        # based on user requirements
        
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Default custom report: Combined sales and inventory summary
        result = []
        
        # Sales summary
        total_sales = db.session.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date.between(start_dt, end_dt)
        ).scalar() or 0
        
        order_count = db.session.query(func.count(Sale.id)).filter(
            Sale.sale_date.between(start_dt, end_dt)
        ).scalar() or 0
        
        # Inventory summary
        total_products = Product.query.filter(Product.is_active == True).count()
        low_stock_count = Product.query.filter(
            Product.quantity_in_stock <= Product.reorder_level
        ).count()
        
        # Customer summary
        total_customers = Customer.query.filter(Customer.is_active == True).count()
        active_customers = db.session.query(func.count(func.distinct(Sale.customer_id))).filter(
            Sale.sale_date.between(start_dt, end_dt)
        ).scalar() or 0
        
        result = [{
            'report_section': 'Sales Summary',
            'metric': 'Total Revenue',
            'value': total_sales,
            'period': f"{start_date} to {end_date}"
        }, {
            'report_section': 'Sales Summary',
            'metric': 'Total Orders',
            'value': order_count,
            'period': f"{start_date} to {end_date}"
        }, {
            'report_section': 'Inventory Summary',
            'metric': 'Total Active Products',
            'value': total_products,
            'period': 'Current'
        }, {
            'report_section': 'Inventory Summary',
            'metric': 'Low Stock Items',
            'value': low_stock_count,
            'period': 'Current'
        }, {
            'report_section': 'Customer Summary',
            'metric': 'Total Customers',
            'value': total_customers,
            'period': 'Current'
        }, {
            'report_section': 'Customer Summary',
            'metric': 'Active Customers',
            'value': active_customers,
            'period': f"{start_date} to {end_date}"
        }]
        
        return result