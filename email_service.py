import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from database import DatabaseManager

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the database manager
db_manager = DatabaseManager()

# Scheduler for email jobs
scheduler = BackgroundScheduler()
scheduler.start()

def send_email(sender: str, recipient: str, subject: str, body: str) -> Dict:
    """
    Send an email and simulate tracking the delivery status (inbox/spam).

    Args:
        sender (str): Email address of the sender.
        recipient (str): Email address of the recipient.
        subject (str): Subject of the email.
        body (str): Body content of the email.

    Returns:
        dict: Simulated email send result, including delivery status.
    """
    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        # Sending email via SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, "jvmf pmas gekp xmes")  # Use an app-specific password
            server.sendmail(sender, recipient, message.as_string())

        # Simulate email delivery status
        delivery_status = "Inbox" if "gmail" in recipient else "Spam"

        # Update delivery statistics in the database
        db_manager.update_email_stats(delivery_status)
        logger.info(f"Email sent to {recipient}, delivery status: {delivery_status}")
        return {"status": "success", "delivery_status": delivery_status}

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return {"status": "failed", "error_message": str(e)}

# New: Send Bulk Emails
def send_bulk_emails(sender: str, recipients: List[str], subject: str, body: str) -> List[Dict]:
    """
    Send emails in bulk.

    Args:
        sender (str): Email address of the sender.
        recipients (list): List of email addresses of the recipients.
        subject (str): Subject of the email.
        body (str): Body content of the email.

    Returns:
        list: List of results for each recipient.
    """
    results = []
    for recipient in recipients:
        result = send_email(sender, recipient, subject, body)
        results.append(result)
    return results

# New: Schedule Emails
def schedule_email(sender: str, recipients: List[str], subject: str, body: str, send_time: str) -> None:
    """
    Schedule an email to be sent at a specific time.

    Args:
        sender (str): Email address of the sender.
        recipients (list): List of email addresses of the recipients.
        subject (str): Subject of the email.
        body (str): Body content of the email.
        send_time (str): Time to send the email (format: 'YYYY-MM-DD HH:MM:SS').
    """
    def job():
        send_bulk_emails(sender, recipients, subject, body)

    scheduler.add_job(job, 'date', run_date=send_time)
    logger.info(f"Email scheduled for {send_time} to {len(recipients)} recipients.")

# New: Generate Email Report
def generate_email_report() -> Dict:
    """
    Generate a report on email delivery analytics.

    Returns:
        dict: Email campaign statistics.
    """
    stats = db_manager.get_email_stats()
    total_emails = sum(stats.values())
    if total_emails == 0:
        return {"total_emails": 0, "success_rate": 0, "spam_rate": 0}

    success_count = stats.get("Inbox", 0)
    spam_count = stats.get("Spam", 0)

    success_rate = (success_count / total_emails) * 100
    spam_rate = (spam_count / total_emails) * 100

    logger.info(f"Email Report: Total: {total_emails}, Success Rate: {success_rate}%, Spam Rate: {spam_rate}%")
    return {
        "total_emails": total_emails,
        "success_rate": success_rate,
        "spam_rate": spam_rate
    }

# For standalone testing
if __name__ == "__main__":
    # Example: Single email
    result = send_email(
        sender="your_email@gmail.com",
        recipient="recipient_email@gmail.com",
        subject="Test Email",
        body="This is a test email."
    )
    print(result)

    # Example: Bulk email
    bulk_result = send_bulk_emails(
        sender="your_email@gmail.com",
        recipients=["recipient1@gmail.com", "recipient2@gmail.com"],
        subject="Bulk Test",
        body="This is a bulk test email."
    )
    print(bulk_result)

    # Example: Schedule email
    schedule_email(
        sender="your_email@gmail.com",
        recipients=["recipient1@gmail.com", "recipient2@gmail.com"],
        subject="Scheduled Email",
        body="This email is scheduled to be sent later.",
        send_time="2024-11-28 10:30:00"
    )

    # Example: Generate report
    report = generate_email_report()
    print(report)
