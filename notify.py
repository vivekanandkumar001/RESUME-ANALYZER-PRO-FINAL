# notify.py
import os
import smtplib
from email.message import EmailMessage
from twilio.rest import Client as TwilioClient
import requests
import time
from dotenv import load_dotenv # .env file load karne ke liye

# .env file load karein (local testing ke liye)
load_dotenv()

# --- Load env vars / secrets ---
# Email (SMTP)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM") # e.g., "whatsapp:+1415XXXXXXX"

# --- Email helper ---
def send_email(to_email, subject, body, html=False):
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASS]):
        print("⚠️ Email credentials incomplete. Skipping email.")
        return False
    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        if html:
            msg.add_alternative(body, subtype="html")
        else:
            msg.set_content(body)
        # Timeout badhaya gaya hai
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=60) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {to_email}: {e}")
        return False

# --- Telegram helper ---
def send_telegram(chat_id, text):
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        print("⚠️ Telegram credentials/chat_id missing. Skipping Telegram.")
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        # Text ko safe rakhein (HTML tags limited)
        payload = {"chat_id": str(chat_id), "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
        resp = requests.post(url, data=payload, timeout=20) # Timeout badhaya
        resp_data = resp.json() # Response ko check karein
        if resp.status_code == 200 and resp_data.get("ok"):
            print(f"✅ Telegram message sent to {chat_id}")
            return True
        else:
            print(f"❌ Telegram API error {resp.status_code}: {resp_data.get('description', resp.text)}")
            return False
    except Exception as e:
        print(f"❌ Error sending Telegram to {chat_id}: {e}")
        return False

# --- WhatsApp via Twilio helper ---
def send_whatsapp_twilio(to_number, text):
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM]):
        print("⚠️ Twilio/WhatsApp credentials incomplete. Skipping WhatsApp.")
        return False
    if not to_number.startswith("+"):
        print(f"⚠️ Invalid WhatsApp number format for {to_number}. Skipping. (Format should be +91...)")
        return False
    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=text,
            from_=TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_number}" # Ensure 'whatsapp:' prefix
        )
        print(f"✅ WhatsApp sent (sid: {message.sid}) to {to_number}")
        return True
    except Exception as e:
        # Twilio errors ko behtar tarike se handle karein
        error_message = str(e)
        if "permission to send messages to the recipient" in error_message:
             print(f"❌ Error sending WhatsApp to {to_number}: User needs to opt-in or Twilio sandbox limitations. {e}")
        else:
             print(f"❌ Error sending WhatsApp to {to_number}: {e}")
        return False

# --- Combined notify wrapper ---
def notify_user(user, job):
    job_title = job.get("title", "Job")
    job_desc = job.get("description", "")
    job_link = job.get("link", "") # Scraper se link milta hai
    score = job.get("score", 0.0) # Match score bhi include karein

    # Basic snippet (first few sentences/lines)
    snippet = job_desc.split('.')[0] + "." if '.' in job_desc else job_desc[:150] + "..."

    # Common Message Parts
    title_line = f"<b>✨ New Job Match ({score*100:.1f}%) : {job_title}</b>"
    snippet_line = f"\n{snippet}\n"
    keywords_line = f"🔑 Keywords: {', '.join(job.get('keywords', ['N/A']))}"
    link_line = f"\n🔗 Link: {job_link}" if job_link else ""
    footer_line = "\n\n(Automated alert by Progeni Analyzer)"

    # Telegram/HTML message
    message_html = f"{title_line}{link_line}{snippet_line}\n{keywords_line}{footer_line}"

    # Plain text message (Email/WhatsApp fallback)
    message_plain = f"✨ New Job Match ({score*100:.1f}%) : {job_title}\n"
    if job_link: message_plain += f"🔗 Link: {job_link}\n"
    message_plain += f"\n{snippet}\n\n"
    message_plain += f"🔑 Keywords: {', '.join(job.get('keywords', ['N/A']))}"
    message_plain += f"\n\n(Automated alert by Progeni Analyzer)"


    # Send notifications based on user preference
    if user.get("notify_email") and user.get("email"):
        send_email(user["email"], f"Progeni Job Match: {job_title}", message_plain, html=False)

    if user.get("notify_telegram") and user.get("telegram_chat_id"):
        # Telegram HTML ko support karta hai
        send_telegram(user["telegram_chat_id"], message_html)

    if user.get("notify_whatsapp") and user.get("whatsapp_number"):
        # WhatsApp limited formatting support karta hai (*bold*, _italic_)
        # Plain text bhejna safe hai
        send_whatsapp_twilio(user["whatsapp_number"], message_plain)

    time.sleep(1.0) # APIs ko hit karne ke beech thoda rukein