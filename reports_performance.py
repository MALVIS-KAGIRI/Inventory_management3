from reports import ReportGenerator
from models import *
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, extract
from decimal import Decimal

class PerformanceReportGenerator(ReportGenerator):
    """Handles all performance and forecasting reports"""
    
    @staticmethod
    def generate_sales_trend_report(start_date, end_date, period_grouping='monthly'):
        """Generate sales trend analysis report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Determine grouping function based on period
        if period_grouping == 'daily':
            date_func = func.date(Sale.sale_date)
        elif period_grouping == 'weekly':
            date_func = func.strftime('%Y-%W', Sale.sale_date)
        elif period_grouping == 'monthly':
            date_func = func.strftime('%Y-%m', Sale.sale_date)
        elif period_grouping == 'quarterly':
            date_func = func.strftime('%Y-Q%q', Sale.sale_date)
        else:  # yearly
            date_func = func.strftime('%Y', Sale.sale_date)
        
        # Query sales aggregated by the specified period
        query = db.session.query(
            date_func.label('period'),
            func.count(Sale.id).label('order_count'),
            func.sum(Sale.total_amount).label('total_revenue')
        ).filter(Sale.sale_date.between(start_dt, end_dt)).group_by('period').order_by('period')
        
        sales_trend = query.all()
        
        # Convert to dictionary
        result = []
        for period, order_count, total_revenue in sales_trend:
            period_dict = {
                'period': period,
                'order_count': order_count or 0,
                'total_revenue': total_revenue or 0
            }
            result.append(period_dict)
        
        return result
    
    @staticmethod
    def generate_inventory_turnover_report(start_date, end_date, period_grouping='monthly'):
        """Generate inventory turnover analysis report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Get all products
        products = Product.query.filter(Product.is_active == True).all()
        
        result = []
        for product in products:
            # Calculate sales in the period
            sales_quantity = db.session.query(func.sum(SaleItem.quantity)).join(Sale).filter(
                SaleItem.product_id == product.id,
                Sale.sale_date.between(start_dt, end_dt)
            ).scalar() or 0
            
            # Calculate average inventory (simplified - using current stock)
            avg_inventory = product.quantity_in_stock
            
            # Calculate turnover ratio
            if avg_inventory > 0:
                turnover_ratio = sales_quantity / avg_inventory
            else:
                turnover_ratio = 0
            
            # Calculate days to sell
            days_to_sell = (365 / turnover_ratio) if turnover_ratio > 0 else 0
            
            product_dict = {
                'product_id': product.id,
                'product_name': product.name,
                'sku': product.sku,
                'category_name': product.category.name,
                'current_stock': product.quantity_in_stock,
                'sales_quantity': sales_quantity,
                'turnover_ratio': round(float(turnover_ratio), 2),
                'days_to_sell': round(float(days_to_sell), 0),
                'performance': 'Fast' if turnover_ratio > 12 else 'Medium' if turnover_ratio > 4 else 'Slow'
            }
            
            result.append(product_dict)
        
        # Sort by turnover ratio (highest first)
        result.sort(key=lambda x: x['turnover_ratio'], reverse=True)
        
        return result
    
    @staticmethod
    def generate_revenue_forecast_report(start_date, end_date, period_grouping='monthly'):
        """Generate revenue forecast report"""
        # This is a simplified forecast based on historical trends
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Get historical sales data for the last 6 months
        six_months_ago = start_dt - timedelta(days=180)
        
        historical_query = db.session.query(
            func.strftime('%Y-%m', Sale.sale_date).label('period'),
            func.sum(Sale.total_amount).label('total_revenue')
        ).filter(Sale.sale_date.between(six_months_ago, start_dt)).group_by('period').order_by('period')
        
        historical_data = historical_query.all()
        
        result = []
        total_historical_revenue = sum([revenue for _, revenue in historical_data])
        avg_monthly_revenue = total_historical_revenue / len(historical_data) if historical_data else 0
        
        # Simple forecast - apply 5% growth rate
        growth_rate = 1.05
        
        # Generate forecast for next 3 months
        forecast_start = end_dt
        for i in range(3):
            forecast_month = forecast_start + timedelta(days=30 * i)
            forecasted_revenue = avg_monthly_revenue * (growth_rate ** (i + 1))
            
            forecast_dict = {
                'period': forecast_month.strftime('%Y-%m'),
                'type': 'Forecast',
                'revenue': round(float(forecasted_revenue), 2),
                'confidence': 'Medium'
            }
            result.append(forecast_dict)
        
        return result
    
    @staticmethod
    def generate_product_profitability_report(start_date, end_date):
        """Generate product profitability analysis report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Get product sales data
        query = db.session.query(
            Product.id,
            Product.name,
            Product.sku,
            Product.cost,
            Product.price,
            Category.name.label('category_name'),
            func.sum(SaleItem.quantity).label('total_quantity_sold'),
            func.sum(SaleItem.total_price).label('total_revenue')
        ).join(SaleItem).join(Sale).join(Category).filter(
            Sale.sale_date.between(start_dt, end_dt)
        ).group_by(Product.id, Product.name, Product.sku, Product.cost, Product.price, Category.name)
        
        product_sales = query.all()
        
        result = []
        for prod_id, name, sku, cost, price, category_name, quantity_sold, revenue in product_sales:
            # Calculate profitability metrics
            total_cost = cost * quantity_sold
            profit = revenue - total_cost
            profit_margin = (profit / revenue * 100) if revenue else 0
            profit_per_unit = (price - cost)
            
            product_dict = {
                'product_id': prod_id,
                'name': name,
                'sku': sku,
                'category_name': category_name,
                'unit_cost': cost,
                'unit_price': price,
                'profit_per_unit': profit_per_unit,
                'quantity_sold': quantity_sold,
                'total_revenue': revenue,
                'total_cost': total_cost,
                'total_profit': profit,
                'profit_margin': round(float(profit_margin), 2),
                'profitability_rank': 'High' if profit_margin > 40 else 'Medium' if profit_margin > 20 else 'Low'
            }
            
            result.append(product_dict)
        
        # Sort by total profit (highest first)
        result.sort(key=lambda x: float(x['total_profit']), reverse=True)
        
        return result
    
    @staticmethod
    def generate_business_growth_report(start_date, end_date):
        """Generate business growth analysis report"""
        start_dt = ReportGenerator.format_date(start_date)
        end_dt = ReportGenerator.format_date(end_date) + timedelta(days=1)
        
        # Calculate period length
        period_days = (end_dt - start_dt).days
        
        # Get current period data
        current_revenue = db.session.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date.between(start_dt, end_dt)
        ).scalar() or 0
        
        current_orders = db.session.query(func.count(Sale.id)).filter(
            Sale.sale_date.between(start_dt, end_dt)
        ).scalar() or 0
        
        current_customers = db.session.query(func.count(func.distinct(Sale.customer_id))).filter(
            Sale.sale_date.between(start_dt, end_dt)
        ).scalar() or 0
        
        # Get previous period data for comparison
        prev_start = start_dt - timedelta(days=period_days)
        prev_end = start_dt
        
        prev_revenue = db.session.query(func.sum(Sale.total_amount)).filter(
            Sale.sale_date.between(prev_start, prev_end)
        ).scalar() or 0
        
        prev_orders = db.session.query(func.count(Sale.id)).filter(
            Sale.sale_date.between(prev_start, prev_end)
        ).scalar() or 0
        
        prev_customers = db.session.query(func.count(func.distinct(Sale.customer_id))).filter(
            Sale.sale_date.between(prev_start, prev_end)
        ).scalar() or 0
        
        # Calculate growth rates
        revenue_growth = ((current_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0
        order_growth = ((current_orders - prev_orders) / prev_orders * 100) if prev_orders else 0
        customer_growth = ((current_customers - prev_customers) / prev_customers * 100) if prev_customers else 0
        
        result = [{
            'metric': 'Revenue',
            'current_period': current_revenue,
            'previous_period': prev_revenue,
            'growth_rate': round(float(revenue_growth), 2),
            'trend': 'Up' if revenue_growth > 0 else 'Down' if revenue_growth < 0 else 'Flat'
        }, {
            'metric': 'Orders',
            'current_period': current_orders,
            'previous_period': prev_orders,
            'growth_rate': round(float(order_growth), 2),
            'trend': 'Up' if order_growth > 0 else 'Down' if order_growth < 0 else 'Flat'
        }, {
            'metric': 'Customers',
            'current_period': current_customers,
            'previous_period': prev_customers,
            'growth_rate': round(float(customer_growth), 2),
            'trend': 'Up' if customer_growth > 0 else 'Down' if customer_growth < 0 else 'Flat'
        }]
        
        return result