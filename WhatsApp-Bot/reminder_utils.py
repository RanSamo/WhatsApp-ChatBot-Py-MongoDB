from datetime import datetime
import pytz
from pymongo import MongoClient
import phonenumbers
from phonenumbers import timezone, geocoder
from dotenv import load_dotenv
import os

load_dotenv()

# Get the MongoDB URI from the environment variables
MONGODB_URI = os.getenv('MONGODB_URI')

# Set up MongoDB connection
client = MongoClient(MONGODB_URI)
db = client['RemindersDB']
reminders_collection = db['reminders']

def get_timezone_and_country_from_phone_number(phone_number):
    try:
        parsed_number = phonenumbers.parse(phone_number)
        time_zones = timezone.time_zones_for_number(parsed_number)
        country = geocoder.country_name_for_number(parsed_number, "en")
        if time_zones:
            return pytz.timezone(time_zones[0]), country
        else:
            return pytz.utc, country
    except phonenumbers.NumberParseException:
        return pytz.utc, "Unknown"

def save_reminder(phone_number, reminder_datetime, content, user_timezone, user_country):
    reminder = {
        "phone_number": phone_number,
        "date": reminder_datetime,
        "content": content,
        "user_timezone": str(user_timezone),
        "user_country": user_country
    }
    reminders_collection.insert_one(reminder)