# dev/config.py
import os
import configparser
import imaplib
import logging

# Set up logging
logging.basicConfig(filename='email_fetch.log', level=logging.INFO)

CONFIG_FILE_PATH = "config.ini"
DEFAULT_CONFIG = {
    'SERVER': 'imap.example.com',
    'PORT': 993,
    'EMAIL': 'user@email.com',
    'PASSWORD': 'password',
    'EMAILS_PER_PAGE': 20
}


def read_config(config_file):
    try:
        config = configparser.RawConfigParser(defaults=DEFAULT_CONFIG)
        config_file = os.path.join('static', config_file)
        config.read(config_file)
        server = config.get('DEFAULT', 'SERVER')
        port = config.get('DEFAULT', 'PORT')
        email_addr = config.get('DEFAULT', 'EMAIL')
        password = config.get('DEFAULT', 'PASSWORD')
        email_count = config.get('DEFAULT', 'EMAILS_PER_PAGE')
        return server, port, email_addr, password, int(email_count)
    except Exception as e:
        logging.error(f"Error reading config: {e}")
        raise



def fetch_and_save_headers():
    try:
        server, port, email_addr, password, email_count = read_config(CONFIG_FILE_PATH)
        imap = imaplib.IMAP4_SSL(server, port)
        imap.login(email_addr, password)
        mailbox = "inbox"
        status, messages = imap.select(mailbox, readonly=True)
        messages = int(messages[0])

        # Fetch and save headers
        start_index = messages  # Adjust as needed
        end_index = messages - email_count + 1   # Adjust as needed

        status, email_ids = imap.search(None, f"{start_index}:{end_index}")
        email_id_list = email_ids[0].split()
        for i in email_id_list:
            status, msg_data = imap.fetch(i, "(RFC822 FLAGS)")
            header_filename = os.path.join('static', f"email_header_{i}.txt")
            with open(header_filename, 'wb') as header_file:
                header_file.write(msg_data[0][1])
            flags_bytes = msg_data[0][0].decode("utf-8")
            print(flags_bytes)
            flag_list = flags_bytes.split(" ")
            length = len(flag_list)
            flags = flag_list[1:length]
            for flag in flags:
                flag = str(flag)
                with open(header_filename, 'a') as header_file:
                    header_file.write(flag)
            

        imap.logout()
    except Exception as e:
        logging.error(f"Error fetching and saving headers: {e}")
        raise

if __name__ == "__main__":
    fetch_and_save_headers()





