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
