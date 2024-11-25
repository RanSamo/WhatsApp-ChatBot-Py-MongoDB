from datetime import datetime
import pytz
from pymongo import MongoClient
from twilio.twiml.messaging_response import MessagingResponse
import os
import phonenumbers
from phonenumbers import timezone, geocoder
from dotenv import load_dotenv

load_dotenv()

# Get the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI')

# Set up MongoDB connection
client = MongoClient(MONGODB_URI)
db = client['RemindersDB']
reminders_collection = db['reminders']

# Define the Israel time zone
israel_tz = pytz.timezone('Asia/Jerusalem')

first_message = True


def get_timezone_and_country_from_phone_number(phone_number):
    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(phone_number)
        
        # Get the time zone(s) for the phone number
        time_zones = timezone.time_zones_for_number(parsed_number)
        
        # Get the country for the phone number
        country = geocoder.country_name_for_number(parsed_number, "en")
        
        if time_zones:
            # Return the first time zone and the country (assuming the phone number is valid and has a time zone)
            return pytz.timezone(time_zones[0]), country
        else:
            # Default to UTC if no time zone is found
            return pytz.utc, country
    except phonenumbers.NumberParseException:
        # Handle invalid phone numbers
        return pytz.utc, "Unknown"


def handle_message(request):
    global first_message
    try:
        incoming_msg = request.form.get('Body').lower()
        from_number = request.form.get('From')
        response = MessagingResponse()
        print(incoming_msg)
        message = response.message()
        responded = False

        user_timezone, user_country = get_timezone_and_country_from_phone_number(from_number)
        print(f"User's time zone: {user_timezone}")

        if first_message:
            reply = "שלום! \nאת/ה רוצה שניצור תזכורת?"
            message.body(reply)
            first_message = False
            responded = True
        elif "כן" in incoming_msg:
            reminder_string = "בבקשה תמלא/י את התאריך הרצוי בפורמט הבא בלבד:\n"\
                              "\nתאריך ושעה @ תזכורת"\
                              "\n\nלדוגמא: 01.01.2022 08:00 @ תזכורת לקניות"
            message.body(reminder_string)
            responded = True
        elif "לא" in incoming_msg:
            reply = "אוקיי, שיהיה לך יום טוב!"
            message.body(reply)
            first_message = True
            responded = True
        elif '@' in incoming_msg:
            parts = incoming_msg.split('@')
            datetime_str = parts[0].strip()
            content = parts[1].strip()
            
            try:
                # Ensure the time part is in HH:MM format
                date_part, time_part = datetime_str.split()
                if len(time_part) == 4:  # e.g., 8:00
                    time_part = '0' + time_part  # Pad with leading zero
                datetime_str = f"{date_part} {time_part}"
                
                # Parse the date and time
                reminder_datetime = datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
                reminder_datetime = israel_tz.localize(reminder_datetime)

                # Check if the date is in the past
                if reminder_datetime < datetime.now(user_timezone):
                    raise ValueError("התאריך שגוי. התאריך הוא בעבר.")
                
                # Create the reminder document
                reminder = {
                    "phone_number": from_number,
                    "date": reminder_datetime,
                    "content": content,
                    "user_timezone": str(user_timezone),
                    "user_country": user_country    
                }
                
                # Insert the reminder into MongoDB
                reminders_collection.insert_one(reminder)
                
                reply = "התזכורת שלך נשמרה בהצלחה!"
                message.body(reply)
                first_message = True
                responded = True
            except ValueError as ve:
                reply = f" פורמט שגוי או תאריך שכבר חלף, \nאנא שלח/י את התזכורת כפי שמצוין בדוגמה."
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