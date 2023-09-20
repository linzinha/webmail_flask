from flask import Flask, send_from_directory, render_template, request, jsonify, Response
import subprocess
import threading
import json
import test

app = Flask(__name__)
venv = '/home/onoaspookyghost/.local/share/virtualenvs/flask-app-template-52jArVZU/bin/python'

@app.route('/')
def index():
    # external_script_thread = threading.Thread(target=run_external_script)
    # external_script_thread.start()
    
    emails, page, more_emails, unread, total = test.process_email(request)
    return render_template('index.html', emails=emails, page=page, more_emails=more_emails, unread=unread, total=total)

# Function to run the external script in a separate thread
def run_external_script():
    global venv
    global initial_email_count_executed
    if not initial_email_count_executed:
        command = [venv, "top_ten.py"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        return_code = process.returncode
        
        print(f"Output:\n{stdout.decode()}")
        print(f"Errors:\n{stderr.decode()}")
        
        if return_code == 0:
            print("Script ran successfully.")
            initial_email_count_executed = True
        else:
            print("Script encountered an error.")
    else:
        print("Not rerunning email count")

@app.route('/read_email/<email_id>')
def message(email_id):
    content = test.read_email(email_id)
    return render_template('read_email.html', content=content)


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
        
if __name__ == '__main__':
    app.run(debug=True)
