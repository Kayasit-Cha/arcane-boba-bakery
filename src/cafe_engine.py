import copy
import random

INGREDIENT_COSTS = {
    "Tea": 4, "Milk": 5, "Sugar": 2, "Matcha": 10,
    "Boba": 6, "BrownSugar": 5, "Peach": 7, "Ice": 2,
    "Taro": 8, "Cocoa": 7, "Dough": 8, "Butter": 6
}

class CyberBobaEngine:
    def __init__(self, menu: dict[str, dict]):
        self.menu = menu
        self.inventory = {
            "Tea": 8, "Milk": 8, "Sugar": 8, "Matcha": 6,
            "Boba": 6, "BrownSugar": 6, "Peach": 6, "Ice": 8,
            "Taro": 6, "Cocoa": 6, "Dough": 8, "Butter": 8
        }
        self.initial_money = 250
        self.stats = {
            "money": 250,
            "revenue": 0,
            "cost": 0,
            "profit": 0,
            "served": 0,
            "reputation": 100
        }

        self.current_day = 1
        self.daily_stats = {"revenue": 0, "cost": 0, "profit": 0, "served": 0}
        self.weekly_history: list[dict] = []

        self.sales_count: dict[str, int] = {name: 0 for name in menu}
        self.tables: list[dict | None] = [None, None, None]

        self.work_items: list[str] = []
        self.is_blended: bool = False
        self.is_baked: bool = False
        self.history: list[dict] = []

        self.seat_new_customer(0)
        self.seat_new_customer(1)

    def calculate_recipe_cost(self, recipe: tuple[str, ...] | list[str]) -> int:
        return sum(INGREDIENT_COSTS.get(ing, 5) for ing in recipe)

    def seat_new_customer(self, table_idx: int | None = None) -> tuple[bool, str]:
        empty_indices = [i for i, t in enumerate(self.tables) if t is None]
        if not empty_indices:
            return False, "โต๊ะหน้าร้านเต็มหมดแล้ว!"

        idx = table_idx if (table_idx is not None and self.tables[table_idx] is None) else random.choice(empty_indices)
        customers = ["น้องมิ้นต์", "พี่เคน", "คุณแพรว", "น้องบอส", "คุณฟ้า", "พี่เจมส์", "น้องโมจิ", "พี่ต้น"]
        item_name = random.choice(list(self.menu.keys()))
        info = self.menu[item_name]
        cost = self.calculate_recipe_cost(info["ingredients"])

        self.tables[idx] = {
            "table_no": idx + 1,
            "customer": random.choice(customers),
            "item": item_name,
            "type": info["type"],
            "price": info["price"],
            "cost": cost,
            "profit": info["price"] - cost,
            "recipe": info["ingredients"],
            "budget": random.choice([120, 140, 160])
        }
        return True, f"ลูกค้า {self.tables[idx]['customer']} เดินไปนั่งที่โต๊ะ {idx + 1} และสั่ง {item_name}!"

    def timeout_customer(self, table_idx: int) -> tuple[bool, str, dict | None]:
        """จัดการเมื่อลูกค้ารอนานจนหมดเวลา: โมโหเดินออกจากร้าน + หักเครดิตร้าน -15%"""
        if not (0 <= table_idx < 3) or self.tables[table_idx] is None:
            return False, "ไม่มีลูกค้าที่โต๊ะนี้", None

        angry_order = copy.deepcopy(self.tables[table_idx])
        self.stats["reputation"] = max(0, self.stats["reputation"] - 15)
        self.tables[table_idx] = None
        self.seat_new_customer(table_idx)
        return (
            True,
            f"😡 ลูกค้า {angry_order['customer']} ที่โต๊ะ {table_idx + 1} โมโหที่รอนานเกินไปและเดินออกจากร้าน! (เครดิตร้าน -15%)",
            angry_order
        )

    def save_work_snapshot(self):
        self.history.append({
            "items": copy.deepcopy(self.work_items),
            "blended": self.is_blended,
            "baked": self.is_baked
        })

    def add_ingredient(self, item: str) -> tuple[bool, str]:
        if self.inventory.get(item, 0) <= 0:
            return False, f"วัตถุดิบ '{item}' หมดสต็อก! กรุณากดปุ่ม '🛒 สั่งซื้อวัตถุดิบ' ด้านบน"
        if len(self.work_items) >= 4:
            return False, "ใส่ส่วนผสมได้สูงสุด 4 อย่าง"
        if self.is_blended or self.is_baked:
            return False, "ผ่านการปั่น/อบแล้ว ไม่สามารถใส่ส่วนผสมเพิ่มได้"

        self.save_work_snapshot()
        self.work_items.append(item)
        return True, f"ใส่ {item} ลงภาชนะเตรียมปรุงแล้ว (มูลค่าวัตถุดิบ {INGREDIENT_COSTS.get(item, 5)}฿)"

    def blend_work(self) -> tuple[bool, str]:
        if not self.work_items:
            return False, "กรุณาใส่วัตถุดิบก่อนนำเข้าเครื่องปั่น"
        if self.is_baked:
            return False, "ขนมอบแล้ว นำไปปั่นไม่ได้!"
        if self.is_blended:
            return False, "ปั่นเรียบร้อยแล้ว!"

        self.save_work_snapshot()
        self.is_blended = True
        return True, "🌪️ ปั่นส่วนผสมจนเนียนละเอียดเป็นสมูทตี้แล้ว!"

    def bake_work(self) -> tuple[bool, str]:
        if not self.work_items:
            return False, "กรุณาใส่แป้งและไส้ขนมก่อนนำเข้าเตาอบ"
        if self.is_blended:
            return False, "น้ำปั่นนำไปอบในเตาไม่ได้!"
        if self.is_baked:
            return False, "อบสุกหอมกรุ่นแล้ว!"

        self.save_work_snapshot()
        self.is_baked = True
        return True, "🔥 อบเบเกอรี่จนกรอบนอกนุ่มในพร้อมเสิร์ฟแล้ว!"

    def undo_work(self) -> tuple[bool, str]:
        if not self.history:
            return False, "ไม่มีขั้นตอนให้ย้อนกลับ"
        prev = self.history.pop()
        self.work_items = prev["items"]
        self.is_blended = prev["blended"]
        self.is_baked = prev["baked"]
        return True, "ย้อนกลับ 1 ขั้นตอนแล้ว"

    def clear_work(self):
        self.history.clear()
        self.work_items.clear()
        self.is_blended = False
        self.is_baked = False

    def dispatch_to_waiter(self, table_idx: int) -> tuple[bool, str, dict | None]:
        if not (0 <= table_idx < 3) or self.tables[table_idx] is None:
            return False, f"โต๊ะ {table_idx + 1} ไม่มีลูกค้านั่งอยู่", None

        order = self.tables[table_idx]
        target_set = set(order["recipe"])
        work_set = set(self.work_items)

        recipe_ok = (work_set == target_set and len(self.work_items) == len(order["recipe"]))
        process_ok = (
            (order["type"] == "NORMAL" and not self.is_blended and not self.is_baked) or
            (order["type"] == "BLENDED" and self.is_blended and not self.is_baked) or
            (order["type"] == "BAKERY" and self.is_baked and not self.is_blended)
        )

        if recipe_ok and process_ok:
            for ing in self.work_items:
                self.inventory[ing] -= 1

            earned = order["price"]
            cost = order["cost"]
            profit = earned - cost

            self.stats["money"] += earned
            self.stats["revenue"] += earned
            self.stats["cost"] += cost
            self.stats["profit"] += profit
            self.stats["served"] += 1
            self.stats["reputation"] = min(100, self.stats["reputation"] + 3)

            self.daily_stats["revenue"] += earned
            self.daily_stats["cost"] += cost
            self.daily_stats["profit"] += profit
            self.daily_stats["served"] += 1

            self.sales_count[order["item"]] = self.sales_count.get(order["item"], 0) + 1

            served_info = copy.deepcopy(order)
            self.tables[table_idx] = None
            self.clear_work()
            self.seat_new_customer(table_idx)
            return True, f"🧚‍♀️ เสิร์ฟ {order['item']} โต๊ะ {table_idx + 1} สำเร็จ! รายรับ +{earned}฿ (กำไรสุทธิ +{profit}฿ | เครดิต +3%)", served_info
        else:
            wasted = self.calculate_recipe_cost(self.work_items)
            self.stats["cost"] += wasted
            self.stats["profit"] -= wasted
            self.stats["reputation"] = max(0, self.stats["reputation"] - 10)
            self.daily_stats["cost"] += wasted
            self.daily_stats["profit"] -= wasted
            self.clear_work()

            reason = "ขั้นตอนผิด (ลืมปั่น/ลืมอบ)" if recipe_ok else "ส่วนผสมไม่ตรงตามสูตร"
            return False, f"❌ {reason}! โต๊ะ {table_idx + 1} ปฏิเสธออเดอร์ (เสียต้นทุน -{wasted}฿ | เครดิต -10%)", None

    def buy_ingredients(self, cart: dict[str, int]) -> tuple[bool, str]:
        total_cost = 0
        purchased_list = []
        for item, qty in cart.items():
            if qty > 0 and item in INGREDIENT_COSTS:
                total_cost += INGREDIENT_COSTS[item] * qty
                purchased_list.append(f"{item} x{qty}")

        if total_cost == 0:
            return False, "กรุณาระบุจำนวนวัตถุดิบที่ต้องการสั่งซื้ออย่างน้อย 1 ชิ้น"
        if self.stats["money"] < total_cost:
            return False, f"เงินสดไม่พอสั่งซื้อ! (ยอดรวม {total_cost}฿ แต่มีเงิน {self.stats['money']}฿)"

        self.stats["money"] -= total_cost
        self.stats["cost"] += total_cost
        self.stats["profit"] -= total_cost

        self.daily_stats["cost"] += total_cost
        self.daily_stats["profit"] -= total_cost

        for item, qty in cart.items():
            if qty > 0 and item in self.inventory:
                self.inventory[item] += qty

        return True, f"🛒 สั่งซื้อวัตถุดิบสำเร็จ ({', '.join(purchased_list)}) จ่ายเงิน -{total_cost}฿ (บวกเข้าต้นทุนสะสมแล้ว)"

    def get_restock_recommendations(self) -> list[dict]:
        recs = []
        for item, qty in self.inventory.items():
            if qty <= 4:
                suggested_qty = 8 - qty
                recs.append({
                    "item": item,
                    "current": qty,
                    "suggested": suggested_qty,
                    "unit_cost": INGREDIENT_COSTS[item],
                    "est_cost": suggested_qty * INGREDIENT_COSTS[item]
                })
        return sorted(recs, key=lambda x: x["current"])

    def close_current_day(self) -> dict:
        day_record = {
            "day": self.current_day,
            "revenue": self.daily_stats["revenue"],
            "cost": self.daily_stats["cost"],
            "profit": self.daily_stats["profit"],
            "served": self.daily_stats["served"],
            "ending_money": self.stats["money"]
        }
        if not any(d["day"] == self.current_day for d in self.weekly_history):
            self.weekly_history.append(day_record)

        growth_pct = round(((self.stats["money"] - self.initial_money) / self.initial_money) * 100, 1)

        return {
            "day_record": day_record,
            "weekly_history": self.weekly_history,
            "recommendations": self.get_restock_recommendations(),
            "is_week_complete": (self.current_day >= 7),
            "initial_money": self.initial_money,
            "current_money": self.stats["money"],
            "total_revenue": self.stats["revenue"],
            "total_cost": self.stats["cost"],
            "total_profit": self.stats["profit"],
            "growth_pct": growth_pct
        }

    def start_next_day(self) -> str:
        if self.current_day >= 7:
            self.current_day = 1
            self.weekly_history.clear()
            self.initial_money = self.stats["money"]
        else:
            self.current_day += 1

        self.daily_stats = {"revenue": 0, "cost": 0, "profit": 0, "served": 0}
        self.clear_work()
        for i in range(3):
            if self.tables[i] is None:
                self.seat_new_customer(i)
        return f"🌅 เปิดร้านวันที่ {self.current_day}/7 แล้ว! พร้อมรับลูกค้าได้เลย"

    def get_top_sellers(self, top_n: int = 3) -> list[tuple[str, int]]:
        sold = [(name, cnt) for name, cnt in self.sales_count.items() if cnt > 0]
        return sorted(sold, key=lambda x: x[1], reverse=True)[:top_n]