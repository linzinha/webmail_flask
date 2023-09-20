from flask import Flask, send_from_directory, render_template, request, jsonify, Response
import subprocess
import threading
import json
import test
import os
import aggregate_email
import top_ten

# app variables
app = Flask(__name__)
initial_email_count_executed = False
top_senders = top_ten.top_counts()
venv = '/home/onoaspookyghost/.local/share/virtualenvs/flask-app-template-52jArVZU/bin/python'

with open('static/emails.json', 'r') as json_file:
    json_data = json.load(json_file)

# Function to run the external script in a separate thread
def get_email_top_counts():
    global venv
    global initial_email_count_executed
    if not initial_email_count_executed:
        command = [venv, "top_ten.py"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return_code = process.returncode
        initial_email_count_executed = True

        if not stdout.decode() == "":
            print(f"Output:\n{stdout.decode()}")
        if not stderr.decode() == "":
            print(f"Errors:\n{stderr.decode()}")
        
        if return_code == 0:
            print("Script ran successfully.")
        else:
            print("Script encountered an error.")
    else:
        print("Not rerunning email count")

@app.route('/read_email/<email_id>')
def message(email_id):
    content = test.read_email(email_id)
    return render_template('read_email.html', content=content)

@app.route('/')
def index():
    global top_senders
    global initial_email_count_executed
    # external_script_thread = threading.Thread(target=get_email_top_counts)
    # external_script_thread.start()
    emails, page, more_emails, unread, total = test.process_email(request)
    return render_template(
        'test_index.html', 
        emails=emails, 
        page=page, 
        more_emails=more_emails, 
        unread=unread, 
        total=total,
        top_senders=top_senders)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/top-ten')
def top_ten():
    global venv
    json_file = '/static/emails.json'
    
    # Run the script using subprocess
    process = subprocess.Popen(
        [venv, 'aggregate_email.py'])
    process.communicate()  # Wait for the process to finish

    # Return a simple success message as a response
    return Response("Script executed successfully", status=200)


@app.route('/logout.html')
def logout():
    imap = test.imap_logout()
    return render_template('logout.html')


if __name__ == '__main__':
    app.run(debug=True)
