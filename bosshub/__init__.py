import json
import time
import os
import sys

# --- Version Control ---
__version__ = "1.5.0-MQTT-Enterprise"
DEFAULT_MQTT_HOST = "141.98.19.212"
DEFAULT_MQTT_PORT = 1883

# --- Cross-Platform Detection & Imports ---
try:
    # ---------------- ESP32 / MicroPython ----------------
    from machine import unique_id, reset
    import urequests as requests
    from umqtt.simple import MQTTClient
    PLATFORM = "ESP32"
    
    def get_unique_id():
        return ''.join(['{:02x}'.format(b) for b in unique_id()])

except ImportError:
    # ---------------- PC / Server (Standard Python) ----------------
    import requests
    import uuid
    import threading
    try:
        import paho.mqtt.client as mqtt
        HAS_PAHO = True
    except ImportError:
        HAS_PAHO = False
        print("[BossHub Warning] 'paho-mqtt' not installed. MQTT features on PC will vary.")

    PLATFORM = "Python/PC"
    
    def get_unique_id():
        node = uuid.getnode()
        return ''.join(['{:02x}'.format((node >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])

class Client:
    """
    BossHub Enterprise Client (HTTP + MQTT)
    รองรับ: Real-time Command, Vending, Washing Machine, POS
    Target: 141.98.19.212
    """
    
    def __init__(self, api_key=None, server_url="https://api.bosshub.io/v1", mqtt_host=DEFAULT_MQTT_HOST, device_id=None):
        # 1. Setup Identity
        self.api_key = api_key or os.getenv('BOSSHUB_API_KEY')
        if not self.api_key:
            # ใน Dev Mode อาจจะยอมให้ผ่านไปก่อน แต่เตือน
            print("[BossHub Warning] API Key missing. HTTP features might fail.")

        self.device_id = device_id if device_id else get_unique_id()
        self.platform = PLATFORM
        
        # 2. Setup HTTP
        self.base_url = server_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Device-ID": self.device_id,
            "X-Platform": self.platform
        }

        # 3. Setup MQTT
        self.mqtt_host = mqtt_host
        self.mqtt_client = None
        self.mqtt_callbacks = {} # เก็บ function ที่ user สั่ง subscribe
        self.is_mqtt_connected = False
        
        print(f"[BossHub] Init Device: {self.device_id} ({self.platform}) -> MQTT: {self.mqtt_host}")

    # ==========================================
    # PART 1: MQTT SYSTEM (The New Engine)
    # ==========================================
    
    def connect_mqtt(self, on_message_callback=None):
        """เริ่มการเชื่อมต่อ MQTT (Auto Select Driver)"""
        self.user_on_message = on_message_callback
        client_id = f"bosshub-{self.device_id}"

        try:
            if PLATFORM == "ESP32":
                # --- MicroPython Logic ---
                self.mqtt_client = MQTTClient(client_id, self.mqtt_host, port=DEFAULT_MQTT_PORT)
                self.mqtt_client.set_callback(self._on_mqtt_message_wrapper)
                self.mqtt_client.connect()
                print("[BossHub MQTT] Connected (ESP32 Mode)")
            
            elif PLATFORM == "Python/PC":
                # --- PC/Server Logic (Paho) ---
                if not HAS_PAHO:
                    raise ImportError("Please run: pip install paho-mqtt")
                
                self.mqtt_client = mqtt.Client(client_id=client_id)
                self.mqtt_client.on_connect = self._on_paho_connect
                self.mqtt_client.on_message = self._on_paho_message
                self.mqtt_client.connect(self.mqtt_host, DEFAULT_MQTT_PORT, 60)
                self.mqtt_client.loop_start() # Background Thread
                print("[BossHub MQTT] Connected (PC Threaded Mode)")

            self.is_mqtt_connected = True
            
            # Subscribe ช่องทางมาตรฐานของตัวเองเสมอ
            # Topic: bosshub/devices/{device_id}/command
            self.subscribe(f"bosshub/devices/{self.device_id}/command")
            
        except Exception as e:
            print(f"[BossHub MQTT Error] Connect Failed: {e}")
            self.is_mqtt_connected = False

    def subscribe(self, topic, callback=None):
        """Subscribe Topic และผูก Callback เฉพาะ Topic นั้น (Optional)"""
        if not self.mqtt_client: return
        
        # ถ้ามี Callback เฉพาะเจาะจง ให้เก็บไว้
        if callback:
            self.mqtt_callbacks[topic] = callback
            
        # สั่ง Library subscribe
        if PLATFORM == "ESP32":
            self.mqtt_client.subscribe(topic)
        else:
            self.mqtt_client.subscribe(topic)
            
        print(f"[BossHub MQTT] Subscribed: {topic}")

    def publish(self, topic, payload):
        """Publish ข้อมูล (Auto Convert Dict/List to JSON)"""
        if not self.mqtt_client: return

        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload)
            
        try:
            self.mqtt_client.publish(topic, payload)
        except Exception as e:
            print(f"[BossHub MQTT Error] Publish failed: {e}")
            # TODO: Logic Auto-Reconnect for ESP32 could go here

    def mqtt_loop(self):
        """
        *** สำคัญสำหรับ ESP32 ***
        ต้องเอาไปใส่ใน while True ของ main.py
        สำหรับ PC ไม่ต้องใส่ เพราะใช้ Thread แล้ว
        """
        if PLATFORM == "ESP32" and self.mqtt_client:
            try:
                self.mqtt_client.check_msg()
            except OSError as e:
                print("[BossHub MQTT] Connection lost. Reconnecting...")
                self.reconnect_mqtt()

    def reconnect_mqtt(self):
        """ระบบกู้ชีพ Connection สำหรับ ESP32"""
        try:
            time.sleep(2)
            self.mqtt_client.connect()
            # ต้อง Subscribe ใหม่ทั้งหมดถ้าหลุด
            self.subscribe(f"bosshub/devices/{self.device_id}/command")
            print("[BossHub MQTT] Reconnected!")
        except Exception as e:
            print(f"[BossHub MQTT] Reconnect failed: {e}")

    # --- Internal MQTT Wrappers ---
    def _on_mqtt_message_wrapper(self, topic, msg):
        """ตัวกลางแปลงข้อมูลก่อนส่งให้ User (ESP32)"""
        topic_str = topic.decode()
        msg_str = msg.decode()
        self._process_message(topic_str, msg_str)

    def _on_paho_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[BossHub MQTT] Paho Connected Success.")
        else:
            print(f"[BossHub MQTT] Connection Refused code={rc}")

    def _on_paho_message(self, client, userdata, msg):
        """ตัวกลางแปลงข้อมูลก่อนส่งให้ User (PC)"""
        self._process_message(msg.topic, msg.payload.decode())

    def _process_message(self, topic, payload_str):
        """Logic กลางในการจัดการข้อความขาเข้า"""
        # 1. พยายามแปลง JSON
        try:
            data = json.loads(payload_str)
        except:
            data = payload_str # ถ้าไม่ใช่ JSON ก็ส่งเป็น String ดิบ

        print(f"[MSG] Topic: {topic} | Data: {data}")

        # 2. ถ้ามี Callback เฉพาะ Topic นั้น ให้เรียกใช้
        if topic in self.mqtt_callbacks:
            self.mqtt_callbacks[topic](data)
        
        # 3. ถ้าไม่มี หรือเป็น Global Callback ให้เรียกตัวหลัก
        elif self.user_on_message:
            self.user_on_message(topic, data)

    # ==========================================
    # PART 2: EXISTING HTTP HELPERS (ยังคงไว้)
    # ==========================================
    def _post(self, endpoint, payload):
        try:
            url = f"{self.base_url}/{endpoint}"
            payload['ts'] = time.time()
            payload['device_id'] = self.device_id
            response = requests.post(url, headers=self.headers, data=json.dumps(payload), timeout=5)
            if response.status_code in [200, 201]:
                return response.json()
            return None
        except Exception:
            return None

    def heartbeat(self):
        # ส่งทั้ง MQTT และ HTTP เพื่อความชัวร์ (Redundant)
        self.publish(f"bosshub/devices/{self.device_id}/status", {"status": "online", "ts": time.time()})
        return self._post("device/heartbeat", {})

    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
        self.publish(f"bosshub/devices/{self.device_id}/log", {"level": level, "msg": message})

# --- Helper ---
def connect(api_key=None, mqtt_host=DEFAULT_MQTT_HOST):
    return Client(api_key=api_key, mqtt_host=mqtt_host)
