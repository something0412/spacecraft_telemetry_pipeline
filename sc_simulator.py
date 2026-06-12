import requests
import random
import time
from datetime import datetime, UTC

ENDPOINT = "http://localhost:8000/telemetry"
SPACECRAFT_ID = "SC-001"
INTERVAL = 1.0  # seconds

state = {
    'temperature': 20.5,
    'battery_voltage': 26.8,
    'altitude': 412.3,
    'attitude': -24.6,
}

def generate_packet():
    global state
    # build and return a dict with all 7 fields
    values = {
        'temperature': state['temperature'] + random.uniform(-0.5, 0.5),
        'battery_voltage': state['battery_voltage'] + random.uniform(-0.05, 0.05),
        'altitude': state['altitude'] + random.uniform(-0.1, 0.1),
        'attitude': state['attitude'] + random.uniform(-0.5, 0.5),
    }
    bounds = {
        'temperature': (-40.0,  85.0),
        'battery_voltage': (22.0,  29.5),
        'altitude': (400.0, 420.0),
        'attitude': (-180.0, 180.0),
    }
    state = {
        'temperature': max(bounds['temperature'][0], min(bounds['temperature'][1], values['temperature'])),
        'battery_voltage': max(bounds['battery_voltage'][0], min(bounds['battery_voltage'][1], values['battery_voltage'])),
        'altitude': max(bounds['altitude'][0], min(bounds['altitude'][1], values['altitude'])),
        'attitude': max(bounds['attitude'][0], min(bounds['attitude'][1], values['attitude'])),
    }

    packet = {
        'spacecraft_id': SPACECRAFT_ID,
        'timestamp': datetime.now(UTC).isoformat(),
        'temperature': state['temperature'],
        'battery_voltage': state['battery_voltage'],
        'altitude': state['altitude'],
        'attitude': state['attitude'],
    }

    # Random spike values to test value_out_of_bounds error handles
    if random.random() < 0.03:
        spike_field = random.choice(['temperature', 'battery_voltage', 'altitude', 'attitude'])
        if random.random() < 0.5:
            packet[spike_field] = random.uniform(bounds[spike_field][1], bounds[spike_field][1]+50.0)
        else:
            packet[spike_field] = random.uniform(bounds[spike_field][0]-50.0, bounds[spike_field][0])

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