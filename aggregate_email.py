import imaplib
import email
from email.header import decode_header
import json
import configparser
import os

config_defaults = "static/config.json"
try:
    with open(config_defaults, 'r') as json_file:
        json_config = json.load(json_file)
except:
    print("blah")

def aggregate():
    # Constants
    JSON_FILE = os.path.join("static", json_config["json counts"])
    DEFAULT_CONFIG = json_config["imap defaults"]
    data = {"sender": {}, "subject": {}}


    try:
        with open(JSON_FILE, 'r') as json_file:
            email_counts = json.load(json_file)
    except:
        print("blah")

    config_file = os.path.join("static", json_config["config file"])
    config = configparser.RawConfigParser(defaults=DEFAULT_CONFIG)
    config.read(config_file)
    server = config.get('DEFAULT', 'SERVER')
    port = config.get('DEFAULT', 'PORT')
    email_addr = config.get('DEFAULT', 'EMAIL')
    password = config.get('DEFAULT', 'PASSWORD')
    imap = imaplib.IMAP4_SSL(server, port)
    imap.login(email_addr, password)

    # Select the mailbox (inbox)
    mailbox = 'INBOX'
    imap.select(mailbox)

    # Search for all emails in the mailbox
    status, email_ids = imap.search(None, 'ALL')
    print(f"Search Status: {status}")

    if status == 'OK':
        email_ids = email_ids[0].split()
        # Loop through each email ID and fetch sender and subject
        for email_id in email_ids:
            status, msg_data = imap.fetch(email_id, '(BODY[HEADER.FIELDS (FROM SUBJECT)])')
            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                # Decode the sender
                from_info = decode_header(msg.get("From"))
                if len(from_info) == 2:
                    From, encoding = from_info
                else:
                    From = from_info[0][0] if isinstance(from_info[0], tuple) else from_info[0]
                    encoding = None  # You can set encoding to None or handle it as needed
                sender = str(From).split(' <')[0]
                # Decode the subject
                subject_info = decode_header(msg["Subject"])
                subject = ""
                for s, e in subject_info:
                    if isinstance(s, bytes):
                        subject += s.decode(e if e else "utf-8")
                    else:
                        subject += s
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)

                # Update sender and subject counts in the data dictionary
                if sender in data["sender"]:
                    data["sender"][sender] += 1
                else:
                    data["sender"][sender] = 1
                
                if subject in data["subject"]:
                    data["subject"][subject] += 1
                else:
                    data["subject"][subject] = 1
            else:
                print(f"Error fetching email {email_id}")
        else:
            print("Error searching for emails in the mailbox.")


    # Save the updated data to the JSON file
    with open(JSON_FILE, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)
