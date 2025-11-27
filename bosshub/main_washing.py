import bosshub
import time

# เชื่อมต่อ (Device ID จะถูก Gen อัตโนมัติถ้าไม่ใส่)
client = bosshub.connect("API_KEY_HERExxxx")

def start_wash():
    print("User selected program. Waiting for payment...")
    
    # 1. ดึงราคาซักจาก Cloud (เผื่ออยากขึ้นราคา ไม่ต้องแก้โค้ด)
    price = client.get_config("wash_price_cold", default=30)
    print(f"Price: {price} THB")
    
    # สมมติเจน QR Code แล้วได้ REF มา
    ref_code = "QR-12345" 
    
    # 2. วนลูปเช็คยอดเงิน
    for _ in range(60): # รอ 60 วินาที
        if client.check_payment(ref_code):
            print("Payment Success! Starting Machine...")
            
            # แจ้ง Server ว่าเครื่องทำงานแล้ว (คนอื่นจะเห็นว่า Busy)
            client.update_status("BUSY")
            client.report_sale("SERVICE_WASH", price)
            
            # จำลองการซัก
            time.sleep(5) 
            
            # จบงาน
            client.update_status("IDLE")
            client.log("Wash Cycle Finished")
            return
            
        time.sleep(1)
    
    print("Timeout. Payment not received.")

# รัน
start_wash()

