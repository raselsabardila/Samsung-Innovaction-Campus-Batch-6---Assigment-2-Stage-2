from machine import Pin, ADC
import time
import dht
from umqtt.simple import MQTTClient
import network
import urequests
import json

DHT11_PIN = Pin(13, Pin.IN)
DHT11_SENSOR = dht.DHT11(DHT11_PIN)

LDR_SENSOR = ADC(Pin(32, Pin.IN))
LDR_SENSOR.atten(ADC.ATTN_11DB)

LED_RED = Pin(12, Pin.OUT)

TOKEN = "BBUS-gQsoaLCDYQyayeolFFSUN5LTq82WQg"
DEVICE_LABEL = "ESP32-DEVICE-1"
VARIABLE_LABEL = ["temperature", "humidity", "luminance", "led_red"]
MQTT_BROKER = "industrial.api.ubidots.com"
        
TOPIC = f"/v1.6/devices/{DEVICE_LABEL}"
CLIENT_ID = "ESP32-DEVICE-1"

URL_API = "http://192.168.0.114:5000/sensor"

PREV_VALUE_LDR = 0
PREV_VALUE_TEMP = 0
PREV_VALUE_HUM = 0

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, user=TOKEN, password="", port=1883)
    client.connect()
    
    print("Terhubung ke Ubidots MQTT Broker")
                
    return client
    
def send_data(client, value, label):
    payload = '{"%s": {"value": %s}}' % (label, value)
    client.publish(TOPIC, payload)
    
    print(f"Mengirim data UBIDOTS {label} : {value}")
    
    headers = {"Content-Type": "application/json"}
    data = {
        "sensor": {
            label: value
        }
    }
    data_json = json.dumps(data)

    print(data_json)
    
    response = urequests.post(URL_API, data=data_json, headers=headers)
    print(response.text)
    response.close()
    
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
        
        if(lumination != PREV_VALUE_LDR) :
            if(lumination <= 2000) :
                if(LED_RED.value() != 1) :
                    LED_RED.value(1)
                    send_data(client, 1, VARIABLE_LABEL[3])
            else :
                if(LED_RED.value() != 0) :
                    LED_RED.value(0)
                    send_data(client, 0, VARIABLE_LABEL[3])
        
        if(temperature != PREV_VALUE_TEMP) :
            send_data(client, temperature, VARIABLE_LABEL[0])
            
        if(humidity != PREV_VALUE_HUM) :
            send_data(client, humidity, VARIABLE_LABEL[1])
        
        if(lumination != PREV_VALUE_LDR) :
            send_data(client, lumination, VARIABLE_LABEL[2])
            
        PREV_VALUE_TEMP = temperature
        PREV_VALUE_HUM = humidity
        PREV_VALUE_LDR = lumination
    except OSError as error :
        print("Gagal membaca sensor: ", error)
        
    time.sleep(1)