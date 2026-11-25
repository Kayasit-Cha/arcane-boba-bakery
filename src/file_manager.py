import os
from datetime import datetime

def load_menu_from_csv(filepath: str) -> dict[str, dict]:
    """อ่านไฟล์ menu.csv และแปลงเป็น Dictionary เก็บราคา ประเภทการทำ และ Tuple ของวัตถุดิบ"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"ไม่พบไฟล์เมนู: {filepath}")

    menu = {}
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            clean_line = line.strip()
            if not clean_line:
                continue
            parts = [p.strip() for p in clean_line.split(",")]
            drink_name = parts[0]
            price = int(parts[1])
            station_type = parts[2].upper()  # NORMAL, BLENDED, BAKERY
            ingredients = tuple(parts[3].split("|"))
            menu[drink_name] = {
                "price": price,
                "type": station_type,
                "ingredients": ingredients
            }
    return menu

def save_daily_report(log_filepath: str, stats: dict, top_drinks: list[tuple[str, int]]) -> None:
    """บันทึกสรุปยอดขายและเมนูขายดีลงไฟล์ sales_history.log"""
    os.makedirs(os.path.dirname(log_filepath), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    top_str = ", ".join(f"{name} ({cnt} ที่)" for name, cnt in top_drinks) or "ไม่มีรายการขาย"

    entry = (
        f"[{timestamp}] รายได้รวม: {stats['revenue']}฿ | ต้นทุน: {stats['cost']}฿ | "
        f"กำไรสุทธิ: {stats['profit']}฿ | เสิร์ฟสำเร็จ: {stats['served']} ที่ | "
        f"เมนูขายดี: {top_str}\n"
    )
    with open(log_filepath, "a", encoding="utf-8") as file:
        file.write(entry)