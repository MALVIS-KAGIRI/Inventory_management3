from datetime import datetime, timedelta
import threading
import time
import schedule
from email_service import email_service
import logging

logger = logging.getLogger(__name__)

class TaskScheduler:
    """Background task scheduler for automated processes"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the task scheduler"""
        if not self.running:
            self.running = True
            
            # Schedule tasks
            schedule.every().day.at("09:00").do(self.check_low_stock)
            schedule.every().monday.at("08:00").do(self.send_weekly_summary)
            
            # Start scheduler thread
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            logger.info("Task scheduler started")
    
    def stop(self):
        """Stop the task scheduler"""
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Task scheduler stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def check_low_stock(self):
        """Check for low stock and send alerts"""
        try:
            logger.info("Running low stock check...")
            success = email_service.send_low_stock_alert()
            if success:
                logger.info("Low stock alert sent successfully")
            else:
                logger.warning("Failed to send low stock alert")
        except Exception as e:
            logger.error(f"Error in low stock check: {str(e)}")
    
    def send_weekly_summary(self):
        """Send weekly business summary"""
        try:
            logger.info("Generating weekly summary...")
            # This could generate and send a weekly report
            # Implementation would depend on specific requirements
        except Exception as e:
            logger.error(f"Error in weekly summary: {str(e)}")

# Global task scheduler instance
task_scheduler = TaskScheduler()