from flask import Flask, request, jsonify
import requests, os
from dotenv import load_dotenv
import logging

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "5g1ljdn0Ba7gaOqWETmhUlcPX9kaLCbh")
WHAPI_URL = "https://gate.whapi.cloud/messages/text"

TEMPLATES = {
    "ain_mana": "היי {name},\nמדבר רובי ממכירות של חברת yes.\nקיבלתי את הפרטים שלך ולא הצלחתי להשיג אותך, אשמח שנדבר מתי מתאים לך?",

    "lkoach_kayam": "היי {name},\nזה רובי מחברת yes הרגע דיברנו, אני שולח לך בכל מקרה את הנייד שלי במידה ויהיה שינוי אשמח לתת מענה באופן אישי.",

    "hatzaat_mchir": "היי {name},\nזה רובי מחברת yes, שלחתי לך בנוסף את הנייד שלי לכל שאלה נוספת שתהיה לך, אשמח לעזור.",

    "sihat_hemshech": "היי {name},\nמדבר רובי מחברת yes, שלחתי לך בנוסף את הנייד שלי אם יש שינוי לגבי השעה שקבענו לדבר, או כל שאלה שיש אני זמין בשבילך.",

    "lkoach_kayam_hatzaa": "היי {name},\nמדבר רובי מחברת yes, קיבלתי את הפרטים שלך וראיתי שאתם לקוחות קיימים.\nאם זה לגבי מנוי נוסף או חדש אני הכתובת, ובמידה לטיפול במנוי הקיים אנא פנו ל*2080.",

    "shavua_tov": "היי {name}, שבוע טוב.\nמדבר רובי מחברת yes, קיבלתי את הפרטים שלך לגבי הצטרפות.\nאשמח לתאם איתך שיחה, אני מ-8:15 זמין מתי מתאים לך?\nמשהו נוסף במידה ואתם לקוחות קיימים sting/yes השירות מול *2080",

    "mivtza": "היי {name},\nיומיים אחרונים למבצע הגדול של yes 👇\n\nמסלול 1 – yes+ כולל אינטרנט סיבים ב־199₪\nכולל את כל ההטבות הבאות:\n• מנוי Netflix ל-3 חודשים בחינם\n• חבילת ספורט 1 (צ'רלטון) ל-3 חודשים בחינם\n• מנוי HBO ל-3 חודשים בחינם\n• מנוי Disney+ ל-3 חודשים בחינם\n• כל הממירים בחינם\n• ראוטר חינם\n\nמסלול 2 – טלוויזיה בלבד ב־99₪\nעם כל ההטבות שלמעלה.\n\nאם רלוונטי תגיבו ואתקשר להתקדם\n*המבצע הינו ללקוחות חדשים בלבד, לקוחות קיימים אנא פנו ל*2080 לקבלת שירות.",
}

def send_whatsapp(phone, message):
    phone = phone.replace("+","").replace("-","").replace(" ","")
    if phone.startswith("0"):
        phone = "972" + phone[1:]
    headers = {"Authorization": f"Bearer {WHAPI_TOKEN}", "Content-Type": "application/json"}
    payload = {"to": f"{phone}@s.whatsapp.net", "body": message}
    response = requests.post(WHAPI_URL, json=payload, headers=headers, timeout=15)
    logger.info(f"Whapi response: {response.json()}")
    return response.json()

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}, 200

@app.route("/webhook/<template_key>", methods=["GET", "POST"])
def webhook(template_key):
    if request.is_json:
        data = request.get_json()
    else:
        data = {**request.form.to_dict(), **request.args.to_dict()}

    logger.info(f"Webhook [{template_key}]: {data}")

    phone = data.get("customer_phone") or data.get("phone")
    name = data.get("customer_name") or data.get("name") or "לקוח יקר"

    if not phone:
        return {"error": "Missing phone"}, 400

    template = TEMPLATES.get(template_key)
    if not template:
        return {"error": f"Unknown template: {template_key}"}, 404

    message = template.format(name=name)
    result = send_whatsapp(phone, message)
    return {"success": True, "result": result}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
