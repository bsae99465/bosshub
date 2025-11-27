import json
import time
import os

# --- Version Control ---
__version__ = "1.0.0-Enterprise"

# --- Cross-Platform Detection (PC vs ESP32) ---
try:
    import urequests as requests
    import machine
    PLATFORM = "ESP32"
    def get_unique_id():
        # ดึง Unique ID จาก Hardware จริงของ ESP32
        return ''.join(['{:02x}'.format(b) for b in machine.unique_id()])
except ImportError:
    import requests
    import uuid
    PLATFORM = "Python/PC"
    def get_unique_id():
        # สร้าง ID จำลองสำหรับ PC (หรือดึงจาก MAC Address ก็ได้)
        node = uuid.getnode()
        return ''.join(['{:02x}'.format((node >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])

class Client:
    """
    BossHub Enterprise Client
    รองรับ: Vending, Washing Machine, POS
    """
    
    def __init__(self, api_key=None, server_url="https://api.bosshub.io/v1", device_id=None):
        self.api_key = api_key or os.getenv('BOSSHUB_API_KEY')
        if not self.api_key:
            raise ValueError("BossHub Error: API Key is missing.")

        # ถ้าไม่กำหนด device_id มา ให้ดึงจาก Hardware เองอัตโนมัติ
        self.device_id = device_id if device_id else get_unique_id()
        self.base_url = server_url.rstrip('/')
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Device-ID": self.device_id,
            "X-Platform": PLATFORM
        }
        
        print(f"[BossHub] Init Device: {self.device_id} on {PLATFORM}")

    def _post(self, endpoint, payload):
        """Internal Safe Request with Error Handling"""
        try:
            url = f"{self.base_url}/{endpoint}"
            # เพิ่ม Timestamp ป้องกัน Replay Attack
            payload['ts'] = time.time()
            payload['device_id'] = self.device_id
            
            # Timeout 10s เพื่อป้องกันโปรแกรมค้าง
            response = requests.post(url, headers=self.headers, data=json.dumps(payload), timeout=10)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"[BossHub Error] API {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"[BossHub Exception] Network Error: {e}")
            return None

    # ==========================================
    # 1. CORE IoT FUNCTIONS (พื้นฐาน)
    # ==========================================
    def heartbeat(self):
        """ส่งสัญญาณชีพ บอก Server ว่าเครื่องยังออนไลน์"""
        return self._post("device/heartbeat", {})

    def update_status(self, state, error_code=None):
        """
        อัปเดตสถานะเครื่อง
        state: 'IDLE', 'BUSY', 'ERROR', 'OFFLINE'
        """
        payload = {"state": state}
        if error_code:
            payload["error_code"] = error_code
        return self._post("device/status", payload)

    def log(self, message, level="INFO"):
        """ส่ง Log เข้า Cloud แทนการ print ดูหน้าจอ"""
        print(f"[{level}] {message}") 
        return self._post("device/log", {"level": level, "message": message})

    # ==========================================
    # 2. PAYMENT & COMMERCE (การเงิน/ขายของ)
    # ==========================================
    def check_payment(self, ref_code):
        """
        เช็คว่าลูกค้ายิง QR จ่ายเงินหรือยัง (สำหรับตู้ Vending/ซักผ้า)
        Return: True ถ้าจ่ายแล้ว, False ถ้ายัง
        """
        res = self._post("payment/check", {"ref_code": ref_code})
        if res and res.get("status") == "paid":
            return True
        return False

    def report_sale(self, product_id, price, payment_method="QR"):
        """
        บันทึกยอดขายและตัดสต็อก (POS/Vending)
        """
        payload = {
            "product_id": product_id,
            "amount": price,
            "method": payment_method
        }
        return self._post("sales/record", payload)

    def get_product_info(self, product_id):
        """ดึงราคาและชื่อสินค้าจาก Server (ไม่ต้อง Hardcode ในเครื่อง)"""
        res = self._post("product/info", {"product_id": product_id})
        return res # Return Dict {name: "Coke", price: 15}

    # ==========================================
    # 3. MAINTENANCE & CONFIG (ดูแลรักษา)
    # ==========================================
    def get_config(self, key, default=None):
        """
        ดึงค่าตั้งค่าจาก Cloud (เช่น ราคาซัก, อุณหภูมิตู้แช่)
        ทำให้เปลี่ยนค่าได้โดยไม่ต้องไปแก้โค้ดหน้างาน
        """
        res = self._post("device/config", {"key": key})
        if res and "value" in res:
            return res["value"]
        return default

    def check_ota_update(self, current_version):
        """เช็คว่ามี Firmware ใหม่ไหม (สำหรับ ESP32)"""
        res = self._post("firmware/check", {"version": current_version})
        if res and res.get("has_update"):
            return res.get("firmware_url")
        return None

# --- Quick Connect Helper ---
def connect(api_key=None):
    return Client(api_key)
