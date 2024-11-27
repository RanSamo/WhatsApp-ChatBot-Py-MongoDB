from flask import Flask, request
from message_handler import handle_message
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

@app.route("/sms", methods=['POST'])
def reply():
    return handle_message(request)

if __name__ == "__main__":
    # Import the scheduler to start it
    import scheduler
    app.run(debug=True)
