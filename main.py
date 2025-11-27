import bosshub
import time

# 1. Setup
# IP: 141.98.19.212 ถูกฝังไว้ใน lib แล้ว (หรือจะใส่ override ก็ได้)
client = bosshub.connect("API_KEY_XXXX")

# 2. กำหนดฟังก์ชันที่จะทำงานเมื่อได้รับคำสั่ง
def on_command_received(topic, data):
    """
    ฟังก์ชันนี้จะทำงานทันทีที่มีคนส่ง MQTT มา
    data: เป็น Dictionary (JSON) เรียบร้อยแล้ว
    """
    cmd = data.get("cmd")
    
    if cmd == "OPEN_DOOR":
        print(">>> สั่งเปิดประตูตู้...")
        # hardware.relay_on()
        client.log("Door Opened Success")
        
    elif cmd == "RESTART":
        print(">>> กำลังรีสตาร์ทเครื่อง...")
        # machine.reset()

    elif cmd == "CHECK_STOCK":
        # ตอบกลับผ่าน MQTT ทันที
        client.publish(f"bosshub/devices/{client.device_id}/response", {
            "coke": 10,
            "pepsi": 5
        })

# 3. เชื่อมต่อ MQTT และผูกฟังก์ชัน
client.connect_mqtt(on_message_callback=on_command_received)

# 4. Main Loop (หัวใจหลักของอุปกรณ์)
print("Device Ready... Waiting for commands.")

while True:
    # [สำคัญ] สำหรับ ESP32 ต้องเรียกบรรทัดนี้เพื่อเช็คข้อความ
    # สำหรับ PC บรรทัดนี้จะไม่มีผลอะไร (เพราะรัน Thread แยกแล้ว)
    client.mqtt_loop()
    
    # ส่ง Heartbeat ทุก 10 วินาที
    # client.heartbeat() 
    # (แนะนำให้ใช้ Timer แยก หรือนับ counter เอาเพื่อไม่ให้ loop ช้า)
    
    time.sleep(0.1) # พักเครื่องนิดนึง
