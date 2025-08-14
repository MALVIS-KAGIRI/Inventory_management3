import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
from models import Product, User, Role
from database import db
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications and alerts"""
    
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_username)
        self.enabled = bool(self.smtp_username and self.smtp_password)
    
    def send_email(self, to_emails, subject, body, html_body=None, attachments=None):
        """Send email to recipients"""
        if not self.enabled:
            logger.warning("Email service not configured. Skipping email send.")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
            msg['Subject'] = subject
            
            # Add text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    with open(attachment, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {os.path.basename(attachment)}'
                        )
                        msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_low_stock_alert(self):
        """Send low stock alert to administrators"""
        try:
            # Get low stock products
            low_stock_products = Product.query.filter(
                Product.quantity_in_stock <= Product.reorder_level,
                Product.is_active == True
            ).all()
            
            if not low_stock_products:
                return True  # No low stock items
            
            # Get admin users
            admin_role = Role.query.filter_by(name='Admin').first()
            if not admin_role:
                return False
            
            admin_users = User.query.filter_by(role_id=admin_role.id, is_active=True).all()
            admin_emails = [user.email for user in admin_users if user.email]
            
            if not admin_emails:
                logger.warning("No admin emails found for low stock alert")
                return False
            
            # Create email content
            subject = f"Low Stock Alert - {len(low_stock_products)} Items Need Attention"
            
            # Text body
            body = f"""
Low Stock Alert - Inventory Management System

Dear Administrator,

We have detected {len(low_stock_products)} products that are at or below their reorder levels:

"""
            
            for product in low_stock_products:
                body += f"• {product.name} (SKU: {product.sku})\n"
                body += f"  Current Stock: {product.quantity_in_stock}\n"
                body += f"  Reorder Level: {product.reorder_level}\n"
                body += f"  Shortage: {max(0, product.reorder_level - product.quantity_in_stock)}\n\n"
            
            body += """
Please review these items and consider placing reorders to maintain adequate inventory levels.

Best regards,
Inventory Management System
"""
            
            # HTML body
            html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #e74c3c; border-bottom: 2px solid #e74c3c; padding-bottom: 10px;">
            🚨 Low Stock Alert
        </h2>
        
        <p>Dear Administrator,</p>
        
        <p>We have detected <strong>{len(low_stock_products)} products</strong> that are at or below their reorder levels:</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #e9ecef;">
                        <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">Product</th>
                        <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">SKU</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Current</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Min Level</th>
                        <th style="padding: 10px; text-align: center; border: 1px solid #dee2e6;">Shortage</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            for product in low_stock_products:
                shortage = max(0, product.reorder_level - product.quantity_in_stock)
                html_body += f"""
                    <tr>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{product.name}</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{product.sku}</td>
                        <td style="padding: 8px; text-align: center; border: 1px solid #dee2e6; color: #e74c3c; font-weight: bold;">{product.quantity_in_stock}</td>
                        <td style="padding: 8px; text-align: center; border: 1px solid #dee2e6;">{product.reorder_level}</td>
                        <td style="padding: 8px; text-align: center; border: 1px solid #dee2e6; color: #dc3545; font-weight: bold;">{shortage}</td>
                    </tr>
"""
            
            html_body += """
                </tbody>
            </table>
        </div>
        
        <p style="margin-top: 20px;">Please review these items and consider placing reorders to maintain adequate inventory levels.</p>
        
        <div style="margin-top: 30px; padding: 15px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px;">
            <p style="margin: 0; color: #155724;">
                <strong>💡 Tip:</strong> You can access the inventory management system to update stock levels and manage reorders.
            </p>
        </div>
        
        <p style="margin-top: 20px;">
            Best regards,<br>
            <strong>Inventory Management System</strong>
        </p>
    </div>
</body>
</html>
"""
            
            return self.send_email(admin_emails, subject, body, html_body)
            
        except Exception as e:
            logger.error(f"Failed to send low stock alert: {str(e)}")
            return False
    
    def send_report_email(self, to_emails, report_title, report_file_path):
        """Send report via email"""
        subject = f"Automated Report: {report_title}"
        
        body = f"""
Dear User,

Please find attached the requested report: {report_title}

Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
Inventory Management System
"""
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4f46e5; border-bottom: 2px solid #4f46e5; padding-bottom: 10px;">
            📊 Automated Report
        </h2>
        
        <p>Dear User,</p>
        
        <p>Please find attached the requested report: <strong>{report_title}</strong></p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0;"><strong>Report Details:</strong></p>
            <ul style="margin: 10px 0;">
                <li>Report Name: {report_title}</li>
                <li>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li>Format: {os.path.splitext(report_file_path)[1].upper().replace('.', '')}</li>
            </ul>
        </div>
        
        <p style="margin-top: 20px;">
            Best regards,<br>
            <strong>Inventory Management System</strong>
        </p>
    </div>
</body>
</html>
"""
        
        return self.send_email(to_emails, subject, body, html_body, [report_file_path])

# Global email service instance
email_service = EmailService()