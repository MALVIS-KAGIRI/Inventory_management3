from reports import ReportGenerator
from models import *
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from decimal import Decimal

class PurchaseReportGenerator(ReportGenerator):
    """Handles all purchase and supplier-related reports"""
    
    @staticmethod
    def generate_supplier_performance_analysis(start_date, end_date, supplier_id=None):
        """Generate supplier performance analysis report"""
        # Get all suppliers
        query = Supplier.query
        
        if supplier_id and int(supplier_id) > 0:
            query = query.filter(Supplier.id == supplier_id)
            
        suppliers = query.all()
        
        result = []
        for supplier in suppliers:
            # In a real system, you would calculate these metrics from purchase data
            supplier_dict = ReportGenerator.convert_to_dict(supplier)
            supplier_dict['total_orders'] = 0
            supplier_dict['on_time_delivery_rate'] = 0
            supplier_dict['quality_rejection_rate'] = 0
            supplier_dict['avg_lead_time_days'] = 0
            supplier_dict['total_spend'] = 0
            
            # Get products from this supplier
            products = Product.query.filter_by(supplier_id=supplier.id).all()
            supplier_dict['product_count'] = len(products)
            
            result.append(supplier_dict)
        
        return result
    
    @staticmethod
    def generate_cost_analysis(start_date, end_date, supplier_id=None):
        """Generate purchase cost analysis report"""
        # Get all products with their suppliers
        query = db.session.query(
            Product,
            Category.name.label('category_name'),
            Supplier.name.label('supplier_name')
        ).join(Category).outerjoin(Supplier)
        
        if supplier_id and int(supplier_id) > 0:
            query = query.filter(Product.supplier_id == supplier_id)
            
        products = query.all()
        
        result = []
        for product, category_name, supplier_name in products:
            product_dict = ReportGenerator.convert_to_dict(product)
            
            # Calculate margins
            margin = product.price - product.cost
            margin_percentage = (margin / product.cost * 100) if product.cost else 0
            
            # Add additional data
            product_dict['category_name'] = category_name
            product_dict['supplier_name'] = supplier_name or "No Supplier"
            product_dict['margin'] = margin
            product_dict['margin_percentage'] = round(float(margin_percentage), 2)
            
            result.append(product_dict)
        
        return result
        
    @staticmethod
    def generate_reorder_suggestions_report(start_date, end_date, supplier_id=None):
        """Generate reorder suggestions report"""
        query = db.session.query(
            Product,
            Category.name.label('category_name'),
            Supplier.name.label('supplier_name')
        ).join(Category).outerjoin(Supplier).filter(Product.quantity_in_stock <= Product.reorder_level)
        
        if supplier_id and int(supplier_id) > 0:
            query = query.filter(Product.supplier_id == supplier_id)
            
        products = query.all()
        
        result = []
        for product, category_name, supplier_name in products:
            product_dict = ReportGenerator.convert_to_dict(product)
            
            # Calculate reorder amount - typically reorder to get to 2x reorder_level
            reorder_amount = (product.reorder_level * 2) - product.quantity_in_stock
            estimated_cost = reorder_amount * product.cost
            
            # Add additional data
            product_dict['category_name'] = category_name
            product_dict['supplier_name'] = supplier_name or "No Supplier"
            product_dict['reorder_amount'] = reorder_amount
            product_dict['estimated_cost'] = estimated_cost
            product_dict['priority'] = "High" if product.quantity_in_stock == 0 else "Medium" if product.quantity_in_stock < product.reorder_level else "Low"
            
            result.append(product_dict)
        
        # Sort by priority and then by quantity in stock
        result.sort(key=lambda x: (0 if x['priority'] == "High" else 1 if x['priority'] == "Medium" else 2, x['quantity_in_stock']))
        
        return result