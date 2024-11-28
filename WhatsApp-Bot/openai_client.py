from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Get the OpenAI API key from environment variables
client =OpenAI( api_key = os.getenv('OPENAI_API_KEY'))

#TODO. need to fix the AI response, this is not working
def get_ai_response(prompt):
    response = client.completions.create(
        model ="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def get_reminder_summary(user_message):
    prompt = f"Extract the reminder details from the following message and summarize it in the format 'Date Time, Reminder':\n\n{user_message}"
    response = client.completions.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    print(response.choices[0].text.strip()) # Debugging
    return response.choices[0].text.strip()