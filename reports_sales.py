from reports import ReportGenerator
from models import *
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from decimal import Decimal

class SalesReportGenerator(ReportGenerator):
    """Handles all sales-related reports"""
    
    @staticmethod
    def generate_sales_history_report(start_date, end_date, customer_id=None, payment_status=None):
        """Generate sales history report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        query = db.session.query(
            Sale,
            Customer.first_name.label('customer_first_name'),
            Customer.last_name.label('customer_last_name'),
            User.username.label('created_by_username')
        ).join(Customer).outerjoin(User, Sale.created_by == User.id)
        
        # Apply filters
        query = query.filter(Sale.sale_date.between(start_dt, end_dt))
        if customer_id and int(customer_id) > 0:
            query = query.filter(Sale.customer_id == customer_id)
        if payment_status and payment_status != 'all':
            query = query.filter(Sale.payment_status == payment_status.capitalize())
            
        sales = query.order_by(Sale.sale_date.desc()).all()
        
        # Convert to dictionary with additional information
        result = []
        for sale, customer_first_name, customer_last_name, created_by_username in sales:
            sale_dict = ReportGenerator.convert_to_dict(sale)
            
            # Add additional data
            sale_dict['customer_name'] = f"{customer_first_name} {customer_last_name}"
            sale_dict['created_by_username'] = created_by_username or "System"
            
            # Get sale items
            sale_items = SaleItem.query.filter_by(sale_id=sale.id).all()
            sale_dict['item_count'] = len(sale_items)
            
            result.append(sale_dict)
        
        return result
    
    @staticmethod
    def generate_product_performance_report(start_date, end_date, product_id=None):
        """Generate product sales performance report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Calculate product sales by quantity and revenue
        query = db.session.query(
            Product.id,
            Product.name,
            Product.sku,
            Category.name.label('category_name'),
            func.sum(SaleItem.quantity).label('total_quantity_sold'),
            func.sum(SaleItem.total_price).label('total_revenue')
        ).join(SaleItem).join(Sale).join(Category).filter(Sale.sale_date.between(start_dt, end_dt)).group_by(
            Product.id, Product.name, Product.sku, Category.name
        )
        
        if product_id and int(product_id) > 0:
            query = query.filter(Product.id == product_id)
            
        product_sales = query.all()
        
        # Convert to dictionary with additional calculations
        result = []
        for prod_id, name, sku, category_name, total_quantity_sold, total_revenue in product_sales:
            # Get the product
            product = Product.query.get(prod_id)
            
            # Calculate metrics
            total_cost = product.cost * (total_quantity_sold or 0)
            profit = (total_revenue or 0) - total_cost
            profit_margin = ((profit / total_revenue) * 100) if total_revenue else 0
            
            product_dict = {
                'id': prod_id,
                'name': name,
                'sku': sku,
                'category_name': category_name,
                'price': product.price,
                'cost': product.cost,
                'current_stock': product.quantity_in_stock,
                'total_quantity_sold': total_quantity_sold or 0,
                'total_revenue': total_revenue or 0,
                'total_cost': total_cost,
                'profit': profit,
                'profit_margin': round(float(profit_margin), 2)
            }
            
            result.append(product_dict)
        
        # Sort by revenue (highest first)
        result.sort(key=lambda x: float(x['total_revenue']), reverse=True)
        
        return result
    
    @staticmethod
    def generate_customer_sales_report(start_date, end_date, customer_id=None):
        """Generate customer sales analysis report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Calculate customer sales
        query = db.session.query(
            Customer.id,
            Customer.first_name,
            Customer.last_name,
            Customer.customer_type,
            func.count(Sale.id).label('total_orders'),
            func.sum(Sale.total_amount).label('total_spent')
        ).join(Sale).filter(Sale.sale_date.between(start_dt, end_dt)).group_by(
            Customer.id, Customer.first_name, Customer.last_name, Customer.customer_type
        )
        
        if customer_id and int(customer_id) > 0:
            query = query.filter(Customer.id == customer_id)
            
        customer_sales = query.all()
        
        # Convert to dictionary with additional calculations
        result = []
        for cust_id, first_name, last_name, customer_type, total_orders, total_spent in customer_sales:
            avg_order_value = (total_spent / total_orders) if total_orders else 0
            
            customer_dict = {
                'id': cust_id,
                'name': f"{first_name} {last_name}",
                'customer_type': customer_type,
                'total_orders': total_orders or 0,
                'total_spent': total_spent or 0,
                'avg_order_value': avg_order_value
            }
            
            # Get most recent order
            last_order = Sale.query.filter_by(customer_id=cust_id).order_by(Sale.sale_date.desc()).first()
            if last_order:
                customer_dict['last_order_date'] = last_order.sale_date
                customer_dict['days_since_last_order'] = (datetime.now() - last_order.sale_date).days
            
            result.append(customer_dict)
        
        # Sort by total spent (highest first)
        result.sort(key=lambda x: float(x['total_spent']), reverse=True)
        
        return result
    
    @staticmethod
    def generate_profit_margin_report(start_date, end_date, product_id=None):
        """Generate profit margin analysis report"""
        # Similar to product performance but with focus on margins
        return SalesReportGenerator.generate_product_performance_report(start_date, end_date, product_id)
    
    @staticmethod
    def generate_payment_collection_report(start_date, end_date, payment_status=None):
        """Generate payment collection status report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        query = db.session.query(
            Sale,
            Customer.first_name.label('customer_first_name'),
            Customer.last_name.label('customer_last_name')
        ).join(Customer)
        
        # Apply filters
        query = query.filter(Sale.sale_date.between(start_dt, end_dt))
        if payment_status and payment_status != 'all':
            query = query.filter(Sale.payment_status == payment_status.capitalize())
            
        sales = query.order_by(Sale.payment_status, Sale.sale_date).all()
        
        # Convert to dictionary with additional information
        result = []
        for sale, customer_first_name, customer_last_name in sales:
            sale_dict = ReportGenerator.convert_to_dict(sale)
            
            # Add additional data
            sale_dict['customer_name'] = f"{customer_first_name} {customer_last_name}"
            
            # Calculate days overdue if applicable
            if sale.payment_status == 'Pending' or sale.payment_status == 'Overdue':
                days_since_sale = (datetime.now() - sale.sale_date).days
                sale_dict['days_outstanding'] = days_since_sale
                # Mark as overdue if more than 30 days
                sale_dict['status'] = 'Overdue' if days_since_sale > 30 else 'Pending'
            else:
                sale_dict['days_outstanding'] = 0
                sale_dict['status'] = sale.payment_status
            
            result.append(sale_dict)
        
        return result