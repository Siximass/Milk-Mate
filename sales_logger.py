import sys
from datetime import datetime

from dotenv import load_dotenv
from sheets_client import get_sheet


def parse_sale_input(raw_input: str):
    """
    รับ input รูปแบบ:
    เมนู:จำนวน:ราคา

    ตัวอย่าง:
    นมสด:3:30
    """
    parts = raw_input.split(":")

    if len(parts) != 3:
        raise ValueError("รูปแบบไม่ถูกต้อง ต้องเป็น เมนู:จำนวน:ราคา")

    menu_name = parts[0].strip()
    quantity = int(parts[1].strip())
    price = float(parts[2].strip())

    total = quantity * price

    return menu_name, quantity, price, total


def log_sale(raw_input: str):
    load_dotenv()

    menu_name, quantity, price, total = parse_sale_input(raw_input)

    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet = get_sheet()

    row = [
        today,
        menu_name,
        quantity,
        price,
        total,
    ]

    sheet.append_row(row)

    print("✅ บันทึกยอดขายสำเร็จ")
    print(f"เมนู: {menu_name}")
    print(f"จำนวน: {quantity}")
    print(f"ราคา: {price}")
    print(f"ยอดรวม: {total}")


def main():
    if len(sys.argv) < 2:
        print("กรุณาใส่ข้อมูลยอดขาย")
        print('ตัวอย่าง: python sales_logger.py "นมสด:3:30"')
        return

    raw_input = sys.argv[1]

    try:
        log_sale(raw_input)
    except Exception as e:
        print("❌ เกิดข้อผิดพลาด")
        print(e)


if __name__ == "__main__":
    main()