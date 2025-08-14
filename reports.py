from flask import render_template, request, make_response, send_file
from datetime import datetime, timedelta
from models import *
from sqlalchemy import func, desc, asc, and_, or_
import csv
import io
import xlsxwriter
from weasyprint import HTML
import tempfile
import os
import json
from collections import defaultdict
from decimal import Decimal

class ReportGenerator:
    """Base report generator class with common functionality"""
    
    @staticmethod
    def format_date(date_str):
        """Convert string date to datetime object"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return datetime.now() - timedelta(days=30) if date_str == 'start_date' else datetime.now()
    
    @staticmethod
    def convert_to_dict(item):
        """Convert SQLAlchemy object to dictionary"""
        return {c.name: getattr(item, c.name) for c in item.__table__.columns}
    
    @staticmethod
    def decimal_default(obj):
        """Handle Decimal serialization for JSON"""
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
    
    @staticmethod
    def export_as_csv(data, filename, headers):
        """Generate CSV file from data"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(headers)
        
        # Write data rows
        for row in data:
            csv_row = []
            for key in headers:
                value = row.get(key, '')
                # Handle datetime objects
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M')
                elif isinstance(value, Decimal):
                    value = float(value)
                csv_row.append(value)
            writer.writerow(csv_row)
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename}.csv'
        response.headers['Content-type'] = 'text/csv'
        return response
    
    @staticmethod
    def export_as_excel(data, filename, headers):
        """Generate Excel file from data"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Report')
        
        # Add header formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4F46E5',
            'color': 'white',
            'border': 1
        })
        
        # Add cell formatting
        cell_format = workbook.add_format({
            'border': 1
        })
        
        # Add date formatting
        date_format = workbook.add_format({
            'border': 1,
            'num_format': 'yyyy-mm-dd'
        })
        
        # Add money formatting
        money_format = workbook.add_format({
            'border': 1,
            'num_format': '$#,##0.00'
        })
        
        # Write headers
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Write data rows
        for row_idx, row in enumerate(data, start=1):
            for col_idx, key in enumerate(headers):
                value = row.get(key, '')
                
                # Format based on value type
                if isinstance(value, datetime):
                    worksheet.write_datetime(row_idx, col_idx, value, date_format)
                elif isinstance(value, (int, float, Decimal)):
                    if 'price' in key or 'cost' in key or 'amount' in key or 'budget' in key or 'value' in key:
                        worksheet.write_number(row_idx, col_idx, float(value), money_format)
                    else:
                        worksheet.write_number(row_idx, col_idx, float(value), cell_format)
                else:
                    worksheet.write(row_idx, col_idx, value, cell_format)
        
        # Auto-adjust columns to fit content
        for i, _ in enumerate(headers):
            worksheet.set_column(i, i, 15)
        
        workbook.close()
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
        response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response
    
    @staticmethod
    def export_as_pdf(data, filename, headers, title, logo=None):
        """Generate PDF file from data"""
        # Create a temporary HTML file
        context = {
            'title': title,
            'headers': headers,
            'data': data,
            'current_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'logo': logo
        }
        
        html_string = render_template('reports/pdf_template.html', **context)
        
        # Generate PDF from HTML
        html = HTML(string=html_string, base_url='')
        result = html.write_pdf()
        
        response = make_response(result)
        response.headers['Content-Disposition'] = f'attachment; filename={filename}.pdf'
        response.headers['Content-type'] = 'application/pdf'
        return response