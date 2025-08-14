from reports import ReportGenerator
from models import *
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from decimal import Decimal

class InventoryReportGenerator(ReportGenerator):
    """Handles all inventory-specific reports"""
    
    @staticmethod
    def generate_inventory_status_report(start_date, end_date, category_id=None, supplier_id=None, include_inactive=False):
        """Generate inventory status report"""
        query = db.session.query(
            Product,
            Category.name.label('category_name'),
            Supplier.name.label('supplier_name')
        ).join(Category).outerjoin(Supplier)
        
        # Apply filters
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        if category_id and int(category_id) > 0:
            query = query.filter(Product.category_id == category_id)
        if supplier_id and int(supplier_id) > 0:
            query = query.filter(Product.supplier_id == supplier_id)
            
        products = query.all()
        
        # Convert to dictionary with additional calculations
        result = []
        for product, category_name, supplier_name in products:
            product_dict = ReportGenerator.convert_to_dict(product)
            
            # Add additional data
            product_dict['category_name'] = category_name
            product_dict['supplier_name'] = supplier_name or "No Supplier"
            product_dict['stock_value'] = float(product.price) * product.quantity_in_stock
            product_dict['needs_reorder'] = "Yes" if product.quantity_in_stock <= product.reorder_level else "No"
            
            result.append(product_dict)
            
        # Sort by stock status (low stock first)
        result.sort(key=lambda x: (0 if x['needs_reorder'] == 'Yes' else 1, x['quantity_in_stock']))
        
        return result
    
    @staticmethod
    def generate_low_stock_report(start_date, end_date, category_id=None, supplier_id=None):
        """Generate low stock report"""
        query = db.session.query(
            Product,
            Category.name.label('category_name'),
            Supplier.name.label('supplier_name')
        ).join(Category).outerjoin(Supplier).filter(Product.quantity_in_stock <= Product.reorder_level)
        
        # Apply filters
        query = query.filter(Product.is_active == True)
        if category_id and int(category_id) > 0:
            query = query.filter(Product.category_id == category_id)
        if supplier_id and int(supplier_id) > 0:
            query = query.filter(Product.supplier_id == supplier_id)
            
        products = query.all()
        
        # Convert to dictionary with additional calculations
        result = []
        for product, category_name, supplier_name in products:
            product_dict = ReportGenerator.convert_to_dict(product)
            
            # Add additional data
            product_dict['category_name'] = category_name
            product_dict['supplier_name'] = supplier_name or "No Supplier"
            product_dict['stock_value'] = float(product.price) * product.quantity_in_stock
            product_dict['shortage'] = max(0, product.reorder_level - product.quantity_in_stock)
            product_dict['shortage_value'] = float(product.price) * product_dict['shortage']
            
            result.append(product_dict)
            
        # Sort by stock shortage (highest shortage first)
        result.sort(key=lambda x: x['shortage'], reverse=True)
        
        return result
        
    @staticmethod
    def generate_stock_movement_history(start_date, end_date, category_id=None, supplier_id=None):
        """Generate stock movement history report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        query = db.session.query(
            StockMovement,
            Product.name.label('product_name'),
            Product.sku.label('product_sku'),
            Category.name.label('category_name'),
            User.username.label('user_name')
        ).join(Product).join(Category).outerjoin(User, StockMovement.created_by == User.id)
        
        # Apply filters
        query = query.filter(StockMovement.created_at.between(start_dt, end_dt))
        if category_id and int(category_id) > 0:
            query = query.filter(Product.category_id == category_id)
        if supplier_id and int(supplier_id) > 0:
            query = query.filter(Product.supplier_id == supplier_id)
            
        movements = query.order_by(StockMovement.created_at.desc()).all()
        
        # Convert to dictionary with additional calculations
        result = []
        for movement, product_name, product_sku, category_name, user_name in movements:
            movement_dict = ReportGenerator.convert_to_dict(movement)
            
            # Add additional data
            movement_dict['product_name'] = product_name
            movement_dict['product_sku'] = product_sku
            movement_dict['category_name'] = category_name
            movement_dict['user_name'] = user_name or "System"
            
            # Format the reference information
            if movement.reference_type == 'ADJUSTMENT':
                movement_dict['reference'] = 'Manual Adjustment'
            elif movement.reference_type == 'ORDER':
                order = Order.query.filter_by(id=movement.reference_id).first()
                movement_dict['reference'] = f"Order #{order.order_number}" if order else "Unknown Order"
            elif movement.reference_type == 'PROJECT':
                project = Project.query.filter_by(id=movement.reference_id).first()
                movement_dict['reference'] = f"Project: {project.name}" if project else "Unknown Project"
            else:
                movement_dict['reference'] = movement.reference_type or "N/A"
            
            result.append(movement_dict)
        
        return result
        
    @staticmethod
    def generate_inventory_valuation_report(start_date, end_date, category_id=None, supplier_id=None, include_inactive=False):
        """Generate inventory valuation report"""
        query = db.session.query(
            Product,
            Category.name.label('category_name'),
            Supplier.name.label('supplier_name')
        ).join(Category).outerjoin(Supplier)
        
        # Apply filters
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        if category_id and int(category_id) > 0:
            query = query.filter(Product.category_id == category_id)
        if supplier_id and int(supplier_id) > 0:
            query = query.filter(Product.supplier_id == supplier_id)
            
        products = query.all()
        
        # Convert to dictionary with additional calculations
        result = []
        total_cost_value = Decimal('0.00')
        total_retail_value = Decimal('0.00')
        total_profit_potential = Decimal('0.00')
        
        for product, category_name, supplier_name in products:
            product_dict = ReportGenerator.convert_to_dict(product)
            
            # Calculate values
            cost_value = product.cost * product.quantity_in_stock
            retail_value = product.price * product.quantity_in_stock
            profit_potential = retail_value - cost_value
            margin_percentage = ((retail_value - cost_value) / cost_value * 100) if cost_value else 0
            
            # Add to totals
            total_cost_value += cost_value
            total_retail_value += retail_value
            total_profit_potential += profit_potential
            
            # Add additional data
            product_dict['category_name'] = category_name
            product_dict['supplier_name'] = supplier_name or "No Supplier"
            product_dict['cost_value'] = cost_value
            product_dict['retail_value'] = retail_value
            product_dict['profit_potential'] = profit_potential
            product_dict['margin_percentage'] = round(float(margin_percentage), 2)
            
            result.append(product_dict)
        
        # Sort by retail value (highest first)
        result.sort(key=lambda x: float(x['retail_value']), reverse=True)
        
        # Add a summary row
        summary = {
            'name': 'TOTAL',
            'sku': '',
            'cost_value': total_cost_value,
            'retail_value': total_retail_value,
            'profit_potential': total_profit_potential,
            'margin_percentage': round(float((total_profit_potential / total_cost_value * 100) if total_cost_value else 0), 2)
        }
        result.append(summary)
        
        return result
    
    @staticmethod
    def generate_inventory_aging_analysis(start_date, end_date, category_id=None, supplier_id=None):
        """Generate inventory aging analysis report"""
        today = datetime.now().date()
        
        query = db.session.query(
            Product,
            Category.name.label('category_name'),
            Supplier.name.label('supplier_name'),
            func.max(StockMovement.created_at).label('last_movement_date')
        ).join(Category).outerjoin(Supplier).outerjoin(
            StockMovement, and_(
                StockMovement.product_id == Product.id,
                StockMovement.movement_type.in_(['IN', 'ADJUSTMENT'])
            )
        ).filter(Product.quantity_in_stock > 0)
        
        # Apply filters
        query = query.filter(Product.is_active == True)
        if category_id and int(category_id) > 0:
            query = query.filter(Product.category_id == category_id)
        if supplier_id and int(supplier_id) > 0:
            query = query.filter(Product.supplier_id == supplier_id)
            
        query = query.group_by(Product, Category.name, Supplier.name)
        products = query.all()
        
        # Convert to dictionary with additional calculations
        result = []
        for product, category_name, supplier_name, last_movement_date in products:
            product_dict = ReportGenerator.convert_to_dict(product)
            
            # Calculate aging
            if last_movement_date:
                days_in_stock = (today - last_movement_date.date()).days
            else:
                # If no movement history, use creation date
                days_in_stock = (today - product.created_at.date()).days
            
            # Determine aging category
            if days_in_stock <= 30:
                aging_category = "< 30 days"
            elif days_in_stock <= 60:
                aging_category = "30-60 days"
            elif days_in_stock <= 90:
                aging_category = "60-90 days"
            elif days_in_stock <= 180:
                aging_category = "90-180 days"
            else:
                aging_category = "> 180 days"
            
            # Calculate value
            inventory_value = product.quantity_in_stock * product.cost
            
            # Add additional data
            product_dict['category_name'] = category_name
            product_dict['supplier_name'] = supplier_name or "No Supplier"
            product_dict['last_movement_date'] = last_movement_date
            product_dict['days_in_stock'] = days_in_stock
            product_dict['aging_category'] = aging_category
            product_dict['inventory_value'] = inventory_value
            
            result.append(product_dict)
        
        # Sort by days in stock (oldest first)
        result.sort(key=lambda x: x['days_in_stock'], reverse=True)
        
        return result