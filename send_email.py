import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Load environment variables if a .env file exists
load_dotenv()

# --- CONFIGURATION ---
# You can set these here or in a .env file
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password") # Use App Password for Gmail
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))

def send_customer_email(recipient_email, subject="Payment Confirmation - Turnitin"):
    """
    Sends the modern HTML payment confirmation email.
    """
    html_file = "customer_email.html"
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found in the current directory.")
        return

    # 1. Read the HTML template
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 2. Setup the MIME message
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(html_content, "html"))

    # 3. Send the email
    try:
        print(f"Connecting to {SMTP_SERVER}...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())
        print(f"✅ Email successfully sent to {recipient_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    print("--- Turnitin Email Sender ---")
    dest = input("Enter recipient email address: ").strip()
    if dest:
        send_customer_email(dest)
    else:
        print("No recipient provided. Exiting.")
