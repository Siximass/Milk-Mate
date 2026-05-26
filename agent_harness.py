import json
import os
import re
from datetime import datetime

from dotenv import load_dotenv
from google import genai

from agent_tools import TOOLS

TRACE_FILE = "agent_trace.log"
MODEL = "gemini-2.0-flash"

SYSTEM_INSTRUCTION = """
คุณคือ Demi ผู้ช่วย AI ของร้าน Milk Mate
หน้าที่ของคุณคือแปลงคำสั่งภาษาไทยให้เป็น JSON action เท่านั้น

ตอบกลับเป็น JSON เท่านั้น ห้ามอธิบายเพิ่ม

รูปแบบที่ต้องตอบ:
{"action": "log_sale", "args": {"menu": "...", "quantity": 1, "price": 1}}

ถ้าคำสั่งไม่เกี่ยวกับการบันทึกยอดขาย ให้ตอบ:
{"action": "unknown", "args": {}}

ตัวอย่าง:
ผู้ใช้: บันทึกยอดขายนมสด 3 แก้ว ราคา 30 บาท
คำตอบ: {"action": "log_sale", "args": {"menu": "นมสด", "quantity": 3, "price": 30}}

ผู้ใช้: ขายชาไทย 2 แก้ว ราคา 45
คำตอบ: {"action": "log_sale", "args": {"menu": "ชาไทย", "quantity": 2, "price": 45}}

ผู้ใช้: วันนี้ขายดีไหม
คำตอบ: {"action": "unknown", "args": {}}
"""


def write_trace(event: str, data: dict) -> None:
    """เขียน trace log เพื่อดูว่า agent รับอะไร ตอบอะไร และเรียก tool อะไร"""
    record = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        **data,
    }

    with open(TRACE_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def extract_json(text: str) -> dict:
    """
    แปลงข้อความจาก AI ให้เป็น JSON
    รองรับกรณี AI เผลอตอบมี ```json ครอบมา
    """
    cleaned = text.strip()

    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise json.JSONDecodeError("ไม่พบ JSON ในคำตอบ AI", cleaned, 0)

    return json.loads(match.group(0))


def get_client():
    """สร้าง Gemini client จาก GOOGLE_API_KEY"""
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError("ไม่พบ GOOGLE_API_KEY ในไฟล์ .env")

    return genai.Client(api_key=api_key)


def call_llm(user_input: str) -> dict:
    """ให้ Gemini แปลงภาษาคนเป็น JSON action"""
    client = get_client()

    response = client.models.generate_content(
        model=MODEL,
        contents=f"{SYSTEM_INSTRUCTION}\n\nคำสั่งจากผู้ใช้: {user_input}",
    )

    raw = response.text.strip()
    write_trace("llm_response", {"raw": raw})

    return extract_json(raw)


def fallback_parse_sale(user_input: str) -> dict:
    """
    ตัวช่วยสำรอง เผื่อ Gemini ติด quota หรือใช้งานไม่ได้
    จับคำสั่งพื้นฐาน เช่น:
    บันทึกยอดขายนมสด 3 แก้ว ราคา 30 บาท
    ขายชาไทย 2 แก้ว ราคา 45
    """
    text = user_input.strip()

    pattern = r"(?:บันทึกยอดขาย|ขาย)\s*(.+?)\s+(\d+)\s*(?:แก้ว|ที่|อัน|杯)?\s*(?:ราคา)?\s*(\d+(?:\.\d+)?)"

    match = re.search(pattern, text)

    if not match:
        return {"action": "unknown", "args": {}}

    menu = match.group(1).strip()
    quantity = int(match.group(2))
    price = float(match.group(3))

    return {
        "action": "log_sale",
        "args": {
            "menu": menu,
            "quantity": quantity,
            "price": price,
        },
    }


def run_agent(user_input: str) -> str:
    """รับคำสั่งผู้ใช้ แล้วให้ agent เลือก tool และเรียกใช้งาน"""
    write_trace("user_input", {"message": user_input})

    try:
        action_data = call_llm(user_input)
    except Exception as error:
        write_trace("llm_error", {"error": str(error)})
        action_data = fallback_parse_sale(user_input)
        write_trace("fallback_action", {"action_data": action_data})

    action = action_data.get("action")
    args = action_data.get("args", {})

    write_trace("selected_action", {"action": action, "args": args})

    if action not in TOOLS:
        write_trace("unknown_action", {"action": action})
        return "⚠️ Demi ยังทำคำสั่งนี้ไม่ได้ ตอนนี้รองรับเฉพาะการบันทึกยอดขายนะ"

    try:
        result = TOOLS[action](**args)
        write_trace("tool_result", {"action": action, "result": result})

        return (
            f"✅ บันทึกสำเร็จ: {result['menu']} "
            f"x{result['quantity']} = {result['total']} บาท"
        )

    except (ValueError, TypeError) as error:
        write_trace("tool_error", {"action": action, "error": str(error)})
        return f"❌ ข้อมูลไม่ถูกต้อง: {error}"

    except Exception as error:
        write_trace("system_error", {"action": action, "error": str(error)})
        return f"❌ ระบบมีปัญหา: {error}"


def main():
    print("Demi Agent ของ Milk Mate พร้อมรับคำสั่ง")
    print("ตัวอย่าง: บันทึกยอดขายนมสด 3 แก้ว ราคา 30 บาท")
    print("พิมพ์ exit เพื่อออก\n")

    while True:
        user_input = input("คุณ: ").strip()

        if user_input.lower() == "exit":
            print("Demi: ไว้เจอกันใหม่น้า 🥛")
            break

        if not user_input:
            print("Demi: กรุณาพิมพ์คำสั่งก่อนนะ\n")
            continue

        result = run_agent(user_input)
        print(f"Demi: {result}\n")


if __name__ == "__main__":
    main()
    