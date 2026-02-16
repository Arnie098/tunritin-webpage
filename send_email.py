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

def send_bulk_emails(subject="Payment Confirmation - Turnitin"):
    """
    Sends the modern HTML payment confirmation email to multiple recipients.
    """
    html_file = "customer_email.html"
    recipients_file = "recipients.txt"
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found.")
        return
    
    if not os.path.exists(recipients_file):
        print(f"Error: {recipients_file} not found. Create it with one email per line.")
        return

    # 1. Read the HTML template
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 2. Read recipients
    with open(recipients_file, "r", encoding="utf-8") as f:
        recipients = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not recipients:
        print("No recipients found in recipients.txt.")
        return

    print(f"--- Preparing to send to {len(recipients)} recipients ---")

    # 3. Connect and loop
    try:
        print(f"Connecting to {SMTP_SERVER}...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            
            for recipient in recipients:
                print(f"Sending to {recipient}...", end=" ")
                message = MIMEMultipart()
                message["From"] = SENDER_EMAIL
                message["To"] = recipient
                message["Subject"] = subject
                message.attach(MIMEText(html_content, "html"))
                
                try:
                    server.sendmail(SENDER_EMAIL, recipient, message.as_string())
                    print("✅")
                except Exception as e:
                    print(f"❌ ({e})")
                    
        print("\n🎉 Bulk sending complete!")
    except Exception as e:
        print(f"\n❌ SMTP Connection failed: {e}")
        print("Tip: If you are using Tencent Cloud, ensure SMTP is enabled in your mailbox settings.")

if __name__ == "__main__":
    print("--- Turnitin Bulk Email Sender ---")
    action = input("Send to all recipients in recipients.txt? (y/n): ").lower()
    if action == 'y':
        send_bulk_emails()
    else:
        dest = input("Enter a single recipient instead (or press Enter to exit): ").strip()
        if dest:
            # Re-using the single send logic if needed, but updated to use logic above
            recipients_file = "recipients.txt"
            with open(recipients_file, "w", encoding="utf-8") as f:
                f.write(dest)
            send_bulk_emails()
