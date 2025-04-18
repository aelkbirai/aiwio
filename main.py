from fastapi import FastAPI, Form
from dotenv import load_dotenv
from openai import OpenAI
from twilio.rest import Client
import os

# Load environment variables from .env file
load_dotenv()

# Setup OpenAI and Twilio clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

# Create FastAPI app
app = FastAPI()

@app.post("/webhook")
async def whatsapp_webhook(Body: str = Form(...), From: str = Form(...)):
    print(f"📩 Message from {From}: {Body}")

    # Get GPT response using OpenAI 1.x API
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a friendly gym assistant. Answer questions about gym hours, prices, and signup options."},
            {"role": "user", "content": Body}
        ]
    )

    reply = response.choices[0].message.content.strip()
    print(f"🤖 GPT reply: {reply}")

    # Send reply to WhatsApp user via Twilio
    from_number = twilio_number if twilio_number.startswith("whatsapp:") else f"whatsapp:{twilio_number}"
    to_number = From if From.startswith("whatsapp:") else f"whatsapp:{From}"
    
    twilio_client.messages.create(
        body=reply,
        from_=twilio_number,
        to=to_number
    )

    return "OK"
