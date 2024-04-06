'''
Creates an MQTT Device in Homeassistant and publishes Data from Senec Website as MQTT sensor data
'''
import os
import paho.mqtt.client as mqtt
import json
import time
import logging
from senec_webgrabber import SenecWebGrabber


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
     d = SenecMQTTDevice()
     d.loop()

class SenecMQTTDevice():

    def __init__(self) -> None:

        #OPTIONS
        self._options = self.read_options()

        self._MQTT_USERNAME = self._options['MQTT_USERNAME']
        self._MQTT_PASSWORD =  self._options['MQTT_PASSWORD']
        self._MQTT_HOST = self._options['MQTT_HOST']
        self._MQTT_PORT = int(self._options['MQTT_PORT'])
        self._TOPIC_PREFIX = self._options['MQTT_TOPIC_PREFIX']
        self._SENSOR_NAME_PREFIX = self._options['MQTT_SENSOR_NAME_PREFIX']
        self._DEVICE_NAME = self._options['MQTT_DEVICE_NAME']
        self._DEVICE_IDENTIFIER = self._options['MQTT_DEVICE_IDENTIFIER']
        self._DEVICE_MANUFACTURER = self._options['MQTT_DEVICE_MANUFACTURER']
        self._DEVICE_MODEL = self._options['MQTT_DEVICE_MODEL']
        self._DEVINCE_INFO = {
            "identifiers": [self._DEVICE_IDENTIFIER], 
            "name":  self._DEVICE_NAME,
            "manufacturer": self._DEVICE_MANUFACTURER, 
            "model": self._DEVICE_MODEL
        }
        self._FRIENDLY_NAMES = {
            "accuexport_total" : "Akku Entladung Gesamt",
            "accuexport_today" : "Akku Entladung Heute",
            "accuexport_now" : "Akku Entladung Momentanwert",
            "accuimport_total" : "Akku Beladung Gesamt" ,
            "accuimport_today" : "Akku Beladung Heute", 
            "accuimport_now" : "Akku Beladung Momentanwert",
            "gridimport_total" : "Netzstrom Bezug Gesamt", 
            "gridimport_today" : "Netzstrom Bezug Heute", 
            "gridimport_now" : "Netzstrom Bezug Momentanwert",
            "gridexport_total" : "Netzstrom Einspeisung Gesamt", 
            "gridexport_today" : "Netzstrom Einspeisung Heute", 
            "gridexport_now" : "Netzstrom Einspeisung Momentanwert",
            "powergenerated_total" : "PV Erzeugung Gesamt",
            "powergenerated_today" : "PV Erzeugung Heute",
            "powergenerated_now" : "PV Erzeugung Momentanwert",
            "consumption_total" : "Stromverbrauch Gesamt", 
            "consumption_today" : "Stromverbrauch Heute",
            "consumption_now" : "Stromverbrauch Momentanwert",
            "acculevel_now" : "Akku Fuellstand Momentanwert",
            "acculevel_today" : "Akku Fuellstand Heute",
        }    

        self._MQTT_SLEEP_TIME = 0.01 # [s] between sending messages
        self._RECONNECT_INTERVAL = 5 # [s] auto-reconnect interval
        self._UPDATE_INTERVAL = 30 # [s] webgrabber interval

        #CONFIG STATUS
        self._config_send=False
        
        #WEBGRABBER
        self._webgrabber = SenecWebGrabber()
        #MQTT
        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self.on_connect
        self._mqtt_client.on_disconnect = self.on_disconnect
        self._mqtt_client.username_pw_set(self._MQTT_USERNAME, self._MQTT_PASSWORD)
        self._mqtt_client.loop_start()

    def read_options(self) -> None:
        """ Read Options from Homeassitant configuration UI """
        with open('/data/options.json', mode="r") as options_file:
            options = json.load(options_file) 
        return options

    def connect(self) -> None:
         try:
              logger.info("Trying to connect to MQTT broker....")
              self._mqtt_client.connect(self._MQTT_HOST, self._MQTT_PORT)
              time.sleep(3)
         except ConnectionRefusedError:
              logger.info("Unable to connect - Connection refused. Trying again in " +str(self._RECONNECT_INTERVAL)+ "seconds")
              time.sleep(self._RECONNECT_INTERVAL)
              
    def on_connect(client, userdata, flags, reason_code, properties):
         logger.info("Connection to broker successfull! rc=" +str(reason_code))

    def on_disconnect(self, client, userdata, reason_code):
         logger.info("Disconnected from broker! rc=" + str(reason_code))

    def loop(self) -> None:
        while(True) :
            if (self._mqtt_client.is_connected()):
                 self.update()
                 self.send()
                 time.sleep(self._UPDATE_INTERVAL)
            else:
                 self.connect()
                  
    def send(self) -> None:
        if not self._config_send:
             self.send_config()
        self.send_states()

    def update(self) -> None:
        self._webgrabber.update()

    def send_config(self) -> None:
        logger.debug("Sending Config...")
        self.send_battery_config()
        self.send_power_config()
        self.send_energy_config()
        self._config_send=True

    def send_states(self) -> None:
        logger.debug("Sending States...")
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
            self._mqtt_client.publish(config_topic,json.dumps(config_payload),retain=True)
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
            self._mqtt_client.publish(config_topic,json.dumps(config_payload),retain=True)
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
            self._mqtt_client.publish(config_topic,json.dumps(config_payload),retain=True)
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
