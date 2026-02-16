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

## Project structure

| File | Purpose |
|------|--------|
| `index.html` | Login page markup and structure |
| `styles.css` | Layout and styling |
| `script.js` | Form display and basic validation |
| `turnitin-login-logo.svg` | Turnitin-style logo |

## Notes

- The form does not submit to a real backend; it only runs client-side validation.
- SSO links are placeholders (`href="#"`); replace with real SSO URLs when integrating.
