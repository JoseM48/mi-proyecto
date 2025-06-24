from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Claves y tokens
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# Endpoint para verificar el webhook con Meta
@app.route("/webhook", methods=["GET"])
def verify():
    verify_token = "miofrontera123"  # Puedes personalizarlo
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == verify_token:
            return challenge, 200
        else:
            return "Forbidden", 403

# Endpoint para recibir mensajes
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        user_msg = message['text']['body']
        phone_number = message['from']

        # Llama a GPT
        gpt_response = get_gpt_response(user_msg)

        # Responde por WhatsApp
        send_whatsapp_message(phone_number, gpt_response)
    except Exception as e:
        print("No se pudo procesar el mensaje:", e)
    return "OK", 200

def get_gpt_response(user_input):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "Eres un asistente virtual para los apartamentos Mio La Frontera en Medellín. Sé cálido, profesional y útil. Si no sabes algo, responde que lo consultará con el equipo."},
            {"role": "user", "content": user_input}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=payload)

from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "¡Hola desde Render! Tu bot está activo."


if __name__ == "__main__":
    app.run(debug=True)
