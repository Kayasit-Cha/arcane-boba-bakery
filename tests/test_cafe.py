import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from cafe_engine import CyberBobaEngine

SAMPLE_MENU = {
    "Thai Milk Tea": {"type": "NORMAL", "price": 45, "ingredients": ("Tea", "Milk", "Sugar")},
    "Matcha Smoothie": {"type": "BLENDED", "price": 65, "ingredients": ("Matcha", "Milk", "Ice")},
    "Butter Croissant": {"type": "BAKERY", "price": 55, "ingredients": ("Dough", "Butter")},
}


class TestArcaneBobaEngine(unittest.TestCase):
    def setUp(self):
        self.cafe = CyberBobaEngine(SAMPLE_MENU)

    def test_add_undo_and_serve_normal_drink(self):
        """TC-01 & TC-04: ทดสอบการใส่วัตถุดิบ ย้อนกลับ (Undo) และเสิร์ฟเมนูชงปกติ"""
        self.cafe.tables[0] = {
            "table_no": 1,
            "customer": "Tester",
            "item": "Thai Milk Tea",
            "type": "NORMAL",
            "price": 45,
            "cost": 11,
            "profit": 34,
            "recipe": ("Tea", "Milk", "Sugar"),
            "budget": 120,
        }

        self.cafe.add_ingredient("Tea")
        self.cafe.add_ingredient("Boba")
        ok_undo, _ = self.cafe.undo_work()
        self.assertTrue(ok_undo)
        self.assertEqual(self.cafe.work_items, ["Tea"])

        self.cafe.add_ingredient("Milk")
        self.cafe.add_ingredient("Sugar")
        ok_serve, _, _ = self.cafe.dispatch_to_waiter(0)

        self.assertTrue(ok_serve)
        self.assertEqual(self.cafe.stats["money"], 295)   # 250 + 45
        self.assertEqual(self.cafe.stats["profit"], 34)   # 45 - 11
        self.assertEqual(self.cafe.stats["served"], 1)
        self.assertEqual(self.cafe.inventory["Tea"], 7)   # 8 - 1

    def test_blended_and_bakery_processes(self):
        """ทดสอบระบบเครื่องปั่น (BLENDED) และเตาอบ (BAKERY) รวมถึงการหักเครดิตเมื่อทำผิดขั้นตอน"""
        self.cafe.tables[0] = {
            "table_no": 1,
            "customer": "TesterBlend",
            "item": "Matcha Smoothie",
            "type": "BLENDED",
            "price": 65,
            "cost": 17,
            "profit": 48,
            "recipe": ("Matcha", "Milk", "Ice"),
            "budget": 140,
        }

        # ลองเสิร์ฟโดยลืมกดปั่น -> ต้องไม่สำเร็จและโดนหักเครดิต -10%
        for ing in ("Matcha", "Milk", "Ice"):
            self.cafe.add_ingredient(ing)
        ok_fail, _, _ = self.cafe.dispatch_to_waiter(0)
        self.assertFalse(ok_fail)
        self.assertEqual(self.cafe.stats["reputation"], 90)

        # ทำใหม่และกดปั่นให้ถูกต้อง -> ต้องเสิร์ฟสำเร็จและได้เครดิตคืน +3%
        for ing in ("Matcha", "Milk", "Ice"):
            self.cafe.add_ingredient(ing)
        ok_blend, _ = self.cafe.blend_work()
        self.assertTrue(ok_blend)
        ok_serve_blend, _, _ = self.cafe.dispatch_to_waiter(0)
        self.assertTrue(ok_serve_blend)
        self.assertEqual(self.cafe.stats["reputation"], 93)

        # ทดสอบเมนูอบ (BAKERY)
        self.cafe.tables[1] = {
            "table_no": 2,
            "customer": "TesterBake",
            "item": "Butter Croissant",
            "type": "BAKERY",
            "price": 55,
            "cost": 14,
            "profit": 41,
            "recipe": ("Dough", "Butter"),
            "budget": 140,
        }
        self.cafe.add_ingredient("Dough")
        self.cafe.add_ingredient("Butter")
        ok_bake, _ = self.cafe.bake_work()
        self.assertTrue(ok_bake)
        ok_serve_bake, _, _ = self.cafe.dispatch_to_waiter(1)
        self.assertTrue(ok_serve_bake)
        self.assertEqual(self.cafe.stats["served"], 2)

    def test_customer_timeout_reputation_penalty(self):
        """TC-05: ทดสอบการหักเครดิตร้าน -15% เมื่อลูกค้ารอนานจนหมดเวลา"""
        self.assertEqual(self.cafe.stats["reputation"], 100)
        ok_timeout, _, _ = self.cafe.timeout_customer(0)
        self.assertTrue(ok_timeout)
        self.assertEqual(self.cafe.stats["reputation"], 85)

    def test_buy_ingredients_market(self):
        """TC-02 & TC-03: ทดสอบการสั่งซื้อวัตถุดิบเข้าคลังและกรณีเงินสดไม่พอ"""
        # Boba (6*5=30) + Tea (4*2=8) = 38 บาท
        ok_buy, _ = self.cafe.buy_ingredients({"Boba": 5, "Tea": 2})
        self.assertTrue(ok_buy)
        self.assertEqual(self.cafe.stats["money"], 212)   # 250 - 38
        self.assertEqual(self.cafe.inventory["Boba"], 11)  # 6 + 5
        self.assertEqual(self.cafe.inventory["Tea"], 10)   # 8 + 2

        # สั่งซื้อเกินเงินที่มี (Matcha 50 ชิ้น = 500 บาท > 212 บาท)
        ok_over, _ = self.cafe.buy_ingredients({"Matcha": 50})
        self.assertFalse(ok_over)

    def test_seven_day_cycle_and_report(self):
        """TC-06: ทดสอบลูปการเปิด-ปิดร้านครบ 7 วันและการสรุปผลประกอบการ"""
        for day in range(1, 7):
            summary = self.cafe.close_current_day()
            self.assertFalse(summary["is_week_complete"])
            self.cafe.start_next_day()
            self.assertEqual(self.cafe.current_day, day + 1)

        final_summary = self.cafe.close_current_day()
        self.assertTrue(final_summary["is_week_complete"])
        self.assertEqual(len(final_summary["weekly_history"]), 7)


if __name__ == "__main__":
    unittest.main(verbosity=2)