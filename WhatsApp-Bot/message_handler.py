from twilio.twiml.messaging_response import MessagingResponse
from reminder_utils import get_timezone_and_country_from_phone_number, save_reminder
from openai_client import get_ai_response, get_reminder_summary
from datetime import datetime
import pytz

first_message = True

def handle_message(request):
    global first_message
    try:
        incoming_msg = request.form.get('Body').lower()
        from_number = request.form.get('From')
        response = MessagingResponse()
        message = response.message()
        responded = False

        user_timezone, user_country = get_timezone_and_country_from_phone_number(from_number)
        ai_response = get_ai_response(incoming_msg)
        print(f"AI response: {ai_response}")

        # if first_message:
        #     if user_country == "Israel":
        #         reply = "שלום! \n יצרת קשר עם הבינה המלאכותית שלנו, אני יודעת לעשות הכל, מנהל איתך שיח על כל נושא שבעולם, ליצירת תזכורות ועד לביצוע רכישות בשלל נושאים, על מה תרצה לדבר?"
        #     else:
        #         reply = "Hello! \nYou have reached our AI assistant. I can help you with anything, from setting reminders to making purchases on various topics. What would you like to talk about?"
        #     message.body(reply)
        #     first_message = False
        #     responded = True
        #TODO. not sure this part is correct, need to start testing it.
        if "תזכורת" in ai_response or "reminder" in ai_response:
            # AI detected a reminder request, summarize the reminder details
            reminder_summary = get_reminder_summary(incoming_msg)
            print(f"Reminder summary: {reminder_summary}")

            try:
                # Extract reminder details from the summary
                parts = reminder_summary.split(',')
                datetime_str = parts[0].strip()
                content = parts[1].strip()

                # Parse the date and time
                reminder_datetime = datetime.strptime(datetime_str, "%m/%d/%Y %H:%M")
                reminder_datetime = user_timezone.localize(reminder_datetime)

                # Check if the date is in the past
                if reminder_datetime < datetime.now(user_timezone):
                    raise ValueError("The date is incorrect. The date is in the past.")

                # Save the reminder to the database
                save_reminder(from_number, reminder_datetime, content, user_timezone, user_country)
                #TODO. need to make sure it's saying it was saved in the correct language.
                message.body("Reminder set successfully!")
                responded = True
            except ValueError as e:
                message.body(str(e))
                responded = True
        else:
            message.body(ai_response)
            responded = True

        return str(response)
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500