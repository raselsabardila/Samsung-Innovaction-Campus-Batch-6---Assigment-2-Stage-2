from machine import Pin, ADC
import time
import dht
import network
from umqtt.simple import MQTTClient

DHT11_PIN = Pin(13, Pin.IN)
DHT11_SENSOR = dht.DHT11(DHT11_PIN)

LDR_SENSOR = ADC(Pin(32, Pin.IN))
LDR_SENSOR.atten(ADC.ATTN_11DB)

TOKEN = "BBUS-gQsoaLCDYQyayeolFFSUN5LTq82WQg"
DEVICE_LABEL = "ESP32-DEVICE-1"
VARIABLE_LABEL = ["temperature", "humidity", "luminance"]
MQTT_BROKER = "industrial.api.ubidots.com"

TOPIC = b"/v1.6/devices/%s" % DEVICE_LABEL.encode("utf-8")
CLIENT_ID = "ESP32-DEVICE-1"

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, user=TOKEN, password="", port=1883)
    client.connect()
    
    print("Terhubung ke Ubidots MQTT Broker")
                
    return client

def send_data(client, value, label):
    payload = '{"%s": {"value": %s}}' % (label, value)
    client.publish(TOPIC, payload)
    
    print("Data terkirim:", payload)

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    print("Menghubungkan ke WiFi...")
    
    while not wlan.isconnected():
        time.sleep(1)

    print("Terhubung ke WiFi:", wlan.ifconfig())

connect_wifi("Rachel", "icikiwir123")
client = connect_mqtt()

while True :
    try :
        DHT11_SENSOR.measure()
        
        temperature = DHT11_SENSOR.temperature()
        humidity = DHT11_SENSOR.humidity()
        
        lumination = LDR_SENSOR.read()			
        
        send_data(client, temperature, VARIABLE_LABEL[0])
        send_data(client, humidity, VARIABLE_LABEL[1])
        send_data(client, lumination, VARIABLE_LABEL[2])
        
        print(f"Suhu: {temperature}°C, Kelembaban: {humidity}%")
        print(f"Intensitas Cahaya : {lumination}")
    except OSError as error :
        print("Gagal membaca sensor: ", error)
        
    time.sleep(1)