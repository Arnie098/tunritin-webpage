import asyncio
import os
import logging
import httpx
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MAILTRAP_API_TOKEN = os.getenv("MAILTRAP_API_TOKEN")
MAILTRAP_SENDER_EMAIL = os.getenv("MAILTRAP_SENDER_EMAIL") or SENDER_EMAIL
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL") or SENDER_EMAIL
SUPABASE_URL = "https://didhzagdaezinojvghpo.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"
MAILTRAP_API_URL = "https://send.api.mailtrap.io/api/send"
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
DAILY_SEND_LIMIT = 550 # 100 (SG) + 150 (MT) + 300 (Brevo)
PROGRESS_FILE = ".send_progress_offset"
LOG_FILE = "sending.log"
SUCCESS_LOG = "sent_recipients.txt"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# --- PROGRESS HELPERS ---
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return int(f.read().strip())
        except: return 0
    return 0

def save_progress(offset):
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(offset))

# --- SUPABASE HELPERS ---
async def fetch_supabase_recipients(client, limit=100):
    url = f"{SUPABASE_URL}/rest/v1/email_list?is_sent=eq.false&limit={limit}"
    headers = {"apikey": SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"}
    resp = await client.get(url, headers=headers)
    return resp.json() if resp.status_code == 200 else []

async def mark_supabase_sent(client, record_id):
    url = f"{SUPABASE_URL}/rest/v1/email_list?id=eq.{record_id}"
    headers = {"apikey": SUPABASE_SERVICE_ROLE_KEY, "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}", "Content-Type": "application/json"}
    await client.patch(url, json={"is_sent": True}, headers=headers)

# --- SENDING CORE ---
async def send_via_sendgrid(client, recipient, subject, html_content):
    data = {
        "personalizations": [{"to": [{"email": recipient}]}],
        "from": {"email": SENDER_EMAIL},
        "subject": subject,
        "content": [{"type": "text/html", "value": html_content}]
    }
    headers = {"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"}
    try:
        resp = await client.post(SENDGRID_API_URL, json=data, headers=headers)
        if resp.status_code == 202: return True, None
        return False, (resp.status_code, resp.text)
    except Exception as e: return False, ("ERR", str(e))

async def send_via_mailtrap(client, recipient, subject, html_content):
    data = {
        "to": [{"email": recipient}],
        "from": {"email": MAILTRAP_SENDER_EMAIL},
        "subject": subject,
        "html": html_content
    }
    headers = {"Authorization": f"Bearer {MAILTRAP_API_TOKEN}", "Content-Type": "application/json"}
    try:
        resp = await client.post(MAILTRAP_API_URL, json=data, headers=headers)
        if resp.status_code in [200, 202]: return True, None
        return False, (resp.status_code, resp.text)
    except Exception as e: return False, ("ERR", str(e))

async def send_via_brevo(client, recipient, subject, html_content):
    data = {
        "sender": {"email": BREVO_SENDER_EMAIL},
        "to": [{"email": recipient}],
        "subject": subject,
        "htmlContent": html_content
    }
    headers = {"api-key": BREVO_API_KEY, "Content-Type": "application/json"}
    try:
        resp = await client.post(BREVO_API_URL, json=data, headers=headers)
        if resp.status_code in [201, 202]: return True, None
        return False, (resp.status_code, resp.text)
    except Exception as e: return False, ("ERR", str(e))

async def main():
    # Detect Providers
    providers = []
    if SENDGRID_API_KEY: providers.append("sendgrid")
    if MAILTRAP_API_TOKEN: providers.append("mailtrap")
    if BREVO_API_KEY: providers.append("brevo")
    
    source = "supabase" if SUPABASE_SERVICE_ROLE_KEY else "file"
    logging.info(f"🚀 Starting automation (Source: {source}, Providers: {providers}, Limit: {DAILY_SEND_LIMIT})")

    if not providers:
        logging.error("No email providers configured!")
        return

    # Load Template
    with open("customer_email.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    subject = "Update: Your Digital Access"

    emails_sent = 0
    provider_index = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while emails_sent < DAILY_SEND_LIMIT:
            current_provider = providers[provider_index]
            
            if source == "supabase":
                batch = await fetch_supabase_recipients(client, 10) # Fetch in small batches to allow rotation
                if not batch: break
                
                for record in batch:
                    if emails_sent >= DAILY_SEND_LIMIT: break
                    
                    # Try current provider
                    success = False
                    if current_provider == "sendgrid":
                        success, err = await send_via_sendgrid(client, record['email'], subject, html_content)
                    elif current_provider == "mailtrap":
                        success, err = await send_via_mailtrap(client, record['email'], subject, html_content)
                    else:
                        success, err = await send_via_brevo(client, record['email'], subject, html_content)
                    
                    if success:
                        emails_sent += 1
                        logging.info(f"✅ [{current_provider.upper()}] Sent: {record['email']} ({emails_sent}/{DAILY_SEND_LIMIT})")
                        await mark_supabase_sent(client, record['id'])
                    else:
                        logging.error(f"❌ [{current_provider.upper()}] Failed: {record['email']} {err}")
                        # Rotate provider on limit or auth error
                        if "limit" in str(err).lower() or any(x in str(err) for x in ["401", "403", "429"]):
                            logging.warning(f"⚠️ Provider {current_provider} failed/limited (Error: {err}). Rotating...")
                            provider_index = (provider_index + 1) % len(providers)
                            if provider_index == 0 and len(providers) > 1:
                                # We tried all providers
                                logging.error("All providers hit their limits. Stopping for today.")
                                return
                            # Continue with next provider for the SAME record in next loop iteration? 
                            # For simplicity, we just move to next provider for next record.
                            current_provider = providers[provider_index]

            else:
                # File Fallback
                offset = load_progress()
                with open("recipients.txt", "r") as f:
                    f.seek(offset)
                    line = f.readline()
                    if not line: break
                    recipient = line.strip()
                    success, err = await send_email_api(client, recipient, subject, html_content)
                    if success:
                        emails_sent += 1
                        save_progress(f.tell())
                        logging.info(f"✅ Sent: {recipient} ({emails_sent}/{DAILY_SEND_LIMIT})")
                    else: logging.error(f"❌ Failed: {recipient} {err}")

    logging.info(f"Batch complete. Total sent: {emails_sent}")
    
    # If in GitHub Actions, we exit after one batch.
    if os.getenv("IS_GITHUB_ACTIONS") == "true":
        logging.info("GitHub Actions detected. Task finished for today.")
        return

if __name__ == "__main__":
    if not SENDGRID_API_KEY:
        print("Error: SENDGRID_API_KEY missing in .env")
    else:
        asyncio.run(main())
