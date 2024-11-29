import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from database import DatabaseManager
import os

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the database manager
db_manager = DatabaseManager()

# Scheduler for email jobs
scheduler = BackgroundScheduler()
scheduler.start()

def send_email(sender: str, recipient: str, subject: str, body: str) -> Dict:
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Gmail SMTP settings
        smtp_server = "smtp.gmail.com"
        port = 587
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')

        # Create SMTP session
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender, gmail_password)
            
            # Update sent count
            db_manager.increment_stat('sent')

            try:
                server.send_message(message)
                # If no exception, consider it delivered to inbox
                db_manager.increment_stat('inbox')
                delivery_status = "inbox"
                logger.info(f"Email sent successfully to {recipient}")
            except smtplib.SMTPResponseException as e:
                db_manager.increment_stat('spam')
                delivery_status = "spam"
                logger.warning(f"Email to {recipient} may have landed in Spam. Error: {e}")
                
        return {"status": "success", "delivery_status": delivery_status}

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        db_manager.increment_stat('spam')
        return {"status": "failed", "error_message": str(e)}

def send_bulk_emails(sender: str, recipients: List[str], subject: str, body: str) -> List[Dict]:
    results = []
    for recipient in recipients:
        result = send_email(sender, recipient, subject, body)
        results.append({"recipient": recipient, **result})
    return results

def schedule_email(sender: str, recipient: str, subject: str, body: str, send_time: str) -> None:
    scheduler.add_job(
        send_email,
        'date',
        run_date=send_time,
        args=[sender, recipient, subject, body]
    )
    logger.info(f"Email scheduled for {send_time}")

def generate_email_report() -> Dict:
    try:
        # Get stats from database
        stats = db_manager.get_all_stats()
        
        # Calculate metrics
        total_emails = stats.get('sent', 0)
        inbox_count = stats.get('inbox', 0)
        spam_count = stats.get('spam', 0)

        # Calculate rates if emails were sent
        if total_emails > 0:
            success_rate = (inbox_count / total_emails) * 100
            spam_rate = (spam_count / total_emails) * 100
        else:
            success_rate = spam_rate = 0.0

        # Log simplified report
        logger.info(f"Analytics Report - Total Sent: {total_emails}")
        logger.info(f"Rates - Success: {success_rate:.1f}%, Spam: {spam_rate:.1f}%")

        # Return only requested metrics
        return {
            "Total Emails Sent": total_emails,
            "Success Rate": f"{success_rate:.1f}%",
            "Spam Rate": f"{spam_rate:.1f}%"
        }
    except Exception as e:
        logger.error(f"Error generating analytics report: {e}")
        return {
            "Total Emails Sent": 0,
            "Success Rate": "0.0%",
            "Spam Rate": "0.0%"
        }

if __name__ == "__main__":
    result = send_email(
        sender="your_email@gmail.com",
        recipient="test@example.com",
        subject="Test Email",
        body="This is a test email."
    )
    print(result)
