from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
count = 0
first_message = True

# Set up MongoDB connection
client = MongoClient('mongodb://localhost:27017/') # will need to add the connection string from the MongoDB Atlas.
db = client['reminder_db']
reminders_collection = db['reminders'] # for both lines, no need to create the db and collection, when first run, MongoDB will create them automatically.

@app.route("/sms", methods=['POST'])
def reply():
    global first_message
    try:
        incoming_msg = request.form.get('Body').lower()
        response = MessagingResponse()
        print(incoming_msg)
        message = response.message()
        responded = False

        if first_message:
            reply = "שלום! \nאתה רוצה שניצור תזכורת?"
            message.body(reply)
            first_message = False
            responded = True
        elif "כן" in incoming_msg:
            reminder_string = "בבקשה תשים את התאריך הרצוי בפורמט הבא בלבד.\n\n"\
                              "תאריך ושעה @ תוכן"
            message.body(reminder_string)
            responded = True
        elif "לא" in incoming_msg:
            reply = "אוקיי, שיהיה לך יום טוב!"
            message.body(reply)
            responded = True
        elif '@' in incoming_msg:
            parts = incoming_msg.split('@')
            datetime_str = parts[0].strip()
            content = parts[1].strip()
            
            try:
                # Parse the date and time
                reminder_datetime = datetime.strptime(datetime_str, "%d/%m/%y %H:%M")
                
                # Check if the date is in the past
                if reminder_datetime < datetime.now():
                    raise ValueError("התאריך שגוי. התאריך הוא בעבר.")
                
                # Create the reminder document
                reminder = {
                    "date": reminder_datetime,
                    "content": content
                }
                
                # Insert the reminder into MongoDB
                reminders_collection.insert_one(reminder)
                
                reply = "התזכורת שלך נשמרה בהצלחה!"
                message.body(reply)
                responded = True
            except ValueError as ve:
                reply = f"פורמט שגוי או תאריך שגוי: {ve}. אנא שלח את התזכורת בפורמט הבא: תאריך ושעה @ תוכן"
                message.body(reply)
                responded = True
            except Exception as e:
                reply = "אירעה שגיאה. אנא נסה שוב."
                message.body(reply)
                responded = True

        return str(response)
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500

if __name__ == "__main__":
    app.run(debug=True)
