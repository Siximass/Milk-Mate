import os
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from sheets_client import get_sheet


def get_yesterday_date() -> str:
    """คืนค่าวันที่เมื่อวานในรูปแบบ YYYY-MM-DD"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def read_sales_for_date(target_date: str):
    """
    อ่านข้อมูลจาก Google Sheet แล้วกรองเฉพาะวันที่ต้องการ
    คาดว่า Sheet มีหัวตาราง:
    วันที่, เมนู, จำนวน, ราคา, ยอดรวม
    """
    sheet = get_sheet()
    rows = sheet.get_all_records()

    sales = []

    for row in rows:
        date_text = str(row.get("วันที่", ""))

        if date_text.startswith(target_date):
            sales.append(row)

    return sales


def summarize_sales(sales):
    """สรุปยอดขายรวมและหาเมนูขายดีที่สุด"""
    total_sales = 0
    menu_quantity = defaultdict(int)

    for sale in sales:
        menu = sale.get("เมนู")
        quantity = int(sale.get("จำนวน", 0))
        total = float(sale.get("ยอดรวม", 0))

        total_sales += total
        menu_quantity[menu] += quantity

    best_menu = None
    best_quantity = 0

    if menu_quantity:
        best_menu = max(menu_quantity, key=menu_quantity.get)
        best_quantity = menu_quantity[best_menu]

    return total_sales, best_menu, best_quantity


def send_telegram_message(message: str):
    """ส่งข้อความไปที่ Telegram"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token:
        raise RuntimeError("ไม่พบ TELEGRAM_BOT_TOKEN ในไฟล์ .env")

    if not chat_id:
        raise RuntimeError("ไม่พบ TELEGRAM_CHAT_ID ในไฟล์ .env")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
    }

    response = requests.post(url, data=payload, timeout=15)

    if response.status_code != 200:
        raise RuntimeError(f"ส่ง Telegram ไม่สำเร็จ: {response.text}")

    return response.json()


def build_report_message(target_date: str, sales) -> str:
    """สร้างข้อความรายงานยอดขาย"""
    if not sales:
        return f"""
🥛 Milk Mate Morning Report

วันที่: {target_date}

เมื่อวานยังไม่มีรายการขายในระบบนะ
วันนี้ขอให้ขายดี ลูกค้าแน่นร้านน้า ✨
""".strip()

    total_sales, best_menu, best_quantity = summarize_sales(sales)

    return f"""
🥛 Milk Mate Morning Report

สรุปยอดขายประจำวันที่ {target_date}

💰 ยอดขายรวม: {total_sales:.2f} บาท
🏆 เมนูขายดี: {best_menu}
📦 จำนวนที่ขายได้: {best_quantity} แก้ว

ขอให้วันนี้ Milk Mate ขายดีทั้งวันเลยน้า ✨
""".strip()


def main():
    load_dotenv()

    target_date = get_yesterday_date()
    sales = read_sales_for_date(target_date)
    message = build_report_message(target_date, sales)

    send_telegram_message(message)

    print("✅ ส่ง Morning Report สำเร็จ")
    print(message)


if __name__ == "__main__":
    main()