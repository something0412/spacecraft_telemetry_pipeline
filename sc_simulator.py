import requests
import random
import time
from datetime import datetime, UTC

ENDPOINT = "http://localhost:8000/telemetry"
SPACECRAFT_ID = "SC-001"
INTERVAL = 1.0  # seconds

def generate_packet():
    # build and return a dict with all 7 fields
    temperature_bounds = (-40.0, 85.0)
    voltage_bounds = (22.0, 29.5)
    altitude_bounds = (400.0, 420.0)
    attitude_bounds = (-180.0, 180.0)
    packet = {
        'spacecraft_id': SPACECRAFT_ID,
        'timestamp': datetime.now(UTC).isoformat(),
        'temperature': random.uniform(temperature_bounds[0], temperature_bounds[1]),
        'battery_voltage': random.uniform(voltage_bounds[0], voltage_bounds[1]),
        'altitude': random.uniform(altitude_bounds[0], altitude_bounds[1]),
        'attitude': random.uniform(attitude_bounds[0], attitude_bounds[1]),
    }
    return packet

def send_packet(packet):
    # POST to ENDPOINT, print success or failure
    try:
        response = requests.post(ENDPOINT, json=packet)
        if not response.ok:
            print(f'Server returned: {response.status_code}')
        else:
            print(response.json())
    except requests.exceptions.RequestException as err:
        print(f"Couldn't connect: {err}")

def run():
    while True:
        packet = generate_packet()
        print(packet)
        send_packet(packet)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    run()