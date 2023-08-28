'''
Creates an MQTT Device in Homeassistant and publishes Data from Senec Website as MQTT sensor data
'''

import paho.mqtt.client as mqtt
import json
import time
import logging
from senec_webgrabber import SenecWebGrabber

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
     d = SenecMQTTDevice()
     d.loop()

class SenecMQTTDevice():

    def __init__(self) -> None:
        #PARAMS Todo: Make configurable
        self._MQTT_USERNAME = ""  # your mqtt username
        self._MQTT_PASSWORD =  "" # your mqtt password
        self._MQTT_HOST = "" # IP adress of homeassitant when using home assistant mqtt broker, else IP adress of broker
        self._MQTT_PORT = 1883 # default MQTT port
        self._TOPIC_PREFIX = "homeassistant/sensor/" # topic that our mqtt data is published to
        self._SENSOR_NAME_PREFIX = "senec" #arbitrary, used for sensor name generation. results in e.g. "senec_acculevel_now" as sensorname
        self._DEVICE_NAME = "Senec Home V4" #arbitrary, used to generate the name of the MQTT device in HA
        self._DEVICE_IDENTIFIER = "XXXXXXXXXXXXXXX" #serial number of your senec (can be looked up in app), used for generation of entity unique ids
        self._DEVICE_MANUFACTURER = "Senec" #arbitrary, will be shown in MQTT device information
        self._DEVICE_MODEL = "Home V4" #arbitrary, will be shown in MQTT device information
        self._DEVINCE_INFO = {
            "identifiers": [self._DEVICE_IDENTIFIER], 
            "name":  self._DEVICE_NAME,
            "manufacturer": self._DEVICE_MANUFACTURER, 
            "model": self._DEVICE_MODEL
        }
        #Translation from API keys to friendly names in home assistant
        self._FRIENDLY_NAMES = {
            "accuexport_total" : "Akku-Einspeisung Gesamt",
            "accuexport_today" : "Akku-Einspeisung Heute",
            "accuexport_now" : "Akku-Einspeisung Momentanwert",
            "accuimport_total" : "Akku-Bezug Gesamt" ,
            "accuimport_today" : "Akku-Bezug Heute", 
            "accuimport_now" : "Akku-Bezug Momentanwert",
            "gridimport_total" : "Netzstrom-Bezug Gesamt", 
            "gridimport_today" : "Netzstrom-Bezug Heute", 
            "gridimport_now" : "Netzstrom-Bezug Momentanwert",
            "gridexport_total" : "Netzstrom-Einspeisung Gesamt", 
            "gridexport_today" : "Netzstrom-Einspeisung Heute", 
            "gridexport_now" : "Netzstrom-Einspeisung Momentanwert",
            "powergenerated_total" : "PV-Erzeugung Gesamt",
            "powergenerated_today" : "PV-Erzeugung Heute",
            "powergenerated_now" : "PV-Erzeugung Momentanwert",
            "consumption_total" : "Stromverbrauch Gesamt", 
            "consumption_today" : "Stromverbrauch Heute",
            "consumption_now" : "Stromverbrauch Momentanwert",
            "acculevel_now" : "Akku Fuellstand Momentanwert",
            "acculevel_today" : "Akku Fuellstand Heute", #available in API, but useless ? 
        }    


        self._MQTT_SLEEP_TIME = 0.01 # [s] interval between sending mqtt messages
        self._UPDATE_INTERVAL = 30 # [s] poll interval from senec api
        
        #WEBGRABBER
        self._webgrabber = SenecWebGrabber()
        #MQTT
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.username_pw_set(self._MQTT_USERNAME, self._MQTT_PASSWORD)
        self._mqtt_client.connect(self._MQTT_HOST, self._MQTT_PORT)
        #STATUS
        self._mqtt_config_send=False
        
    def loop(self) -> None:
        while(True) :
            self.update()
            self.send()
            time.sleep(self._UPDATE_INTERVAL)
            
        
    def send(self) -> None:
        if not self._mqtt_config_send:
            self.send_config()
        self.send_states()


    def update(self) -> None:
        self._webgrabber.update()


    def send_config(self) -> None:
        logger.debug("send_config()")
        self.send_battery_config()
        self.send_power_config()
        self.send_energy_config()
        self._mqtt_config_send=True   

    def send_states(self) -> None:
        logger.debug("send_states()")
        self.send_battery_states()
        self.send_power_states()
        self.send_energy_states()        


    def send_battery_config(self) -> None:
        for key in self._webgrabber._battery_entities:
            sensor_name = str(self._SENSOR_NAME_PREFIX + "_" + str(key))
            config_topic = str(self._TOPIC_PREFIX + sensor_name + "/config")
            state_topic = str(self._TOPIC_PREFIX + sensor_name + "/state")
            friendly_name = self._FRIENDLY_NAMES[key]
            config_payload = self.get_battery_config_payload(sensor_name, state_topic, friendly_name)
            logger.debug("senor_name: " + sensor_name)
            logger.debug("config_topic: " + config_topic)
            logger.debug("state_topic: " + state_topic)
            logger.debug("config_payload: " + str(config_payload))
            self._mqtt_client.publish(config_topic,json.dumps(config_payload))
            time.sleep(self._MQTT_SLEEP_TIME)
           
    def send_power_config(self) -> None:
        for key in self._webgrabber._power_entities:
            sensor_name = str(self._SENSOR_NAME_PREFIX + "_" + str(key))
            config_topic = str(self._TOPIC_PREFIX + sensor_name + "/config")
            state_topic = str(self._TOPIC_PREFIX + sensor_name + "/state")
            friendly_name = self._FRIENDLY_NAMES[key]
            config_payload = self.get_power_config_payload(sensor_name,state_topic, friendly_name)
            logger.debug("senor_name: " + sensor_name)
            logger.debug("config_topic: " + config_topic)
            logger.debug("state_topic: " + state_topic)
            logger.debug("config_payload: " + str(config_payload))
            self._mqtt_client.publish(config_topic,json.dumps(config_payload))
            time.sleep(self._MQTT_SLEEP_TIME)
            

    def send_energy_config(self) -> None:
        for key in self._webgrabber._energy_entities:
            sensor_name = str(self._SENSOR_NAME_PREFIX + "_" + str(key))
            config_topic = str(self._TOPIC_PREFIX + sensor_name + "/config")
            state_topic = str(self._TOPIC_PREFIX + sensor_name + "/state")
            friendly_name = self._FRIENDLY_NAMES[key]
            config_payload = self.get_energy_config_payload(sensor_name,state_topic, friendly_name)
            logger.debug("senor_name: " + sensor_name)
            logger.debug("config_topic: " + config_topic)
            logger.debug("state_topic: " + state_topic)
            logger.debug("config_payload: " + str(config_payload))
            self._mqtt_client.publish(config_topic,json.dumps(config_payload))
            time.sleep(self._MQTT_SLEEP_TIME)
          

    def send_battery_states(self) -> None:
        for key in self._webgrabber._battery_entities:
            sensor_name = str(self._SENSOR_NAME_PREFIX + "_" + str(key))
            state_topic = str(self._TOPIC_PREFIX + sensor_name + "/state")
            value = self._webgrabber._battery_entities[key]
            self._mqtt_client.publish(state_topic, str(round(value,2)))
            time.sleep(self._MQTT_SLEEP_TIME)
            

    def send_power_states(self) -> None:
        for key in self._webgrabber._power_entities:
            sensor_name = str(self._SENSOR_NAME_PREFIX + "_" + str(key))
            state_topic = str(self._TOPIC_PREFIX + sensor_name + "/state")
            value = self._webgrabber._power_entities[key]
            self._mqtt_client.publish(state_topic, str(round(value,2)))
            time.sleep(self._MQTT_SLEEP_TIME)
            

    def send_energy_states(self) -> None:
        for key in self._webgrabber._energy_entities:
            sensor_name = str(self._SENSOR_NAME_PREFIX + "_" + str(key))
            state_topic = str(self._TOPIC_PREFIX + sensor_name + "/state")
            value = self._webgrabber._energy_entities[key]
            self._mqtt_client.publish(state_topic, str(round(value,2)))
            time.sleep(self._MQTT_SLEEP_TIME)
            
    def get_battery_config_payload(self, sensor_name, state_topic, friendly_name) -> dict:  
        config_payload = {
            "device": self._DEVINCE_INFO,
            "name" : friendly_name,
            "device_class": "battery",
            "state_class": "measurement",
            "unit_of_measurement": "%",
            "state_topic":  state_topic,
            "unique_id": str(self._DEVICE_IDENTIFIER + "_" + sensor_name),
            "object_id" : sensor_name,
            "qos" : 0,
            "retain" : True,
            "force_update" : True
        }
        return config_payload
    
    def get_power_config_payload(self, sensor_name, state_topic, friendly_name) -> dict:  
        config_payload = {
            "device": self._DEVINCE_INFO,
            "name" : friendly_name,
            "device_class" : "power",
            "state_class" : "measurement",
            "unit_of_measurement" : "kW",
            "state_topic":  state_topic,
            "unique_id": str(self._DEVICE_IDENTIFIER + "_" + sensor_name),
            "object_id" : sensor_name,
            "qos" : 0,
            "retain" : True,
            "force_update" : True
        }
        return config_payload
    
    def get_energy_config_payload(self, sensor_name, state_topic, friendly_name) -> dict:  
        config_payload = {
            "device": self._DEVINCE_INFO,
            "name" : friendly_name,
            "device_class": "energy",
            "state_class": "total_increasing",
            "unit_of_measurement": "kWh",
            "state_topic":  state_topic,
            "unique_id": str(self._DEVICE_IDENTIFIER + "_" + sensor_name),
            "object_id" : sensor_name,
            "qos" : 0,
            "retain" : True,
            "force_update" : True
        }
        return config_payload

if __name__=="__main__":
    main()
