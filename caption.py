import os
from dotenv import load_dotenv
from google import genai


def generate_captions(menu_name: str, price: str) -> str:
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return """
ไม่พบ GOOGLE_API_KEY

กรุณาตรวจสอบว่า:
1. มีไฟล์ .env อยู่ในโฟลเดอร์โปรเจกต์
2. ในไฟล์ .env เขียนแบบนี้:
   GOOGLE_API_KEY=your_api_key_here
"""

    client = genai.Client(api_key=api_key)

    prompt = f"""
คุณคือผู้ช่วยเขียนแคปชั่น Instagram ให้ร้าน Milk Mate
ร้านขายนมและเครื่องดื่มสไตล์น่ารัก อบอุ่น เป็นกันเอง

ช่วยเขียนแคปชั่นภาษาไทยสำหรับเมนู:
ชื่อเมนู: {menu_name}
ราคา: {price} บาท

ขอ 3 แบบ:
1. Cute: น่ารัก อบอุ่น มีอีโมจิ
2. Minimal: สั้น เรียบ เท่
3. Gen-Z: ภาษาวัยรุ่น เป็นกันเอง

ข้อกำหนด:
- เขียนเป็นภาษาไทย
- ไม่ยาวเกินไป
- เหมาะกับโพสต์ Instagram
- ใส่ชื่อร้าน Milk Mate ได้อย่างเป็นธรรมชาติ

รูปแบบคำตอบ:
Cute: ...
Minimal: ...
Gen-Z: ...
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"""
เกิดข้อผิดพลาดในการเรียก Gemini API

สาเหตุที่เป็นไปได้:
- โควตา Gemini API หมด
- API key ยังไม่มีสิทธิ์ใช้งาน
- ระบบของ Google จำกัดการใช้งานชั่วคราว
- Model ที่เลือกยังใช้ไม่ได้กับบัญชีนี้

รายละเอียด error:
{e}
"""


def main():
    print("=== Milk Mate Caption Generator ===")

    menu_name = input("ชื่อเมนู: ")
    price = input("ราคา: ")

    result = generate_captions(menu_name, price)

    print("\n=== Caption Results ===")
    print(result)


if __name__ == "__main__":
    main()