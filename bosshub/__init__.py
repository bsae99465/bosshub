import json
import time
import os

__version__ = "0.1.0"

# --- Cross-Platform Import Strategy ---
# ตรวจสอบว่ารันบน MicroPython (ESP32) หรือ Python ปกติ
try:
    import urequests as requests
    PLATFORM = "ESP32/MicroPython"
except ImportError:
    import requests
    PLATFORM = "Python/Standard"

class Client:
    """
    Main Client class for interacting with BossHub Cloud.
    """
    
    def __init__(self, api_key=None, server_url="https://api.bosshub.io/v1"):
        # Support loading API KEY from Environment Variable
        self.api_key = api_key or os.getenv('BOSSHUB_API_KEY')
        
        if not self.api_key:
            raise ValueError("BossHub API Key is required! Pass it to connect() or set BOSSHUB_API_KEY env var.")

        self.base_url = server_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"BossHub-Client/{__version__} ({PLATFORM})",
            "X-Device-Platform": PLATFORM
        }
        
    def _post(self, endpoint, payload):
        """Internal helper for POST requests"""
        try:
            url = f"{self.base_url}/{endpoint}"
            # Timeout 10s เพื่อไม่ให้โปรแกรมค้างถ้าน็ตหลุด
            response = requests.post(url, headers=self.headers, data=json.dumps(payload), timeout=10)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                # Return dict with error info instead of None for better debugging
                return {"error": True, "status": response.status_code, "msg": response.text}
        except Exception as e:
            print(f"[BossHub Error] Connection failed: {e}")
            return {"error": True, "msg": str(e)}

    # --- Core Features ---
    def heartbeat(self, device_id):
        return self._post("device/heartbeat", {"device_id": device_id, "ts": time.time()})

    def log(self, level, message):
        """Send cloud logs"""
        # Print local debug
        print(f"[{level}] BossHub: {message}") 
        return self._post("system/log", {"level": level, "message": message})

    def get_config(self, key_name):
        """Fetch remote config for this device"""
        res = self._post("config/get", {"key": key_name})
        return res.get("value") if res else None

# --- Helper Factory ---
def connect(api_key=None):
    """Shortcut function to initialize the client"""
    return Client(api_key)
