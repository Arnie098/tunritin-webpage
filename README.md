# Turnitin Login UI

A static replica of the Turnitin login page: email/password form, SSO-style buttons (Google, Clever), and supporting links.

## Running the project

No build step or dependencies. Use any of these options:

### Option 1: Open the HTML file

Double-click `index.html` or open it from your browser’s **File → Open** menu.

### Option 2: Local HTTP server (recommended)

From the project folder, start a simple server:

**Node (npx):**
```bash
npx serve .
```
Then open http://localhost:3000 (or the URL shown in the terminal).

**Python 3:**
```bash
python -m http.server 8000
```
Then open http://localhost:8000

**Python 2:**
```bash
python -m SimpleHTTPServer 8000
```
Then open http://localhost:8000

## Email Automation (Python + Supabase)

This project includes a powerful bulk email sender that integrates with SendGrid and Supabase for reliable, stateful delivery.

### Features
- **Supabase Backend**: Manages 464k+ recipients with ease.
- **Auto-Tracking**: Automatically marks recipients as sent in the database.
- **SendGrid Integration**: Uses high-delivery SendGrid v3 API.
- **Daily Throttling**: Automatically sends 100 emails every 24 hours to stay within Free Plan limits.

### Getting Started
1.  **Configure Env**: Add your keys to a `.env` file (see `.env.example`).
2.  **Run Locally**: `python send_email.py`
3.  **Deploy**: Push to GitHub and add your secrets to Actions for 24h automated sending.

## Project structure

| File | Purpose |
|------|--------|
| `index.html` | Login page markup and structure |
| `send_email.py` | Main automation script |
| `.github/workflows/` | Daily automation trigger |
| `customer_email.html`| Email template |

## Security Note

Sensitive files like `.env`, `config.js`, and private recipient lists are explicitly ignored via `.gitignore`. Always use GitHub Secrets for cloud deployment.
