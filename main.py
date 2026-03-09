"""
WhatsApp Middleware Server — Whapi.cloud
-----------------------------------------
"""

from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "5g1ljdn0Ba7gaOqWETmhUlcPX9kaLCbh")
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
API_SECRET = os.getenv("API_SECRET", "rubi2080")

TEMPLATES = {
    "אין מענה": "היי {name},\nמדבר רובי ממכירות של חברת yes.\nקיבלתי את הפרטים שלך ולא הצלחתי להשיג אותך, אשמח שנדבר מתי מתאים לך?",
    "לקוח קיים": "היי {name},\nזה רובי מחברת yes הרגע דיברנו, אני שולח לך בכל מקרה את הנייד שלי במידה ויהיה שינוי אשמח לתת מענה באופן אישי.",
    "נשלחה הצעת מחיר": "היי {name},\nזה רובי מחברת yes, שלחתי לך בנוסף את הנייד שלי לכל שאלה נוספת שתהיה לך, אשמח לעזור.",
    "שיחת המשך": "היי {name},\nמדבר רובי מחברת yes, שלחתי לך בנוסף את הנייד שלי אם יש שינוי לגבי השעה שקבענו לדבר, או כל שאלה שיש אני זמין בשבילך.",
    "לקוח קיים - הצעה": "היי {name},\nמדבר רובי מחברת yes, קיבלתי את הפרטים שלך וראיתי שאתם לקוחות קיימים.\nאם זה לגבי מנוי נוסף או חדש אני הכתובת, ובמידה לטיפול במנוי הקיים אנא פנו ל*2080.",
}

DEFAULT_TEMPLATE = "היי {name},\nמדבר רובי ממכירות של חברת yes.\nקיבלתי את הפרטים שלך, אשמח לדבר מתי שנוח לך."


def send_whatsapp(phone, message):
    phone = phone.replace("+", "").replace("-", "").replace(" ", "")
    if phone.startswith("0"):
        phone = "972" + phone[1:]
    headers = {"Authorization": f"Bearer {WHAPI_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": f"{phone}@s.whatsapp.net", "body": message}
    response = requests.post(WHAPI_URL, json=payload, headers=headers, timeout=15)
    return response.json()


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json() if request.is_json else request.form.to_dict()
    if not data or data.get("secret") != API_SECRET:
        return {"error": "Unauthorized"}, 401
    phone = data.get("customer_phone") or data.get("phone")
    name = data.get("customer_name") or data.get("name") or "לקוח יקר"
    template_key = data.get("template", "אין מענה")
    if not phone:
        return {"error": "Missing phone"}, 400
    message = TEMPLATES.get(template_key, DEFAULT_TEMPLATE).format(name=name)
    result = send_whatsapp(phone, message)
    return {"success": True, "result": result}, 200


@app.route("/send", methods=["POST"])
def send_direct():
    data = request.get_json()
    if not data or data.get("secret") != API_SECRET:
        return {"error": "Unauthorized"}, 401
    phone = data.get("phone")
    message = data.get("message")
    if not phone or not message:
        return {"error": "Missing phone or message"}, 400
    result = send_whatsapp(phone, message)
    return {"success": True, "result": result}, 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
