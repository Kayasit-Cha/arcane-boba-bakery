import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from cafe_engine import CyberBobaEngine, INGREDIENT_COSTS
from file_manager import load_menu_from_csv, save_daily_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
MENU_FILE = os.path.join(BASE_DIR, "data", "menu.csv")
LOG_FILE = os.path.join(BASE_DIR, "sales_history.log")

engine = CyberBobaEngine(load_menu_from_csv(MENU_FILE))
status_message = "🔮 ยินดีต้อนรับสู่ Arcane Boba & Bakery (วันที่ 1/7)! รีบเสิร์ฟก่อนลูกค้าโมโหและหักเครดิตร้าน"

class BobaWebHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(SRC_DIR, "index.html"), "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404)

    def do_POST(self):
        global status_message
        if self.path == "/api/action":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            action = data.get("action")
            served_info = None
            angry_info = None
            day_summary = None

            if action == "ADD":
                _, status_message = engine.add_ingredient(data["item"])
            elif action == "BLEND":
                _, status_message = engine.blend_work()
            elif action == "BAKE":
                _, status_message = engine.bake_work()
            elif action == "UNDO":
                _, status_message = engine.undo_work()
            elif action == "CLEAR":
                engine.clear_work()
                status_message = "ล้างภาชนะเตรียมปรุงแล้ว"
            elif action == "SERVE_TABLE":
                _, status_message, served_info = engine.dispatch_to_waiter(data["table_idx"])
            elif action == "TIMEOUT_CUSTOMER":
                _, status_message, angry_info = engine.timeout_customer(data["table_idx"])
            elif action == "NEW_CUSTOMER":
                _, status_message = engine.seat_new_customer()
            elif action == "BUY_SUPPLIES":
                _, status_message = engine.buy_ingredients(data.get("cart", {}))
            elif action == "CLOSE_DAY":
                day_summary = engine.close_current_day()
                status_message = f"🌙 ปิดร้านสรุปยอดประจำวันที่ {engine.current_day}/7 เรียบร้อย!"
            elif action == "NEXT_DAY":
                status_message = engine.start_next_day()
            elif action == "SAVE_REPORT":
                save_daily_report(LOG_FILE, engine.stats, engine.get_top_sellers())
                status_message = "บันทึกสรุปยอดขายและกำไรลงไฟล์ sales_history.log เรียบร้อยแล้ว!"

            payload = {
                "day": engine.current_day,
                "stats": engine.stats,
                "daily_stats": engine.daily_stats,
                "inventory": engine.inventory,
                "costs": INGREDIENT_COSTS,
                "tables": engine.tables,
                "work": {
                    "items": engine.work_items,
                    "is_blended": engine.is_blended,
                    "is_baked": engine.is_baked,
                    "cost": engine.calculate_recipe_cost(engine.work_items)
                },
                "served_info": served_info,
                "angry_info": angry_info,
                "day_summary": day_summary,
                "recommendations": engine.get_restock_recommendations(),
                "top_sellers": engine.get_top_sellers(),
                "message": status_message
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", PORT), BobaWebHandler)
    print(f"🔮 เปิดร้าน Arcane Boba & Bakery (7-Day Tycoon) ที่พอร์ต: {PORT}")
    if "PORT" not in os.environ:
        webbrowser.open(f"http://127.0.0.1:{PORT}")
    server.serve_forever()