# Arcane Boba & Witchery Bakery (7-Day Tycoon)

เว็บแอปพลิเคชันเกมจำลองการบริหารร้านชานมไข่มุกและเบเกอรี่เวทมนตร์ในระยะเวลา 7 วัน พัฒนาด้วยภาษา Python ร่วมกับสถาปัตยกรรม Client–Server (HTTP & JSON API)

## ลิงก์เข้าใช้งานและ Source Code
* **Live Demo (เล่นผ่านเว็บ):** [วางลิงก์เว็บจาก Render ของคุณ]
* **GitHub Repository:** https://github.com/Kayasit-Cha/arcane-boba-bakery

## โครงสร้างโปรเจกต์ (Project Structure)
* `data/menu.csv` — ฐานข้อมูลเมนู สูตรวัตถุดิบ ราคาขาย และประเภทการปรุง (ปกติ / ปั่น / อบ)
* `src/main.py` — Web Server หลักสำหรับให้บริการหน้าเว็บและจัดการ JSON API
* `src/cafe_engine.py` — แกนประมวลผลตรรกะเกม ระบบการเงิน คลังวัตถุดิบ สถานะเครื่องปั่น/เตาอบ และความอดทนลูกค้า
* `src/file_manager.py` — ระบบอ่านข้อมูลจากไฟล์ CSV และบันทึกประวัติการขายลงไฟล์ Log
* `src/index.html` — ส่วนติดต่อผู้ใช้งาน (Frontend UI), แอนิเมชันลูกค้า และกราฟสรุปผลประกอบการ
* `tests/test_cafe.py` — ชุดทดสอบการทำงานของระบบ (Unit Test Cases)

## วิธีติดตั้งและรันโปรแกรมในเครื่อง (Local Setup)
1. เปิด Terminal ในโฟลเดอร์หลักของโปรเจกต์ (`CyberBoba_Project`)
2. รันคำสั่งเริ่มต้นเซิร์ฟเวอร์:
   ```bash
   uv run src/main.py