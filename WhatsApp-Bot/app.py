from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from dateutil.parser import parse


app = Flask(__name__)
count=0


@app.route("/sms", methods=['POST'])
def reply():
    try:
        incoming_msg = request.form.get('Body').lower()
        response = MessagingResponse()
        print(incoming_msg)
        message = response.message()
        responded = False
        words = incoming_msg.split('@')
        if "שלום" in incoming_msg:
            reply = "שלום! \nאתה רוצה שניצור תזכורת?"
            message.body(reply)
            responded = True

        if len(words) == 1 and "כן" in incoming_msg:
            reminder_string = "בבקשה תשים את התאריך הרצוי בפורמט הבא בלבד.\n\n"\
            "תאריך @ הקלד פה את התאריך "
            message.body(reminder_string)
            responded = True
        if len(words) == 1 and "לא" in incoming_msg:
            reply = "אוקיי, להתראות!"
            message.body(reply)
            responded = True

        return str(response)
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500
    
    # elif len(words) != 1:
    #     input_type = words[0].strip().lower()
    #     input_string = words[1].strip()
    #     if input_type == "date":
    #         reply="Please enter the reminder message in the following format only.\n\n"\
    #         "*Reminder @* _type the message_"
    #         set_reminder_date(input_string)
    #         message.body(reply)
    #         responded = True
    #     if input_type == "reminder":
    #         print("yuhu")
    #         reply="Your reminder is set!"
    #         set_reminder_body(input_string)
    #         message.body(reply)
    #         responded = True
        
    # if not responded:
    #     print("why", input_type)
    #     message.body('Incorrect request format. Please enter in the correct format')
    
    # return str(response)
    
# def set_reminder_date(msg):
#     p= parse(msg)
#     date=p.strftime('%d/%m/%Y')
#     save_reminder_date(date)
#     return 0
    
# def set_reminder_body(msg):
#     save_reminder_body(msg)
#     return 0
    
     
#     return reminder_message


if __name__ == "__main__":
    app.run(debug=True)
    
