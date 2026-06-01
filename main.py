from flask import Flask, request, jsonify
import requests, os
from dotenv import load_dotenv
import logging

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WHAPI_TOKEN = os.getenv("WHAPI_TOKEN", "5g1ljdn0Ba7gaOqWETmhUlcPX9kaLCbh")
WHAPI_URL = "https://gate.whapi.cloud/channels/DRAXTH-E77P4/messages/text"

TEMPLATES = {
    "ain_mana": "היי {name},\nקיבלתי את הפרטים שלך ולא הצלחתי להשיג אותך, אשמח שנדבר מתי מתאים לך.\nמדבר רובי ממכירות של yes",
    "lkoach_kayam": "היי {name},\nהרגע דיברנו, אני שולח לך בכל מקרה את הניוד שלי במלדה וידיה שניי אשמח לתת מענה באופן אישי זה רובי מחברתך yes",
    "hatzaat_mchir": "היי {name},\nשלחתי לך בנוסף את הניוד שלי לכל שאלה נוספת שתהיה לך, אשמח לעזור. זה רובי מחברתך yes",
    "sihat_hemshech": "היי {name},\nבנוסף את הניוד שלי לדבר, או כל שאלה שיש אם זמין בשבילך. מדבר רובי מחברתך yes",
    "lkoach_kayam_hatzaa": "היי {name},\nתודה יום טוב.\nמתבצע מול השירות שלנו שלוחה 1 או 3, הינכם לקחות קיימים בהמשך לשיחתנו, הינכם לקחות קיימים שלי\n",
    "shava_tov": "היי {name},\nתאם איתך שיחה, אני מ-8:15 זמין מתי מתאים לך?\nמשהו נוסף במטרה לקחות קיימים. מדבר רובי מחברת yes",
    "mivtza": "היי {name},\nמסלול yes+ מגיני \n\n1 מסלול – yes יומיים האחרונים •\nכולל אינטרנט סיבים ב-ש199\n\nכולל את כל ההטבות הבאות:\n• תיבות מקבלים:\n• ראושרן\nבנוסף קופות חדשים בחינם• 3\n• 7 מחירים חדשים בחינם\n• nyes+ עד\nסיבום בזה 1000 כנה",
    "mivtza_charig": "היי {name},\nסיבום בזה 1000 כנה + ראושרן\nבנוסף קופות מקבלים:\n• 3 חדשים בחינם\n• 7 מחירים חדשים בחינם\n• nyes+",
    "lkoach_chadash": "היי {name},\nאת הפרטים שלך, ובכה לפני השידה שלנו רציתי לוודא פרט קצר:\nהאם אתה לקוח שלי\nמדבר רובי מהמכירות של yes",
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

# ← זה החדש: מקבל events מWhapi ומחזיר 200 מיד
# בלעדיו Whapi בולע הודעות נכנסות ולא מעביר לאייפון
@app.route("/whapi-incoming", methods=["POST", "GET"])
def whapi_incoming():
    logger.info(f"Whapi incoming event: {request.get_json(silent=True)}")
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
