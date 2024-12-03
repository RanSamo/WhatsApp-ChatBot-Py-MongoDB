from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Get the OpenAI API key from environment variables
client =OpenAI()

#TODO. need to fix the AI response, this is not working
def get_ai_response(prompt):
    response = client.chat.completions.create(
        model ="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an assistant that helps the user with everything he asks for and more important when you see he wants to set a reminder you need to analyze it and sent it in the format 'Date Time, Reminder'"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def get_reminder_summary(user_message):
    prompt = f"Extract the reminder details from the following message and summarize it in the format 'Date Time (if you receive the date in this format: %d.%m.%Y %H:%M, change it to %d/%m/%Y %H:%M and don't write the word 'Date'.) , Reminder (no need to write thee actual word 'reminder', can just write the content)':\n\n{user_message}"
    response = client.chat.completions.create(
        model ="gpt-4o",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": prompt}
        ]
    )
    print(response.choices[0].message.content) # Debugging
    return response.choices[0].message.content