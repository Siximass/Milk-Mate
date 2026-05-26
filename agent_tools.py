from datetime import datetime

from dotenv import load_dotenv
from sheets_client import get_sheet


def validate_sale(menu: str, quantity: int, price: float) -> None:
    """Guardrails: ตรวจข้อมูลก่อนบันทึกยอดขาย"""
    if not menu or not menu.strip():
        raise ValueError("ชื่อเมนูห้ามว่าง")

    if quantity <= 0:
        raise ValueError("จำนวนต้องมากกว่า 0")

    if price <= 0:
        raise ValueError("ราคาต้องมากกว่า 0")


def log_sale(menu: str, quantity: int, price: float) -> dict:
    """
    Tool สำหรับบันทึกยอดขายลง Google Sheets จริง
    """
    load_dotenv()

    validate_sale(menu, quantity, price)

    total = quantity * price
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet = get_sheet()

    row = [
        timestamp,
        menu,
        quantity,
        price,
        total,
    ]

    sheet.append_row(row)

    return {
        "status": "success",
        "menu": menu,
        "quantity": quantity,
        "price": price,
        "total": total,
        "timestamp": timestamp,
    }


TOOLS = {
    "log_sale": log_sale,
}