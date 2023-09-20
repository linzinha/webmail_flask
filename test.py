# dev/config.py
import logging
import webbrowser
from flask import render_template, request
import os
import email
from email import utils
from email.header import decode_header
import configparser
import imaplib
import time

CONFIG_FILE_PATH = "config.ini"
DEFAULT_CONFIG = {
    'SERVER': 'imap.example.com',
    'PORT': 993,
    'EMAIL': 'user@email.com',
    'PASSWORD': 'password',
    'EMAILS_PER_PAGE': 20
}

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def create_config():
    cwd = os.getcwd()
    contents_in_folder = os.listdir(cwd)
    static_status = None
    templates_status = None
    for item in contents_in_folder:
        if os.path.isdir(item) and item == 'static':
            static_status = True
        if os.path.isdir(item) and item == 'templates':
            templates_status = True
    if not static_status or not templates_status:
        print('folder structure compromised, repair the application')
    else:
        config_ini = os.path.join('static', CONFIG_FILE_PATH)
        if not os.path.exists(config_ini):
            config = configparser.ConfigParser(defaults=DEFAULT_CONFIG)
            config['DEFAULT'] = DEFAULT_CONFIG
            with open(config_ini, 'w') as config_file:
                config.write(config_file)


# read from the config file
def read_config(config_file):
    config_file = os.path.join('static', config_file)
    create_config()
    config = configparser.RawConfigParser(defaults=DEFAULT_CONFIG)
    config.read(config_file)
    server = config.get('DEFAULT', 'SERVER')
    port = config.get('DEFAULT', 'PORT')
    email_addr = config.get('DEFAULT', 'EMAIL')
    password = config.get('DEFAULT', 'PASSWORD')
    email_count = config.get('DEFAULT', 'EMAILS_PER_PAGE')
    return server, port, email_addr, password, int(email_count)


def get_counts(imap):
    r1, total = imap.search(None, "ALL")
    total_emails = len(total[0].split())
    r2, unread = imap.search(None, "UNSEEN")
    unread_emails = len(unread[0].split())

    return unread_emails, total_emails


def read_email(email_id):
    server, port, email_addr, password, email_count = read_config(CONFIG_FILE_PATH)
    imap = imaplib.IMAP4_SSL(server, port)
    imap.login(email_addr, password)
    mailbox = "inbox"
    status, messages = imap.select(mailbox)

    # Fetch the content of the selected email
    status, email_data = imap.fetch(email_id, "(RFC822)")
    if status == 'OK':
        email_message = email.message_from_bytes(email_data[0][1])
        
        # Get the email content (you can adjust this based on your needs)
        content = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" not in content_disposition:
                    payload = part.get_payload(decode=True)
                    if payload:
                        content = payload.decode('utf-8', errors='ignore')
        else:
            payload = email_message.get_payload(decode=True)
            if payload:
                content = payload.decode('utf-8', errors='ignore')

        return content
    
def imap_logout():
    server, port, email_addr, password, email_count = read_config(CONFIG_FILE_PATH)
    imap = imaplib.IMAP4_SSL(server, port)
    imap.logout()


def process_email(request):
    server, port, email_addr, password, email_count = read_config(CONFIG_FILE_PATH)
    imap = imaplib.IMAP4_SSL(server, port)
    imap.login(email_addr, password)
    mailbox = "inbox"
    status, messages = imap.select(mailbox)
    # Get counts
    total, unread = get_counts(imap,)

    # status, unread_messages = imap.search(None, "UNSEEN")
    # unread_count = len(unread_messages[0].split())
    messages = int(messages[0])

    # Get the requested page from the query parameter
    page = int(request.args.get('page', 1))  # Default to page 1
    # Calculate the start and end indices for the current page
    start_index = (page - 1) * email_count + 1
    end_index = start_index + email_count - 1

    # Search for emails in the specified range
    status, email_ids = imap.search(None, f"{start_index}:{end_index}")
    emails = []
    email_id_list = email_ids[0].split()
    num = 0
    for i in range(messages, messages-email_count, -1):
        # fetch the email message by ID
        status, msg_data = imap.fetch(str(i), "(BODY.PEEK[])")
        flags = msg_data[0][1]
        is_read = b'\\Seen' in flags  # Check if the "\\Seen" flag is present
        num+=1
        for response in msg_data:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                print((msg))
                subject_info = decode_header(msg["Subject"])
                subject = ""
                for s, e in subject_info:
                    if isinstance(s, bytes):
                        subject += s.decode(e if e else "utf-8")
                    else:
                        subject += s
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)
                from_info = decode_header(msg.get("From"))
                if len(from_info) == 2:
                    From, encoding = from_info
                else:
                    From = from_info[0][0] if isinstance(from_info[0], tuple) else from_info[0]
                    encoding = None  # You can set encoding to None or handle it as needed
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            email_message += body
                        elif "attachment" in content_disposition:
                            # download attachment
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    email_message = msg.get_payload(decode=True).decode()
                time_format = "%a, %d %b %Y %H:%M"
                timestamp = time.strftime(time_format, email.utils.parsedate(msg.get('Date')))
                sender = str(From).split(' <')[0]

                # Generate a unique link for each email based on its email_id
                email_link = f"/read_email/{str(i)}"

                emails.append({
                    "date": timestamp,
                    "subject": subject,
                    "sender": sender,
                    "email_id": i,
                    'unread': is_read,
                })

    # Determine if there are more emails to fetch
    more_emails = len(email_id_list) == email_count

    return emails, page, more_emails, total, unread


