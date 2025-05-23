"""
Symulator urządzenia fitness - generuje i wysyła dane przez MQTT do Azure IoT Hub.
"""

import json
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt
import hmac
import hashlib
import base64
import urllib.parse
from config import IOT_HUB_NAME, DEVICE_ID, STORAGE_ACCOUNT_NAME, BLOB_CONTAINER_NAME, SIMULATION_INTERVAL

def generate_sas_token(hostname, device_id, key, expiry=3600):
    """Generuje token SAS dla urządzenia IoT Hub"""
    uri = f"{hostname}/devices/{device_id}"
    encoded_uri = urllib.parse.quote(uri, safe='')
    ttl = int(time.time()) + expiry
    sign_key = f"{encoded_uri}\n{ttl}"
    signature = base64.b64encode(
        hmac.new(
            base64.b64decode(key),
            sign_key.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    token = f"SharedAccessSignature sr={encoded_uri}&sig={urllib.parse.quote(signature)}&se={ttl}"
    return token

# Konfiguracja MQTT
HOST_NAME = "tf-iota7a8b266.azure-devices.net"
DEVICE_ID = "fitness_watch_1"
SHARED_ACCESS_KEY = "A2o8rjLjvMpRyWcaXZj+1RAJgYmeUvYzK3aEFiFredw="

MQTT_HOST = HOST_NAME
MQTT_PORT = 8883
MQTT_USERNAME = f"{HOST_NAME}/{DEVICE_ID}"
MQTT_PASSWORD = generate_sas_token(HOST_NAME, DEVICE_ID, SHARED_ACCESS_KEY)
MQTT_TOPIC = f"devices/{DEVICE_ID}/messages/events/"

# Zmienne globalne
client = None
connected = False

def on_connect(client, userdata, flags, rc):
    """Callback wywoływany po połączeniu z MQTT"""
    global connected
    if rc == 0:
        connected = True
        print("Połączono z IoT Hub")
    else:
        connected = False
        print(f"Błąd połączenia, kod: {rc}")

def on_disconnect(client, userdata, rc):
    """Callback wywoływany po rozłączeniu z MQTT"""
    global connected
    connected = False
    print("Rozłączono z IoT Hub")
    if rc != 0:
        print(f"Nieoczekiwane rozłączenie, kod: {rc}")
        # Próba ponownego połączenia
        time.sleep(10)
        try:
            client.reconnect()
        except:
            pass

def generate_heart_rate():
    """Generowanie realistycznych danych tętna"""
    base_rate = 70
    variation = random.randint(-5, 5)
    return max(60, min(100, base_rate + variation))

def generate_steps():
    """Generowanie liczby kroków"""
    return random.randint(0, 100)

def generate_temperature():
    """Generowanie temperatury ciała"""
    return round(36.5 + random.uniform(-0.2, 0.2), 1)

def generate_blood_oxygen():
    """Generowanie poziomu tlenu we krwi"""
    return round(95 + random.uniform(-2, 2), 1)

def generate_activity_data():
    """Generowanie danych aktywności"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "heart_rate": generate_heart_rate(),
        "steps": generate_steps(),
        "temperature": generate_temperature(),
        "blood_oxygen": generate_blood_oxygen(),
        "activity_type": random.choice(["walking", "running", "resting", "exercising"])
    }

def main():
    global client
    # Tworzenie klienta MQTT
    client = mqtt.Client(DEVICE_ID, protocol=mqtt.MQTTv311)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()
    
    # Ustawienie callbacków
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    try:
        # Połączenie z IoT Hub
        client.connect(MQTT_HOST, MQTT_PORT, 60)
        client.loop_start()
        
        # Główna pętla wysyłania danych
        while True:
            try:
                if connected:
                    data = generate_activity_data()
                    message = json.dumps(data)
                    
                    # Wysłanie wiadomości
                    client.publish(MQTT_TOPIC, message, qos=1)
                    print(f"Wysłano dane: {data}")
                else:
                    print("Oczekiwanie na połączenie...")
                
                time.sleep(SIMULATION_INTERVAL)
            except Exception as e:
                print(f"Błąd podczas wysyłania danych: {e}")
                time.sleep(5)
                
    except KeyboardInterrupt:
        print("\nZatrzymywanie symulatora...")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()

if __name__ == "__main__":
    main() 