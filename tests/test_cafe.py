import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from cafe_engine import CyberBobaEngine

def test_serve_and_undo():
    sample_menu = {
        "Thai Milk Tea": {"price": 45, "ingredients": ("Tea", "Milk", "Sugar")},
        "Peach Iced Tea": {"price": 40, "ingredients": ("Tea", "Peach", "Ice")}
    }
    cafe = CyberBobaEngine(sample_menu)
    cafe.customer_queue[0] = {
        "customer": "Tester", "drink": "Thai Milk Tea",
        "price": 45, "recipe": ("Tea", "Milk", "Sugar"), "budget": 100
    }

    cafe.add_ingredient("Tea")
    cafe.add_ingredient("Boba")
    ok_undo, _ = cafe.undo_ingredient()
    assert ok_undo is True
    assert cafe.current_cup == ["Tea"]

    cafe.add_ingredient("Milk")
    cafe.add_ingredient("Sugar")
    ok_serve, _ = cafe.serve_order()
    assert ok_serve is True
    assert cafe.stats["money"] == 195
    assert cafe.stats["served"] == 1

def test_recursion_combo_finder():
    sample_menu = {
        "A": {"price": 40, "ingredients": ("Tea",)},
        "B": {"price": 55, "ingredients": ("Milk",)},
        "C": {"price": 60, "ingredients": ("Boba",)}
    }
    cafe = CyberBobaEngine(sample_menu)
    combo = cafe.find_combo_for_budget(100)
    assert len(combo) == 2
    assert "A (40฿)" in combo and "C (60฿)" in combo

if __name__ == "__main__":
    test_serve_and_undo()
    test_recursion_combo_finder()
    print("✅ All Cyber Boba Test Cases Passed Successfully!")ห