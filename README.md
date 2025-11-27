BossHub Python Client
Official Python library for interacting with BossHub Cloud Platform.
Designed for IoT Devices (Raspberry Pi, Servers) and MicroPython (ESP32).
Installation
Method 1: Install from source (For Development)
Download the source code and run:
pip install .

Method 2: Install via PyPI (Future)
pip install bosshub

Usage
import bosshub

# Connect
client = bosshub.connect("YOUR_API_KEY")

# Send Log
client.log("INFO", "Machine Started")

# Send Heartbeat
client.heartbeat("DEVICE-001")

Features
 * Auto-detect platform (Standard Python vs MicroPython)
 * Built-in Error Handling
 * Support Environment Variables


my_project/
├── setup.py
├── README.md
└── bosshub/
    └── __init__.py

**วิธีที่ 1: ติดตั้งลงเครื่องเลย (Development Mode)**
เปิด Terminal ในโฟลเดอร์นี้แล้วพิมพ์:
```bash
pip install -e .
*(Option `-e` คือ editable หมายความว่าถ้าคุณบอสแก้โค้ดใน `__init__.py` ปุ๊บ เวลาเรียกใช้ `import bosshub` โค้ดจะเปลี่ยนตามทันที ไม่ต้องลงใหม่ เหมาะกับช่วงกำลังพัฒนา)*

**วิธีที่ 2: สร้างไฟล์ .whl ไปแจกทีมงาน**
```bash
pip install wheel
python setup.py bdist_wheel
จะได้ไฟล์ในโฟลเดอร์ `dist/bosshub-0.1.0-py3-none-any.whl` เอาไฟล์นี้ส่งให้ลูกน้อง แล้วให้เขาพิมพ์:
```bash
pip install bosshub-0.1.0-py3-none-any.whl

เสร็จเรียบร้อยครับ! ตอนนี้ `import bosshub` ได้ทุกที่ในเครื่องแล้วครับ
