# webmail_flask
 
A self-hosted webmail client built with Python and Flask, created to add the features I wanted that mainstream webmail lacked.
 
The first feature is **sender analytics**: the app reads the whole inbox over IMAP, counts how many messages each sender (and each subject line) has sent, and shows the top ten senders. That makes it easy to see who fills the inbox most and where to unsubscribe or filter.
 
> Status: personal prototype, not production-ready. See [Security notes](#security-notes) before running it anywhere but your own machine.
 
## Features
 
- **Inbox view:** paginated list of the newest messages with sender, subject, date, and read/unread status, plus total and unread counts
- **Message view:** opens a message and renders its body (attachments are skipped in this view)
- **Top senders:** aggregates sender and subject counts across the whole inbox and lists the ten most frequent senders
- **Encrypted connection:** connects to the mail server with IMAP over TLS (`IMAP4_SSL`, port 993)
## Planned
 
- **Package tracking:** detect shipping notifications and show delivery status in one place
- **Exposure tracking:** keep a record of every service the address has been given to, so a leak or a spam source can be traced back to where it came from
## How it works
 
| File | Role |
| --- | --- |
| `app.py` | Flask app and routes: inbox (`/`), message (`/read_email/<id>`), top senders (`/top-ten`) |
| `email_functions.py` | Reads the config, connects to IMAP, builds the inbox page, fetches a message |
| `aggregate_email.py` | Walks every message's `From` and `Subject` headers and writes counts to `static/emails.json` |
| `top_ten.py` | Sorts the counts and returns the ten most frequent senders |
| `get_email_content.py` | Standalone script that saves recent message headers to disk, read-only |
| `test.py`, `test_app.py` | Development copies of the app used to try new features (not automated tests) |
| `templates/`, `static/` | Jinja templates, CSS, and JavaScript for the UI |
 
Only headers (`From`, `Subject`) are fetched for the sender counts, which keeps the full-inbox scan light.
 
## Setup
 
Requires Python 3 and an email account that allows IMAP access (for Gmail and similar providers, use an app password rather than your main password).
 
```bash
git clone https://github.com/linzinha/webmail_flask.git
cd webmail_flask
python3 -m venv venv && source venv/bin/activate
pip install flask
```
 
1. Run the app once (`python app.py`). It creates `static/config.ini` with placeholder values, then stop it.
2. Edit `static/config.ini` with your IMAP server, port, address, password, and how many emails to show per page.
3. In `app.py`, set `venv` to your own virtual environment's Python (for example `venv/bin/python`).
4. Start it again with `python app.py` and open http://127.0.0.1:5000.
`config.ini` and `emails.json` are listed in `.gitignore` so credentials and inbox data stay out of the repo.
 
## Security notes
 
This is an early python learning project that mostly has been developed with an offline json file and so has a number of security concerns that need to be addressed before running it live.
Do NOT run it out of the box:
 
- **Credentials are served as a static file.** `config.ini` lives in `static/`, which Flask serves over HTTP, so anyone who can reach the app can download the password. Fix: move the config outside `static/`, or read credentials from environment variables or the OS keyring.
- **Password stored in plain text.** Fix: environment variables, a secrets manager, or OAuth for providers that support it.
- **Email HTML rendered unsanitized.** The message view uses Jinja's `|safe`, so script in a malicious email could run in the browser (stored XSS). Fix: sanitize with a library such as `bleach`, or render plain text in a sandboxed iframe with a strict Content Security Policy.
- **Debug mode is on.** `app.run(debug=True)` exposes the interactive debugger. Fix: turn it off and serve with a production WSGI server.
- **No login.** Anyone who reaches the port can read the mailbox. Fix: bind to `127.0.0.1` only, or add authentication.
- **Attachments written to disk by subject name.** Fix: store in a dedicated directory with sanitized, unique filenames.
## Tech
 
Python · Flask · Jinja2 · `imaplib` (IMAP over TLS) · `email` (MIME parsing) · JavaScript / jQuery
 
