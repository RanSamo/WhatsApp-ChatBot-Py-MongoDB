from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
import os
import time
import threading
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

# Get the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI')

# Set up MongoDB connection
client = MongoClient(MONGODB_URI)
db = client['RemindersDB']
reminders_collection = db['reminders']

# Define the Israel time zone
israel_tz = pytz.timezone('Asia/Jerusalem')

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# Initialize Twilio client
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_reminder(phone_number, content):
    # Ensure the from number has the whatsapp: prefix
    from_number = f"whatsapp:{TWILIO_PHONE_NUMBER}"
    
    message = twilio_client.messages.create(
        body=content,
        from_=from_number,
        to=phone_number  # Use the phone number directly from the database
    )
    print(f"Sent reminder to {phone_number}: {content}")

def check_reminders():
    while True:
        try:
            # Get the current time in UTC
            now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
            
            # Convert the current time to Israel time zone
            now_israel = now_utc.astimezone(israel_tz)
            
            # Query the reminders collection for reminders that are due
            due_reminders = reminders_collection.find({
                "date": {
                    "$lte": now_utc
                }
            })
            
            for reminder in due_reminders:
                # Convert the reminder time to Israel time zone
                reminder_time_utc = reminder['date']
                reminder_time_israel = reminder_time_utc.astimezone(israel_tz)
                
                # Send the reminder to the client
                send_reminder(reminder['phone_number'], reminder['content'])
                
                # Remove the reminder from the collection after sending
                reminders_collection.delete_one({"_id": reminder["_id"]})
            
            # Sleep for a minute before checking again
            time.sleep(60)
        except Exception as e:
            print(f"Error in scheduler: {e}")

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=check_reminders)
scheduler_thread.daemon = True
scheduler_thread.start()